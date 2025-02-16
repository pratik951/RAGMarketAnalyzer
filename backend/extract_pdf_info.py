from pdf2image import convert_from_path
import pytesseract

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pdf_to_txt(input_pdf, output_txt):
    try:
        # Ensure poppler_path is correctly set
        images = convert_from_path(input_pdf, poppler_path=r'C:\Users\prati\Desktop\RAGING\poppler-24.08.0\Library\bin')
        text = ""
        for i, image in enumerate(images):
            page_text = pytesseract.image_to_string(image)
            text += page_text + "\n"
        with open(output_txt, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)
        print(f"Successfully converted {input_pdf} to {output_txt} using Tesseract OCR.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def pdfs_to_txt(input_pdfs, output_txt):
    try:
        text = ""
        for input_pdf in input_pdfs:
            text += f"\n----- Text from {input_pdf} -----\n"
            images = convert_from_path(input_pdf, poppler_path=r'C:\Users\prati\Desktop\RAGING\poppler-24.08.0\Library\bin')
            for image in images:
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"
        with open(output_txt, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)
        print(f"Successfully converted PDFs to {output_txt} using Tesseract OCR.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    input_pdfs = [
        r'C:\Users\prati\Desktop\RAGING\backend\resources\2023-conocophillips-aim-presentation.pdf',
        r'C:\Users\prati\Desktop\RAGING\backend\resources\2024-conocophillips-proxy-statement.pdf'  # Replace with the actual second PDF path if needed
    ]
    pdfs_to_txt(input_pdfs, r'C:\Users\prati\Desktop\RAGING\backend\resources\output.txt')
    # The generated output.txt can now be used as the knowledge base for ChatGPT RAG integration.