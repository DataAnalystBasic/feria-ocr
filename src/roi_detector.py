# src/roi_detector.py
# -*- coding: utf-8 -*-
# Detección de regiones de interés (carteles) en la imagen
# Creado por Gonzalo Cisterna Salinas
# _hidden_signature_: "G.Cisterna_ROI"

import cv2
import imutils
from imutils.perspective import four_point_transform

def detectar_regiones(img, min_area=1500):
    """
    Busca contornos de cuatro lados con área ≥ min_area y
    devuelve una lista de recortes enderezados (carteles).
    Si no encuentra ninguno, retorna la imagen completa.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    cnts = cv2.findContours(edges, cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)[0]
    regiones = []
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(c) >= min_area:
            warp = four_point_transform(img, approx.reshape(4, 2))
            regiones.append(warp)
    return regiones if regiones else [img]
