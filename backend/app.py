import os
import re
import json
import logging
from dotenv import load_dotenv
import openai
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pdfplumber
from pydantic import BaseModel
from rag import RAG  # Import the RAG class
from transformers import pipeline

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")

# Initialize FastAPI app
app = FastAPI()

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to extract text from a PDF file
def extract_pdf_text(filepath):
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for idx, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text
                else:
                    warning_msg = f"No text extracted from page {idx} in {filepath}"
                    logging.warning(warning_msg)
                    text += f"\n[No text found on page {idx}]"
    except Exception as e:
        error_msg = f"Error reading {filepath}: {e}"
        logging.error(error_msg)
        text += "\n" + error_msg
    return text

# Update base_path to point to the "resources" folder
base_path = os.path.join(os.path.dirname(__file__), "resources")
base_path1 = os.path.join(os.path.dirname(__file__))
# Load the output from output.txt (the ChatGPT knowledge base)
try:
    with open(os.path.join(base_path, "output.txt"), 'r', encoding='utf-8') as f:
        pdf_knowledge = f.read()
except Exception as e:
    logging.error(f"Error reading output.txt: {e}")
    pdf_knowledge = "No extracted knowledge available"

# Set your OpenAI API key from an environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize RAG with the knowledge base and OpenAI API key
rag = RAG(pdf_knowledge.split('\n'), openai.api_key)

# Initialize sentiment analysis and topic modeling pipelines
sentiment_analyzer = pipeline("sentiment-analysis")
topic_modeler = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# Define request models
class QueryRequest(BaseModel):
    query: str

class CompareRequest(BaseModel):
    report1: str
    report2: str

# Root endpoint (for testing)
@app.get("/", response_class=HTMLResponse)
async def index():
    with open("C:/Users/prati/Desktop/RAGING/frontend/index.html", "r", encoding="utf-8") as f:
        return f.read()

# Query endpoint with prompt engineering and JSON extraction via regex
@app.post("/api/query", response_class=JSONResponse)
async def query(request: QueryRequest):
    query_text = request.query
    # Retrieve relevant knowledge using RAG
    retrieved_knowledge = rag.retrieve(query_text)
    truncated_pdf_knowledge = "\n".join(retrieved_knowledge)

    # Build a system prompt that instructs GPT to respond with JSON including "answer" and "sources"
    system_prompt = (
        "You are an expert market research analyst using a RAG approach. "
        "Below is the extracted knowledge from various reports:\n\n" + truncated_pdf_knowledge + "\n\n"
        "When answering the user's query, provide your response strictly in JSON format with exactly two keys:\n"
        '"answer": a detailed explanation answering the query, and\n'
        '"sources": an array containing the exact sentences (as they appear in the extracted knowledge) that you used to form your answer.\n'
        "Make sure your JSON response does not include any additional text or formatting."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query_text}
            ],
            temperature=0.7
        )
        result = response.choices[0].message['content']
        logging.info("Raw GPT response: " + result)

        # Extract JSON using regex
        json_match = re.search(r'(\{.*\})', result, re.DOTALL)
        if json_match:
            try:
                parsed_response = json.loads(json_match.group(1))
                answer_text = parsed_response.get("answer", "")
                sources_list = parsed_response.get("sources", [])
            except Exception as parse_error:
                answer_text = result  # fallback to full response if parsing fails
                sources_list = []
        else:
            answer_text = result
            sources_list = []

        # Perform sentiment analysis on the answer text
        sentiment = sentiment_analyzer(answer_text)
        # Perform topic modeling on the answer text
        topics = topic_modeler(answer_text, candidate_labels=["finance", "strategy", "operations", "sustainability"])

        return JSONResponse(content={
            "status": "success",
            "answer": answer_text,
            "sources": sources_list,
            "sentiment": sentiment,
            "topics": topics,
            "source": "ChatGPT"
        })
    except openai.error.RateLimitError as e:
        error_msg = ("Rate limit error: You exceeded your current quota. "
                     "Please check your OpenAI account plan, billing details, and consult https://platform.openai.com/docs/guides/error-codes/api-errors.")
        logging.error(error_msg + f" Details: {e}")
        raise HTTPException(status_code=429, detail=error_msg)
    except Exception as e:
        error_msg = f"Query endpoint error: {e}"
        logging.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Compare endpoint with similar JSON output formatting
@app.post("/api/compare", response_class=JSONResponse)
async def compare(request: CompareRequest):
    report1 = request.report1
    report2 = request.report2
    prompt = (f"Using the knowledge extracted from the reports:\n\n{pdf_knowledge}\n\n"
              f"Compare the following two market research reports and provide a detailed analysis "
              f"highlighting similarities and differences. Additionally, list the specific sentences or sources from the extracted knowledge that support your analysis.\n\n"
              f"Report 1:\n{report1}\n\nReport 2:\n{report2}\n\n"
              "Provide your response strictly in JSON format with the following keys:\n"
              '"comparison": your detailed comparative analysis, and\n'
              '"sources": an array of sentences or source excerpts from the extracted knowledge used in your analysis.\n'
              "Ensure that your response is only a valid JSON object with no additional text."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in market research analysis using a RAG approach."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        result = response.choices[0].message['content']

        json_match = re.search(r'(\{.*\})', result, re.DOTALL)
        if json_match:
            try:
                parsed_response = json.loads(json_match.group(1))
                comparison_text = parsed_response.get("comparison", "")
                sources_list = parsed_response.get("sources", [])
            except Exception as e:
                comparison_text = result
                sources_list = []
        else:
            comparison_text = result
            sources_list = []

        return JSONResponse(content={
            "status": "success",
            "comparison": comparison_text,
            "sources": sources_list,
            "source": "ChatGPT"
        })
    except Exception as e:
        logging.error(f"Compare endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Run the app
if __name__ == "__main__":
    import uvicorn
    print("Starting app with OpenAI API Key:", openai.api_key)
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)
