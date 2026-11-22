# views/entrenar_modelo.py
"""
Módulo 5: Entrenar Modelo - Random Forest.
Enfocado exclusivamente en el clasificador Random Forest (100 árboles).
Muestra métricas detalladas, matriz de confusión 3x3 y explicación de aprendizaje.
"""

import threading
from datetime import datetime
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

from ui.theme import (
    AZUL, AZUL_OSCURO, AZUL_SELECCION, FONDO, BLANCO, BORDE, TEXTO, TEXTO_MUTED,
    ROJO, ROJO_CLARO, AMBAR, VERDE, FONT_FAMILY, FONT_PAGE_TITLE, FONT_SUBTITLE,
    FONT_CARD_TITLE, FONT_BODY, FONT_BODY_BOLD, FONT_TABLE_HEAD, FONT_TABLE_CELL,
    FONT_TABLE_CELL_BOLD, FONT_BUTTON, BORDER_WIDTH, RADIUS_CARD, RADIUS_INPUT,
    RADIUS_BUTTON, BTN_HEIGHT_TRAIN, BTN_HEIGHT_TOOL
)
from ui.components import (
    PageHeader, DataTable, Badge, BotonPrimario, BotonContorno, cargar_icono_ctk
)
from database.db import obtener_dataset
from ml.trainer import entrenar_random_forest, guardar_modelo, cargar_modelo

