import customtkinter as ctk
from database.db import obtener_estadisticas
from ml.trainer import cargar_modelo
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

COLOR_FRAUDE     = "#ef4444"
COLOR_SOSPECHOSO = "#f59e0b"
COLOR_LEGITIMO   = "#22c55e"

class PanelGeneralView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Panel General - Resumen del Sistema",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#1e293b"
                     ).pack(anchor="w", padx=30, pady=(25, 2))
        ctk.CTkLabel(self, text="Estado general del detector de fraudes digitales en español boliviano",
                     font=ctk.CTkFont(size=13), text_color="#64748b"
                     ).pack(anchor="w", padx=30, pady=(0, 20))

        # Tarjetas de estadísticas
        frame_stats = ctk.CTkFrame(self, fg_color="transparent")
        frame_stats.pack(fill="x", padx=30, pady=(0, 20))

        self.card_total     = self._stat_card(frame_stats, "Total Mensajes\nAnalizados:", "0", "#1e40af")
        self.card_fraudes   = self._stat_card(frame_stats, "Fraudes\nDetectados:", "0", COLOR_FRAUDE)
        self.card_sosp      = self._stat_card(frame_stats, "Mensajes\nSospechosos:", "0", COLOR_SOSPECHOSO)
        self.card_legitimos = self._stat_card(frame_stats, "Mensajes\nLegítimos:", "0", COLOR_LEGITIMO)

        # Fila inferior: estado modelo + gráfico
        frame_inferior = ctk.CTkFrame(self, fg_color="transparent")
        frame_inferior.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Estado del modelo
        self.frame_modelo = ctk.CTkFrame(frame_inferior, fg_color="white", border_width=1,
                                          border_color="#e2e8f0", corner_radius=12)
        self.frame_modelo.pack(side="left", fill="both", expand=True, padx=(0,10))
        ctk.CTkLabel(self.frame_modelo, text="Estado del Modelo Activo",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#1e293b"
                     ).pack(anchor="w", padx=20, pady=(15,10))
        self.lbl_algoritmo  = self._info_label(self.frame_modelo, "Algoritmo:", "Sin modelo")
        self.lbl_f1         = self._info_label(self.frame_modelo, "F1-Score (Fraude):", "-")
        self.lbl_recall     = self._info_label(self.frame_modelo, "Recall (Fraude):", "-")
        self.lbl_fecha      = self._info_label(self.frame_modelo, "Último entrenamiento:", "-")
        self.badge_estado   = ctk.CTkFrame(self.frame_modelo, fg_color="#94a3b8", corner_radius=8, width=100, height=28)
        self.badge_estado.pack(anchor="w", padx=20, pady=(10,15))
        self.badge_estado.pack_propagate(False)
        self.lbl_badge = ctk.CTkLabel(self.badge_estado, text="Sin entrenar",
                                       font=ctk.CTkFont(size=11, weight="bold"), text_color="white")
        self.lbl_badge.place(relx=0.5, rely=0.5, anchor="center")

        # Gráfico distribución
        self.frame_grafico = ctk.CTkFrame(frame_inferior, fg_color="white", border_width=1,
                                           border_color="#e2e8f0", corner_radius=12)
        self.frame_grafico.pack(side="right", fill="both", expand=True)
        ctk.CTkLabel(self.frame_grafico, text="Distribución de Categorías Evaluadas",
                     font=ctk.CTkFont(size=14, weight="bold"), text_color="#1e293b"
                     ).pack(anchor="w", padx=20, pady=(15,5))
        self.canvas_grafico = None

    def _stat_card(self, parent, titulo, valor, color):
        card = ctk.CTkFrame(parent, fg_color="white", border_width=2, border_color=color,
                            corner_radius=12, width=160, height=100)
        card.pack(side="left", padx=8, fill="y")
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=12), text_color="#64748b",
                     justify="center").pack(pady=(12,2))
        lbl = ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=28, weight="bold"), text_color=color)
        lbl.pack()
        return lbl

    def _info_label(self, parent, clave, valor):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=2)
        ctk.CTkLabel(f, text=clave, font=ctk.CTkFont(size=12), text_color="#64748b", width=180, anchor="w").pack(side="left")
        lbl = ctk.CTkLabel(f, text=valor, font=ctk.CTkFont(size=12, weight="bold"), text_color="#1e293b")
        lbl.pack(side="left")
        return lbl

    def on_show(self):
        self._actualizar()

    def _actualizar(self):
        stats = obtener_estadisticas()
        self.card_total.configure(text=str(stats["total"]))
        self.card_fraudes.configure(text=str(stats["fraudes"]))
        self.card_sosp.configure(text=str(stats["sospechosos"]))
        self.card_legitimos.configure(text=str(stats["legitimos"]))

        # Modelo
        _, info = cargar_modelo()
        if info:
            self.lbl_algoritmo.configure(text=info.get("algoritmo", "-"))
            self.lbl_f1.configure(text=f"{info.get('f1', 0)}%")
            self.lbl_recall.configure(text=f"{info.get('recall', 0)}%")
            self.lbl_fecha.configure(text=info.get("fecha", "-"))
            self.badge_estado.configure(fg_color=COLOR_LEGITIMO)
            self.lbl_badge.configure(text="Operativo")
        else:
            self.lbl_algoritmo.configure(text="Sin modelo entrenado")
            self.badge_estado.configure(fg_color="#94a3b8")
            self.lbl_badge.configure(text="Sin entrenar")

        # Gráfico
        self._dibujar_grafico(stats)

    def _dibujar_grafico(self, stats):
        if self.canvas_grafico:
            self.canvas_grafico.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(4, 2.5))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")

        categorias = ["Fraude", "Sospechoso", "Legítimo"]
        valores    = [stats["fraudes"], stats["sospechosos"], stats["legitimos"]]
        colores    = [COLOR_FRAUDE, COLOR_SOSPECHOSO, COLOR_LEGITIMO]

        bars = ax.barh(categorias, valores, color=colores, height=0.5)
        ax.set_xlabel("Cantidad", fontsize=9)
        ax.tick_params(axis='both', labelsize=9)
        for bar, val in zip(bars, valores):
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    str(val), va='center', fontsize=9)
        plt.tight_layout()

        self.canvas_grafico = FigureCanvasTkAgg(fig, master=self.frame_grafico)
        self.canvas_grafico.draw()
        self.canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=(0,10))
        plt.close(fig)
