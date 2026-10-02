from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter, landscape
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
    # Hoja horizontal para que quepan las 6 tablas como en tu foto
    page_w, page_h = landscape(letter)
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    fecha = datetime.datetime.now().strftime("%d-%m-%Y")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BARAJA_DIR = os.path.join(BASE_DIR, "baraja")

    # Buscar cuantas imágenes tienes (54)
    archivos = [f for f in os.listdir(BARAJA_DIR) if f.lower().endswith('.jpg')]

    for p in range(1, cantidad+1):
        # Título
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, page_h-20, f"POCITO #{p} - {nombre} {telefono} - {fecha}")

        # 6 tablas: 3 arriba, 3 abajo
        tablas_x = [20, 275, 530]
        tablas_y = [page_h-270, 20] # arriba y abajo

        tabla_w = 235
        tabla_h = 235

        for idx in range(6):
            col = idx % 3
            fila = idx // 3
            x0 = tablas_x[col]
            y0 = tablas_y[fila]

            # Borde negro grueso como en tu foto
            c.setLineWidth(2)
            c.rect(x0, y0, tabla_w, tabla_h)

            # 16 cartas por tabla (4x4) - sin repetir dentro de la tabla
            numeros_tabla = random.sample(range(1, 76), 16)

            cols = 4
            rows = 4
            cell_w = tabla_w / cols
            cell_h = tabla_h / rows

            for r in range(rows):
                for cc in range(cols):
                    pos = r * cols + cc
                    num = numeros_tabla[pos]

                    cx = x0 + cc * cell_w
                    # y invertido porque reportlab empieza abajo
                    cy = y0 + (rows-1-r) * cell_h

                    # Dibuja cuadrito interno
                    c.setLineWidth(0.5)
                    c.rect(cx, cy, cell_w, cell_h)

                    img_name = f"{num:02d}.jpg"
                    img_path = os.path.join(BARAJA_DIR, img_name)

                    if os.path.exists(img_path):
                        # Dibuja la carta llenando la celda
                        c.drawImage(img_path, cx+1, cy+1, width=cell_w-2, height=cell_h-2, preserveAspectRatio=True)
                    else:
                        # Si te faltan las 21, pone el número
                        c.setFont("Helvetica-Bold", 10)
                        c.drawCentredString(cx+cell_w/2, cy+cell_h/2, str(num))

        c.showPage()

    c.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"pocitos_{nombre}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run()
