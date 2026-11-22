# views/panel_general.py
"""
Módulo 3: Panel General - Resumen del Sistema.
Implementado fielmente según las Reglas Globales (Prompt 2).
"""

import logging
import sqlite3
from datetime import datetime
import tkinter as tk
import customtkinter as ctk

from ui.theme import (
    AZUL, AZUL_OSCURO, AZUL_SELECCION, FONDO, BLANCO, BORDE, TEXTO, TEXTO_MUTED,
    ROJO, ROJO_CLARO, AMBAR, AMBAR_CLARO, VERDE, VERDE_CLARO, SIDEBAR_HOVER,
    FONT_FAMILY, FONT_PAGE_TITLE, FONT_SUBTITLE, FONT_CARD_TITLE, FONT_STAT_NUM,
    FONT_BODY, FONT_BODY_BOLD, FONT_BUTTON, BORDER_WIDTH, RADIUS_CARD, RADIUS_BUTTON,
    BTN_HEIGHT_TOOL
)
from ui.components import PageHeader, Badge, BotonPrimario
from database.db import obtener_estadisticas
from ml.trainer import cargar_modelo

logger = logging.getLogger(__name__)

def _metrica_fmt(valor) -> str:
    """Formatea métricas a porcentaje con un decimal."""
    try:
        num = float(valor)
        if 0 <= num <= 1.0:
            num = num * 100.0
        return f"{num:.1f}%"
    except (ValueError, TypeError):
        return "—"

