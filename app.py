from flask import Flask, render_template, request, send_file, url_for
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os, random, datetime, io
from PIL import Image

app = Flask(__name__)

# --- GENERADOR PDF (MISMA LÓGICA QUE TU .EXE) ---
def generar_pdf_web(num_tabloides, orientacion):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    w, h = letter
    if orientacion == "H":
        w, h = h, w
        c.setPageSize((w, h))

    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    nombre_pdf = f"POCITOS_6_JUEGOS_X_TABLOIDE_{num_tabloides}tab_{orientacion}_{fecha}.pdf"
    
    # Simulación de generación (aquí va tu lógica real de pocitos)
    for i in range(num_tabloides):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, h-40, f"POCITO #{i+1} - Eliud Monsivais 8115566250 - {fecha}")
        # Dibuja 6 tablitas por hoja
        y = h - 80
        for j in range(6):
            c.setFont("Helvetica", 10)
            c.drawString(40, y, f"Juego {j+1}: " + " - ".join([str(random.randint(1,75)) for _ in range(15)]))
            y -= 20
        c.showPage()

    c.save()
    buffer.seek(0)
    
    # Guarda temporal
    path = f"/tmp/{nombre_pdf}"
    with open(path, "wb") as f:
        f.write(buffer.getvalue())
    return path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    try:
        num = int(request.form.get('num_tabloides', 5))
        num = max(1, min(500, num))
        ori = request.form.get('orientacion', 'H')
        pdf_path = generar_pdf_web(num, ori)
        return send_file(pdf_path, as_attachment=True, download_name=os.path.basename(pdf_path))
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)