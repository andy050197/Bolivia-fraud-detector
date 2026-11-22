import os
import pickle
import copy
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score, confusion_matrix
from sklearn.pipeline import Pipeline
import sys

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "modelo_activo.pkl")
INFO_PATH  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "modelo_info.pkl")

# Algoritmo Oficial del Proyecto: Random Forest Classifier
ALGORITMOS = {
    "Random Forest": Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1, sublinear_tf=True)),
        ('clf', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
}

def entrenar_random_forest(mensajes, etiquetas):
    """
    Entrena exclusivamente el clasificador Random Forest (100 árboles de decisión)
    sobre el corpus en español boliviano y calcula métricas + matriz de confusión.
    """
    try:
        X_train, X_test, y_train, y_test = train_test_split(
            mensajes, etiquetas, test_size=0.2, random_state=42, stratify=etiquetas
        )
    except ValueError:
        X_train, X_test, y_train, y_test = train_test_split(
            mensajes, etiquetas, test_size=0.2, random_state=42
        )

    pipeline = copy.deepcopy(ALGORITMOS["Random Forest"])
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    clases = sorted(set(etiquetas))
    idx = clases.index('fraude') if 'fraude' in clases else 0

    f1_arr  = f1_score(y_test, y_pred, labels=clases, average=None, zero_division=0)
    pre_arr = precision_score(y_test, y_pred, labels=clases, average=None, zero_division=0)
    rec_arr = recall_score(y_test, y_pred, labels=clases, average=None, zero_division=0)
    acc = accuracy_score(y_test, y_pred)
    cm  = confusion_matrix(y_test, y_pred, labels=clases)

    resultado = {
        "nombre": "Random Forest",
        "f1": round(f1_arr[idx] * 100, 1),
        "precision": round(pre_arr[idx] * 100, 1),
        "recall": round(rec_arr[idx] * 100, 1),
        "accuracy": round(acc * 100, 1),
        "cm": cm,
        "cm_labels": clases,
        "pipeline": pipeline,
        "n_arboles": 100,
        "total_entrenamiento": len(X_train),
        "total_evaluacion": len(X_test)
    }

    return resultado

def entrenar_todos(mensajes, etiquetas, algoritmos_seleccionados=None):
    """Mantiene compatibilidad retornando la lista con el clasificador Random Forest."""
    res = entrenar_random_forest(mensajes, etiquetas)
    return [res], "Random Forest", res["pipeline"]

def guardar_modelo(pipeline, info: dict):
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(pipeline, f)
    with open(INFO_PATH, 'wb') as f:
        pickle.dump(info, f)

def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        return None, None
    try:
        with open(MODEL_PATH, 'rb') as f:
            pipeline = pickle.load(f)
        info = {}
        if os.path.exists(INFO_PATH):
            with open(INFO_PATH, 'rb') as f:
                info = pickle.load(f)
        return pipeline, info
    except Exception:
        return None, None
