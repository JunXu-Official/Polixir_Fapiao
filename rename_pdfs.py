import os
import re
import time
from PyPDF2 import PdfReader
from merge_pdfs import merge_pdfs

# --- Configuration ---
PDF_DIRECTORY = 'merge_pdf'
# --- End of Configuration ---

def rename_pdfs_by_travel_date():
    """
    Renames PDF files based on the extracted travel date found within them.
    """
    print(f"--- Starting PDF renaming process in: {PDF_DIRECTORY} ---\n")

    if not os.path.isdir(PDF_DIRECTORY):
        print(f"Error: Directory not found at '{PDF_DIRECTORY}'")
        return

    pdf_files = [f for f in os.listdir(PDF_DIRECTORY) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print("No PDF files found to rename.")
        return

    # Regex to find the first date after the keyword.
    date_pattern = re.compile(r'行程起止日期：(\d{4}-\d{2}-\d{2})')

    for pdf_file in pdf_files:
        old_path = os.path.join(PDF_DIRECTORY, pdf_file)
        print(f"Processing file: '{pdf_file}'...")
        
        extracted_date = None
        try:
            reader = PdfReader(old_path)
            for page in reader.pages:
                text = page.extract_text()
                if not text:
                    continue
                
                match = date_pattern.search(text)
                if match:
                    extracted_date = match.group(1)
                    break # Found the date, no need to check other pages
            
            if extracted_date:
                new_filename = f"{extracted_date}_打车.pdf"
                new_path = os.path.join(PDF_DIRECTORY, new_filename)
                
                # Check if a file with the new name already exists
                if os.path.exists(new_path):
                    print(f"  Skipped: A file named '{new_filename}' already exists.")
                    continue

                os.rename(old_path, new_path)
                print(f"  Successfully renamed to '{new_filename}'")
            else:
                print("  Skipped: Could not find '行程起止日期' in this file.")

        except Exception as e:
            print(f"  Error processing file: {e}")

    print("\n--- Renaming process completed. ---")

if __name__ == '__main__':
    rename_pdfs_by_travel_date()
