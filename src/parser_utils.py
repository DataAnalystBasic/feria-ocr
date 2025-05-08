# src/parser_utils.py
# -*- coding: utf-8 -*-
# Parseo de líneas OCR y corrección fuzzy
# Creado por Gonzalo Cisterna Salinas
# _hidden_signature_: "CisternaSalinas_Parser"

import re
from rapidfuzz import process, fuzz
from catalogo import PRODUCTOS, UNIDADES

def mejor_coincidencia(candidatos,
                       catalogo,
                       umbral=60):
    if not candidatos:
        return ''
    texto = max(candidatos, key=len).lower()
    match, score, _ = process.extractOne(
        texto, catalogo,
        scorer=fuzz.token_sort_ratio
    )
    return match if score >= umbral else texto

def extraer_campos(lines):
    """
    Dado un listado de líneas OCR, devuelve:
    (producto, unidad, precio)
    """
    # — PRECIO —
    nums = []
    for l in lines:
        for m in re.findall(r'\d{1,3}(?:[.,]\d{3})*', l):
            nums.append(int(m.replace('.', '').replace(',', '')))
    precio = str(max(nums)) if nums else ''

    # — UNIDAD —
    uni_raw = re.findall(
        r'\b(?:c/u|k?g|kilo|gr|gramos|corte|unidad|pila)\b',
        ' '.join(lines), flags=re.IGNORECASE
    )
    unidad = mejor_coincidencia(uni_raw, UNIDADES)

    # — PRODUCTO —
    candidatos = [
        l for l in lines
        if re.fullmatch(r'[A-Za-zÁÉÍÓÚÑáéíóúñ ]+', l)
    ]
    producto = mejor_coincidencia(candidatos, PRODUCTOS)

    return producto, unidad, precio
