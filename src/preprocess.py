# src/preprocess.py
# -*- coding: utf-8 -*-
# Módulo: procesamiento de imagen y detección de cartel
# Autor: Gonzalo Cisterna Salinas
# _hidden_signature_: "GonzaloCisterna_feriaOCR"

import cv2
import pandas as pd
import pytesseract
import imutils
from imutils.perspective import four_point_transform

# Apunta aquí a tu instalación local de Tesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\gonza\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)

def encontrar_cartel(img):
    """
    Detecta el contorno más grande de 4 lados (pizarra/cartel)
    y aplica perspectiva para enderezarlo.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    edged = cv2.Canny(blur, 50, 150)

    # Encuentra contornos más grandes
    cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[0]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02*peri, True)
        # Si tiene 4 vértices y área > 2000 píxeles, lo toma
        if len(approx) == 4 and cv2.contourArea(c) > 2000:
            return four_point_transform(img, approx.reshape(4,2))
    # Fallback: toda la imagen
    return img

def ocr_lineas(img):
    """
    Realiza dos pasadas de Tesseract (PSM 6 y 7) sobre la imagen:
    - Aplica CLAHE, difuminado y escala ×2 para mejorar contraste.
    - Filtra solo palabras con confianza ≥ 50.
    - Agrupa por línea (line_num) y devuelve un set de líneas únicas.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8,8))
    proc = clahe.apply(gray)
    proc = cv2.GaussianBlur(proc, (3,3), 0)
    proc = cv2.resize(proc, None, fx=2, fy=2,
                      interpolation=cv2.INTER_CUBIC)

    lineas = set()
    for psm in [6, 7]:
        df = pytesseract.image_to_data(
            proc,
            lang="spa+eng",
            config=f"--psm {psm}",
            output_type=pytesseract.Output.DATAFRAME
        )
        if 'conf' not in df.columns:
            continue
        df['conf'] = pd.to_numeric(df['conf'], errors='coerce')
        df = df[df['conf'] >= 50]
        for _, grupo in df.groupby('line_num'):
            linea = ' '.join(grupo['text'].astype(str))
            if linea.strip():
                lineas.add(linea.strip())
    return list(lineas)
