
import os
import re
import shutil
import time
import io
import zipfile
from flask import (Flask, render_template, request, redirect, url_for,
                   send_from_directory, flash, session, send_file)
from werkzeug.utils import secure_filename
# --- PyPDF2 Import Fix ---
# Use older, more compatible class names to avoid ImportError in some environments
from PyPDF2 import PdfFileReader, PdfFileMerger
# --- End of Fix ---
from openpyxl import Workbook

app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'download_pdf'
MERGED_FOLDER = 'merge_pdf'
GENERATED_FOLDER = 'generated'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MERGED_FOLDER'] = MERGED_FOLDER
app.config['GENERATED_FOLDER'] = GENERATED_FOLDER
app.config['SECRET_KEY'] = 'a_very_secret_key_for_prod'
# --- End of Configuration ---

# --- Custom Jinja2 Filter ---
@app.template_filter('basename')
def basename_filter(s):
    return os.path.basename(s)
# --- End of Filter ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_or_create_dir(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)

@app.route('/')
def index():
    session.clear()
    clear_or_create_dir(app.config['UPLOAD_FOLDER'])
    clear_or_create_dir(app.config['MERGED_FOLDER'])
    clear_or_create_dir(app.config['GENERATED_FOLDER'])
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files_route():
    if 'files[]' not in request.files:
        flash('没有文件被选择', 'danger')
        return redirect(url_for('index'))

    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        flash('未选择任何有效文件', 'warning')
        return redirect(url_for('index'))

    upload_dir = app.config['UPLOAD_FOLDER']
    clear_or_create_dir(upload_dir)
    
    uploaded_filepaths = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.abspath(os.path.join(upload_dir, filename))
            file.save(filepath)
            uploaded_filepaths.append(filepath)
    
    session['uploaded_files'] = sorted(uploaded_filepaths)
    flash(f'{len(uploaded_filepaths)} 个文件上传成功!', 'success')
    return render_template('index.html', uploaded_files=session['uploaded_files'])

@app.route('/merge', methods=['POST'])
def merge_files_route():
    if 'uploaded_files' not in session:
        flash('请先上传PDF文件。', 'warning')
        return redirect(url_for('index'))

    try:
        clear_or_create_dir(app.config['MERGED_FOLDER'])
        merge_logic(app.config['UPLOAD_FOLDER'], app.config['MERGED_FOLDER'])
        time.sleep(1)
        rename_logic(app.config['MERGED_FOLDER'])
        
        merged_files = sorted(os.listdir(app.config['MERGED_FOLDER']))
        session['merged_files'] = merged_files
        
        flash('PDF文件预处理成功!', 'success')
        return render_template('index.html', 
                               uploaded_files=session.get('uploaded_files'), 
                               merged_files=session.get('merged_files'))
    except Exception as e:
        flash(f'处理文件时出错: {e}', 'danger')
        return render_template('index.html', uploaded_files=session.get('uploaded_files'))

