import os
import pickle
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
import sys

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "modelo_activo.pkl")
INFO_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "modelo_info.pkl")

ALGORITMOS = {
    "SVM (TF-IDF)": Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ('clf', SVC(kernel='linear', probability=True, C=1.0))
    ]),
    "Naive Bayes": Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ('clf', MultinomialNB())
    ]),
    "Regresión Logística": Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ('clf', LogisticRegression(max_iter=1000, C=1.0))
    ]),
    "Random Forest": Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ]),
}

def entrenar_todos(mensajes, etiquetas, algoritmos_seleccionados):
    """
    Entrena los algoritmos seleccionados y retorna métricas + el mejor modelo.
    Retorna: lista de dicts con métricas por algoritmo, nombre del mejor, mejor pipeline.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        mensajes, etiquetas, test_size=0.2, random_state=42, stratify=etiquetas
    )

    resultados = []
    mejor_f1 = -1
    mejor_nombre = None
    mejor_pipeline = None
    mejor_cm = None

    for nombre in algoritmos_seleccionados:
        if nombre not in ALGORITMOS:
            continue
        pipeline = ALGORITMOS[nombre]
        # Clonar pipeline para no reutilizar el mismo objeto
        import copy
        p = copy.deepcopy(pipeline)
        p.fit(X_train, y_train)
        y_pred = p.predict(X_test)

        # Métricas para clase "fraude"
        labels = sorted(list(set(etiquetas)))
        f1  = f1_score(y_test, y_pred, labels=['fraude'], average='macro', zero_division=0)
        pre = precision_score(y_test, y_pred, labels=['fraude'], average='macro', zero_division=0)
        rec = recall_score(y_test, y_pred, labels=['fraude'], average='macro', zero_division=0)
        acc = accuracy_score(y_test, y_pred)
        cm  = confusion_matrix(y_test, y_pred, labels=sorted(set(etiquetas)))

        resultados.append({
            "nombre": nombre,
            "f1": round(f1 * 100, 1),
            "precision": round(pre * 100, 1),
            "recall": round(rec * 100, 1),
            "accuracy": round(acc * 100, 1),
            "cm": cm,
            "cm_labels": sorted(set(etiquetas)),
            "pipeline": p
        })

        if f1 > mejor_f1:
            mejor_f1 = f1
            mejor_nombre = nombre
            mejor_pipeline = p
            mejor_cm = cm

    return resultados, mejor_nombre, mejor_pipeline

def guardar_modelo(pipeline, info: dict):
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(pipeline, f)
    with open(INFO_PATH, 'wb') as f:
        pickle.dump(info, f)

def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        return None, None
    with open(MODEL_PATH, 'rb') as f:
        pipeline = pickle.load(f)
    info = {}
    if os.path.exists(INFO_PATH):
        with open(INFO_PATH, 'rb') as f:
            info = pickle.load(f)
    return pipeline, info
