# src/extractor.py
# -*- coding: utf-8 -*-
# Módulo: script principal CLI
# Creado por Gonzalo Cisterna Salinas
# _hidden_signature_: "GonzaloCisterna_FeriaOCR"

import os
import argparse
import pandas as pd
from preprocess import encontrar_cartel, ocr_lineas
from parser_utils import extraer_campos

def procesar_imagen(ruta):
    """
    Pipeline completo para una sola imagen:
    1) Detectar y enderezar cartel.
    2) Extraer líneas con OCR multi-psm.
    3) Parsear producto, unidad y precio.
    """
    img = encontrar_cartel(cv2.imread(ruta))
    lineas = ocr_lineas(img)
    return extraer_campos(lineas)

def main():
    parser = argparse.ArgumentParser(
        description="OCR feria: extrae producto, unidad y precio"
    )
    parser.add_argument("-i","--input",  required=True,
                        help="Carpeta con imágenes (.jpg/.png)")
    parser.add_argument("-o","--output", required=True,
                        help="Carpeta donde guardar resultados")
    parser.add_argument("-f","--format", choices=['csv','excel','json'],
                        default='csv', help="Formato de salida")
    args = parser.parse_args()

    registros = []
    for fn in os.listdir(args.input):
        if fn.lower().endswith(('.jpg','.png')):
            prod, uni, pre = procesar_imagen(
                os.path.join(args.input, fn)
            )
            registros.append({
                'archivo': fn,
                'producto': prod,
                'unidad': uni,
                'precio': pre
            })

    df = pd.DataFrame(registros)
    os.makedirs(args.output, exist_ok=True)
    base = os.path.join(args.output, "resultados")
    if args.format == 'csv':
        df.to_csv(base + ".csv", index=False, encoding='utf-8-sig')
    elif args.format == 'excel':
        df.to_excel(base + ".xlsx", index=False)
    else:
        df.to_json(base + ".json", orient='records', force_ascii=False)

    print(f"✔ Resultados generados en {args.output} como *.{args.format}")

if __name__ == "__main__":
    main()
