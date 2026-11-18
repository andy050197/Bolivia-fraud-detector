# ui/components.py
"""
Componentes reutilizables de CustomTkinter para Bolivia Fraud Detector.
Desacoplados y ajustados fielmente al diseño de los 5 Mockups.
"""

import customtkinter as ctk
from ui.theme import (
    AZUL, AZUL_OSCURO, AZUL_SELECCION, BLANCO, BORDE, TEXTO, TEXTO_MUTED,
    ROJO, ROJO_CLARO, AMBAR, AMBAR_CLARO, VERDE, VERDE_CLARO, GRIS_BURBUJA,
    FONT_FAMILY, FONT_BADGE, RADIUS_CARD, RADIUS_BADGE, RADIUS_PILL
)

def crear_badge_categoria(parent, categoria: str):
    """Crea una píldora compacta de categoría (Fraude, Sospechoso, Legítimo)."""
    cat_lower = str(categoria).lower().strip()
    if cat_lower == "fraude":
        color_fondo = ROJO
        texto = "Fraude"
    elif cat_lower == "sospechoso":
        color_fondo = AMBAR
        texto = "Sospechoso"
    else:
        color_fondo = VERDE
        texto = "Legítimo"

    badge = ctk.CTkFrame(parent, fg_color=color_fondo, corner_radius=RADIUS_BADGE, width=86, height=24)
    badge.pack_propagate(False)
    lbl = ctk.CTkLabel(
        badge,
        text=texto,
        font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
        text_color=BLANCO
    )
    lbl.place(relx=0.5, rely=0.5, anchor="center")
    return badge

def crear_chip_resumen(parent, texto: str):
    """Chip ovalado celeste (AZUL_SELECCION) utilizado en el Dataset de mensajes."""
    chip = ctk.CTkFrame(parent, fg_color=AZUL_SELECCION, corner_radius=RADIUS_PILL, height=32)
    lbl = ctk.CTkLabel(
        chip,
        text=texto,
        font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
        text_color=AZUL_OSCURO
    )
    lbl.pack(padx=16, pady=4)
    return chip

def crear_header_vista(parent, titulo: str, subtitulo: str = None):
    """Encabezado estandarizado para cada una de las 5 vistas."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=40, pady=(32, 16))

    ctk.CTkLabel(
        frame,
        text=titulo,
        font=ctk.CTkFont(family=FONT_FAMILY, size=28, weight="bold"),
        text_color=AZUL_OSCURO
    ).pack(anchor="w")

    if subtitulo:
        ctk.CTkLabel(
            frame,
            text=subtitulo,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14),
            text_color=TEXTO_MUTED
        ).pack(anchor="w", pady=(6, 0))

    return frame
