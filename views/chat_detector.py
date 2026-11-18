import customtkinter as ctk
from ml.predictor import analizar_mensaje
from database.db import guardar_analisis

# Colores del tema
COLOR_FRAUDE     = "#ef4444"
COLOR_SOSPECHOSO = "#f59e0b"
COLOR_LEGITIMO   = "#22c55e"
COLOR_BG_RESULT  = "#fef2f2"
COLOR_BORDER     = "#fca5a5"

EJEMPLOS = {
    "🏆 Premio falso":        "Felicidades has ganado Bs 5.000. Para reclamar tu premio debes realizar un depósito de Bs 150 por QR y enviar tu comprobante.",
    "💬 Mensaje normal":      "Hola hermano, nos vemos en la facultad a las 2, no llegues tarde.",
    "🏦 Bloqueo de cuenta":   "URGENTE: Tu cuenta bancaria fue suspendida. Ingresa al enlace tinyurl.com/banco-seguro para verificar tus datos.",
}

class ChatDetectorView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")
        self._build_ui()

    def _build_ui(self):
        # Título
        ctk.CTkLabel(self, text="Chat Detector - Análisis de Mensajes",
                     font=ctk.CTkFont(size=22, weight="bold"),
                     text_color="#1e293b").pack(anchor="w", padx=30, pady=(25, 2))
        ctk.CTkLabel(self, text="Pega un mensaje sospechoso de WhatsApp, SMS o redes sociales para evaluar su riesgo",
                     font=ctk.CTkFont(size=13), text_color="#64748b").pack(anchor="w", padx=30, pady=(0, 15))

        # Botones de ejemplos
        frame_ejemplos = ctk.CTkFrame(self, fg_color="transparent")
        frame_ejemplos.pack(anchor="w", padx=30, pady=(0, 15))
        for label, texto in EJEMPLOS.items():
            ctk.CTkButton(frame_ejemplos, text=label, width=170, height=32,
                          fg_color="white", text_color="#374151", border_width=1,
                          border_color="#d1d5db", hover_color="#f3f4f6",
                          font=ctk.CTkFont(size=12),
                          command=lambda t=texto: self._cargar_ejemplo(t)
                          ).pack(side="left", padx=5)

        # Área de resultado (burbuja + análisis)
        self.frame_resultado = ctk.CTkScrollableFrame(self, fg_color="#f8fafc", corner_radius=10, height=320)
        self.frame_resultado.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        self.lbl_placeholder = ctk.CTkLabel(self.frame_resultado,
                                             text="El análisis aparecerá aquí...",
                                             text_color="#94a3b8", font=ctk.CTkFont(size=13))
        self.lbl_placeholder.pack(pady=60)

        # Input + botón analizar
        frame_input = ctk.CTkFrame(self, fg_color="white", border_width=1, border_color="#e2e8f0", corner_radius=10)
        frame_input.pack(fill="x", padx=30, pady=(0, 20))
        self.txt_input = ctk.CTkTextbox(frame_input, height=55, font=ctk.CTkFont(size=13),
                                         fg_color="white", border_width=0, text_color="#1e293b")
        self.txt_input.pack(side="left", fill="both", expand=True, padx=10, pady=8)
        self.txt_input.insert("0.0", "Escribe o pega aquí el mensaje sospechoso...")
        self.txt_input.bind("<FocusIn>", self._clear_placeholder)
        ctk.CTkButton(frame_input, text="Analizar", width=110, height=40,
                      fg_color="#1e40af", hover_color="#1d4ed8",
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._analizar).pack(side="right", padx=10, pady=8)

    def _clear_placeholder(self, event=None):
        contenido = self.txt_input.get("0.0", "end").strip()
        if contenido == "Escribe o pega aquí el mensaje sospechoso...":
            self.txt_input.delete("0.0", "end")

    def _cargar_ejemplo(self, texto):
        self.txt_input.delete("0.0", "end")
        self.txt_input.insert("0.0", texto)

    def _analizar(self):
        mensaje = self.txt_input.get("0.0", "end").strip()
        if not mensaje or mensaje == "Escribe o pega aquí el mensaje sospechoso...":
            return

        resultado = analizar_mensaje(mensaje)
        guardar_analisis(mensaje, resultado["categoria"], resultado["nivel_riesgo"], resultado["confianza"])
        self._mostrar_resultado(mensaje, resultado)

    def _mostrar_resultado(self, mensaje, resultado):
        # Limpiar frame de resultado
        for widget in self.frame_resultado.winfo_children():
            widget.destroy()

        cat = resultado["categoria"]
        color_cat = {"fraude": COLOR_FRAUDE, "sospechoso": COLOR_SOSPECHOSO, "legitimo": COLOR_LEGITIMO}.get(cat, "#64748b")
        nivel = resultado["nivel_riesgo"]
        confianza = resultado["confianza"]
        indicadores = resultado["indicadores"]
        recomendacion = resultado["recomendacion"]

        # Burbuja del mensaje (simulando WhatsApp)
        frame_burbuja = ctk.CTkFrame(self.frame_resultado, fg_color="#e2e8f0", corner_radius=12)
        frame_burbuja.pack(anchor="e", padx=20, pady=(15, 5), fill="x")
        ctk.CTkLabel(frame_burbuja, text=mensaje[:300], wraplength=580,
                     font=ctk.CTkFont(size=13), text_color="#1e293b",
                     justify="left").pack(padx=15, pady=10)

        # Card de análisis
        frame_card = ctk.CTkFrame(self.frame_resultado, fg_color=COLOR_BG_RESULT if cat == "fraude" else "#f0fdf4" if cat == "legitimo" else "#fffbeb",
                                   corner_radius=12, border_width=2, border_color=color_cat)
        frame_card.pack(fill="x", padx=20, pady=5)

        # Header: clasificación
        frame_header = ctk.CTkFrame(frame_card, fg_color=color_cat, corner_radius=6)
        frame_header.pack(anchor="w", padx=15, pady=(12, 6))
        ctk.CTkLabel(frame_header, text=f"  CLASIFICACIÓN: {cat.upper()}  ",
                     font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="white").pack(padx=5, pady=3)

        ctk.CTkLabel(frame_card, text=f"Nivel de riesgo: {nivel}",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color="#1e293b").pack(anchor="w", padx=15)
        ctk.CTkLabel(frame_card, text=f"Confianza del modelo: {round(confianza*100, 1)}%",
                     font=ctk.CTkFont(size=13, weight="bold"), text_color="#1e293b").pack(anchor="w", padx=15, pady=(2,8))

        if indicadores:
            ctk.CTkLabel(frame_card, text="Indicadores encontrados:",
                         font=ctk.CTkFont(size=13, weight="bold"), text_color="#1e293b").pack(anchor="w", padx=15)
            for ind in indicadores:
                ctk.CTkLabel(frame_card, text=f"  • {ind}",
                             font=ctk.CTkFont(size=12), text_color="#374151").pack(anchor="w", padx=15)

        # Recomendación
        frame_rec = ctk.CTkFrame(frame_card, fg_color="white", corner_radius=8)
        frame_rec.pack(fill="x", padx=15, pady=(10, 12))
        ctk.CTkLabel(frame_rec, text="Recomendación:", font=ctk.CTkFont(size=12, weight="bold"),
                     text_color="#1e293b").pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(frame_rec, text=recomendacion, wraplength=550,
                     font=ctk.CTkFont(size=12), text_color="#374151", justify="left").pack(anchor="w", padx=10, pady=(0,8))
