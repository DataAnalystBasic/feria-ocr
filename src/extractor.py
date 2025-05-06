# src/extractor.py

import os
import re
import argparse
import cv2
import pandas as pd
import pytesseract

# -- 1) Configuración de Tesseract --
# Si no lo detecta automáticamente, descomenta y ajusta la ruta:
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\gonza\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)
def preprocess(img_path):
    """
    1) Leer en BGR.
    2) Pasar a gris.
    3) Aplicar CLAHE (ecualiza y resalta contrastes).
    4) Difuminar suavemente.
    5) Umbralizar en BINARIO inverso (texto claro sobre fondo oscuro).
    6) Cerrar pequeños huecos (morfología).
    """
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(gray)
    blur = cv2.GaussianBlur(cl, (3,3), 0)
    _, thr = cv2.threshold(blur, 0, 255,
                           cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    return cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel, iterations=1)

def ocr_image(img):
    """
    1) Llama a pytesseract.image_to_data para obtener cada palabra con su caja y confianza.
    2) Filtra solo las conf ≥ 50.
    3) Devuelve una lista de líneas (agrupando palabras por línea).
    """
    data = pytesseract.image_to_data(
        img,
        lang='spa+eng',
        config='--psm 6',   # asume un bloque de texto uniforme
        output_type=pytesseract.Output.DATAFRAME
    )
    # Filtrar por confianza
    data = data[data.confidence >= 50]
    lines = []
    # Agrupar por línea de texto reconocido
    for _, group in data.groupby('line_num'):
        text = ' '.join(group.text.astype(str).tolist())
        if text.strip():
            lines.append(text.strip())
    return lines

def parse_fields(lines):
    """
    1) Precio: busca todos los números “1.200” o “1200” y toma el mayor.
    2) Unidad: extrae 'kilo', 'kg', 'corte' o 'unidad'.
    3) Producto: de las líneas sin dígitos, escoge la palabra más larga.
    """
    # ——— PRECIOS —————————————————————————————————
    nums = []
    for l in lines:
        for m in re.findall(r'(\d{1,3}(?:\.\d{3})*)', l):
            nums.append(int(m.replace('.', '')))
    precio = str(max(nums)) if nums else ''

    # ——— UNIDADES ———————————————————————————————
    u = re.findall(r'\b(kilo|kg|corte|unidad)\b',
                   ' '.join(lines), flags=re.IGNORECASE)
    unidad = u[0].lower() if u else ''

    # ——— PRODUCTO ———————————————————————————————
    candidatos = [l.lower() for l in lines
                  if re.match(r'^[A-Za-záéíóúñ]+$', l)]
    producto = max(candidatos, key=len) if candidatos else ''

    return producto, unidad, precio

def main():
    parser = argparse.ArgumentParser(
        description="OCR feria: extrae producto, unidad y precio")
    parser.add_argument("-i","--input", required=True,
                        help="Carpeta con imágenes (.jpg/.png)")
    parser.add_argument("-o","--output", required=True,
                        help="Carpeta donde guardar resultados")
    parser.add_argument("-f","--format", choices=["csv","excel","json"],
                        default="csv", help="Formato de salida")
    args = parser.parse_args()

    registros = []
    for fname in os.listdir(args.input):
        if not fname.lower().endswith(('.jpg','.png')):
            continue
        ruta = os.path.join(args.input, fname)
        img_proc = preprocess(ruta)
        lines = ocr_image(img_proc)
        prod, uni, pre = parse_fields(lines)
        registros.append({
            'archivo': fname,
            'producto': prod,
            'unidad': uni,
            'precio': pre
        })

    df = pd.DataFrame(registros)
    os.makedirs(args.output, exist_ok=True)
    base = os.path.join(args.output, "resultados")
    if args.format == "csv":
        df.to_csv(base + ".csv", index=False, encoding="utf-8-sig")
    elif args.format == "excel":
        df.to_excel(base + ".xlsx", index=False)
    else:
        df.to_json(base + ".json", orient="records", force_ascii=False)

    print(f"✔ Resultados guardados en {args.output} como *.{args.format}")

if __name__ == "__main__":
    main()
