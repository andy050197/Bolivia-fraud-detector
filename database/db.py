import sqlite3
import os
import sys
import re
import csv
from datetime import datetime


def _obtener_ruta_db():
    """Devuelve una ruta persistente tanto en desarrollo como en el .exe compilado."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "fraude_detector.db")


DB_PATH = _obtener_ruta_db()


def get_connection():
    return sqlite3.connect(DB_PATH)


def inicializar_db():
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # Tabla de historial de análisis
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                mensaje_anonimizado TEXT NOT NULL,
                categoria TEXT NOT NULL,
                nivel_riesgo TEXT NOT NULL,
                confianza REAL NOT NULL
            )
        """)

        # Tabla del dataset de entrenamiento
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dataset (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mensaje TEXT NOT NULL,
                categoria TEXT NOT NULL,
                origen TEXT DEFAULT 'Manual',
                subcategoria TEXT DEFAULT ''
            )
        """)

        conn.commit()
    finally:
        conn.close()


def guardar_analisis(mensaje, categoria, nivel_riesgo, confianza):
    """Guarda un análisis en el historial, anonimizando el mensaje."""
    anonimizado = re.sub(r'https?://\S+', '[URL]', mensaje)
    anonimizado = re.sub(r'Bs\.?\s*\d+[\.,]?\d*', 'Bs [MONTO]', anonimizado)
    anonimizado = re.sub(r'\+591\s*\d+', '[TELÉFONO]', anonimizado)
    anonimizado = re.sub(r'\b\d{7,}\b', '[NÚMERO]', anonimizado)

    anonimizado = anonimizado[:80] + ("..." if len(anonimizado) > 80 else "")
    porcentaje_confianza = round(confianza * 100, 1) if confianza <= 1.0 else round(confianza, 1)

    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO historial (fecha, mensaje_anonimizado, categoria, nivel_riesgo, confianza) VALUES (?, ?, ?, ?, ?)",
            (datetime.now().strftime("%d/%m/%Y %H:%M"), anonimizado, categoria, nivel_riesgo, porcentaje_confianza)
        )
        conn.commit()
    finally:
        conn.close()


def obtener_historial(filtro_categoria=None, busqueda=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT id, fecha, mensaje_anonimizado, categoria, nivel_riesgo, confianza FROM historial"
        params = []
        condiciones = []

        if filtro_categoria and filtro_categoria != "Todas":
            condiciones.append("categoria = ?")
            params.append(filtro_categoria)
        if busqueda:
            condiciones.append("mensaje_anonimizado LIKE ?")
            params.append(f"%{busqueda}%")

        if condiciones:
            query += " WHERE " + " AND ".join(condiciones)
        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()


def eliminar_historial_item(item_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historial WHERE id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()


def limpiar_historial():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM historial")
        conn.commit()
    finally:
        conn.close()


def obtener_estadisticas():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM historial")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM historial WHERE LOWER(categoria) = 'fraude'")
        fraudes = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM historial WHERE LOWER(categoria) = 'sospechoso'")
        sospechosos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM historial WHERE LOWER(categoria) = 'legitimo'")
        legitimos = cursor.fetchone()[0]
        return {
            "total": total,
            "fraudes": fraudes,
            "sospechosos": sospechosos,
            "legitimos": legitimos
        }
    finally:
        conn.close()


def obtener_dataset():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, mensaje, categoria, origen, subcategoria FROM dataset ORDER BY id")
        return cursor.fetchall()
    finally:
        conn.close()


def agregar_mensaje_dataset(mensaje, categoria, origen="Manual", subcategoria=""):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dataset (mensaje, categoria, origen, subcategoria) VALUES (?, ?, ?, ?)",
            (mensaje, categoria, origen, subcategoria)
        )
        conn.commit()
    finally:
        conn.close()


def eliminar_mensaje_dataset(item_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM dataset WHERE id = ?", (item_id,))
        conn.commit()
    finally:
        conn.close()


def cargar_csv_a_dataset(filepath):
    if not os.path.exists(filepath):
        return 0

    conn = get_connection()
    try:
        cursor = conn.cursor()
        insertados = 0
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                mensaje = row.get("mensaje", "").strip()
                categoria = row.get("categoria", "").strip()
                if not mensaje or not categoria:
                    continue

                # Evita insertar mensajes repetidos si se vuelve a importar el mismo CSV
                cursor.execute("SELECT 1 FROM dataset WHERE mensaje = ? LIMIT 1", (mensaje,))
                if cursor.fetchone() is None:
                    cursor.execute(
                        "INSERT INTO dataset (mensaje, categoria, origen, subcategoria) VALUES (?, ?, ?, ?)",
                        (mensaje, categoria, row.get("origen", "CSV"), row.get("subcategoria", ""))
                    )
                    insertados += 1
        conn.commit()
        return insertados
    finally:
        conn.close()