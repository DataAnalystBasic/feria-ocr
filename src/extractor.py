# src/extractor.py

import os
import re
import argparse
import cv2
import pandas as pd

# 1) Importamos PaddleOCR
from paddleocr import PaddleOCR

def preprocess(path):
    """
    1. Lee la imagen desde disco.
    2. Pasa a escala de grises.
    3. Aplica CLAHE (ecualización adaptativa por regiones).
    4. Difumina ligeramente para reducir ruido.
    """
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # CLAHE mejora contraste en zonas oscuras y claras
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(gray)
    # Suave desenfoque
    proc = cv2.GaussianBlur(cl, (3,3), 0)
    return proc

def ocr_text(img, ocr):
    """
    Ejecuta OCR sobre la imagen preprocesada.
    Filtra resultados con confianza ≥0.5.
    Devuelve lista de líneas de texto.
    """
    # PaddleOCR devuelve [[ [x1,y1],…,[x4,y4] ], (texto, conf)] por línea
    result = ocr.ocr(img, cls=True)
    lines = []
    for line in result:
        for box, (txt, conf) in line:
            if conf >= 0.5:
                lines.append(txt)
    return lines

def parse_fields(lines):
    """
    1. Precio: extrae todos los números estilo “1.200” o “1200” y toma el mayor.
    2. Unidad: busca “kilo”, “kg”, “corte” o “unidad”.
    3. Producto: de las líneas sin dígitos, escoge la más larga.
    """
    # —– Precio —————————————————————————————————————
    nums = []
    for l in lines:
        for m in re.findall(r'(\d{1,3}(?:\.\d{3})*)', l):
            nums.append(int(m.replace('.', '')))
    precio = str(max(nums)) if nums else ''

    # —– Unidad —————————————————————————————————————
    u = re.findall(r'\b(kilo|kg|corte|unidad)\b',
                   ' '.join(lines), flags=re.IGNORECASE)
    unidad = u[0].lower() if u else ''

    # —– Producto ——————————————————————————————————
    candidatos = [l.lower() for l in lines
                  if re.match(r'^[A-Za-záéíóúñ]+$', l)]
    producto = max(candidatos, key=len) if candidatos else ''

    return producto, unidad, precio

def main():
    # 1) Argumentos de línea de comandos
    p = argparse.ArgumentParser(
        description="OCR feria con PaddleOCR: extrae producto, unidad y precio")
    p.add_argument('-i','--input', required=True,
                   help="Carpeta con imágenes (.jpg/.png)")
    p.add_argument('-o','--output', required=True,
                   help="Carpeta donde guardar resultados")
    p.add_argument('-f','--format', choices=['csv','excel','json'],
                   default='csv', help="Formato de salida")
    args = p.parse_args()

    # 2) Inicializar PaddleOCR (español + detección de ángulo)
    ocr = PaddleOCR(lang='es', use_angle_cls=True)

    registros = []
    for fn in os.listdir(args.input):
        if not fn.lower().endswith(('.jpg','.png')): continue
        path = os.path.join(args.input, fn)
        img = preprocess(path)
        lines = ocr_text(img, ocr)
        prod, uni, pre = parse_fields(lines)
        registros.append({
            'archivo': fn,
            'producto': prod,
            'unidad': uni,
            'precio': pre
        })

    # 3) Guardar resultados
    df = pd.DataFrame(registros)
    os.makedirs(args.output, exist_ok=True)
    base = os.path.join(args.output, 'resultados')
    if args.format == 'csv':
        df.to_csv(base + '.csv', index=False, encoding='utf-8-sig')
    elif args.format == 'excel':
        df.to_excel(base + '.xlsx', index=False)
    else:
        df.to_json(base + '.json', orient='records', force_ascii=False)

    print(f"✔ Resultados guardados en {args.output} como *.{args.format}")

if __name__ == '__main__':
    main()
