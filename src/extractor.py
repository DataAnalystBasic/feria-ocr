# extractor.py
import os
import re
import easyocr
import cv2
import pandas as pd

# 1) Inicializar el lector de OCR (idiomas: español e inglés)
reader = easyocr.Reader(['es','en'], gpu=False)

# 2) Función para preprocesar cada imagen
def preprocess(path):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # umbral adaptativo para resaltar texto en pizarras y carteles
    return cv2.adaptiveThreshold(gray, 255,
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)

# 3) Función para extraer texto crudo
def ocr_text(preproc_img):
    # detail=0 devuelve solo la lista de strings
    return reader.readtext(preproc_img, detail=0)

# 4) Función para extraer precio y unidad
def parse_fields(text_lines):
    precio, unidad, producto = None, None, None
    for line in text_lines:
        # buscar precios en formato 1.000 o 1000
        m = re.search(r'(\d{1,3}(?:\.\d{3})*)(?:\s*\$?)', line)
        if m:
            precio = m.group(1)
        # buscar unidades comunes
        if re.search(r'\b(kilo|kg|corte|u?ni?dad)\b', line, re.IGNORECASE):
            unidad = re.search(r'\b(kilo|kg|corte|unidad)\b', line, re.IGNORECASE).group(1)
        # buscar nombre de producto (asumiendo que es la única palabra en minúscula al inicio)
        if re.match(r'^[A-Za-záéíóúñ]+$', line):
            producto = line.lower()
    return producto, unidad, precio

def main():
    resultados = []
    carpeta = os.path.join(os.path.dirname(__file__),'..','images')
    for fname in os.listdir(carpeta):
        if not fname.lower().endswith(('.jpg','.png')): continue
        ruta = os.path.join(carpeta, fname)
        img_proc = preprocess(ruta)
        lines = ocr_text(img_proc)
        prod, uni, pre = parse_fields(lines)
        resultados.append({
            'archivo': fname,
            'producto': prod or '',
            'unidad': uni or '',
            'precio': pre or '',
        })
    # 5) Guardar a CSV
    df = pd.DataFrame(resultados)
    df.to_csv(os.path.join(os.path.dirname(__file__),'..','outputs','resultados.csv'), index=False, encoding='utf-8-sig')
    print("Procesamiento completado. Revisa outputs/resultados.csv")

if __name__ == '__main__':
    main()
