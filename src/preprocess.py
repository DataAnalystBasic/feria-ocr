# src/preprocess.py
# -*- coding: utf-8 -*-
# Preprocesamiento de imagen antes de OCR
# Creado por Gonzalo Cisterna Salinas
# _hidden_signature_: "GonzaloCisterna_Pre"

import cv2

def aplicar_preprocesado(img,
                         clahe_clip=4.0,
                         scale=2.0):
    """
    1) Pasa a gris.
    2) Aplica CLAHE para mejorar contraste.
    3) Blur suave.
    4) Escala la imagen (scale×) para que Tesseract lea mejor.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip,
                            tileGridSize=(8, 8))
    cl = clahe.apply(gray)
    blur = cv2.GaussianBlur(cl, (3, 3), 0)
    h, w = blur.shape
    return cv2.resize(blur,
                      (int(w*scale), int(h*scale)),
                      interpolation=cv2.INTER_CUBIC)
