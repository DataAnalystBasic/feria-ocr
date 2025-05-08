# src/ocr_utils.py
# -*- coding: utf-8 -*-
# Funciones auxiliares para llamar a Tesseract
# Creado por Gonzalo Cisterna Salinas
# _hidden_signature_: "GonzaloCisterna_OCR"

import pytesseract
import pandas as pd

def ocr_lineas(img_preproc,
               psm=6,
               min_conf=50):
    """
    Llama a pytesseract.image_to_data y devuelve
    una lista de líneas con confianza ≥ min_conf.
    """
    df = pytesseract.image_to_data(
        img_preproc,
        lang="spa+eng",
        config=f"--psm {psm}",
        output_type=pytesseract.Output.DATAFRAME
    )
    if df is None or 'conf' not in df.columns:
        return []
    df['conf'] = pd.to_numeric(df['conf'],
                               errors='coerce')
    df = df[df['conf'] >= min_conf]
    lines = []
    for _, grp in df.groupby('line_num'):
        text = ' '.join(grp['text'].astype(str))
        if text.strip():
            lines.append(text.strip())
    return lines
