# RAG-Powered Market Research Analysis Tool

This project is a web application that implements a Retrieval-Augmented Generation (RAG) system to analyze and compare market research reports. Users can input natural language queries to receive AI-generated insights along with source references.

## Project Structure

```
project-root/
├── backend/
│   ├── app.py
│   ├── extract_pdf_info.py
│   ├── rag.py
│   ├── requirements.txt
│   └── resources/
│       ├── 2023-conocophillips-aim-presentation.pdf
│       ├── 2024-conocophillips-proxy-statement.pdf
│       └── output.txt
├── frontend/
│   ├── index.html
│   ├── main.js
│   └── styles.css
├── .env
└── README.md
```

## Setup and Run Instructions

### Backend
1. **Navigate to the `backend` directory:**
   ```bash
   cd backend
   ```
2. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the FastAPI application:**
   ```bash
   uvicorn app:app --reload
   ```
   The backend server will start on [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Frontend
- Open the `frontend/index.html` file in your web browser.
- Use the "Submit Query" button to get insights.

## Features
- **AI-Powered Insights:** Uses a dummy RAG pipeline implementation (to be extended with a real RAG system).
- **Natural Language Query Interface:** Users can input queries to receive insights.
- **Double-Clickable Source:** Results include a double-clickable link to reveal source information.
- **Sentiment Analysis:** Provides sentiment analysis of the AI-generated insights.
- **Topic Modeling:** Identifies and displays topics related to the AI-generated insights.



