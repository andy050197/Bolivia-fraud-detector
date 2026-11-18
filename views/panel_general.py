"""Resumen de SQLite y del modelo activo; no entrena ni modifica datos."""
import logging
import sqlite3
from datetime import datetime

import customtkinter as ctk
from ui.theme import AZUL, BLANCO, SIDEBAR_HOVER
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
from database.db import obtener_estadisticas
from ml.trainer import cargar_modelo

COLOR_FRAUDE = "#ef4444"
COLOR_SOSPECHOSO = "#f59e0b"
COLOR_LEGITIMO = "#22c55e"
logger = logging.getLogger(__name__)


def _metrica(valor):
    """trainer guarda métricas en porcentaje, no en escala 0–1."""
    try:
        numero = float(valor)
        return f"{numero:.1f}%" if 0 <= numero <= 100 else "No disponible"
    except (ValueError, TypeError):
        return "No disponible"


class PanelGeneralView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#eef3f8")
        self.canvas_grafico = None
        self._figura = None
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(self, text="Panel General - Resumen del Sistema", anchor="w",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#1e293b").grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 4))
        cabecera = ctk.CTkFrame(self, fg_color="transparent")
        cabecera.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 16))
        cabecera.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(cabecera, text="Detector de fraudes digitales en español boliviano", text_color="#64748b").grid(row=0, column=0, sticky="w")
        ctk.CTkButton(cabecera, text="Actualizar", fg_color=AZUL, hover_color=SIDEBAR_HOVER, text_color=BLANCO, width=105, command=self._actualizar).grid(row=0, column=1)
        tarjetas = ctk.CTkFrame(self, fg_color="transparent")
        tarjetas.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 16))
        for columna in range(4):
            tarjetas.grid_columnconfigure(columna, weight=1, uniform="tarjetas")
        self.card_total = self._stat_card(tarjetas, 0, "Total mensajes\nanalizados", "#1e40af")
        self.card_fraudes = self._stat_card(tarjetas, 1, "Fraudes\ndetectados", COLOR_FRAUDE)
        self.card_sosp = self._stat_card(tarjetas, 2, "Mensajes\nsospechosos", COLOR_SOSPECHOSO)
        self.card_legitimos = self._stat_card(tarjetas, 3, "Mensajes\nlegítimos", COLOR_LEGITIMO)
        # El contenedor permite desplazarse verticalmente en ventanas bajas.
        contenido = ctk.CTkFrame(self, fg_color="transparent")
        contenido.grid(row=3, column=0, sticky="nsew", padx=18)
        contenido.grid_columnconfigure((0, 1), weight=1, uniform="bloques")
        contenido.grid_rowconfigure(0, weight=1)
        self.frame_modelo = ctk.CTkFrame(contenido, fg_color="white", border_width=1, border_color="#e2e8f0", corner_radius=12)
        self.frame_modelo.grid(row=0, column=0, sticky="nsew", padx=4, pady=(0, 12))
        ctk.CTkLabel(self.frame_modelo, text="Estado del Modelo Activo", font=ctk.CTkFont(size=15, weight="bold"), text_color="#1e293b").pack(anchor="w", padx=18, pady=(14, 8))
        self.lbl_algoritmo = self._info_label("Algoritmo:")
        self.lbl_f1 = self._info_label("F1-Score (Fraude):")
        self.lbl_recall = self._info_label("Recall (Fraude):")
        self.lbl_fecha = self._info_label("Último entrenamiento:")
        self.lbl_badge = ctk.CTkLabel(self.frame_modelo, text="Pendiente de consulta", text_color="#64748b")
        self.lbl_badge.pack(anchor="w", padx=18, pady=(8, 14))
        self.frame_grafico = ctk.CTkFrame(contenido, fg_color="white", border_width=1, border_color="#e2e8f0", corner_radius=12)
        self.frame_grafico.grid(row=0, column=1, sticky="nsew", padx=4, pady=(0, 10))
        ctk.CTkLabel(self.frame_grafico, text="Distribución de Categorías Evaluadas", font=ctk.CTkFont(size=15, weight="bold"), text_color="#1e293b").pack(anchor="w", padx=18, pady=(14, 4))
        self.lbl_estado = ctk.CTkLabel(self, text="", anchor="w", text_color="#64748b", wraplength=620)
        self.lbl_estado.grid(row=4, column=0, sticky="ew", padx=24, pady=10)

    def _stat_card(self, parent, columna, titulo, color):
        card = ctk.CTkFrame(parent, fg_color="white", border_width=1, border_color="#aeb9c5", corner_radius=12)
        card.grid(row=0, column=columna, sticky="nsew", padx=4)
        ctk.CTkLabel(card, text=titulo, text_color="#64748b", font=ctk.CTkFont(size=16)).pack(anchor="center", padx=8, pady=(12, 3))
        etiqueta = ctk.CTkLabel(card, text="—", font=ctk.CTkFont(size=28, weight="bold"), text_color="#142448")
        etiqueta.pack(anchor="center", padx=8, pady=(0, 12))
        if columna:
            ctk.CTkFrame(card, height=5, fg_color=color).pack(fill="x", padx=4, pady=(0, 2))
        return etiqueta

    def _info_label(self, titulo):
        fila = ctk.CTkFrame(self.frame_modelo, fg_color="transparent")
        fila.pack(fill="x", padx=18, pady=2)
        fila.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(fila, text=titulo, text_color="#64748b", width=145, anchor="w").grid(row=0, column=0, sticky="nw")
        etiqueta = ctk.CTkLabel(fila, text="—", text_color="#1e293b", anchor="w", justify="left", wraplength=145)
        etiqueta.grid(row=0, column=1, sticky="ew")
        return etiqueta

    def on_show(self):
        self._actualizar()

    def _actualizar(self):
        errores = []
        try:
            stats = obtener_estadisticas()
        except sqlite3.Error:
            logger.exception("No se pudieron consultar las estadísticas")
            for tarjeta in (self.card_total, self.card_fraudes, self.card_sosp, self.card_legitimos):
                tarjeta.configure(text="—")
            self._dibujar_grafico(None)
            errores.append("No se pudieron consultar las estadísticas.")
        else:
            for tarjeta, clave in ((self.card_total, "total"), (self.card_fraudes, "fraudes"),
                                    (self.card_sosp, "sospechosos"), (self.card_legitimos, "legitimos")):
                tarjeta.configure(text=str(stats[clave]))
            self._dibujar_grafico(stats)
        # Ambas fuentes se actualizan independientemente: un fallo no oculta la otra.
        self._restablecer_modelo()
        try:
            modelo, info = cargar_modelo()
            if modelo is not None:
                if not isinstance(info, dict):
                    raise ValueError("Metadatos del modelo inválidos")
                self.lbl_algoritmo.configure(text=info.get("algoritmo") or "No disponible")
                self.lbl_f1.configure(text=_metrica(info.get("f1")))
                self.lbl_recall.configure(text=_metrica(info.get("recall")))
                self.lbl_fecha.configure(text=info.get("fecha") or "No disponible")
                self.lbl_badge.configure(text="Modelo cargado" if info else "Modelo cargado - Sin metadatos", text_color="#15803d")
        except Exception:
            # pickle puede fallar por archivo incompleto, versión o dependencia.
            logger.exception("No se pudo cargar el modelo activo")
            self.lbl_badge.configure(text="Error al cargar el modelo", text_color="#b91c1c")
            errores.append("No se pudo cargar el modelo activo.")
        self.lbl_estado.configure(text=(" ".join(errores) + " Pulsa Actualizar para reintentar." if errores
                                       else "Actualizado: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
                                  text_color="#b91c1c" if errores else "#64748b")

    def _restablecer_modelo(self):
        self.lbl_algoritmo.configure(text="Sin modelo entrenado")
        for etiqueta in (self.lbl_f1, self.lbl_recall, self.lbl_fecha):
            etiqueta.configure(text="—")
        self.lbl_badge.configure(text="Sin entrenar", text_color="#64748b")

    def _liberar_grafico(self):
        if self.canvas_grafico is not None:
            self.canvas_grafico.get_tk_widget().destroy()
            self.canvas_grafico = None
        if self._figura is not None:
            self._figura.clear()
            self._figura = None

    def _dibujar_grafico(self, stats):
        self._liberar_grafico()
        fig = self._figura = Figure(figsize=(3, 2), layout="constrained", dpi=100, facecolor="white")
        ax = fig.add_subplot(111)
        valores = [stats[clave] for clave in ("fraudes", "sospechosos", "legitimos")] if stats is not None else []
        if not valores or not any(valores):
            ax.axis("off")
            texto = "Estadísticas no disponibles" if stats is None else "Aún no hay análisis para graficar"
            ax.text(0.5, 0.5, texto, ha="center", va="center", color="#64748b", transform=ax.transAxes)
        else:
            barras = ax.barh(["Fraude", "Sospechoso", "Legítimo"], valores,
                             color=[COLOR_FRAUDE, COLOR_SOSPECHOSO, COLOR_LEGITIMO], height=0.5)
            ax.invert_yaxis()
            ax.set_xlim(0, max(valores) * 1.3)
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xlabel("Cantidad de mensajes", fontsize=12)
            ax.tick_params(axis="both", labelsize=12)
            for borde in ("top", "right"):
                ax.spines[borde].set_visible(False)
            for barra, valor in zip(barras, valores):
                ax.annotate(str(valor), (valor, barra.get_y() + barra.get_height()/2),
                             xytext=(5, 0), textcoords="offset points", va="center", fontsize=12)
        ax.set_axisbelow(True)
        ax.grid(axis="x", alpha=0.22)
        self.canvas_grafico = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        self.canvas_grafico.draw()
        self.canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def destroy(self):
        self._liberar_grafico()
        super().destroy()
