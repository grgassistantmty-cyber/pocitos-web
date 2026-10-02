from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import random, io, datetime

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
    
    for p in range(1, cantidad+1):
        # Título de cada pocito
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height-50, f"POCITO #{p} - {nombre} {telefono} - {fecha}")
        
        y = height-100
        for j in range(1, 7): # 6 juegos por pocito
            numeros = random.sample(range(1, 76), 15)
            numeros.sort()
            
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, f"Juego {j}:")
            
            # Dibuja los 15 números en cuadritos bonitos
            x = 120
            c.setFont("Helvetica", 10)
            for num in numeros:
                c.rect(x, y-5, 30, 18)
                c.drawCentredString(x+15, y, str(num))
                x += 32
                if x > 550: # salto si se acaba la línea
                    break
            
            y -= 30
            if y < 50: # nueva página si se llena
                c.showPage()
                y = height-50
        
        if p < cantidad:
            c.showPage()

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"pocitos_{nombre}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run()
