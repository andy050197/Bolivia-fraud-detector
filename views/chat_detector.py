# views/chat_detector.py
"""
Módulo 1: Chat Detector - Análisis de Mensajes.
Uniformado con las Reglas Globales (Prompt 2).
"""

import os
import customtkinter as ctk
from PIL import Image

from ui.theme import (
    AZUL, AZUL_OSCURO, AZUL_SELECCION, FONDO, BLANCO, BORDE, TEXTO, TEXTO_MUTED,
    ROJO, ROJO_CLARO, AMBAR, AMBAR_CLARO, VERDE, VERDE_CLARO, GRIS_BURBUJA,
    FONT_FAMILY, FONT_PAGE_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD,
    FONT_BUTTON, BORDER_WIDTH, RADIUS_CARD, RADIUS_INPUT, RADIUS_PILL,
    BADGE_HEIGHT_CHAT, BTN_HEIGHT_TOOL
)
from ui.components import PageHeader, Badge, BotonPrimario, BotonContorno
from ml.predictor import analizar_mensaje
from database.db import guardar_analisis

EJEMPLOS = [
    ("Ejemplo: Premio falso", "Felicidades, has ganado Bs 5.000. Para reclamar tu premio debes realizar un depósito de Bs 150 por QR y enviar tu comprobante."),
    ("Ejemplo: Préstamo dudoso", "Te ofrecemos préstamo rápido sin garante ni burocracia hasta Bs 10000. Solo necesitas tu CI."),
    ("Ejemplo: Mensaje normal", "Hola hermano, nos vemos en la facultad a las 2.")
]

