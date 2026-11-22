# train_agent.py
"""
Script Independiente de Entrenamiento para el Agente Bolivia Fraud Detector.
Entrena el clasificador Random Forest (100 árboles) con TF-IDF sobre el corpus boliviano,
calcula métricas detalladas, matriz de confusión 3x3 y exporta el modelo activo.
"""

import os
import sys
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, accuracy_score
)
from sklearn.pipeline import Pipeline
from datetime import datetime

# Rutas del proyecto
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
DB_PATH    = os.path.join(DATA_DIR, "fraude_detector.db")
CSV_PATH   = os.path.join(DATA_DIR, "mensajes.csv")
MODEL_PATH = os.path.join(DATA_DIR, "modelo_activo.pkl")
INFO_PATH  = os.path.join(DATA_DIR, "modelo_info.pkl")

def cargar_datos():
    """Carga los mensajes y etiquetas desde SQLite (o CSV de respaldo)."""
    try:
        from database.db import obtener_dataset, inicializar_db
        inicializar_db()
        filas = obtener_dataset()
        if filas:
            df = pd.DataFrame(filas, columns=["id", "mensaje", "categoria", "origen", "subcategoria"])
            print(f"[+] Datos cargados exitosamente desde SQLite: {len(df)} registros.")
            return df
    except Exception as e:
        print(f"[-] Aviso al leer SQLite: {e}")

    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        print(f"[+] Datos cargados desde CSV ({CSV_PATH}): {len(df)} registros.")
        return df

    raise FileNotFoundError("No se encontró la base de datos ni el archivo CSV en 'data/'.")

def construir_pipeline():
    """
    Construye la arquitectura de aprendizaje:
    1. TF-IDF Vectorizer: Extrae frecuencias de palabras y pares de palabras (unigramas y bigramas).
       Captura combinaciones como 'yapeame bs', 'cuenta suspendida', 'envio qr', 'premio entel'.
    2. Random Forest Classifier: Bosque de 100 árboles de decisión que votan para la clasificación final.
    """
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),    # Unigramas y Bigramas
            min_df=1,              # Incluye términos presentes al menos 1 vez
            sublinear_tf=True,     # Escala logarítmica para frecuencias de términos
            lowercase=True
        )),
        ('clf', RandomForestClassifier(
            n_estimators=100,      # 100 árboles de decisión
            random_state=42,       # Semilla determinista
            n_jobs=-1              # Ejecución multihilo paralela
        ))
    ])
    return pipeline

