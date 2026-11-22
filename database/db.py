import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "fraude_detector.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def inicializar_db():
    conn = get_connection()
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
    conn.close()

def guardar_analisis(mensaje, categoria, nivel_riesgo, confianza):
    """Guarda un análisis en el historial, anonimizando el mensaje."""
    import re
    # Anonimizar: reemplazar números, URLs, montos manteniendo el mensaje íntegro
    anonimizado = re.sub(r'https?://\S+', '[URL]', mensaje)
    anonimizado = re.sub(r'Bs\.?\s*\d+[\.,]?\d*', 'Bs [MONTO]', anonimizado)
    anonimizado = re.sub(r'\b\d{7,}\b', '[NÚMERO]', anonimizado)
    anonimizado = re.sub(r'\+591\s*\d+', '[TELÉFONO]', anonimizado)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historial (fecha, mensaje_anonimizado, categoria, nivel_riesgo, confianza) VALUES (?, ?, ?, ?, ?)",
        (datetime.now().strftime("%d/%m/%Y %H:%M"), anonimizado, categoria, nivel_riesgo, round(confianza * 100, 1))
    )
    conn.commit()
    conn.close()

def obtener_historial(filtro_categoria=None, busqueda=None):
    conn = get_connection()
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
    rows = cursor.fetchall()
    conn.close()
    return rows

def eliminar_historial_item(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historial WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def limpiar_historial():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historial")
    conn.commit()
    conn.close()

def obtener_estadisticas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM historial")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM historial WHERE categoria = 'fraude'")
    fraudes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM historial WHERE categoria = 'sospechoso'")
    sospechosos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM historial WHERE categoria = 'legitimo'")
    legitimos = cursor.fetchone()[0]
    conn.close()
    return {"total": total, "fraudes": fraudes, "sospechosos": sospechosos, "legitimos": legitimos}

def obtener_dataset():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, mensaje, categoria, origen, subcategoria FROM dataset ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows

def agregar_mensaje_dataset(mensaje, categoria, origen="Manual", subcategoria=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO dataset (mensaje, categoria, origen, subcategoria) VALUES (?, ?, ?, ?)",
        (mensaje, categoria, origen, subcategoria)
    )
    conn.commit()
    conn.close()

def actualizar_mensaje_dataset(item_id, mensaje, categoria, origen="Manual", subcategoria=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE dataset SET mensaje = ?, categoria = ?, origen = ?, subcategoria = ? WHERE id = ?",
        (mensaje, categoria, origen, subcategoria, item_id)
    )
    conn.commit()
    conn.close()

def eliminar_mensaje_dataset(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dataset WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def cargar_csv_a_dataset(filepath):
    import csv
    conn = get_connection()
    cursor = conn.cursor()
    insertados = 0
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cursor.execute(
                "INSERT INTO dataset (mensaje, categoria, origen, subcategoria) VALUES (?, ?, ?, ?)",
                (row.get('mensaje',''), row.get('categoria',''), row.get('origen','CSV'), row.get('subcategoria',''))
            )
            insertados += 1
    conn.commit()
    conn.close()
    return insertados
