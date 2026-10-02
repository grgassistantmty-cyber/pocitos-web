import os, random
from collections import Counter
from datetime import datetime
from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import landscape, portrait
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
import io

app = Flask(__name__)

PLANTILLA_CHICAS = [
    [("A","G"), ("B","H"), ("C","I"), ("D","J"), ("E","K"), ("F","L")],
    [("G","M"), ("H","N"), ("I","O"), ("J","P"), ("K","Q"), ("L","R")],
    [("M","A"), ("N","B"), ("O","C"), ("P","D"), ("Q","E"), ("R","F")],
    [("A","S"), ("B","T"), ("C","U"), ("D","V"), ("E","W"), ("F","X")],
    [("S","M"), ("T","N"), ("U","O"), ("V","P"), ("W","Q"), ("X","R")],
]
LETRAS = sorted(list(set([l for fila in PLANTILLA_CHICAS for pocito in fila for l in pocito])))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BARAJA_DIR = os.path.join(BASE_DIR, "baraja")

def generar_pdf_bytes(num_tabloides, orientacion):
    if not os.path.exists(BARAJA_DIR):
        raise Exception(f"No existe carpeta baraja en {BARAJA_DIR}")
    cartas = sorted([f for f in os.listdir(BARAJA_DIR) if f.lower().endswith(('.jpg','.jpeg','.png'))])
    if len(cartas) < 54:
        raise Exception(f"Solo hay {len(cartas)} cartas, necesitas 54")

    contador = Counter()
    buffer = io.BytesIO()

    if "H" in orientacion or "h" in orientacion.lower():
        PAGE_W, PAGE_H = landscape((11*inch, 17*inch))
        J_COLS, J_ROWS = 3, 2
    else:
        PAGE_W, PAGE_H = portrait((11*inch, 17*inch))
        J_COLS, J_ROWS = 2, 3

    c = canvas.Canvas(buffer, pagesize=(PAGE_W, PAGE_H))

    for _ in range(num_tabloides):
        margen = 0.15*inch
        sep = 0.28*inch
        area_w = PAGE_W - margen*2 - sep*(J_COLS-1)
        area_h = PAGE_H - margen*2 - sep*(J_ROWS-1)
        juego_w = area_w / J_COLS
        juego_h = area_h / J_ROWS

        for jr in range(J_ROWS):
            for jc in range(J_COLS):
                j_x = margen + jc*(juego_w + sep)
                j_y = margen + (J_ROWS-1-jr)*(juego_h + sep)

                todas = sorted(cartas, key=lambda x: contador[x])
                grandes = todas[:30]
                random.shuffle(grandes)
                for g in grandes: contador[g] += 1

                chicas_rest = [x for x in cartas if x not in grandes]
                random.shuffle(chicas_rest)
                # Si faltan letras, repite
                while len(chicas_rest) < len(LETRAS):
                    chicas_rest += chicas_rest
                mapa = {letra: img for letra, img in zip(LETRAS, chicas_rest)}

                COLS, ROWS = 6, 5
                cell_w = juego_w / COLS
                cell_h = juego_h / ROWS

                for r in range(ROWS):
                    for col_idx in range(COLS):
                        g_idx = col_idx*5 + r
                        grande_img = grandes[g_idx]
                        lt, lb = PLANTILLA_CHICAS[r][col_idx]
                        x = j_x + col_idx*cell_w
                        y = j_y + (ROWS-1-r)*cell_h
                        g_w = cell_w * 0.615
                        s_w = cell_w - g_w
                        s_h = cell_h / 2
                        try:
                            c.drawImage(ImageReader(os.path.join(BARAJA_DIR, grande_img)), x, y, width=g_w, height=cell_h, preserveAspectRatio=True)
                            c.drawImage(ImageReader(os.path.join(BARAJA_DIR, mapa[lt])), x+g_w, y+s_h, width=s_w, height=s_h, preserveAspectRatio=True)
                            c.drawImage(ImageReader(os.path.join(BARAJA_DIR, mapa[lb])), x+g_w, y, width=s_w, height=s_h, preserveAspectRatio=True)
                        except Exception as e:
                            print(f"Error imagen: {e}")
                        c.setLineWidth(0.8)
                        c.rect(x, y, cell_w, cell_h)
                c.setLineWidth(3)
                c.rect(j_x, j_y, juego_w, juego_h)
        c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    try:
        num = int(request.form.get('cantidad', 5))
        ori = request.form.get('orientacion', 'Horizontal')
        pdf = generar_pdf_bytes(num, ori)
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        return send_file(pdf, as_attachment=True, download_name=f"POCITOS_{num}tab_{fecha}.pdf", mimetype='application/pdf')
    except Exception as e:
        return f"<h1>Error: {e}</h1><p>Revisa que en GitHub tengas la carpeta baraja con 54 jpg</p><a href='/'>Volver</a>", 500

if __name__ == '__main__':
    app.run()
