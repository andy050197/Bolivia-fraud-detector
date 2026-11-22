# views/historial.py
"""
Módulo 2: Historial de Análisis - Registro de Consultas.
Implementado fielmente según las Reglas Globales (Prompt 2).
"""

import logging
import sqlite3
from tkinter import messagebox
import customtkinter as ctk

from ui.theme import (
    AZUL, AZUL_OSCURO, AZUL_SELECCION, FONDO, BLANCO, BORDE, TEXTO, TEXTO_MUTED,
    ROJO, ROJO_CLARO, AMBAR, VERDE, FONT_FAMILY, FONT_PAGE_TITLE, FONT_SUBTITLE,
    FONT_BODY, FONT_BODY_BOLD, FONT_TABLE_HEAD, FONT_TABLE_CELL, FONT_BUTTON,
    BORDER_WIDTH, RADIUS_CARD, RADIUS_INPUT, RADIUS_BUTTON, BTN_HEIGHT_TOOL,
    INPUT_HEIGHT_TOOL, SIDEBAR_HOVER
)
from ui.components import (
    PageHeader, DataTable, Badge, BotonPeligro, Buscador, cargar_icono_ctk
)
from database.db import obtener_historial, eliminar_historial_item, limpiar_historial

logger = logging.getLogger(__name__)

CATEGORIAS = {
    "Todas las categorías": None,
    "Fraude": "fraude",
    "Sospechoso": "sospechoso",
    "Legítimo": "legitimo"
}

def _formatear_fecha_hora(fecha_raw: str) -> str:
    """Divide 'DD/MM/YYYY HH:MM' en dos líneas para la tabla."""
    if not fecha_raw:
        return "—"
    partes = str(fecha_raw).split(" ")
    if len(partes) >= 2:
        return f"{partes[0]}\n{partes[1]}"
    return str(fecha_raw)

def _formatear_confianza(valor) -> str:
    """Devuelve confianza formateada a un decimal (ej. 78.0%)."""
    try:
        num = float(valor)
        if 0 <= num <= 1.0:
            num = num * 100.0
        return f"{num:.1f}%"
    except (ValueError, TypeError):
        return "—"