class PanelGeneralView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FONDO, corner_radius=0)
        self._build_ui()
        self._actualizar()

    def _build_ui(self):
        # 1. Encabezado Oficial con Botón de Actualizar alineado a la derecha
        frame_top = ctk.CTkFrame(self, fg_color="transparent")
        frame_top.pack(fill="x", padx=40, pady=(32, 16))

        info_header = ctk.CTkFrame(frame_top, fg_color="transparent")
        info_header.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            info_header,
            text="Panel General - Resumen del Sistema",
            font=ctk.CTkFont(family=FONT_PAGE_TITLE[0], size=FONT_PAGE_TITLE[1], weight=FONT_PAGE_TITLE[2]),
            text_color=AZUL_OSCURO
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_header,
            text="Estado general del detector de fraudes digitales en español boliviano",
            font=ctk.CTkFont(family=FONT_SUBTITLE[0], size=FONT_SUBTITLE[1]),
            text_color=TEXTO_MUTED
        ).pack(anchor="w", pady=(6, 0))

        self.btn_refresh = BotonPrimario(
            frame_top,
            text="Actualizar",
            width=130,
            height=BTN_HEIGHT_TOOL,
            command=self._actualizar
        )
        self.btn_refresh.pack(side="right", anchor="center")

        # 2. Fila Superior: 4 Tarjetas Estadísticas con gap 24px
        self.frame_tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tarjetas.pack(fill="x", padx=40, pady=(0, 24))

        for col in range(4):
            self.frame_tarjetas.grid_columnconfigure(col, weight=1, uniform="stat_cards")

        # Tarjeta 1: Total (sin barra inferior)
        self.lbl_num_total = self._crear_stat_card(
            col=0,
            titulo="Total Mensajes\nAnalizados:",
            color_barra=None
        )

        # Tarjeta 2: Fraudes (barra ROJO)
        self.lbl_num_fraudes = self._crear_stat_card(
            col=1,
            titulo="Fraudes\nDetectados:",
            color_barra=ROJO
        )

        # Tarjeta 3: Sospechosos (barra AMBAR)
        self.lbl_num_sospechosos = self._crear_stat_card(
            col=2,
            titulo="Mensajes\nSospechosos:",
            color_barra=AMBAR
        )

        # Tarjeta 4: Legítimos (barra VERDE)
        self.lbl_num_legitimos = self._crear_stat_card(
            col=3,
            titulo="Mensajes\nLegítimos:",
            color_barra=VERDE
        )

        # 3. Fila Inferior: 2 Tarjetas del mismo ancho y misma altura (Sección 3)
        self.frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inferior.pack(fill="both", expand=True, padx=40, pady=(0, 24))

        self.frame_inferior.grid_columnconfigure(0, weight=1, uniform="bloques_inf")
        self.frame_inferior.grid_columnconfigure(1, weight=1, uniform="bloques_inf")
        self.frame_inferior.grid_rowconfigure(0, weight=1)

        # --- TARJETA IZQUIERDA: Estado del Modelo Activo ---
        self.card_modelo = ctk.CTkFrame(
            self.frame_inferior,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD
        )
        self.card_modelo.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        ctk.CTkLabel(
            self.card_modelo,
            text="Estado del Modelo Activo",
            font=ctk.CTkFont(family=FONT_CARD_TITLE[0], size=FONT_CARD_TITLE[1], weight=FONT_CARD_TITLE[2]),
            text_color=AZUL_OSCURO
        ).pack(anchor="w", padx=24, pady=(20, 16))

        # Contenedor de filas clave-valor alineadas en 2 columnas
        frame_filas_mod = ctk.CTkFrame(self.card_modelo, fg_color="transparent")
        frame_filas_mod.pack(fill="x", padx=24, pady=(0, 20))

        self.lbl_val_algoritmo = self._crear_fila_modelo(frame_filas_mod, 0, "Algoritmo:")
        self.lbl_val_f1 = self._crear_fila_modelo(frame_filas_mod, 1, "F1-Score (Fraude):")
        self.lbl_val_recall = self._crear_fila_modelo(frame_filas_mod, 2, "Recall (Fraude):")
        self.lbl_val_fecha = self._crear_fila_modelo(frame_filas_mod, 3, "Último entrenamiento:")

        # Badge Operativo / Sin entrenar
        self.frame_badge_mod = ctk.CTkFrame(self.card_modelo, fg_color="transparent")
        self.frame_badge_mod.pack(anchor="w", padx=24, pady=(4, 20))
        self.badge_widget = Badge(self.frame_badge_mod, categoria="Sin entrenar", alto=30, ancho=110)
        self.badge_widget.pack(side="left")

        # --- TARJETA DERECHA: Distribución de Categorías Evaluadas ---
        self.card_distribucion = ctk.CTkFrame(
            self.frame_inferior,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD
        )
        self.card_distribucion.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        ctk.CTkLabel(
            self.card_distribucion,
            text="Distribución de Categorías Evaluadas",
            font=ctk.CTkFont(family=FONT_CARD_TITLE[0], size=FONT_CARD_TITLE[1], weight=FONT_CARD_TITLE[2]),
            text_color=AZUL_OSCURO
        ).pack(anchor="w", padx=24, pady=(20, 10))

        # Canvas nativo para barras horizontales gruesas y nítidas
        self.canvas_dist = tk.Canvas(self.card_distribucion, bg=BLANCO, highlightthickness=0)
        self.canvas_dist.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self.canvas_dist.bind("<Configure>", lambda e: self._redibujar_barras())

        self._datos_categorias = {"fraudes": 0, "sospechosos": 0, "legitimos": 0, "total": 0}

    def _crear_stat_card(self, col: int, titulo: str, color_barra=None):
        pad_x = (0, 12) if col == 0 else ((12, 0) if col == 3 else 12)
        card = ctk.CTkFrame(
            self.frame_tarjetas,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD
        )
        card.grid(row=0, column=col, sticky="nsew", padx=pad_x)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            inner,
            text=titulo,
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=15, weight=FONT_BODY_BOLD[2]),
            text_color=TEXTO_MUTED,
            justify="center"
        ).pack(anchor="center", pady=(0, 8))

        lbl_num = ctk.CTkLabel(
            inner,
            text="0",
            font=ctk.CTkFont(family=FONT_STAT_NUM[0], size=FONT_STAT_NUM[1], weight=FONT_STAT_NUM[2]),
            text_color=AZUL_OSCURO
        )
        lbl_num.pack(anchor="center", pady=(0, 8))

        if color_barra:
            # Barra inferior de 6px respetando el borde
            barra = ctk.CTkFrame(card, height=6, fg_color=color_barra, corner_radius=3)
            barra.pack(fill="x", side="bottom", padx=8, pady=(0, 6))

        return lbl_num

    def _crear_fila_modelo(self, parent, row_idx: int, label_text: str):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=38)
        row.pack(fill="x", pady=4)
        row.pack_propagate(False)

        ctk.CTkLabel(
            row,
            text=label_text,
            font=ctk.CTkFont(family=FONT_BODY[0], size=16),
            text_color=TEXTO_MUTED
        ).pack(side="left", anchor="center")

        lbl_val = ctk.CTkLabel(
            row,
            text="—",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=16, weight="bold"),
            text_color=AZUL_OSCURO
        )
        lbl_val.pack(side="right", anchor="center")
        return lbl_val

    def _actualizar(self):
        # 1. Consultar estadísticas de SQLite
        try:
            stats = obtener_estadisticas()
        except sqlite3.Error:
            logger.exception("Error al consultar estadísticas para el panel")
            stats = {"total": 0, "fraudes": 0, "sospechosos": 0, "legitimos": 0}

        self.lbl_num_total.configure(text=str(stats.get("total", 0)))
        self.lbl_num_fraudes.configure(text=str(stats.get("fraudes", 0)))
        self.lbl_num_sospechosos.configure(text=str(stats.get("sospechosos", 0)))
        self.lbl_num_legitimos.configure(text=str(stats.get("legitimos", 0)))

        self._datos_categorias = stats
        self._redibujar_barras()

        # 2. Consultar modelo activo
        try:
            modelo, info = cargar_modelo()
            if modelo is not None and isinstance(info, dict):
                self.lbl_val_algoritmo.configure(text=str(info.get("algoritmo", "Random Forest")))
                self.lbl_val_f1.configure(text=_metrica_fmt(info.get("f1")))
                self.lbl_val_recall.configure(text=_metrica_fmt(info.get("recall")))
                self.lbl_val_fecha.configure(text=str(info.get("fecha", "—")))

                self.badge_widget.destroy()
                self.badge_widget = Badge(self.frame_badge_mod, categoria="Operativo", alto=30, ancho=110)
                self.badge_widget.pack(side="left")
            else:
                self._reset_info_modelo()
        except Exception:
            logger.exception("Error al cargar modelo en panel")
            self._reset_info_modelo()

    def _reset_info_modelo(self):
        self.lbl_val_algoritmo.configure(text="Sin modelo entrenado")
        self.lbl_val_f1.configure(text="—")
        self.lbl_val_recall.configure(text="—")
        self.lbl_val_fecha.configure(text="—")

        self.badge_widget.destroy()
        self.badge_widget = Badge(self.frame_badge_mod, categoria="Sin entrenar", alto=30, ancho=110)
        self.badge_widget.pack(side="left")

    def _redibujar_barras(self):
        self.canvas_dist.delete("all")
        w = self.canvas_dist.winfo_width()
        h = self.canvas_dist.winfo_height()

        if w < 100 or h < 100:
            return

        total = self._datos_categorias.get("total", 0)
        if total == 0:
            self.canvas_dist.create_text(
                w / 2, h / 2,
                text="Sin datos todavía",
                font=(FONT_FAMILY, 16),
                fill=TEXTO_MUTED
            )
            return

        # Dibujar cuadrícula vertical tenue de fondo
        num_grid_lines = 5
        x_start = 120
        x_end = w - 60
        disp_width = max(50, x_end - x_start)

        for i in range(num_grid_lines + 1):
            gx = x_start + (disp_width * i / num_grid_lines)
            self.canvas_dist.create_line(gx, 20, gx, h - 30, fill="#E2E8F0", width=1)
            # Porcentaje guía
            pct_val = int((100 * i) / num_grid_lines)
            self.canvas_dist.create_text(
                gx, h - 16,
                text=f"{pct_val}%",
                font=(FONT_FAMILY, 11),
                fill=TEXTO_MUTED
            )

        # 3 barras horizontales gruesas (alto ≈ 44px)
        items = [
            ("Fraude", self._datos_categorias.get("fraudes", 0), ROJO),
            ("Sospechoso", self._datos_categorias.get("sospechosos", 0), AMBAR),
            ("Legítimo", self._datos_categorias.get("legitimos", 0), VERDE)
        ]

        bar_height = 40
        espacio_disponible = (h - 60)
        gap = (espacio_disponible - (bar_height * 3)) / 4
        y_curr = 24 + gap

        max_val = max(1, total)

        for etiqueta, valor, color in items:
            pct = valor / max_val
            bar_len = max(8, disp_width * pct)

            # Etiqueta de categoría a la izquierda
            self.canvas_dist.create_text(
                x_start - 14, y_curr + (bar_height / 2),
                text=etiqueta,
                font=(FONT_FAMILY, 14, "bold"),
                fill=AZUL_OSCURO,
                anchor="e"
            )

            # Barra con esquinas redondeadas
            x0 = x_start
            y0 = y_curr
            x1 = x_start + bar_len
            y1 = y_curr + bar_height

            # Dibujar rectángulo redondeado simulado
            r = 8
            self.canvas_dist.create_rectangle(x0 + r, y0, x1 - r, y1, fill=color, outline="")
            self.canvas_dist.create_rectangle(x0, y0 + r, x1, y1 - r, fill=color, outline="")
            self.canvas_dist.create_oval(x0, y0, x0 + 2*r, y0 + 2*r, fill=color, outline="")
            self.canvas_dist.create_oval(x0, y1 - 2*r, x0 + 2*r, y1, fill=color, outline="")
            self.canvas_dist.create_oval(x1 - 2*r, y0, x1, y0 + 2*r, fill=color, outline="")
            self.canvas_dist.create_oval(x1 - 2*r, y1 - 2*r, x1, y1, fill=color, outline="")

            # Texto de cantidad y porcentaje
            pct_txt = f"{valor} ({(valor/total)*100:.1f}%)" if total > 0 else "0"
            self.canvas_dist.create_text(
                x1 + 10, y_curr + (bar_height / 2),
                text=pct_txt,
                font=(FONT_FAMILY, 13, "bold"),
                fill=AZUL_OSCURO,
                anchor="w"
            )

            y_curr += bar_height + gap

    def on_show(self):
        self._actualizar()
