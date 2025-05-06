# src/extractor.py

import os
import re
import argparse
import easyocr
import cv2
import pandas as pd

def preprocess(path):
    """
    1) Lee la imagen en escala de grises.
    2) Ecualiza el histograma (mejora contraste).
    3) Difumina para reducir ruido.
    4) Aplica umbral Otsu inverso (texto claro sobre fondo oscuro).
    5) Cierra pequeños huecos en las letras (morfología).
    """
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(
        blur, 0, 255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    return morph

def ocr_text(preproc_img, reader):
    """
    Ejecuta OCR con detalle para obtener bounding boxes y confianza.
    Filtra solo los textos con confianza ≥ 0.4.
    """
    results = reader.readtext(preproc_img, detail=1)
    lines = [text for box, text, conf in results if conf >= 0.4]
    return lines

def parse_fields(lines):
    """
    1) Precio: busca todos los números formateados (p. ej. 1.200) y toma el mayor.
    2) Unidad: busca las palabras kilo, kg, corte o unidad.
    3) Producto: de las líneas restantes, escoge la palabra más larga sin dígitos.
    """
    # ——— EXTRAER PRECIOS —————————————————————————————————————
    prices = []
    for line in lines:
        # Encuentra grupos como “1.200” o “1200”
        for match in re.findall(r'(\d+(?:\.\d{3})*)', line):
            # Convertir “1.200” → 1200
            prices.append(int(match.replace('.', '')))
    precio = str(max(prices)) if prices else ''

    # ——— EXTRAER UNIDAD —————————————————————————————————————
    unidades = re.findall(
        r'\b(kilo|kg|corte|unidad)\b',
        ' '.join(lines),
        flags=re.IGNORECASE
    )
    unidad = unidades[0].lower() if unidades else ''

    # ——— EXTRAER PRODUCTO ——————————————————————————————————
    # Candidatos: líneas con solo letras (sin números)
    candidatos = [
        l.lower() for l in lines
        if re.match(r'^[A-Za-záéíóúñ]+$', l)
    ]
    # Escoge la palabra más larga (por lo general el nombre más descriptivo)
    producto = max(candidatos, key=len) if candidatos else ''

    return producto, unidad, precio

def main():
    # 1) Configurar argumentos CLI
    parser = argparse.ArgumentParser(
        description="OCR de feria: extrae producto, unidad y precio"
    )
    parser.add_argument("-i", "--input",  required=True,
                        help="Carpeta con imágenes (.jpg, .png)")
    parser.add_argument("-o", "--output", required=True,
                        help="Carpeta donde guardar resultados")
    parser.add_argument("-f", "--format", choices=["csv","excel","json"],
                        default="csv", help="Formato de salida")
    args = parser.parse_args()

    # 2) Inicializar lector OCR (ESP + ENG)
    reader = easyocr.Reader(['es','en'], gpu=False)

    # 3) Procesar cada imagen
    registros = []
    for fname in os.listdir(args.input):
        if not fname.lower().endswith(('.jpg','.png')):
            continue
        path = os.path.join(args.input, fname)
        img_proc = preprocess(path)
        lines = ocr_text(img_proc, reader)
        prod, uni, pre = parse_fields(lines)
        registros.append({
            'archivo': fname,
            'producto': prod,
            'unidad': uni,
            'precio': pre
        })

    # 4) Volcar a DataFrame y exportar
    df = pd.DataFrame(registros)
    os.makedirs(args.output, exist_ok=True)
    base = os.path.join(args.output, "resultados")
    if args.format == "csv":
        df.to_csv(base + ".csv", index=False, encoding='utf-8-sig')
    elif args.format == "excel":
        df.to_excel(base + ".xlsx", index=False)
    else:
        df.to_json(base + ".json", orient="records", force_ascii=False)

    print(f"✔ Resultados guardados en {args.output} como *.{args.format}")

if __name__ == "__main__":
    main()