@app.route('/generate', methods=['POST'])
def generate_report_route():
    if 'merged_files' not in session:
        flash('请先预处理PDF文件。', 'warning')
        return render_template('index.html', uploaded_files=session.get('uploaded_files'))

    try:
        clear_or_create_dir(app.config['GENERATED_FOLDER'])
        report_filename = report_logic(app.config['MERGED_FOLDER'], app.config['GENERATED_FOLDER'])
        session['report_filename'] = report_filename
        
        flash('报销单已成功生成!', 'success')
        return render_template('index.html', 
                               uploaded_files=session.get('uploaded_files'), 
                               merged_files=session.get('merged_files'),
                               report_filename=session.get('report_filename'))
    except Exception as e:
        flash(f'生成报销单时出错: {e}', 'danger')
        return render_template('index.html', 
                               uploaded_files=session.get('uploaded_files'), 
                               merged_files=session.get('merged_files'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['GENERATED_FOLDER'], filename, as_attachment=True)

@app.route('/download_all')
def download_all_route():
    if 'merged_files' not in session or not session['merged_files']:
        flash('没有可供下载的发票文件。', 'warning')
        return redirect(url_for('index'))

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        merged_dir = app.config['MERGED_FOLDER']
        for filename in session['merged_files']:
            file_path = os.path.join(merged_dir, filename)
            if os.path.exists(file_path):
                zf.write(file_path, arcname=filename)

    memory_file.seek(0)
    return send_file(memory_file, download_name='报销发票.zip', as_attachment=True, mimetype='application/zip')

# --- Logic Functions (adapted for older PyPDF2) ---

def merge_logic(source_dir, output_dir):
    pdf_files = sorted([f for f in os.listdir(source_dir) if f.lower().endswith('.pdf')])
    if not pdf_files:
        raise Exception("没有找到可合并的PDF文件。")

    merged_count = 0
    for i in range(0, len(pdf_files), 2):
        file1_path = os.path.join(source_dir, pdf_files[i])
        if i + 1 >= len(pdf_files):
            shutil.copy(file1_path, os.path.join(output_dir, f'1-{merged_count + 1}.pdf'))
            continue

        file2_path = os.path.join(source_dir, pdf_files[i+1])
        merger = PdfFileMerger()
        merged_count += 1
        output_filename = os.path.join(output_dir, f'1-{merged_count}.pdf')
        merger.append(file1_path)
        merger.append(file2_path)
        with open(output_filename, "wb") as f_out:
            merger.write(f_out)
        merger.close()

def rename_logic(pdf_dir):
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    date_pattern = re.compile(r'行程起止日期：(\d{4}-\d{2}-\d{2})')

    for pdf_file in pdf_files:
        old_path = os.path.join(pdf_dir, pdf_file)
        try:
            with open(old_path, 'rb') as f:
                reader = PdfFileReader(f)
                extracted_date = None
                for page_num in range(reader.numPages):
                    text = reader.getPage(page_num).extractText()
                    if text and (match := date_pattern.search(text)):
                        extracted_date = match.group(1)
                        break
            
            if extracted_date:
                base_filename = f"{extracted_date}_打车"
                new_filename = f"{base_filename}.pdf"
                new_path = os.path.join(pdf_dir, new_filename)
                
                counter = 1
                while os.path.exists(new_path):
                    new_filename = f"{base_filename}_{counter}.pdf"
                    new_path = os.path.join(pdf_dir, new_filename)
                    counter += 1
                
                os.rename(old_path, new_path)
        except Exception as e:
            print(f"重命名文件 {pdf_file} 时出错: {e}")

def report_logic(pdf_dir, output_dir):
    output_file = os.path.join(output_dir, '报销单.xlsx')
    pdf_files = sorted([f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')])

    wb = Workbook()
    ws = wb.active
    ws.title = "报销明细"
    ws.append(["时间", "费用类型", "报销金额", "发票号码"])

    date_pattern = re.compile(r'行程起止日期：(\d{4}-\d{2}-\d{2})')
    invoice_pattern = re.compile(r'发票号码\s*:\s*(\d+)')
    total_pattern = re.compile(r'（小写）\s*([\d.]+)')

    for pdf_file in pdf_files:
        file_path = os.path.join(pdf_dir, pdf_file)
        try:
            full_text = ""
            with open(file_path, 'rb') as f:
                reader = PdfFileReader(f)
                for page_num in range(reader.numPages):
                    page_text = reader.getPage(page_num).extractText()
                    if page_text:
                        full_text += page_text

            date_match = date_pattern.search(full_text)
            invoice_match = invoice_pattern.search(full_text)
            total_match = total_pattern.search(full_text)

            travel_date = date_match.group(1) if date_match else '未找到'
            invoice_suffix = invoice_match.group(1)[-8:] if invoice_match else '未找到'
            total_amount = total_match.group(1) if total_match else '未找到'
            
            ws.append([travel_date, "打车票", total_amount, invoice_suffix])
        except Exception as e:
            ws.append(['错误', '错误', '错误', f"处理 {pdf_file} 失败: {e}"])

    wb.save(output_file)
    return os.path.basename(output_file)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