class EntrenarModeloView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FONDO, corner_radius=0)
        self._resultado = None
        self._pipeline_entrenado = None
        self.canvas_cm = None

        self._build_ui()
        self._cargar_estado_inicial()

    def _build_ui(self):
        # 1. Encabezado Oficial
        PageHeader(
            self,
            titulo="Entrenar Modelo - Random Forest",
            subtitulo="Entrena y evalúa el clasificador Random Forest (100 árboles) en español boliviano"
        )

        # 2. Fila Superior: Tarjeta del Algoritmo + Botón Iniciar Entrenamiento (56px)
        frame_superior = ctk.CTkFrame(
            self,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD
        )
        frame_superior.pack(fill="x", padx=40, pady=(0, 16))

        inner_sup = ctk.CTkFrame(frame_superior, fg_color="transparent")
        inner_sup.pack(fill="x", padx=24, pady=16)

        # Izquierda: Información del algoritmo oficial
        col_izq = ctk.CTkFrame(inner_sup, fg_color="transparent")
        col_izq.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            col_izq,
            text="Algoritmo Oficial: Random Forest Classifier",
            font=ctk.CTkFont(family=FONT_CARD_TITLE[0], size=18, weight="bold"),
            text_color=AZUL_OSCURO
        ).pack(anchor="w", pady=(0, 4))

        ctk.CTkLabel(
            col_izq,
            text="Ensemble de 100 árboles de decisión con vectorización TF-IDF (unigramas y bigramas). Robusto contra sobreajuste.",
            font=ctk.CTkFont(family=FONT_BODY[0], size=14),
            text_color=TEXTO_MUTED
        ).pack(anchor="w")

        # Derecha: Botón Iniciar Entrenamiento (56px de alto)
        self.btn_entrenar = BotonPrimario(
            inner_sup,
            text="Iniciar Entrenamiento",
            icon="play_white.png",
            width=230,
            height=BTN_HEIGHT_TRAIN,
            command=self._iniciar_entrenamiento
        )
        self.btn_entrenar.pack(side="right", padx=(20, 0))

        # Barra de progreso para hilo de entrenamiento
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=4,
            corner_radius=2,
            fg_color=BORDE,
            progress_color=AZUL
        )
        self.progress_bar.pack(fill="x", padx=40, pady=(0, 8))
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()

        # Etiqueta de estado
        self.lbl_estado = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(family=FONT_BODY[0], size=14),
            text_color=TEXTO_MUTED
        )
        self.lbl_estado.pack(anchor="w", padx=40, pady=(0, 10))

        # 3. Tarjeta Métricas de Clasificación usando DataTable (Alineada 100%)
        columnas_metricas = [
            ("Algoritmo", 1, "w", 280),
            ("F1-Score (Fraude)", 0, "center", 150),
            ("Precisión", 0, "center", 120),
            ("Sensibilidad (Recall)", 0, "center", 150),
            ("Exactitud", 0, "center", 120),
            ("Estado", 0, "center", 110)
        ]

        self.tabla_metricas = DataTable(
            self,
            columnas=columnas_metricas,
            empty_message="Aún no se ha ejecutado ningún entrenamiento de Random Forest"
        )
        self.tabla_metricas.pack(fill="x", expand=False, padx=40, pady=(0, 16))

        # 4. Fila Inferior: Matriz de Confusión + Guía Lateral (2 Tarjetas de igual altura)
        frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        frame_inferior.pack(fill="both", expand=True, padx=40, pady=(0, 16))

        frame_inferior.grid_columnconfigure(0, weight=6, uniform="bloques_matriz")
        frame_inferior.grid_columnconfigure(1, weight=4, uniform="bloques_matriz")
        frame_inferior.grid_rowconfigure(0, weight=1)

        # Tarjeta Izquierda: Matriz de Confusión
        self.card_cm = ctk.CTkFrame(
            frame_inferior,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD
        )
        self.card_cm.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        self.lbl_titulo_cm = ctk.CTkLabel(
            self.card_cm,
            text="Matriz de Confusión: Random Forest (3x3)",
            font=ctk.CTkFont(family=FONT_CARD_TITLE[0], size=16, weight="bold"),
            text_color=AZUL_OSCURO
        )
        self.lbl_titulo_cm.pack(anchor="w", padx=20, pady=(16, 6))

        self.frame_canvas_cm = ctk.CTkFrame(self.card_cm, fg_color="transparent")
        self.frame_canvas_cm.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.lbl_cm_placeholder = ctk.CTkLabel(
            self.frame_canvas_cm,
            text="Pulsa 'Iniciar Entrenamiento' para visualizar la matriz de confusión de Random Forest.",
            font=ctk.CTkFont(family=FONT_BODY[0], size=14),
            text_color=TEXTO_MUTED
        )
        self.lbl_cm_placeholder.pack(pady=60)

        # Tarjeta Derecha: Guía de Aprendizaje e Interpretación
        card_guia = ctk.CTkFrame(
            frame_inferior,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD
        )
        card_guia.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        head_guia = ctk.CTkFrame(card_guia, fg_color="transparent")
        head_guia.pack(anchor="w", padx=20, pady=(16, 10))

        img_info = cargar_icono_ctk("info.png", size=(22, 22))
        if img_info:
            ctk.CTkLabel(head_guia, text="", image=img_info).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            head_guia,
            text="¿Cómo aprende Random Forest?",
            font=ctk.CTkFont(family=FONT_CARD_TITLE[0], size=16, weight="bold"),
            text_color=AZUL_OSCURO
        ).pack(side="left")

        puntos_guia = [
            ("• Bosque de 100 Árboles:", "Combina 100 árboles de decisión independientes. Cada árbol vota por Fraude, Sospechoso o Legítimo."),
            ("• Vocabulario Boliviano:", "Aprende patrones dialectales como 'yapeame', 'tigo money', 'encomienda', 'ganaste bs' y enlaces."),
            ("• Diagonal de Aciertos:", "Las casillas azul oscuro muestran los mensajes clasificados con exactitud en su clase real."),
            ("• Falsos Negativos:", "Evita que fraudes reales sean confundidos como legítimos, priorizando un Recall elevado.")
        ]
        for tit, desc in puntos_guia:
            ctk.CTkLabel(
                card_guia,
                text=tit,
                font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=13, weight="bold"),
                text_color=TEXTO
            ).pack(anchor="w", padx=20, pady=(4, 1))

            ctk.CTkLabel(
                card_guia,
                text=desc,
                font=ctk.CTkFont(family=FONT_BODY[0], size=12),
                text_color=TEXTO_MUTED,
                wraplength=280,
                justify="left"
            ).pack(anchor="w", padx=20, pady=(0, 4))

        # 5. Barra Inferior Final: Modelo Seleccionado para Producción con borde 2px
        self.banner_activo = ctk.CTkFrame(
            self,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD,
            height=54
        )
        self.banner_activo.pack(fill="x", padx=40, pady=(0, 24))
        self.banner_activo.pack_propagate(False)

        frame_banner_izq = ctk.CTkFrame(self.banner_activo, fg_color="transparent")
        frame_banner_izq.pack(side="left", padx=20)

        ctk.CTkLabel(
            frame_banner_izq,
            text="Modelo Seleccionado para Producción: ",
            font=ctk.CTkFont(family=FONT_BODY[0], size=16),
            text_color=TEXTO
        ).pack(side="left")

        self.lbl_nombre_activo = ctk.CTkLabel(
            frame_banner_izq,
            text="Random Forest Classifier (100 árboles)",
            font=ctk.CTkFont(family=FONT_PAGE_TITLE[0], size=18, weight="bold"),
            text_color=AZUL_OSCURO
        )
        self.lbl_nombre_activo.pack(side="left", padx=(4, 16))

        # Badge ACTIVO a la derecha
        self.frame_badge_activo = ctk.CTkFrame(self.banner_activo, fg_color="transparent")
        self.frame_badge_activo.pack(side="right", padx=20)

        self.badge_activo = Badge(self.frame_badge_activo, categoria="ACTIVO", alto=30, ancho=110)
        self.badge_activo.pack(side="right")

    def _cargar_estado_inicial(self):
        pipeline, info = cargar_modelo()
        if pipeline is not None and isinstance(info, dict):
            f1_val = info.get("f1", "—")
            rec_val = info.get("recall", "—")
            prec_val = info.get("precision", "—")
            acc_val = info.get("accuracy", "—")
            fecha_val = info.get("fecha", "—")

            self.tabla_metricas.clear()
            def make_badge_estado(parent):
                return Badge(parent, categoria="ACTIVO", alto=28, ancho=95)

            self.tabla_metricas.add_row(
                [
                    "1. Random Forest Classifier   ✓",
                    f"{f1_val}%",
                    f"{prec_val}%",
                    f"{rec_val}%",
                    f"{acc_val}%",
                    make_badge_estado
                ],
                is_highlighted=True
            )
            # Si existen datos de matriz guardados, mostrarla
            if "cm" in info and "cm_labels" in info:
                self._dibujar_matriz(info)
        else:
            self.tabla_metricas.show_empty("Aún no se ha ejecutado ningún entrenamiento de Random Forest")

    def _iniciar_entrenamiento(self):
        filas = obtener_dataset()
        if len(filas) < 10:
            self.lbl_estado.configure(
                text="El dataset contiene menos de 10 mensajes. Agrega más registros en el módulo Dataset.",
                text_color=ROJO
            )
            return

        self.btn_entrenar.configure(state="disabled", text="Entrenando...")
        self.progress_bar.pack(fill="x", padx=40, pady=(0, 8))
        self.progress_bar.start()
        self.lbl_estado.configure(
            text="Entrenando Random Forest con 100 árboles de decisión... por favor espera.",
            text_color=TEXTO_MUTED
        )

        mensajes = [f[1] for f in filas]
        etiquetas = [f[2] for f in filas]

        def tarea_hilo():
            try:
                res = entrenar_random_forest(mensajes, etiquetas)
                self._resultado = res
                self._pipeline_entrenado = res["pipeline"]

                # Guardar automáticamente como modelo activo
                guardar_modelo(res["pipeline"], {
                    "algoritmo": "Random Forest",
                    "f1": res["f1"],
                    "recall": res["recall"],
                    "precision": res["precision"],
                    "accuracy": res["accuracy"],
                    "fecha": datetime.now().strftime("%d/%m/%Y"),
                    "cm": res["cm"].tolist() if hasattr(res["cm"], "tolist") else res["cm"],
                    "cm_labels": res["cm_labels"]
                })

                self.after(0, self._finalizar_entrenamiento_exitoso)
            except Exception as e:
                self.after(0, lambda err=str(e): self._finalizar_entrenamiento_error(err))

        threading.Thread(target=tarea_hilo, daemon=True).start()

    def _finalizar_entrenamiento_error(self, err_msg: str):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_entrenar.configure(state="normal", text="Iniciar Entrenamiento")
        self.lbl_estado.configure(
            text=f"Error durante el entrenamiento: {err_msg}",
            text_color=ROJO
        )

    def _finalizar_entrenamiento_exitoso(self):
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        self.btn_entrenar.configure(state="normal", text="Iniciar Entrenamiento")

        res = self._resultado
        self.lbl_estado.configure(
            text=f"Entrenamiento completado con éxito. Random Forest operativo (F1-Score: {res['f1']}%, Recall: {res['recall']}%).",
            text_color=VERDE
        )

        # Renderizar fila de Random Forest en la tabla
        self.tabla_metricas.clear()

        def make_badge_estado(parent):
            return Badge(parent, categoria="ACTIVO", alto=28, ancho=95)

        self.tabla_metricas.add_row(
            [
                "1. Random Forest Classifier   ✓",
                f"{res['f1']:.1f}%",
                f"{res['precision']:.1f}%",
                f"{res['recall']:.1f}%",
                f"{res['accuracy']:.1f}%",
                make_badge_estado
            ],
            is_highlighted=True
        )

        # Dibujar matriz de confusión
        self._dibujar_matriz(res)

    def _dibujar_matriz(self, res: dict):
        try:
            self.lbl_cm_placeholder.pack_forget()
        except Exception:
            pass

        if self.canvas_cm:
            try:
                self.canvas_cm.get_tk_widget().destroy()
            except Exception:
                pass
            self.canvas_cm = None

        cm = np.array(res["cm"])
        labels = res["cm_labels"]

        # Formatear etiquetas con mayúscula inicial y tildes para máxima legibilidad
        nombres_clases = [
            {"fraude": "Fraude", "legitimo": "Legítimo", "sospechoso": "Sospechoso"}.get(str(l).lower(), str(l).capitalize())
            for l in labels
        ]

        fig, ax = plt.subplots(figsize=(4.8, 3.2), dpi=100)
        fig.patch.set_facecolor('#FFFFFF')
        ax.set_facecolor('#FFFFFF')

        im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        # Rotación a 20 grados para evitar que las etiquetas se sobrepongan
        ax.set_xticklabels(nombres_clases, fontsize=9.5, color=TEXTO, rotation=20, ha='right')
        ax.set_yticklabels(nombres_clases, fontsize=9.5, color=TEXTO)
        ax.tick_params(axis='x', pad=6)
        ax.tick_params(axis='y', pad=6)
        ax.set_xlabel("Predicción del Modelo", fontsize=10, fontweight='bold', color=AZUL_OSCURO, labelpad=8)
        ax.set_ylabel("Etiqueta Real", fontsize=10, fontweight='bold', color=AZUL_OSCURO, labelpad=8)

        thresh = cm.max() / 2. if cm.max() > 0 else 1.0
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(
                    j, i, str(cm[i, j]),
                    ha="center", va="center",
                    fontsize=12, fontweight='bold',
                    color="white" if cm[i, j] > thresh else AZUL_OSCURO
                )

        plt.tight_layout()

        self.canvas_cm = FigureCanvasTkAgg(fig, master=self.frame_canvas_cm)
        self.canvas_cm.draw()
        self.canvas_cm.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        plt.close(fig)

    def on_show(self):
        self._cargar_estado_inicial()
