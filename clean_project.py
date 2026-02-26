import os
import shutil

# --- Configuration ---
# Define the paths to the directories and files to be cleaned.
MERGE_DIR = 'merge_pdf'
DOWNLOAD_DIR = 'download_pdf' # As requested by the user
EXCEL_FILE = '报销单.xlsx'
# --- End of Configuration ---

def delete_files_in_dir(directory_path):
    """A helper function to delete all files within a given directory."""
    if not os.path.isdir(directory_path):
        print(f"Directory '{os.path.basename(directory_path)}' not found. Skipping.")
        return

    files = os.listdir(directory_path)
    if not files:
        print(f"Directory '{os.path.basename(directory_path)}' is already empty.")
        return

    print(f"Cleaning directory: '{os.path.basename(directory_path)}'...")
    for filename in files:
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
                print(f"  Deleted file: {filename}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                print(f"  Deleted sub-directory: {filename}")
        except Exception as e:
            print(f"  Failed to delete {file_path}. Reason: {e}")

def clean_project_files():
    """
    Main function to clean up all generated files and directories.
    """
    print("--- Starting project cleanup process ---\n")

    # 1. Clean the 'merge' directory
    delete_files_in_dir(MERGE_DIR)
    print("-" * 20)

    # 2. Clean the 'download_pdf' directory
    delete_files_in_dir(DOWNLOAD_DIR)
    print("-" * 20)

    # 3. Delete the Excel report file
    if os.path.isfile(EXCEL_FILE):
        try:
            os.remove(EXCEL_FILE)
            print(f"Deleted Excel report: {os.path.basename(EXCEL_FILE)}")
        except Exception as e:
            print(f"Failed to delete Excel file. Reason: {e}")
    else:
        print(f"Excel report '{os.path.basename(EXCEL_FILE)}' not found. Skipping.")
    
    print("\n--- Cleanup process completed. ---")

if __name__ == '__main__':
    clean_project_files()
