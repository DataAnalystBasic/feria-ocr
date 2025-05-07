import os, re, argparse
import cv2
import pandas as pd
import pytesseract
import imutils
from imutils.perspective import four_point_transform
from rapidfuzz import process, fuzz
from catalogo import PRODUCTOS, UNIDADES

# Ajusta a tu ruta:
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\gonza\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)

# ---------- 1. LOCALIZAR Y ENDEREZAR EL CARTEL -----------------
def encontrar_cartel(img):
    """Devuelve el recorte warp de la región más grande de 4 lados (posible pizarra)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blur, 50, 150)

    cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[0]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02*peri, True)
        if len(approx) == 4 and cv2.contourArea(c) > 5000:
            return four_point_transform(img, approx.reshape(4,2))
    # fallback: imagen entera
    return img

# ---------- 2. PRE‑PROCESADO + OCR MULTI‑PASO -------------------
def ocr_lineas(img):
    """Devuelve conjunto de líneas tras dos pasadas de Tesseract."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # CLAHE mejora contraste
    clahe = cv2.createCLAHE(2.0, (8,8))
    proc = clahe.apply(gray)
    proc = cv2.GaussianBlur(proc, (3,3), 0)
    # escalar ×2
    proc = cv2.resize(proc, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    lineas = set()
    for psm in [6, 7]:
        df = pytesseract.image_to_data(
            proc, lang="spa+eng",
            config=f"--psm {psm}",
            output_type=pytesseract.Output.DATAFRAME
        )
        if 'conf' not in df:               # OCR vacío
            continue
        df['conf'] = pd.to_numeric(df['conf'], errors='coerce')
        df = df[df['conf'] >= 50]
        for _, g in df.groupby('line_num'):
            linea = ' '.join(g.text.astype(str))
            if linea.strip():
                lineas.add(linea.strip())
    return list(lineas)

# ---------- 3. PARSEO + FUZZY MATCH -----------------------------
def mejor_coincidencia(candidatos, catalogo, umbral=70):
    if not candidatos: return ''
    texto = max(candidatos, key=len).lower()
    match, score, _ = process.extractOne(texto, catalogo,
                                         scorer=fuzz.token_sort_ratio)
    return match if score >= umbral else texto  # si falla, deja OCR tal cual

def extraer_campos(lineas):
    # precio
    nums = [int(x.replace('.',''))
            for l in lineas for x in re.findall(r'\d{1,3}(?:\.\d{3})*', l)]
    precio = str(max(nums)) if nums else ''

    # unidad
    uni_raw = re.findall(r'\b(k?g|kilo|corte|unidad)\b',
                         ' '.join(lineas), flags=re.IGNORECASE)
    unidad = mejor_coincidencia(uni_raw, UNIDADES)

    # producto
    candidatos = [l for l in lineas if re.fullmatch(r'[A-Za-zÁÉÍÓÚÑáéíóúñ ]+', l)]
    producto = mejor_coincidencia(candidatos, PRODUCTOS)

    return producto, unidad, precio

# ---------- 4. PIPELINE -----------------------------------------
def procesar_imagen(ruta):
    img = cv2.imread(ruta)
    cartel = encontrar_cartel(img)
    lineas = ocr_lineas(cartel)
    return extraer_campos(lineas)

# ---------- 5. CLI ----------------------------------------------
def main():
    ap = argparse.ArgumentParser("OCR feria mejorado")
    ap.add_argument("-i","--input", required=True)
    ap.add_argument("-o","--output", required=True)
    ap.add_argument("-f","--format", choices=['csv','excel','json'],
                    default='csv')
    args = ap.parse_args()

    registros = []
    for fn in os.listdir(args.input):
        if fn.lower().endswith(('.jpg','.png')):
            p, u, pr = procesar_imagen(os.path.join(args.input, fn))
            registros.append({'archivo': fn,
                              'producto': p, 'unidad': u, 'precio': pr})

    df = pd.DataFrame(registros)
    os.makedirs(args.output, exist_ok=True)
    base = os.path.join(args.output, "resultados")
    if args.format=='csv':
        df.to_csv(base+".csv", index=False, encoding='utf-8-sig')
    elif args.format=='excel':
        df.to_excel(base+".xlsx", index=False)
    else:
        df.to_json(base+".json", orient='records', force_ascii=False)

    print(f"✔ Generado {base}.{args.format}")

if __name__ == "__main__":
    main()