class ChatDetectorView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FONDO, corner_radius=0)
        self._cargar_avatar()
        self._build_ui()

    def _cargar_avatar(self):
        avatar_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons", "avatar_shield.png")
        if os.path.exists(avatar_path):
            self.img_avatar = ctk.CTkImage(Image.open(avatar_path), size=(40, 40))
        else:
            self.img_avatar = None

    def _build_ui(self):
        # 1. Encabezado Oficial
        PageHeader(
            self,
            titulo="Chat Detector - Análisis de Mensajes",
            subtitulo="Pega un mensaje sospechoso de WhatsApp, SMS o redes sociales para evaluar su riesgo"
        )

        # 2. Fila de 3 Botones de Ejemplo (Borde 2px AZUL, texto AZUL_OSCURO bold 16px, radio 20)
        frame_pildoras = ctk.CTkFrame(self, fg_color="transparent")
        frame_pildoras.pack(fill="x", padx=40, pady=(0, 16))

        for etiqueta, contenido in EJEMPLOS:
            btn = ctk.CTkButton(
                frame_pildoras,
                text=etiqueta,
                height=BTN_HEIGHT_TOOL,
                corner_radius=RADIUS_PILL,
                fg_color="transparent",
                border_width=BORDER_WIDTH,
                border_color=AZUL,
                text_color=AZUL_OSCURO,
                hover_color="#E0E7FF",
                font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
                command=lambda t=contenido: self._cargar_ejemplo(t)
            )
            btn.pack(side="left", padx=(0, 12))

        # 3. Área de Conversación con Scroll transparente
        self.scroll_chat = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=0,
            scrollbar_button_color="#CBD5E1",
            scrollbar_button_hover_color=AZUL
        )
        self.scroll_chat.pack(fill="both", expand=True, padx=40, pady=(0, 10))

        # Placeholder inicial centrado
        self.lbl_placeholder = ctk.CTkLabel(
            self.scroll_chat,
            text="El análisis aparecerá aquí...",
            text_color=TEXTO_MUTED,
            font=ctk.CTkFont(family=FONT_BODY[0], size=FONT_BODY[1])
        )
        self.lbl_placeholder.pack(pady=90)

        # 4. Barra Inferior Fija (Input ancho + Botón Analizar)
        frame_barra_inferior = ctk.CTkFrame(self, fg_color="transparent")
        frame_barra_inferior.pack(fill="x", padx=40, pady=(0, 8))

        self.entry_mensaje = ctk.CTkEntry(
            frame_barra_inferior,
            height=48,
            corner_radius=RADIUS_INPUT,
            border_width=BORDER_WIDTH,
            border_color="#93C5FD",
            fg_color=BLANCO,
            text_color=TEXTO,
            placeholder_text="Escribe o pega aquí el mensaje sospechoso...",
            placeholder_text_color=TEXTO_MUTED,
            font=ctk.CTkFont(family=FONT_BODY[0], size=16)
        )
        self.entry_mensaje.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.entry_mensaje.bind("<Return>", lambda e: self._ejecutar_analisis())

        btn_analizar = BotonPrimario(
            frame_barra_inferior,
            text="Analizar",
            width=130,
            height=48,
            command=self._ejecutar_analisis
        )
        btn_analizar.pack(side="right")

        # 5. Aviso preventivo ético discreto
        lbl_aviso = ctk.CTkLabel(
            self,
            text="Herramienta preventiva de apoyo. Verifica cualquier comunicación sospechosa a través de canales oficiales.",
            font=ctk.CTkFont(family=FONT_BODY[0], size=12),
            text_color=TEXTO_MUTED
        )
        lbl_aviso.pack(padx=40, pady=(0, 14), anchor="w")

    def _cargar_ejemplo(self, texto: str):
        self.entry_mensaje.delete(0, "end")
        self.entry_mensaje.insert(0, texto)
        self._ejecutar_analisis()

    def _ejecutar_analisis(self):
        texto = self.entry_mensaje.get().strip()
        if not texto or texto == "Escribe o pega aquí el mensaje sospechoso...":
            return

        self.entry_mensaje.delete(0, "end")

        resultado = analizar_mensaje(texto)
        guardar_analisis(
            texto,
            resultado["categoria"],
            resultado["nivel_riesgo"],
            resultado["confianza"]
        )

        self._renderizar_resultado(texto, resultado)

    def _renderizar_resultado(self, texto_usuario: str, res: dict):
        for widget in self.scroll_chat.winfo_children():
            widget.destroy()

        cat = res["categoria"].lower()
        if cat == "fraude":
            color_tema = ROJO
            fondo_card = ROJO_CLARO
        elif cat == "sospechoso":
            color_tema = AMBAR
            fondo_card = AMBAR_CLARO
        else:
            color_tema = VERDE
            fondo_card = VERDE_CLARO

        # --- A. MENSAJE DEL USUARIO (Alineado a la DERECHA, gris burbuja) ---
        frame_msg_wrap = ctk.CTkFrame(self.scroll_chat, fg_color="transparent")
        frame_msg_wrap.pack(fill="x", pady=(10, 16))

        burbuja_usuario = ctk.CTkFrame(
            frame_msg_wrap,
            fg_color=GRIS_BURBUJA,
            corner_radius=12
        )
        burbuja_usuario.pack(side="right", padx=(100, 20))

        ctk.CTkLabel(
            burbuja_usuario,
            text=texto_usuario,
            wraplength=520,
            font=ctk.CTkFont(family=FONT_BODY[0], size=16),
            text_color=BLANCO,
            justify="left"
        ).pack(padx=18, pady=12)

        # --- B. RESPUESTA DEL SISTEMA (Alineada a la IZQUIERDA con avatar) ---
        frame_resp_wrap = ctk.CTkFrame(self.scroll_chat, fg_color="transparent")
        frame_resp_wrap.pack(fill="x", pady=(0, 20))

        if self.img_avatar:
            lbl_avatar = ctk.CTkLabel(frame_resp_wrap, image=self.img_avatar, text="")
            lbl_avatar.pack(side="left", anchor="n", padx=(10, 12), pady=6)

        # Tarjeta exterior de resultado con borde y radio
        card_exterior = ctk.CTkFrame(
            frame_resp_wrap,
            fg_color=fondo_card,
            border_width=BORDER_WIDTH,
            border_color=color_tema,
            corner_radius=RADIUS_CARD
        )
        card_exterior.pack(side="left", fill="x", padx=(0, 100))

        # Franja vertical izquierda de 6px
        franja_lateral = ctk.CTkFrame(card_exterior, fg_color=color_tema, width=6, corner_radius=0)
        franja_lateral.pack(side="left", fill="y")

        card_inner = ctk.CTkFrame(card_exterior, fg_color="transparent")
        card_inner.pack(side="left", fill="both", expand=True, padx=22, pady=18)

        # 1. Badge Píldora oficial (36px de alto en chat)
        badge_wrap = ctk.CTkFrame(card_inner, fg_color="transparent")
        badge_wrap.pack(anchor="w", pady=(0, 10))
        Badge(badge_wrap, categoria=cat, alto=BADGE_HEIGHT_CHAT, ancho=140).pack(side="left")

        # 2. Nivel de riesgo
        frame_riesgo = ctk.CTkFrame(card_inner, fg_color="transparent")
        frame_riesgo.pack(anchor="w", pady=2)
        ctk.CTkLabel(
            frame_riesgo,
            text="Nivel de riesgo: ",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=16, weight="bold"),
            text_color=TEXTO
        ).pack(side="left")
        ctk.CTkLabel(
            frame_riesgo,
            text=str(res.get("nivel_riesgo", "MEDIO")),
            font=ctk.CTkFont(family=FONT_BODY[0], size=16),
            text_color=TEXTO
        ).pack(side="left")

        # 3. Confianza del modelo
        frame_conf = ctk.CTkFrame(card_inner, fg_color="transparent")
        frame_conf.pack(anchor="w", pady=2)
        ctk.CTkLabel(
            frame_conf,
            text="Confianza del modelo: ",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=16, weight="bold"),
            text_color=TEXTO
        ).pack(side="left")
        ctk.CTkLabel(
            frame_conf,
            text=f"{round(res['confianza']*100, 1)}%",
            font=ctk.CTkFont(family=FONT_BODY[0], size=16),
            text_color=TEXTO
        ).pack(side="left")

        # 4. Indicadores encontrados
        indicadores = res.get("indicadores", [])
        if indicadores:
            ctk.CTkLabel(
                card_inner,
                text="Indicadores encontrados:",
                font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=16, weight="bold"),
                text_color=TEXTO
            ).pack(anchor="w", pady=(8, 2))

            for ind in indicadores:
                ctk.CTkLabel(
                    card_inner,
                    text=f"  • {ind}",
                    font=ctk.CTkFont(family=FONT_BODY[0], size=15),
                    text_color=TEXTO
                ).pack(anchor="w", pady=1)

        # 5. Caja blanca interior de recomendación con borde 2px
        caja_rec = ctk.CTkFrame(
            card_inner,
            fg_color=BLANCO,
            corner_radius=RADIUS_CARD,
            border_width=BORDER_WIDTH,
            border_color=BORDE
        )
        caja_rec.pack(fill="x", pady=(14, 4))

        rec_inner = ctk.CTkFrame(caja_rec, fg_color="transparent")
        rec_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(
            rec_inner,
            text="Recomendación:",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=15, weight="bold"),
            text_color=TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(
            rec_inner,
            text=res.get("recomendacion", ""),
            wraplength=520,
            font=ctk.CTkFont(family=FONT_BODY[0], size=15),
            text_color=TEXTO,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))
