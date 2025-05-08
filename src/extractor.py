# src/extractor.py
# -*- coding: utf-8 -*-
# Script principal: recorre imágenes y genera CSV/Excel/JSON
# Creado por Gonzalo Cisterna Salinas
# _hidden_signature_: "GonzaloCisterna_Main"

import os
import argparse
import pandas as pd
import cv2
import pytesseract

# Ajusta a tu instalación real:
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\gonza\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)

from roi_detector import detectar_regiones
from preprocess import aplicar_preprocesado
from ocr_utils    import ocr_lineas
from parser_utils import extraer_campos

def procesar_imagen(path):
    img = cv2.imread(path)
    regiones = detectar_regiones(img)

    resultados = []
    for reg in regiones:
        prep = aplicar_preprocesado(reg)
        # Dos pasadas: PSM 6 y 7
        lines6 = ocr_lineas(prep, psm=6)
        lines7 = ocr_lineas(prep, psm=7)
        lines = list(dict.fromkeys(lines6 + lines7))
        resultados.append(extraer_campos(lines))

    # Agregar el valor más frecuente de cada campo
    if not resultados:
        return '','',''
    from collections import Counter
    prods = [r[0] for r in resultados if r[0]]
    unis  = [r[1] for r in resultados if r[1]]
    pres  = [r[2] for r in resultados if r[2]]
    prod = Counter(prods).most_common(1)[0][0] if prods else ''
    uni  = Counter(unis).most_common(1)[0][0] if unis else ''
    pre  = Counter(pres).most_common(1)[0][0] if pres else ''
    return prod, uni, pre

def main():
    ap = argparse.ArgumentParser(
        description="OCR Feria: extrae producto, unidad y precio"
    )
    ap.add_argument("-i","--input", required=True,
                    help="Carpeta con imágenes (.jpg/.png)")
    ap.add_argument("-o","--output", required=True,
                    help="Carpeta donde guardar resultados")
    ap.add_argument("-f","--format", choices=['csv','excel','json'],
                    default='csv', help="Formato de salida")
    args = ap.parse_args()

    rows = []
    for fn in os.listdir(args.input):
        if fn.lower().endswith(('.jpg','.png')):
            p,u,pr = procesar_imagen(
                os.path.join(args.input,fn)
            )
            rows.append({'archivo':fn,
                         'producto':p,
                         'unidad':u,
                         'precio':pr})

    df = pd.DataFrame(rows)
    os.makedirs(args.output, exist_ok=True)
    base = os.path.join(args.output, "resultados")
    if args.format=='csv':
        df.to_csv(base+".csv", index=False, encoding='utf-8-sig')
    elif args.format=='excel':
        df.to_excel(base+".xlsx", index=False)
    else:
        df.to_json(base+".json", orient='records',
                   force_ascii=False)

    print(f"✔ Resultados guardados en {base}.{args.format}")

if __name__ == "__main__":
    main()
