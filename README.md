# 🛡️ Bolivia Fraud Detector

> Detector de estafas y fraudes digitales en **español boliviano** — WhatsApp, SMS y redes sociales.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikit-learn)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-green)
![SQLite](https://img.shields.io/badge/DB-SQLite-lightblue)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Descripción

Bolivia Fraud Detector es una aplicación de escritorio (`.exe`) que clasifica mensajes de texto como **Fraude**, **Sospechoso** o **Legítimo**, usando Machine Learning entrenado con patrones de estafas reales en español boliviano (premios falsos, phishing bancario, encomiendas falsas, Yape/Tigo Money fraudulento, etc.).

---

## 🖥️ Pantallas del sistema

| Pantalla | Descripción |
|---|---|
| **Chat Detector** | Pega un mensaje y recibe clasificación + indicadores + recomendación |
| **Historial de Análisis** | Registro anonimizado de todos los mensajes evaluados (SQLite) |
| **Panel General** | Dashboard con estadísticas y estado del modelo activo |
| **Dataset de Mensajes** | Corpus de entrenamiento: agregar, importar CSV, exportar |
| **Entrenar Modelo** | Compara SVM, Naive Bayes, Regresión Logística y Random Forest |

---

## ⚙️ Requisitos

- **Python 3.11** → [Descargar aquí](https://python.org/downloads) *(marcar "Add Python to PATH")*
- Windows 10/11

---

## 🚀 Instalación rápida

### Opción A — Script automático (recomendado)
```bash
# Doble clic en:
instalar.bat
```

### Opción B — Manual
```bash
git clone https://github.com/andy050197/bolivia-fraud-detector.git
cd bolivia-fraud-detector
pip install -r requirements.txt
python main.py
```

---

## 📦 Compilar el .exe

Para generar el ejecutable standalone (sin necesidad de Python):

```bash
# Doble clic en:
compilar_exe.bat

# O manualmente:
pyinstaller --onefile --windowed --name BoliviaFraudDetector --add-data "data;data" --add-data "assets;assets" main.py
```

El archivo `BoliviaFraudDetector.exe` aparecerá en la carpeta `dist/`.

---

## 🧠 Algoritmos de ML disponibles

| Algoritmo | F1-Score típico | Notas |
|---|---|---|
| **SVM (TF-IDF)** | ~92% | ✅ Mejor resultado — modelo por defecto |
| Random Forest | ~89% | Alta precisión, más lento |
| Regresión Logística | ~86% | Rápido y confiable |
| Naive Bayes | ~78% | Muy ligero |

---

## 📁 Estructura del proyecto

```
bolivia-fraud-detector/
├── main.py                  # Punto de entrada
├── requirements.txt         # Dependencias Python
├── instalar.bat             # Instalador automático
├── compilar_exe.bat         # Generador del .exe
├── views/
│   ├── chat_detector.py
│   ├── historial.py
│   ├── panel_general.py
│   ├── dataset.py
│   └── entrenar_modelo.py
├── ml/
│   ├── trainer.py           # Entrenamiento y comparación de modelos
│   └── predictor.py         # Clasificación de mensajes nuevos
├── database/
│   └── db.py                # SQLite — historial y dataset
├── data/
│   └── mensajes.csv         # Dataset inicial de fraudes bolivianos
└── assets/                  # Imágenes y recursos
```

---

## 🤝 Contribuir

1. Haz fork del repositorio
2. Crea tu rama: `git checkout -b feature/mi-mejora`
3. Haz commit: `git commit -m "Agrego nuevos mensajes de fraude"`
4. Push: `git push origin feature/mi-mejora`
5. Abre un Pull Request

### ¿Cómo agregar más mensajes al dataset?
- Desde la app: pestaña **Dataset de Mensajes → + Nuevo Mensaje**
- Desde CSV: **Dataset de Mensajes → Importar CSV** (columnas: `mensaje, categoria, origen, subcategoria`)

---

## 📄 Licencia

MIT License — libre para uso educativo y académico.

---

*Proyecto desarrollado para el curso de Inteligencia Artificial — Universidad Mayor de San Simón, Bolivia 🇧🇴*
