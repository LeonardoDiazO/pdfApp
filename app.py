from flask import Flask, render_template, request, send_file, redirect, url_for
from PyPDF2 import PdfReader, PdfWriter
import os
from werkzeug.utils import secure_filename
# from waitress import serve

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def merge_pdfs(pdf_paths, output_path):
    writer = PdfWriter()
    for pdf_path in pdf_paths:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            writer.add_page(page)
    with open(output_path, "wb") as f:
        writer.write(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        files = request.files.getlist('pdfs')
        order = request.form.get('order', '')  # ejemplo: "2,0,1"

        if not order:
            return "Orden de archivos no especificada", 400

        try:
            order_indices = list(map(int, order.split(",")))
        except ValueError:
            return "Formato de orden inválido", 400

        uploaded_files = []
        for i, file in enumerate(files):
            if file.filename.endswith('.pdf'):
                filename = secure_filename(f"{i}_{file.filename}")
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(path)
                uploaded_files.append(path)

        try:
            ordered_paths = [uploaded_files[i] for i in order_indices]
        except IndexError:
            return "Error en la correspondencia del orden", 400

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'merged_output.pdf')
        merge_pdfs(ordered_paths, output_path)

        for path in uploaded_files:
            os.remove(path)

        return send_file(output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    # Para desarrollo:
    app.run(debug=True)

    # Para producción con waitress:
    # serve(app, host='0.0.0.0', port=10000)
