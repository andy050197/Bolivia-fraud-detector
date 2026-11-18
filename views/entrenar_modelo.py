import customtkinter as ctk
import threading
from datetime import datetime
from database.db import obtener_dataset
from ml.trainer import entrenar_todos, guardar_modelo
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

COLOR_FRAUDE     = "#ef4444"
COLOR_SOSPECHOSO = "#f59e0b"
COLOR_LEGITIMO   = "#22c55e"
COLOR_ACTIVO     = "#1e40af"

ALGORITMOS_DISP  = ["SVM (TF-IDF)", "Naive Bayes", "Regresión Logística", "Random Forest"]

class EntrenarModeloView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")
        self._resultados = []
        self._mejor = None
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Entrenar Modelo - Comparativa de Algoritmos",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#1e293b"
                     ).pack(anchor="w", padx=30, pady=(25,2))
        ctk.CTkLabel(self, text="Selecciona algoritmos para comparar y evaluar sus métricas en español boliviano",
                     font=ctk.CTkFont(size=13), text_color="#64748b"
                     ).pack(anchor="w", padx=30, pady=(0,15))

        # Selección de algoritmos
        frame_sel = ctk.CTkFrame(self, fg_color="transparent")
        frame_sel.pack(anchor="w", padx=30, pady=(0,15))
        ctk.CTkLabel(frame_sel, text="Selección de Algoritmos:", font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="#374151").pack(side="left", padx=(0,15))

        self.checks = {}
        for alg in ALGORITMOS_DISP:
            var = ctk.BooleanVar(value=True)
            cb = ctk.CTkCheckBox(frame_sel, text=alg, variable=var, font=ctk.CTkFont(size=12))
            cb.pack(side="left", padx=10)
            self.checks[alg] = var

        self.btn_entrenar = ctk.CTkButton(frame_sel, text="▶ Iniciar Entrenamiento", width=180, height=36,
                                           fg_color="#1e40af", hover_color="#1d4ed8",
                                           font=ctk.CTkFont(size=13, weight="bold"),
                                           command=self._iniciar_entrenamiento)
        self.btn_entrenar.pack(side="right", padx=(20,0))

        self.lbl_estado = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color="#64748b")
        self.lbl_estado.pack(anchor="w", padx=30)

        # Tabla de métricas
        ctk.CTkLabel(self, text="Métricas de Clasificación (Clase: Fraude)",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#1e293b"
                     ).pack(anchor="w", padx=30, pady=(10,5))

        # Cabecera tabla
        cab = ctk.CTkFrame(self, fg_color="#f1f5f9", corner_radius=0)
        cab.pack(fill="x", padx=30)
        for texto, ancho in [("Algoritmo",220),("F1-Score",90),("Precision",90),("Recall",90),("Accuracy",90),("Ver Matriz",90)]:
            ctk.CTkLabel(cab, text=texto, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#374151", width=ancho, anchor="w").pack(side="left", padx=5, pady=8)

        self.frame_tabla = ctk.CTkFrame(self, fg_color="white", height=180)
        self.frame_tabla.pack(fill="x", padx=30)

        # Área de matriz de confusión + modelo seleccionado
        frame_inf = ctk.CTkFrame(self, fg_color="transparent")
        frame_inf.pack(fill="both", expand=True, padx=30, pady=(10,10))

        self.frame_cm = ctk.CTkFrame(frame_inf, fg_color="white", border_width=1,
                                      border_color="#e2e8f0", corner_radius=10)
        self.frame_cm.pack(side="left", fill="both", expand=True, padx=(0,10))
        self.canvas_cm = None

        # Leyenda
        frame_leyenda = ctk.CTkFrame(frame_inf, fg_color="#f8fafc", corner_radius=10, width=220)
        frame_leyenda.pack(side="right", fill="y")
        frame_leyenda.pack_propagate(False)
        ctk.CTkLabel(frame_leyenda, text="¿Cómo leer esta matriz?",
                     font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e293b"
                     ).pack(anchor="w", padx=15, pady=(15,8))
        for txt in ["• Diagonal azul oscuro: Aciertos exactos del modelo.",
                    "• Fuera de diagonal: Errores de clasificación (falsos positivos/negativos).",
                    "• Objetivo: Maximizar aciertos en Fraude y reducir falsas alarmas."]:
            ctk.CTkLabel(frame_leyenda, text=txt, font=ctk.CTkFont(size=11), text_color="#374151",
                         wraplength=190, justify="left").pack(anchor="w", padx=15, pady=3)

        # Banner modelo activo
        self.frame_activo = ctk.CTkFrame(self, fg_color="#f1f5f9", corner_radius=10, height=50)
        self.frame_activo.pack(fill="x", padx=30, pady=(0,20))
        self.frame_activo.pack_propagate(False)
        self.lbl_modelo_activo = ctk.CTkLabel(self.frame_activo,
                                               text="Modelo Seleccionado para Producción:  —",
                                               font=ctk.CTkFont(size=13, weight="bold"), text_color="#374151")
        self.lbl_modelo_activo.place(relx=0.3, rely=0.5, anchor="center")

    def _iniciar_entrenamiento(self):
        seleccionados = [alg for alg, var in self.checks.items() if var.get()]
        if not seleccionados:
            self.lbl_estado.configure(text="⚠ Selecciona al menos un algoritmo.", text_color=COLOR_FRAUDE)
            return

        filas = obtener_dataset()
        if len(filas) < 10:
            self.lbl_estado.configure(text="⚠ El dataset tiene menos de 10 mensajes. Agrega más datos.", text_color=COLOR_FRAUDE)
            return

        self.btn_entrenar.configure(state="disabled", text="Entrenando...")
        self.lbl_estado.configure(text="⏳ Entrenando modelos, por favor espere...", text_color="#64748b")

        mensajes  = [f[1] for f in filas]
        etiquetas = [f[2] for f in filas]

        def tarea():
            resultados, mejor_nombre, mejor_pipeline = entrenar_todos(mensajes, etiquetas, seleccionados)
            self._resultados = resultados
            self._mejor = mejor_nombre
            if mejor_pipeline and mejor_nombre:
                info_mejor = next(r for r in resultados if r["nombre"] == mejor_nombre)
                guardar_modelo(mejor_pipeline, {
                    "algoritmo": mejor_nombre,
                    "f1": info_mejor["f1"],
                    "recall": info_mejor["recall"],
                    "precision": info_mejor["precision"],
                    "accuracy": info_mejor["accuracy"],
                    "fecha": datetime.now().strftime("%d/%m/%Y")
                })
            self.after(0, self._mostrar_resultados)

        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar_resultados(self):
        self.btn_entrenar.configure(state="normal", text="▶ Iniciar Entrenamiento")
        self.lbl_estado.configure(text=f"✅ Entrenamiento completado. Mejor modelo: {self._mejor}", text_color=COLOR_LEGITIMO)

        for w in self.frame_tabla.winfo_children():
            w.destroy()

        for i, r in enumerate(sorted(self._resultados, key=lambda x: x["f1"], reverse=True)):
            es_mejor = r["nombre"] == self._mejor
            bg = "#eff6ff" if es_mejor else "white"
            frame_fila = ctk.CTkFrame(self.frame_tabla, fg_color=bg)
            frame_fila.pack(fill="x", pady=1)
            ctk.CTkFrame(frame_fila, fg_color="#e2e8f0", height=1).pack(fill="x")
            f = ctk.CTkFrame(frame_fila, fg_color=bg)
            f.pack(fill="x")

            nombre_txt = f"{i+1}. {r['nombre']}" + (" ✓" if es_mejor else "")
            ctk.CTkLabel(f, text=nombre_txt, width=220, font=ctk.CTkFont(size=12, weight="bold" if es_mejor else "normal"),
                         text_color=COLOR_ACTIVO if es_mejor else "#374151", anchor="w").pack(side="left", padx=5, pady=6)
            for val, ancho in [(f"{r['f1']}%",90),(f"{r['precision']}%",90),(f"{r['recall']}%",90),(f"{r['accuracy']}%",90)]:
                ctk.CTkLabel(f, text=val, width=ancho, font=ctk.CTkFont(size=12),
                             text_color="#1e293b", anchor="w").pack(side="left", padx=5)
            ctk.CTkButton(f, text="👁 Ver", width=70, height=28,
                          fg_color=COLOR_ACTIVO if es_mejor else "white",
                          text_color="white" if es_mejor else "#374151",
                          border_width=0 if es_mejor else 1, border_color="#d1d5db",
                          command=lambda res=r: self._mostrar_cm(res)).pack(side="left", padx=5)

        # Mostrar CM del mejor por defecto
        mejor_res = next((r for r in self._resultados if r["nombre"] == self._mejor), None)
        if mejor_res:
            self._mostrar_cm(mejor_res)

        self.lbl_modelo_activo.configure(
            text=f"Modelo Seleccionado para Producción:  {self._mejor}     ",
            text_color="#1e293b"
        )

    def _mostrar_cm(self, resultado):
        if self.canvas_cm:
            self.canvas_cm.get_tk_widget().destroy()

        cm     = resultado["cm"]
        labels = resultado["cm_labels"]
        fig, ax = plt.subplots(figsize=(3.5, 2.8))
        im = ax.imshow(cm, interpolation='nearest', cmap='Blues')
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_yticklabels(labels, fontsize=8)
        ax.set_xlabel("Predicción del Modelo", fontsize=8)
        ax.set_ylabel("Etiqueta Real", fontsize=8)
        thresh = cm.max() / 2.
        for i in range(cm.shape[0]):
            for j in range(cm.shape[1]):
                ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=10,
                        color="white" if cm[i, j] > thresh else "#1e293b")
        plt.tight_layout()

        self.canvas_cm = FigureCanvasTkAgg(fig, master=self.frame_cm)
        self.canvas_cm.draw()
        self.canvas_cm.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig)
