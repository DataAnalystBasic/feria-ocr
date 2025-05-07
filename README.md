Perfecto, aquí tienes el contenido actualizado para tu `README.md`, compatible con lo que has construido hasta ahora. Este archivo resume claramente la funcionalidad, uso, estructura de carpetas y detalles técnicos del proyecto **feria-ocr**, con tu firma integrada de forma profesional y discreta.

---

```markdown
# Feria OCR

**Automatiza la lectura de precios, productos y unidades desde letreros fotográficos en ferias libres.**

Este proyecto permite procesar imágenes tomadas en ferias (mercados locales) y extraer automáticamente:
- 📌 El **nombre del producto**
- 📦 El **formato o unidad de venta**
- 💲 El **precio**

Usa detección de contornos para encontrar los carteles, corrige la perspectiva, aplica OCR (con Tesseract) y normaliza los datos usando fuzzy matching contra catálogos predefinidos.

---

## 🗂 Estructura del proyecto

```

feria-ocr/
├── images/              ← Imágenes a procesar (.jpg, .png)
├── outputs/             ← Archivos generados (CSV, Excel, JSON)
├── src/
│   ├── extractor.py         ← Script principal CLI
│   ├── preprocess.py        ← OCR + preprocesamiento de imagen
│   ├── parser\_utils.py      ← Parseo y corrección con fuzzy matching
│   └── catalogo.py          ← Catálogo de productos y unidades
├── requirements.txt
└── README.md

```

---

## ⚙ Requisitos

- Python 3.8+
- Tesseract OCR instalado en:
```

C:\Users\gonza\AppData\Local\Programs\Tesseract-OCR\tesseract.exe

````
- Entorno virtual recomendado:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
````

### 📦 Instalar dependencias manualmente

```bash
pip install opencv-python pytesseract pandas imutils rapidfuzz
```

---

## 🚀 Uso

1. Coloca tus imágenes en la carpeta `images/`
2. Ejecuta desde terminal:

```bash
python src/extractor.py -i images -o outputs -f csv
```

Opciones de formato:

* `-f csv` (por defecto)
* `-f excel`
* `-f json`

3. El archivo final `resultados.csv` estará en `outputs/`

---

## 🧠 ¿Cómo funciona?

1. **Preprocesamiento**
   Se localiza el cartel más grande mediante contornos. Luego se aplica:

   * Corrección de perspectiva (warp)
   * Ecualización adaptativa (CLAHE)
   * Escalado (×2)
   * OCR doble pasada (`--psm 6` y `--psm 7`)

2. **Parseo**

   * Extrae números como precios (mayor valor en el texto).
   * Detecta unidades comunes como “kilo”, “kg”, etc.
   * Usa *fuzzy matching* para corregir errores de OCR en el nombre del producto.

3. **Exportación**

   * Exporta los resultados a `.csv`, `.xlsx` o `.json`.

---

## 🔧 Personalización

Puedes modificar el contenido del archivo:

```python
src/catalogo.py
```

Para:

* Agregar más productos
* Añadir nuevas unidades o formatos

---

## ✍ Autor

Este software fue desarrollado por **Gonzalo Cisterna Salinas**, Técnico en Automatización y Analista Programador, como parte de su portafolio de proyectos en ciencia de datos y visión computacional.

*Firma digital incluida dentro del código:*
`# _hidden_signature_: "GonzaloCisterna_feriaOCR"`

---

## 🧪 ¿Qué sigue?

* [ ] Interfaz gráfica simple con Streamlit para revisión/corrección rápida.
* [ ] Entrenamiento de modelo de detección (YOLOv8) para aislar mejor los carteles.
* [ ] Generar ejecutable (.exe) portable para usuarios sin Python.

---

## 📄 Licencia

Este proyecto es de libre uso para fines educativos o de automatización personal. Se solicita atribución en caso de reutilización.

```

---

¿Deseas que también cree el `requirements.txt` actualizado con las dependencias exactas de este proyecto?
```