class HistorialView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FONDO, corner_radius=0)
        self._pendiente_busqueda = None
        self._filas_cache = {}
        self._modal_detalle = None

        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        # 1. Encabezado Oficial
        PageHeader(
            self,
            titulo="Historial de Análisis - Registro de Consultas",
            subtitulo="Consulta los mensajes evaluados previamente almacenados de forma anonimizada en SQLite"
        )

        # 2. Barra de herramientas en una sola fila (alineada a 40px con la tabla)
        frame_toolbar = ctk.CTkFrame(self, fg_color="transparent")
        frame_toolbar.pack(fill="x", padx=40, pady=(0, 20))

        # Botón Peligro "Limpiar Historial" alineado a la derecha
        self.btn_limpiar = BotonPeligro(
            frame_toolbar,
            text="Limpiar Historial",
            icon="trash_red.png",
            width=175,
            height=BTN_HEIGHT_TOOL,
            command=self._confirmar_limpiar
        )
        self.btn_limpiar.pack(side="right")

        # Selector de Categoría (alto 44px, ancho ~210px) a la derecha
        self.combo_cat = ctk.CTkOptionMenu(
            frame_toolbar,
            values=list(CATEGORIAS.keys()),
            width=210,
            height=BTN_HEIGHT_TOOL,
            corner_radius=RADIUS_INPUT,
            fg_color=BLANCO,
            button_color=BLANCO,
            button_hover_color=AZUL_SELECCION,
            text_color=AZUL_OSCURO,
            dropdown_font=ctk.CTkFont(family=FONT_BODY[0], size=FONT_BODY[1]),
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
            command=lambda v: self._cargar_datos()
        )
        self.combo_cat.set("Todas las categorías")
        self.combo_cat.pack(side="right", padx=(0, 12))

        # Buscador con bordes 2px completos y debounce automático
        self.entry_busqueda = Buscador(
            frame_toolbar,
            placeholder_text="Buscar por palabra clave...",
            command=self._cargar_datos,
            height=BTN_HEIGHT_TOOL
        )
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # 3. Tabla de datos centralizada con DataTable (Mensaje expandido con weight=1)
        columnas_historial = [
            ("Fecha y Hora", 0, "center", 115),
            ("Mensaje Anonimizado", 1, "w", 260),
            ("Categoría", 0, "center", 125),
            ("Nivel de Riesgo", 0, "center", 130),
            ("Confianza", 0, "center", 95),
            ("Acciones", 0, "center", 85)
        ]

        self.tabla = DataTable(
            self,
            columnas=columnas_historial,
            empty_message="Aún no hay análisis registrados"
        )
        self.tabla.pack(fill="both", expand=True, padx=40, pady=(0, 24))

    def _cargar_datos(self):
        busqueda = self.entry_busqueda.get().strip()
        filtro_cat = CATEGORIAS.get(self.combo_cat.get())

        try:
            filas = obtener_historial(filtro_categoria=filtro_cat, busqueda=busqueda or None)
        except sqlite3.Error as e:
            logger.exception("Error al consultar historial")
            self.tabla.show_empty(f"Error al conectar con la base de datos: {e}")
            self.btn_limpiar.configure(state="disabled")
            return

        self._filas_cache.clear()
        self.tabla.clear()

        if not filas:
            self.tabla.show_empty("Aún no hay análisis registrados")
            self.btn_limpiar.configure(state="disabled")
            return

        self.btn_limpiar.configure(state="normal")

        img_eye = cargar_icono_ctk("eye_blue.png", size=(20, 20))
        img_trash = cargar_icono_ctk("trash_red.png", size=(20, 20))

        for fila in filas:
            id_, fecha, msg_anon, cat, riesgo, confianza = fila
            self._filas_cache[id_] = fila

            # Celda 0: Fecha y Hora (dos líneas)
            celda_fecha = _formatear_fecha_hora(fecha)

            # Celda 1: Mensaje Anonimizado
            celda_msg = msg_anon

            # Celda 2: Badge oficial
            def make_badge(parent, c=cat):
                b = Badge(parent, categoria=c, alto=30, ancho=110)
                return b

            # Celda 3: Nivel de riesgo
            celda_riesgo = str(riesgo).upper()

            # Celda 4: Confianza
            celda_conf = _formatear_confianza(confianza)

            # Celda 5: Acciones (Ojo azul marino + Papelera roja, 20px)
            def make_acciones(parent, item_id=id_):
                f_acc = ctk.CTkFrame(parent, fg_color="transparent", width=70, height=36)
                f_acc.pack_propagate(False)

                btn_ojo = ctk.CTkButton(
                    f_acc,
                    text="",
                    image=img_eye,
                    width=28,
                    height=28,
                    fg_color="transparent",
                    hover_color="#E0E7FF",
                    corner_radius=6,
                    command=lambda i=item_id: self._ver_detalle(i)
                )
                btn_ojo.pack(side="left", padx=2)

                btn_borrar = ctk.CTkButton(
                    f_acc,
                    text="",
                    image=img_trash,
                    width=28,
                    height=28,
                    fg_color="transparent",
                    hover_color=ROJO_CLARO,
                    corner_radius=6,
                    command=lambda i=item_id: self._confirmar_eliminar(i)
                )
                btn_borrar.pack(side="left", padx=2)
                return f_acc

            self.tabla.add_row(
                [celda_fecha, celda_msg, make_badge, celda_riesgo, celda_conf, make_acciones],
                is_highlighted=False
            )

        self.tabla.finalize_rows()

    def _ver_detalle(self, item_id: int):
        fila = self._filas_cache.get(item_id)
        if not fila:
            return

        if self._modal_detalle is not None and self._modal_detalle.winfo_exists():
            self._modal_detalle.destroy()

        id_, fecha, msg_anon, cat, riesgo, confianza = fila

        modal = self._modal_detalle = ctk.CTkToplevel(self)
        modal.title(f"Detalle del Análisis #{id_}")
        modal.geometry("580x460")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        # Cabecera modal
        ctk.CTkLabel(
            modal,
            text=f"Análisis #{id_}  •  {fecha}",
            font=ctk.CTkFont(family=FONT_PAGE_TITLE[0], size=20, weight="bold"),
            text_color=AZUL_OSCURO
        ).pack(anchor="w", padx=24, pady=(24, 8))

        # Metadatos del análisis
        frame_meta = ctk.CTkFrame(modal, fg_color="transparent")
        frame_meta.pack(anchor="w", padx=24, pady=(0, 16))

        Badge(frame_meta, categoria=cat, alto=30, ancho=110).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            frame_meta,
            text=f"Riesgo: {riesgo}   |   Confianza: {_formatear_confianza(confianza)}",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=FONT_BODY_BOLD[1], weight=FONT_BODY_BOLD[2]),
            text_color=TEXTO
        ).pack(side="left")

        # Texto del mensaje anonimizado
        ctk.CTkLabel(
            modal,
            text="Mensaje Evaluado (Anonimizado para privacidad):",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=14, weight="bold"),
            text_color=TEXTO_MUTED
        ).pack(anchor="w", padx=24, pady=(0, 6))

        txt_box = ctk.CTkTextbox(
            modal,
            height=140,
            font=ctk.CTkFont(family=FONT_BODY[0], size=15),
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD
        )
        txt_box.pack(fill="x", padx=24, pady=(0, 12))
        txt_box.insert("1.0", msg_anon)
        txt_box.configure(state="disabled")

        ctk.CTkLabel(
            modal,
            text="Por seguridad, enlaces, teléfonos y montos monetarios se almacenan ofuscados.",
            font=ctk.CTkFont(family=FONT_BODY[0], size=12),
            text_color=TEXTO_MUTED
        ).pack(anchor="w", padx=24)

        # Botón cerrar
        btn_cerrar = ctk.CTkButton(
            modal,
            text="Cerrar",
            width=120,
            height=40,
            corner_radius=RADIUS_BUTTON,
            fg_color=AZUL,
            hover_color=SIDEBAR_HOVER,
            text_color=BLANCO,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
            command=modal.destroy
        )
        btn_cerrar.pack(side="right", padx=24, pady=20)
        modal.bind("<Escape>", lambda e: modal.destroy())

    def _confirmar_eliminar(self, item_id: int):
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar el registro #{item_id} del historial?",
            icon="warning"
        ):
            try:
                eliminar_historial_item(item_id)
                self._cargar_datos()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo eliminar el registro: {e}")

    def _confirmar_limpiar(self):
        if messagebox.askyesno(
            "Limpiar Historial",
            "¿Estás seguro de eliminar TODOS los registros del historial?\nEsta acción no se puede deshacer.",
            icon="warning"
        ):
            try:
                limpiar_historial()
                self._cargar_datos()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"No se pudo limpiar el historial: {e}")

    def on_show(self):
        self._cargar_datos()
