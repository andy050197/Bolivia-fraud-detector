# Bolivia Fraud Detector

Detector de estafas y fraudes digitales en español boliviano — WhatsApp, SMS y redes sociales.

---

<<<<<<< HEAD
## Descripción
=======
## Descripcion
>>>>>>> origin/develop

Bolivia Fraud Detector es una aplicacion de escritorio (.exe) que clasifica mensajes de texto como Fraude, Sospechoso o Legitimo, usando Machine Learning entrenado con patrones de estafas reales en espanol boliviano (premios falsos, phishing bancario, encomiendas falsas, Yape/Tigo Money fraudulento, etc.).

---

## Pantallas del sistema

| Pantalla | Descripcion |
|---|---|
| Chat Detector | Pega un mensaje y recibe clasificacion + indicadores + recomendacion |
| Historial de Analisis | Registro anonimizado de todos los mensajes evaluados (SQLite) |
| Panel General | Dashboard con estadisticas y estado del modelo activo |
| Dataset de Mensajes | Corpus de entrenamiento: agregar, importar CSV, exportar |
| Entrenar Modelo | Compara SVM, Naive Bayes, Regresion Logistica y Random Forest |

---

## Requisitos

<<<<<<< HEAD
- **Python 3.11** → [Descargar aquí](https://python.org/downloads) (marcar "Add Python to PATH")
=======
- Python 3.11 — Descargar en: https://python.org/downloads (marcar "Add Python to PATH" al instalar)
>>>>>>> origin/develop
- Windows 10/11

---

<<<<<<< HEAD
## Instalación rápida
=======
## Instalacion rapida
>>>>>>> origin/develop

### Opcion A — Script automatico (recomendado)
```bash
instalar.bat
```

### Opcion B — Manual
```bash
git clone [https://github.com/andy050197/bolivia-fraud-detector.git](https://github.com/andy050197/bolivia-fraud-detector.git)
cd bolivia-fraud-detector
pip install -r requirements.txt
python main.py
```

---

## Compilar el .exe

Para generar el ejecutable standalone (sin necesidad de Python instalado):

```bash
compilar_exe.bat
```

O manualmente:

```bash
pyinstaller --onefile --windowed --name BoliviaFraudDetector --add-data "data;data" --add-data "assets;assets" main.py
```

El archivo BoliviaFraudDetector.exe aparecera en la carpeta dist/.

---

## Algoritmos de ML disponibles

| Algoritmo | F1-Score tipico | Notas |
|---|---|---|
<<<<<<< HEAD
| **SVM (TF-IDF)** | ~92% | Mejor resultado — modelo por defecto |
| Random Forest | ~89% | Alta precisión, más lento |
| Regresión Logística | ~86% | Rápido y confiable |
=======
| SVM (TF-IDF) | ~92% | Mejor resultado, modelo por defecto |
| Random Forest | ~89% | Alta precision, mas lento |
| Regresion Logistica | ~86% | Rapido y confiable |
>>>>>>> origin/develop
| Naive Bayes | ~78% | Muy ligero |

---

## Estructura del proyecto

```
bolivia-fraud-detector/
├── main.py                  # Punto de entrada
├── requirements.txt         # Dependencias Python
├── instalar.bat             # Instalador automatico
├── compilar_exe.bat         # Generador del .exe
├── views/
│   ├── chat_detector.py
│   ├── historial.py
│   ├── panel_general.py
│   ├── dataset.py
│   └── entrenar_modelo.py
├── ml/
│   ├── trainer.py           # Entrenamiento y comparacion de modelos
│   └── predictor.py         # Clasificacion de mensajes nuevos
├── database/
│   └── db.py                # SQLite - historial y dataset
├── data/
│   └── mensajes.csv         # Dataset inicial de fraudes bolivianos
└── assets/                  # Imagenes y recursos
```

---

## Contribuir

1. Haz fork del repositorio
2. Crea tu rama: git checkout -b feature/mi-mejora
3. Haz commit: git commit -m "Agrego nuevos mensajes de fraude"
4. Push: git push origin feature/mi-mejora
5. Abre un Pull Request

Como agregar mas mensajes al dataset:
- Desde la app: pestana Dataset de Mensajes, boton Nuevo Mensaje
- Desde CSV: Dataset de Mensajes, boton Importar CSV (columnas: mensaje, categoria, origen, subcategoria)

---

## Licencia

MIT License - libre para uso educativo y academico.

Proyecto desarrollado para el curso de Inteligencia Artificial - Universidad Mayor de San Simon, Bolivia

