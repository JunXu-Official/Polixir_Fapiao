import os
import re
import time
from PyPDF2 import PdfReader
from openpyxl import Workbook
from merge_pdfs import merge_pdfs
from rename_pdfs import rename_pdfs_by_travel_date

# --- Configuration ---
PDF_DIRECTORY = 'merge_pdf'
OUTPUT_EXCEL_FILE = '报销单.xlsx'
# --- End of Configuration ---

def create_expense_report():
    """
    Extracts details from PDFs and creates an Excel spreadsheet.
    """
    print(f"--- Creating Excel report from PDFs in: {PDF_DIRECTORY} ---\n")

    if not os.path.isdir(PDF_DIRECTORY):
        print(f"Error: Directory not found at '{PDF_DIRECTORY}'")
        return

    pdf_files = sorted([f for f in os.listdir(PDF_DIRECTORY) if f.lower().endswith('.pdf')])

    if not pdf_files:
        print("No PDF files found to process.")
        return

    # --- Regex Patterns ---
    date_pattern = re.compile(r'行程起止日期：(\d{4}-\d{2}-\d{2})')
    invoice_pattern = re.compile(r'发票号码\s*:\s*(\d+)')
    total_pattern = re.compile(r'（小写）\s*([\d.]+)')
    # --- End of Patterns ---

    # Create a new Excel workbook and select the active sheet
    wb = Workbook()
    ws = wb.active
    ws.title = "报销明细"

    # Write header row
    headers = ["时间", "费用类型", "报销金额", "发票号码"]
    ws.append(headers)

    # Process each PDF file
    for pdf_file in pdf_files:
        file_path = os.path.join(PDF_DIRECTORY, pdf_file)
        print(f"Processing file: {pdf_file}...")

        try:
            reader = PdfReader(file_path)
            full_text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])

            # Extract details using regex
            date_match = date_pattern.search(full_text)
            invoice_match = invoice_pattern.search(full_text)
            total_match = total_pattern.search(full_text)

            # Get the extracted data or set a default value
            travel_date = date_match.group(1) if date_match else '未找到'
            invoice_suffix = invoice_match.group(1)[-8:] if invoice_match else '未找到'
            total_amount = total_match.group(1) if total_match else '未找到'
            expense_type = "打车票"

            # Append the data as a new row to the Excel sheet
            ws.append([travel_date, expense_type, total_amount, invoice_suffix])
            print(f"  -> Added row: {travel_date}, {expense_type}, {total_amount}, {invoice_suffix}")

        except Exception as e:
            print(f"  Error processing file '{pdf_file}': {e}")
            ws.append(['错误', '错误', '错误', f"处理 {pdf_file} 失败"]) # Add an error row

    # Save the Excel file
    try:
        wb.save(OUTPUT_EXCEL_FILE)
        print(f"\n--- Successfully created Excel file: {OUTPUT_EXCEL_FILE} ---")
    except Exception as e:
        print(f"\nError saving Excel file: {e}")

if __name__ == '__main__':

    merge_pdfs()
    time.sleep(1) # Wait for merge to complete
    rename_pdfs_by_travel_date()
    time.sleep(1) # Wait for rename to complete
    create_expense_report()
