from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random, io, os, datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    nombre = request.form.get('nombre', 'Cliente')
    telefono = request.form.get('telefono', '')
    cantidad = int(request.form.get('cantidad', 1))
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    for p in range(1, cantidad+1):
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, height-40, f"POCITO #{p} - {nombre} - {telefono} - {fecha}")
        
        y = height-80
        for j in range(1, 7):
            numeros = random.sample(range(1, 76), 15)
            c.setFont("Helvetica-Bold", 11)
            c.drawString(40, y, f"Juego {j}:")
            
            x = 110
            for num in numeros:
                # Busca 01.jpg dentro de carpeta baraja/
                img_path = os.path.join(BASE_DIR, "baraja", f"{num:02d}.jpg")
                if os.path.exists(img_path):
                    c.drawImage(img_path, x, y-12, width=30, height=30)
                else:
                    # si no la encuentra, pone el numerito
                    c.rect(x, y-5, 28, 18)
                    c.drawCentredString(x+14, y, str(num))
                x += 34
            
            y -= 40
            if y < 70:
                c.showPage()
                y = height-50
        
        if p < cantidad:
            c.showPage()

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"pocitos_{nombre}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run()