def entrenar_y_evaluar():
    print("=" * 70)
    print("  ENTRENAMIENTO DEL AGENTE: BOLIVIA FRAUD DETECTOR (RANDOM FOREST)")
    print("=" * 70)

    # 1. Cargar datos
    df = cargar_datos()
    mensajes = df["mensaje"].astype(str).tolist()
    etiquetas = df["categoria"].astype(str).str.lower().tolist()

    print("\n[1] Distribución del Corpus de Entrenamiento:")
    for cat in sorted(set(etiquetas)):
        cnt = etiquetas.count(cat)
        pct = (cnt / len(etiquetas)) * 100
        print(f"    • {cat.capitalize():<12}: {cnt:>4} mensajes ({pct:.1f}%)")

    # 2. División Estratificada (80% Entrenamiento, 20% Evaluación)
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            mensajes, etiquetas, test_size=0.2, random_state=42, stratify=etiquetas
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            mensajes, etiquetas, test_size=0.2, random_state=42
        )

    print(f"\n[2] División de Datos:")
    print(f"    • Entrenamiento : {len(X_train)} mensajes (80%)")
    print(f"    • Evaluación    : {len(X_test)} mensajes (20%)")

    # 3. Entrenamiento del Pipeline
    print("\n[3] Entrenando Random Forest con 100 árboles de decisión...")
    pipeline = construir_pipeline()
    pipeline.fit(X_train, y_train)
    print("    [OK] Modelo ajustado exitosamente sobre el vocabulario dialectal boliviano.")

    # 4. Evaluación en Test Set
    y_pred = pipeline.predict(X_test)
    clases = sorted(set(etiquetas))

    acc = accuracy_score(y_test, y_pred)
    idx_fraude = clases.index('fraude') if 'fraude' in clases else 0
    f1_fraude = f1_score(y_test, y_pred, labels=clases, average=None, zero_division=0)[idx_fraude]
    rec_fraude = recall_score(y_test, y_pred, labels=clases, average=None, zero_division=0)[idx_fraude]
    prec_fraude = precision_score(y_test, y_pred, labels=clases, average=None, zero_division=0)[idx_fraude]

    print("\n[4] Métricas de Rendimiento en Clase 'Fraude':")
    print(f"    • F1-Score (Fraude) : {f1_fraude * 100:.1f}%  (Equilibrio entre precisión y detección)")
    print(f"    • Recall (Fraude)   : {rec_fraude * 100:.1f}%  (Capacidad de no dejar escapar estafas)")
    print(f"    • Precision (Fraude): {prec_fraude * 100:.1f}%  (Certeza cuando alerta de fraude)")
    print(f"    • Accuracy Global   : {acc * 100:.1f}%  (Exactitud sobre todas las clases)")

    print("\n[5] Reporte de Clasificación Completo:")
    print(classification_report(y_test, y_pred, target_names=clases, zero_division=0))

    # 5. Matriz de Confusión 3x3
    cm = confusion_matrix(y_test, y_pred, labels=clases)
    print("[6] Matriz de Confusión (3x3):")
    print(f"    Etiquetas: {clases}")
    print("    " + "-" * 40)
    print(f"    {'Real \\ Pred':<15}" + "".join([f"{c:<10}" for c in clases]))
    print("    " + "-" * 40)
    for i, row in enumerate(cm):
        row_str = f"    {clases[i]:<15}" + "".join([f"{val:<10}" for val in row])
        print(row_str)
    print("    " + "-" * 40)
    print("    * Nota: La diagonal principal indica predicciones correctas.")

    # 6. Importancia de Características (Top Términos y Patrones)
    try:
        vectorizer = pipeline.named_steps['tfidf']
        rf = pipeline.named_steps['clf']
        feature_names = np.array(vectorizer.get_feature_names_out())
        importances = rf.feature_importances_
        indices = np.argsort(importances)[::-1][:15]

        print("\n[7] Top 15 Patrones/Palabras Clave más Influyentes en la Detección:")
        for rank, idx in enumerate(indices, 1):
            term = feature_names[idx]
            peso = importances[idx]
            print(f"    {rank:>2}. '{term}': peso={peso:.4f}")
    except Exception:
        pass

    # 7. Exportación del Modelo a Disco
    print("\n[8] Exportando modelo entrenado para la aplicación:")
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"    • Modelo guardado en: {MODEL_PATH}")

    info = {
        "algoritmo": "Random Forest",
        "f1": round(f1_fraude * 100, 1),
        "recall": round(rec_fraude * 100, 1),
        "precision": round(prec_fraude * 100, 1),
        "accuracy": round(acc * 100, 1),
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "total_registros": len(df),
        "cm": cm.tolist(),
        "cm_labels": clases
    }
    with open(INFO_PATH, 'wb') as f:
        pickle.dump(info, f)
    print(f"    • Metadatos guardados en: {INFO_PATH}")

    # 8. Pruebas Interactivas en Vivo
    print("\n" + "=" * 70)
    print("  PRUEBA EN VIVO DEL AGENTE CON MENSAJES DE EJEMPLO")
    print("=" * 70)
    ejemplos = [
        "Felicidades ganaste Bs 10.000 por sorteo de Entel. Paga Bs 150 por QR para envío.",
        "Te ofrecemos préstamo rápido sin garante hasta Bs 20.000 solo con tu CI.",
        "Hola hermano, nos vemos a las 3 en la plaza principal.",
        "URGENTE: Tu cuenta bancaria del Banco Unión fue suspendida, entra al enlace para verificar."
    ]

    for ej in ejemplos:
        pred = pipeline.predict([ej])[0]
        proba = pipeline.predict_proba([ej])[0]
        idx_p = list(pipeline.classes_).index(pred)
        conf = proba[idx_p] * 100
        print(f"\nMensaje : \"{ej}\"")
        print(f"Dictamen: [{pred.upper()}] con confianza del {conf:.1f}%")

    print("\n" + "=" * 70)
    print("  [EXITO] Entrenado y listo para ser utilizado en CustomTkinter!")
    print("=" * 70)

if __name__ == "__main__":
    entrenar_y_evaluar()
