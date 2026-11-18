from ml.trainer import cargar_modelo

# Indicadores de fraude en español boliviano
INDICADORES = {
    "fraude": [
        ("Promesa de premio económico", ["ganaste", "ganó", "premio", "sorteo", "ganaste bs", "seleccionado"]),
        ("Solicitud de depósito anticipado por QR", ["deposita", "depositar", "paga", "yapeame", "tigo money", "qr", "envía tu comprobante"]),
        ("Condicionamiento de pago previo", ["para reclamar", "para liberar", "para recibir", "paga primero", "antes de"]),
        ("Enlace sospechoso", ["tinyurl", "bit.ly", "link.bo", "click aquí", "ingresa al enlace", "http"]),
        ("Urgencia artificial", ["urgente", "urgentemente", "inmediato", "bloqueada", "suspendida", "vence hoy"]),
        ("Solicitud de datos personales", ["clave", "contraseña", "pin", "número de tarjeta", "datos bancarios", "ci número"]),
        ("Phishing bancario", ["banco unión", "banco bisa", "bnb", "cuenta bloqueada", "tarjeta bloqueada"]),
        ("Oferta de trabajo irreal", ["ganar desde casa", "trabajo fácil", "sin experiencia", "bs diarios garantizados"]),
    ],
    "sospechoso": [
        ("Oferta de préstamo sin garantía", ["préstamo rápido", "sin garante", "sin burocracia", "prestamo inmediato"]),
        ("Inversión con retorno garantizado", ["inversión segura", "retorno garantizado", "criptomonedas", "rentabilidad"]),
        ("Venta con pago adelantado", ["paga adelantado", "deposita antes", "precio muy bajo"]),
    ]
}

NIVEL_RIESGO = {
    "fraude": "ALTO",
    "sospechoso": "MEDIO",
    "legitimo": "BAJO"
}

RECOMENDACIONES = {
    "fraude": "⚠️ No realices ningún depósito ni compartas tus datos. Verifica por canales oficiales del banco u operadora.",
    "sospechoso": "🔍 Sé cauteloso. Verifica la identidad del remitente y no entregues dinero ni datos sin confirmar.",
    "legitimo": "✅ Este mensaje parece legítimo. Si tienes dudas, contacta directamente a la entidad por sus canales oficiales."
}

def analizar_mensaje(texto: str):
    """
    Analiza un mensaje y retorna:
    - categoria: 'fraude', 'sospechoso', 'legitimo'
    - confianza: float 0-1
    - nivel_riesgo: str
    - indicadores: list of str
    - recomendacion: str
    """
    pipeline, info = cargar_modelo()
    texto_lower = texto.lower()

    # Detectar indicadores encontrados
    indicadores_encontrados = []
    for categoria_ind, lista in INDICADORES.items():
        for nombre_ind, keywords in lista:
            if any(kw in texto_lower for kw in keywords):
                indicadores_encontrados.append(nombre_ind)

    if pipeline is None:
        # Sin modelo: usar heurística simple
        if len(indicadores_encontrados) >= 2:
            categoria = "fraude"
            confianza = 0.80
        elif len(indicadores_encontrados) == 1:
            categoria = "sospechoso"
            confianza = 0.65
        else:
            categoria = "legitimo"
            confianza = 0.70
    else:
        probs = pipeline.predict_proba([texto])[0]
        clases = pipeline.classes_
        idx = probs.argmax()
        categoria = clases[idx]
        confianza = probs[idx]

    return {
        "categoria": categoria,
        "confianza": confianza,
        "nivel_riesgo": NIVEL_RIESGO.get(categoria, "MEDIO"),
        "indicadores": indicadores_encontrados,
        "recomendacion": RECOMENDACIONES.get(categoria, "")
    }
