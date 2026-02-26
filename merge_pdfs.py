import os
from PyPDF2 import PdfMerger

# --- Configuration ---
# IMPORTANT: Make sure the pdf files to be merged are in this directory
SOURCE_DIRECTORY = 'download_pdf'
# Merged files will be saved here
OUTPUT_DIRECTORY = 'merge_pdf'
# --- End of Configuration ---

def merge_pdfs():
    """
    Merges pairs of PDF files from the source directory and saves them
    to the output directory.
    """
    print(f"Searching for PDF files in: {SOURCE_DIRECTORY}")

    # Ensure output directory exists
    if not os.path.exists(OUTPUT_DIRECTORY):
        print(f"Creating output directory: {OUTPUT_DIRECTORY}")
        os.makedirs(OUTPUT_DIRECTORY)

    # Get all PDF files and sort them
    try:
        pdf_files = sorted([f for f in os.listdir(SOURCE_DIRECTORY) if f.lower().endswith('.pdf')])
    except FileNotFoundError:
        print(f"Error: Source directory not found at '{SOURCE_DIRECTORY}'")
        print("Please make sure the SOURCE_DIRECTORY is correct and contains your PDF files.")
        return

    if not pdf_files:
        print(f"No PDF files found in '{SOURCE_DIRECTORY}'. Nothing to merge.")
        return

    print(f"Found {len(pdf_files)} PDF files to process.")

    merged_file_count = 0
    # Process files in pairs
    for i in range(0, len(pdf_files), 2):
        # Get a pair of files
        file1 = pdf_files[i]
        try:
            file2 = pdf_files[i+1]
        except IndexError:
            print(f"Warning: Odd number of PDF files. '{file1}' will not be merged.")
            continue

        merger = PdfMerger()
        merged_file_count += 1
        output_filename = os.path.join(OUTPUT_DIRECTORY, f'1-{merged_file_count}.pdf')

        print(f"Merging '{file1}' and '{file2}' into '{output_filename}'")

        try:
            path1 = os.path.join(SOURCE_DIRECTORY, file1)
            path2 = os.path.join(SOURCE_DIRECTORY, file2)
            merger.append(path1)
            merger.append(path2)
            merger.write(output_filename)
            merger.close()
        except Exception as e:
            print(f"Error merging '{file1}' and '{file2}': {e}")

    print("\nPDF merging process completed.")
    if merged_file_count > 0:
        print(f"Successfully created {merged_file_count} merged PDF file(s) in '{OUTPUT_DIRECTORY}'.")
    else:
        print("No files were merged.")

if __name__ == '__main__':
    # --- Installation Note ---
    # This script requires the PyPDF2 library.
    # If you don't have it installed, run the following command in your terminal:
    # pip install PyPDF2
    # -------------------------
    merge_pdfs()
