# src/parser_utils.py
# -*- coding: utf-8 -*-
# Módulo: reglas de parseo y corrección (fuzzy matching)
# Autor: Gonzalo Cisterna Salinas
# _hidden_signature_: "CisternaSalinas_DataAnalyst"

import re
from rapidfuzz import process, fuzz
from catalogo import PRODUCTOS, UNIDADES

def mejor_coincidencia(candidatos, catalogo, umbral=60):
    """
    Toma la cadena más larga de candidatos y, si su similitud
    con algún término del catálogo ≥ umbral, devuelve el match.
    """
    if not candidatos:
        return ''
    texto = max(candidatos, key=len).lower()
    match, score, _ = process.extractOne(
        texto, catalogo, scorer=fuzz.token_sort_ratio
    )
    return match if score >= umbral else texto

def extraer_campos(lineas):
    """
    1) Precio: busca todos los números estilo “1.200” o “1,200”, toma el mayor.
    2) Unidad: fuzzy-match contra UNIDADES.
    3) Producto: fuzzy-match contra PRODUCTOS.
    Devuelve (producto, unidad, precio) como cadenas.
    """
    # ——— PRECIO ————————————————————————————————————————
    nums = []
    for l in lineas:
        for m in re.findall(r'\d{1,3}(?:[.,]\d{3})*', l):
            nums.append(int(m.replace('.', '').replace(',', '')))
    precio = str(max(nums)) if nums else ''

    # ——— UNIDAD ———————————————————————————————————————
    uni_raw = re.findall(
        r'\b(k?g|kilo|gr|gramos|corte|unidad|bandeja)\b',
        ' '.join(lineas),
        flags=re.IGNORECASE
    )
    unidad = mejor_coincidencia(uni_raw, UNIDADES)

    # ——— PRODUCTO —————————————————————————————————————
    candidatos = [
        l for l in lineas
        if re.fullmatch(r'[A-Za-zÁÉÍÓÚÑáéíóúñ ]+', l)
    ]
    producto = mejor_coincidencia(candidatos, PRODUCTOS)

    return producto, unidad, precio
