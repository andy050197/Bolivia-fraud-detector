# views/dataset.py
"""
Módulo 4: Dataset de Mensajes - Corpus de Entrenamiento.
Implementado fielmente según las Reglas Globales (Prompt 2).
"""

import os
import re
import csv
import logging
from tkinter import filedialog, messagebox
import customtkinter as ctk

from ui.theme import (
    AZUL, AZUL_OSCURO, AZUL_SELECCION, FONDO, BLANCO, BORDE, TEXTO, TEXTO_MUTED,
    ROJO, ROJO_CLARO, AMBAR, AMBAR_CLARO, VERDE, VERDE_CLARO, FONT_FAMILY,
    FONT_PAGE_TITLE, FONT_SUBTITLE, FONT_BODY, FONT_BODY_BOLD, FONT_TABLE_HEAD,
    FONT_TABLE_CELL, FONT_BUTTON, FONT_BADGE, BORDER_WIDTH, RADIUS_CARD,
    RADIUS_INPUT, RADIUS_BUTTON, BTN_HEIGHT_TOOL, INPUT_HEIGHT_TOOL, SIDEBAR_HOVER
)
from ui.components import (
    PageHeader, DataTable, Badge, BotonPrimario, BotonContorno, Buscador,
    crear_chip_resumen, cargar_icono_ctk
)
from database.db import (
    obtener_dataset, agregar_mensaje_dataset,
    actualizar_mensaje_dataset, eliminar_mensaje_dataset,
    cargar_csv_a_dataset
)

logger = logging.getLogger(__name__)

REGISTROS_POR_PAGINA = 20

CATEGORIAS_MAP = {
    "Todas las categorías": None,
    "Fraude": "fraude",
    "Sospechoso": "sospechoso",
    "Legítimo": "legitimo"
}

# =====================================================================
# Normalización para detección de duplicados semánticos
# =====================================================================

def _normalizar_para_duplicado(texto: str) -> str:
    """
    Normaliza un mensaje eliminando variables (montos, teléfonos, URLs, números)
    para detectar mensajes que son estructuralmente iguales aunque cambien los valores.
    Ejemplo: 'Yapeame Bs 150...' == 'Yapeame Bs 300...' → True
    """
    t = texto.lower().strip()
    t = re.sub(r'bs\.?\s*[\d.,]+', 'bs X', t)      # montos bolivianos: Bs 150, Bs. 1,000
    t = re.sub(r'https?://\S+', 'URL', t)            # URLs
    t = re.sub(r'\+?591\s*\d[\d\s\-]{6,}', 'TEL', t)  # teléfonos bolivianos
    t = re.sub(r'\b\d{4,}\b', 'N', t)               # números de 4+ dígitos
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


# =====================================================================
# Modal unificado para Importar / Exportar CSV
# =====================================================================
def _mostrar_modal_csv(parent, modo: str, **kwargs) -> bool:
    """
    Modal bonito unificado para confirmación de Importar o Exportar CSV.

    modo='importar': kwargs: nombre_archivo, cnt_fraude, cnt_sosp, cnt_legit,
                             total, duplicados, formato_invalido
    modo='exportar': kwargs: nombre_archivo, ruta_completa,
                             cnt_fraude, cnt_sosp, cnt_legit, total

    Retorna True si el usuario confirma, False si cancela.
    """
    result = {"valor": False}

    modal = ctk.CTkToplevel(parent)
    modal.title("Confirmar Importación" if modo == "importar" else "Confirmar Exportación")
    modal.geometry("520x490")
    modal.resizable(False, False)
    try:
        modal.transient(parent.winfo_toplevel())
    except Exception:
        pass
    modal.grab_set()
    modal.configure(fg_color=FONDO)

    # ── Cabecera ──────────────────────────────────────────────────────
    frame_header = ctk.CTkFrame(modal, fg_color="transparent")
    frame_header.pack(fill="x", padx=28, pady=(24, 0))

    color_icono = AZUL if modo == "importar" else VERDE
    icono_txt   = "Importar CSV" if modo == "importar" else "Exportar CSV"

    lbl_icono = ctk.CTkLabel(
        frame_header,
        text=icono_txt,
        font=ctk.CTkFont(family=FONT_PAGE_TITLE[0], size=20, weight="bold"),
        text_color=color_icono
    )
    lbl_icono.pack(anchor="w")

    subtitulo = (
        "Revisa los registros antes de importar al dataset"
        if modo == "importar"
        else "Revisa el resumen antes de exportar el dataset"
    )
    ctk.CTkLabel(
        frame_header,
        text=subtitulo,
        font=ctk.CTkFont(family=FONT_BODY[0], size=13),
        text_color=TEXTO_MUTED
    ).pack(anchor="w", pady=(4, 0))

    # ── Divisor ───────────────────────────────────────────────────────
    ctk.CTkFrame(modal, fg_color=BORDE, height=1).pack(fill="x", padx=28, pady=(14, 0))

    # ── Tarjeta de información ────────────────────────────────────────
    card = ctk.CTkFrame(
        modal,
        fg_color=BLANCO,
        border_width=BORDER_WIDTH,
        border_color=BORDE,
        corner_radius=RADIUS_CARD
    )
    card.pack(fill="x", padx=28, pady=14)

    def fila_info(label: str, valor: str, color_val: str = TEXTO):
        """Crea una fila etiqueta/valor dentro de la tarjeta."""
        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=16, pady=5)
        ctk.CTkLabel(
            f,
            text=label,
            font=ctk.CTkFont(family=FONT_BODY[0], size=13),
            text_color=TEXTO_MUTED,
            anchor="w",
            width=160
        ).pack(side="left")
        ctk.CTkLabel(
            f,
            text=valor,
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=13, weight="bold"),
            text_color=color_val,
            anchor="w"
        ).pack(side="left", padx=(8, 0))

    def fila_badge(label: str, valor: int, color_badge: str, color_texto: str):
        """Crea una fila con badge de color para conteos de categoría."""
        f = ctk.CTkFrame(card, fg_color="transparent")
        f.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(
            f,
            text=label,
            font=ctk.CTkFont(family=FONT_BODY[0], size=13),
            text_color=TEXTO_MUTED,
            anchor="w",
            width=160
        ).pack(side="left")
        badge_frame = ctk.CTkFrame(f, fg_color=color_badge, corner_radius=10, width=48, height=24)
        badge_frame.pack(side="left", padx=(8, 0))
        badge_frame.pack_propagate(False)
        ctk.CTkLabel(
            badge_frame,
            text=str(valor),
            font=ctk.CTkFont(family=FONT_BADGE[0], size=12, weight="bold"),
            text_color=color_texto
        ).place(relx=0.5, rely=0.5, anchor="center")

    # Archivo
    nombre_archivo = kwargs.get("nombre_archivo", "—")
    fila_info("Archivo:", nombre_archivo, AZUL_OSCURO)

    # Separador interno
    ctk.CTkFrame(card, fg_color=BORDE, height=1).pack(fill="x", padx=16, pady=6)

    # Conteos por categoría
    cnt_fraude = kwargs.get("cnt_fraude", 0)
    cnt_sosp   = kwargs.get("cnt_sosp", 0)
    cnt_legit  = kwargs.get("cnt_legit", 0)
    total      = kwargs.get("total", cnt_fraude + cnt_sosp + cnt_legit)

    fila_info("Total registros:", str(total), AZUL_OSCURO)
    fila_badge("Fraude:",      cnt_fraude, ROJO,  BLANCO)
    fila_badge("Sospechoso:",  cnt_sosp,   AMBAR, BLANCO)
    fila_badge("Legitimo:",    cnt_legit,  VERDE, BLANCO)

    if modo == "importar":
        duplicados       = kwargs.get("duplicados", 0)
        formato_invalido = kwargs.get("formato_invalido", 0)
        if duplicados > 0:
            ctk.CTkFrame(card, fg_color=BORDE, height=1).pack(fill="x", padx=16, pady=6)
            fila_info("Duplicados omitidos:", str(duplicados), AMBAR)
        if formato_invalido > 0:
            fila_info("Formato invalido:", str(formato_invalido), ROJO)
    else:
        ruta_completa = kwargs.get("ruta_completa", "—")
        ctk.CTkFrame(card, fg_color=BORDE, height=1).pack(fill="x", padx=16, pady=6)
        # Truncar ruta larga
        ruta_display = ruta_completa if len(ruta_completa) <= 52 else "..." + ruta_completa[-49:]
        fila_info("Destino:", ruta_display, TEXTO_MUTED)

    # ── Aviso si hay duplicados ───────────────────────────────────────
    if modo == "importar" and kwargs.get("duplicados", 0) > 0:
        frame_aviso = ctk.CTkFrame(modal, fg_color="#FEF3C7", corner_radius=8)
        frame_aviso.pack(fill="x", padx=28, pady=(0, 10))
        ctk.CTkLabel(
            frame_aviso,
            text=f"  {kwargs['duplicados']} mensaje(s) ya existen en el dataset y seran omitidos (deteccion normalizada).",
            font=ctk.CTkFont(family=FONT_BODY[0], size=12),
            text_color="#92400E",
            anchor="w",
            justify="left"
        ).pack(anchor="w", padx=12, pady=8)

    # ── Botones ───────────────────────────────────────────────────────
    frame_btns = ctk.CTkFrame(modal, fg_color="transparent")
    frame_btns.pack(fill="x", padx=28, pady=(4, 24))

    def on_cancelar():
        result["valor"] = False
        modal.destroy()

    def on_confirmar():
        result["valor"] = True
        modal.destroy()

    ctk.CTkButton(
        frame_btns,
        text="Cancelar",
        width=130,
        height=BTN_HEIGHT_TOOL,
        corner_radius=RADIUS_BUTTON,
        fg_color="transparent",
        border_width=BORDER_WIDTH,
        border_color=AZUL,
        hover_color="#E0E7FF",
        text_color=AZUL_OSCURO,
        font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
        command=on_cancelar
    ).pack(side="right", padx=(10, 0))

    texto_confirmar = "Confirmar Importacion" if modo == "importar" else "Confirmar Exportacion"
    ctk.CTkButton(
        frame_btns,
        text=texto_confirmar,
        width=185,
        height=BTN_HEIGHT_TOOL,
        corner_radius=RADIUS_BUTTON,
        fg_color=AZUL if modo == "importar" else VERDE,
        hover_color=SIDEBAR_HOVER if modo == "importar" else "#15803D",
        text_color=BLANCO,
        font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
        command=on_confirmar
    ).pack(side="right")

    modal.bind("<Escape>", lambda e: on_cancelar())
    modal.wait_window()
    return result["valor"]


class DatasetView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=FONDO, corner_radius=0)
        self._pagina_actual = 1
        self._total_paginas = 1
        self._filas_filtradas = []
        self._filas_cache = {}

        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        # 1. Encabezado Oficial (Sin subtítulo según Sección 4)
        PageHeader(
            self,
            titulo="Dataset de Mensajes - Corpus de Entrenamiento",
            subtitulo=None
        )

        # 2. Fila 1: 3 Botones Primarios con Icono (Alto 44px, Gap 12px)
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.pack(fill="x", padx=40, pady=(0, 16))

        self.btn_nuevo = BotonPrimario(
            frame_acciones,
            text="Nuevo Mensaje",
            icon="plus_white.png",
            width=165,
            height=BTN_HEIGHT_TOOL,
            command=self._abrir_modal_nuevo
        )
        self.btn_nuevo.pack(side="left", padx=(0, 12))

        self.btn_importar = BotonPrimario(
            frame_acciones,
            text="Importar CSV",
            icon="download_white.png",
            width=155,
            height=BTN_HEIGHT_TOOL,
            command=self._importar_csv
        )
        self.btn_importar.pack(side="left", padx=(0, 12))

        self.btn_exportar = BotonPrimario(
            frame_acciones,
            text="Exportar CSV",
            icon="upload_white.png",
            width=155,
            height=BTN_HEIGHT_TOOL,
            command=self._exportar_csv
        )
        self.btn_exportar.pack(side="left")

        # 3. Fila 2: Buscador + OptionMenu (Alto 44px, alineado al borde derecho de la tabla)
        frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtros.pack(fill="x", padx=40, pady=(0, 16))

        # OptionMenu con borde AZUL 2px (Sección 4) a la derecha
        self.combo_cat = ctk.CTkOptionMenu(
            frame_filtros,
            values=list(CATEGORIAS_MAP.keys()),
            width=210,
            height=BTN_HEIGHT_TOOL,
            corner_radius=RADIUS_INPUT,
            fg_color=BLANCO,
            button_color=BLANCO,
            button_hover_color=AZUL_SELECCION,
            text_color=AZUL_OSCURO,
            dropdown_font=ctk.CTkFont(family=FONT_BODY[0], size=FONT_BODY[1]),
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
            command=lambda v: self._filtrar_y_renderizar()
        )
        self.combo_cat.set("Todas las categorías")
        self.combo_cat.pack(side="right")

        # Buscador con bordes 2px completos y debounce automático a la izquierda
        self.entry_busqueda = Buscador(
            frame_filtros,
            placeholder_text="Buscar...",
            command=self._filtrar_y_renderizar,
            height=BTN_HEIGHT_TOOL
        )
        self.entry_busqueda.pack(side="left", fill="x", expand=True, padx=(0, 12))

        # 4. Fila 3: Chips de Resumen fijos (sin recreación para evitar distorsiones)
        self.frame_chips = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_chips.pack(fill="x", padx=40, pady=(0, 16))

        self.chip_total = crear_chip_resumen(self.frame_chips, "Total Registros: 0")
        self.chip_total.pack(side="left", padx=(0, 12))

        self.chip_fraude = crear_chip_resumen(self.frame_chips, "Fraude: 0")
        self.chip_fraude.pack(side="left", padx=(0, 12))

        self.chip_sosp = crear_chip_resumen(self.frame_chips, "Sospechoso: 0")
        self.chip_sosp.pack(side="left", padx=(0, 12))

        self.chip_legit = crear_chip_resumen(self.frame_chips, "Legítimo: 0")
        self.chip_legit.pack(side="left")

        # 5. Fila 4: Tabla con DataTable (Texto del mensaje expandido con weight=1)
        columnas_dataset = [
            ("ID", 0, "center", 55),
            ("Texto del mensaje", 1, "w", 260),
            ("Categoría", 0, "center", 125),
            ("Origen", 0, "center", 110),
            ("Tipo de Fraude", 0, "center", 135),
            ("Acciones", 0, "center", 85)
        ]

        self.tabla = DataTable(
            self,
            columnas=columnas_dataset,
            empty_message="No se encontraron mensajes en el dataset"
        )
        self.tabla.pack(fill="both", expand=True, padx=40, pady=(0, 12))

        # 6. Fila 5: Paginación de 20 registros alineada abajo a la derecha
        self.frame_paginacion = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_paginacion.pack(fill="x", padx=40, pady=(0, 20))

        self.btn_next_pag = ctk.CTkButton(
            self.frame_paginacion,
            text="Siguiente >",
            width=110,
            height=36,
            corner_radius=RADIUS_INPUT,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            text_color=AZUL_OSCURO,
            hover_color=AZUL_SELECCION,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=14, weight=FONT_BUTTON[2]),
            command=self._pagina_siguiente
        )
        self.btn_next_pag.pack(side="right", padx=(8, 0))

        self.lbl_info_pag = ctk.CTkLabel(
            self.frame_paginacion,
            text="Página 1 de 1",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=14, weight=FONT_BODY_BOLD[2]),
            text_color=TEXTO_MUTED
        )
        self.lbl_info_pag.pack(side="right", padx=8)

        self.btn_prev_pag = ctk.CTkButton(
            self.frame_paginacion,
            text="< Anterior",
            width=110,
            height=36,
            corner_radius=RADIUS_INPUT,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            text_color=AZUL_OSCURO,
            hover_color=AZUL_SELECCION,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=14, weight=FONT_BUTTON[2]),
            command=self._pagina_anterior
        )
        self.btn_prev_pag.pack(side="right")

    def _cargar_datos(self):
        """Carga todas las filas desde SQLite."""
        self._filas_raw = obtener_dataset()
        self._filtrar_y_renderizar(reset_page=True)

    def _filtrar_y_renderizar(self, reset_page: bool = False):
        if reset_page:
            self._pagina_actual = 1

        busqueda = self.entry_busqueda.get().strip().lower()
        filtro_cat = CATEGORIAS_MAP.get(self.combo_cat.get())

        filas = self._filas_raw

        # Estadísticas globales del corpus
        total_global = len(filas)
        fraudes_global = sum(1 for f in filas if f[2] == "fraude")
        sosp_global    = sum(1 for f in filas if f[2] == "sospechoso")
        legit_global   = sum(1 for f in filas if f[2] == "legitimo")

        # Actualizar valores de chips de forma fluida (sin destruir widgets para evitar distorsiones)
        self.chip_total.lbl.configure(text=f"Total Registros: {total_global:,}")
        self.chip_fraude.lbl.configure(text=f"Fraude: {fraudes_global:,}")
        self.chip_sosp.lbl.configure(text=f"Sospechoso: {sosp_global:,}")
        self.chip_legit.lbl.configure(text=f"Legítimo: {legit_global:,}")

        # Filtrado en memoria
        if filtro_cat:
            filas = [f for f in filas if f[2] == filtro_cat]
        if busqueda:
            filas = [f for f in filas if busqueda in f[1].lower() or busqueda in (f[4] or "").lower()]

        self._filas_filtradas = filas

        # Calcular Paginación
        total_items = len(filas)
        self._total_paginas = max(1, (total_items + REGISTROS_POR_PAGINA - 1) // REGISTROS_POR_PAGINA)
        if self._pagina_actual > self._total_paginas:
            self._pagina_actual = self._total_paginas

        self.lbl_info_pag.configure(text=f"Página {self._pagina_actual} de {self._total_paginas} ({total_items} registros)")
        self.btn_prev_pag.configure(state="normal" if self._pagina_actual > 1 else "disabled")
        self.btn_next_pag.configure(state="normal" if self._pagina_actual < self._total_paginas else "disabled")

        # Segmentar página
        inicio = (self._pagina_actual - 1) * REGISTROS_POR_PAGINA
        fin = inicio + REGISTROS_POR_PAGINA
        pagina_filas = filas[inicio:fin]

        self._filas_cache.clear()
        self.tabla.clear()

        if not pagina_filas:
            self.tabla.show_empty("No se encontraron registros coincidentes")
            return

        img_edit = cargar_icono_ctk("edit_blue.png", size=(20, 20))
        img_trash = cargar_icono_ctk("trash_red.png", size=(20, 20))

        for fila in pagina_filas:
            id_, mensaje, cat, origen, subcat = fila
            self._filas_cache[id_] = fila

            # Celda 0: ID
            celda_id = str(id_)

            # Celda 1: Mensaje
            celda_msg = mensaje

            # Celda 2: Badge
            def make_badge(parent, c=cat):
                b = Badge(parent, categoria=c, alto=30, ancho=110)
                return b

            # Celda 3: Origen
            celda_origen = origen or "—"

            # Celda 4: Tipo de Fraude (subcategoría)
            celda_subcat = subcat or "—"

            # Celda 5: Acciones (Editar azul marino + Papelera roja, 20px)
            def make_acciones(parent, item_id=id_):
                f_acc = ctk.CTkFrame(parent, fg_color="transparent", width=70, height=36)
                f_acc.pack_propagate(False)

                btn_edit = ctk.CTkButton(
                    f_acc,
                    text="",
                    image=img_edit,
                    width=28,
                    height=28,
                    fg_color="transparent",
                    hover_color=AZUL_SELECCION,
                    corner_radius=6,
                    command=lambda i=item_id: self._abrir_modal_editar(i)
                )
                btn_edit.pack(side="left", padx=2)

                btn_del = ctk.CTkButton(
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
                btn_del.pack(side="left", padx=2)
                return f_acc

            self.tabla.add_row(
                [celda_id, celda_msg, make_badge, celda_origen, celda_subcat, make_acciones],
                is_highlighted=False
            )

        self.tabla.finalize_rows()

    def _pagina_anterior(self):
        if self._pagina_actual > 1:
            self._pagina_actual -= 1
            self._filtrar_y_renderizar(reset_page=False)

    def _pagina_siguiente(self):
        if self._pagina_actual < self._total_paginas:
            self._pagina_actual += 1
            self._filtrar_y_renderizar(reset_page=False)

    def _abrir_modal_nuevo(self):
        self._mostrar_modal_formulario(titulo="Nuevo Mensaje de Entrenamiento", item_id=None)

    def _abrir_modal_editar(self, item_id: int):
        self._mostrar_modal_formulario(titulo=f"Editar Mensaje #{item_id}", item_id=item_id)

    def _mostrar_modal_formulario(self, titulo: str, item_id: int = None):
        modal = ctk.CTkToplevel(self)
        modal.title(titulo)
        modal.geometry("580x520")
        modal.transient(self.winfo_toplevel())
        modal.grab_set()

        datos_previos = self._filas_cache.get(item_id) if item_id else None

        # Título
        ctk.CTkLabel(
            modal,
            text=titulo,
            font=ctk.CTkFont(family=FONT_PAGE_TITLE[0], size=22, weight="bold"),
            text_color=AZUL_OSCURO
        ).pack(anchor="w", padx=28, pady=(24, 12))

        # Texto del mensaje (obligatorio)
        ctk.CTkLabel(
            modal,
            text="Texto del Mensaje * (Obligatorio):",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=14, weight="bold"),
            text_color=TEXTO
        ).pack(anchor="w", padx=28, pady=(0, 6))

        txt_mensaje = ctk.CTkTextbox(
            modal,
            height=100,
            font=ctk.CTkFont(family=FONT_BODY[0], size=14),
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_CARD
        )
        txt_mensaje.pack(fill="x", padx=28, pady=(0, 12))
        if datos_previos:
            txt_mensaje.insert("1.0", datos_previos[1])

        # Categoría (obligatoria)
        ctk.CTkLabel(
            modal,
            text="Categoría *:",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=14, weight="bold"),
            text_color=TEXTO
        ).pack(anchor="w", padx=28, pady=(0, 6))

        combo_categoria = ctk.CTkOptionMenu(
            modal,
            values=["fraude", "sospechoso", "legitimo"],
            width=240,
            height=INPUT_HEIGHT_TOOL,
            corner_radius=RADIUS_INPUT,
            fg_color=BLANCO,
            button_color=AZUL_SELECCION,
            text_color=AZUL_OSCURO,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=14, weight="bold")
        )
        if datos_previos:
            combo_categoria.set(datos_previos[2])
        else:
            combo_categoria.set("fraude")
        combo_categoria.pack(anchor="w", padx=28, pady=(0, 12))

        # Origen
        ctk.CTkLabel(
            modal,
            text="Origen (ej. WhatsApp, SMS, Facebook):",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=14, weight="bold"),
            text_color=TEXTO
        ).pack(anchor="w", padx=28, pady=(0, 6))

        entry_origen = ctk.CTkEntry(
            modal,
            height=INPUT_HEIGHT_TOOL,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_INPUT,
            font=ctk.CTkFont(family=FONT_BODY[0], size=14),
            placeholder_text="WhatsApp"
        )
        entry_origen.pack(fill="x", padx=28, pady=(0, 12))
        if datos_previos:
            entry_origen.insert(0, datos_previos[3] or "")

        # Tipo de Fraude / Subcategoría
        ctk.CTkLabel(
            modal,
            text="Tipo de Fraude / Subcategoría:",
            font=ctk.CTkFont(family=FONT_BODY_BOLD[0], size=14, weight="bold"),
            text_color=TEXTO
        ).pack(anchor="w", padx=28, pady=(0, 6))

        entry_subcat = ctk.CTkEntry(
            modal,
            height=INPUT_HEIGHT_TOOL,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            corner_radius=RADIUS_INPUT,
            font=ctk.CTkFont(family=FONT_BODY[0], size=14),
            placeholder_text="Premio Falso, Phishing Bancario, etc."
        )
        entry_subcat.pack(fill="x", padx=28, pady=(0, 20))
        if datos_previos:
            entry_subcat.insert(0, datos_previos[4] or "")

        def guardar():
            msg = txt_mensaje.get("1.0", "end").strip()
            cat = combo_categoria.get().strip()
            orig = entry_origen.get().strip() or "Manual"
            subc = entry_subcat.get().strip()

            if not msg:
                messagebox.showwarning("Campo obligatorio", "Debes ingresar el texto del mensaje.", parent=modal)
                return

            try:
                if item_id:
                    actualizar_mensaje_dataset(item_id, msg, cat, orig, subc)
                else:
                    agregar_mensaje_dataset(msg, cat, orig, subc)
                modal.destroy()
                self._cargar_datos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el registro: {e}", parent=modal)

        # Botones Cancelar / Guardar
        frame_btn_modal = ctk.CTkFrame(modal, fg_color="transparent")
        frame_btn_modal.pack(fill="x", padx=28, pady=(0, 20))

        ctk.CTkButton(
            frame_btn_modal,
            text="Cancelar",
            width=120,
            height=BTN_HEIGHT_TOOL,
            corner_radius=RADIUS_BUTTON,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDE,
            text_color=TEXTO,
            hover_color=FONDO,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
            command=modal.destroy
        ).pack(side="right", padx=(10, 0))

        ctk.CTkButton(
            frame_btn_modal,
            text="Guardar",
            width=140,
            height=BTN_HEIGHT_TOOL,
            corner_radius=RADIUS_BUTTON,
            fg_color=AZUL,
            hover_color=SIDEBAR_HOVER,
            text_color=BLANCO,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
            command=guardar
        ).pack(side="right")

    def _confirmar_eliminar(self, item_id: int):
        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Deseas eliminar el registro #{item_id} del dataset?",
            icon="warning"
        ):
            try:
                eliminar_mensaje_dataset(item_id)
                self._cargar_datos()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el registro: {e}")

    def _importar_csv(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo CSV para importar",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        try:
            # --- Primera pasada: leer y analizar el CSV ---
            with open(ruta, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                campos = [c.lower().strip() for c in (reader.fieldnames or [])]
                if "mensaje" not in campos or "categoria" not in campos:
                    messagebox.showerror(
                        "Formato invalido",
                        "El CSV debe contener al menos las columnas obligatorias: 'mensaje' y 'categoria'."
                    )
                    return
                filas_csv = list(reader)

            # Normalizar todos los existentes para comparación semántica
            existentes_norm = {_normalizar_para_duplicado(f[1]) for f in self._filas_raw}

            pendientes = []
            omitidos_formato = 0
            omitidos_duplicado = 0

            for row in filas_csv:
                msg  = row.get("mensaje", "").strip()
                cat  = row.get("categoria", "").strip().lower()
                orig = row.get("origen", "CSV").strip() or "CSV"
                subc = row.get("subcategoria", "").strip()

                if not msg or cat not in ("fraude", "sospechoso", "legitimo"):
                    omitidos_formato += 1
                    continue

                # Detección normalizada: detecta duplicados aunque cambien montos/URLs/teléfonos
                if _normalizar_para_duplicado(msg) in existentes_norm:
                    omitidos_duplicado += 1
                    continue

                pendientes.append((msg, cat, orig, subc))

            # Conteos por categoría de los pendientes
            cnt_fraude = sum(1 for p in pendientes if p[1] == "fraude")
            cnt_sosp   = sum(1 for p in pendientes if p[1] == "sospechoso")
            cnt_legit  = sum(1 for p in pendientes if p[1] == "legitimo")

            if len(pendientes) == 0:
                messagebox.showinfo(
                    "Sin registros nuevos",
                    "No se encontraron registros nuevos para importar.\n"
                    + (f"({omitidos_duplicado} ya existen en el dataset)" if omitidos_duplicado else "")
                )
                return

            # --- Modal bonito de confirmación ---
            confirmado = _mostrar_modal_csv(
                self,
                modo="importar",
                nombre_archivo=os.path.basename(ruta),
                cnt_fraude=cnt_fraude,
                cnt_sosp=cnt_sosp,
                cnt_legit=cnt_legit,
                total=len(pendientes),
                duplicados=omitidos_duplicado,
                formato_invalido=omitidos_formato
            )
            if not confirmado:
                return

            # --- Segunda pasada: insertar solo si el usuario confirmó ---
            for msg, cat, orig, subc in pendientes:
                agregar_mensaje_dataset(msg, cat, orig, subc)

            self._cargar_datos()
            messagebox.showinfo(
                "Importacion Completada",
                f"Se importaron {len(pendientes)} registros nuevos correctamente."
                + (f"\nSe omitieron {omitidos_duplicado} registros similares." if omitidos_duplicado else "")
            )

        except Exception as e:
            messagebox.showerror("Error de importacion", f"No se pudo leer el archivo CSV: {e}")

    def _exportar_csv(self):
        # --- Recopilar estadísticas antes del diálogo de archivo ---
        filas = obtener_dataset()
        if not filas:
            messagebox.showinfo("Dataset vacio", "No hay registros en el dataset para exportar.")
            return

        cnt_fraude = sum(1 for f in filas if f[2] == "fraude")
        cnt_sosp   = sum(1 for f in filas if f[2] == "sospechoso")
        cnt_legit  = sum(1 for f in filas if f[2] == "legitimo")

        # --- Elegir archivo de destino ---
        ruta = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Archivos CSV", "*.csv")],
            title="Guardar Dataset como CSV"
        )
        if not ruta:
            return

        # --- Modal bonito de confirmación ---
        confirmado = _mostrar_modal_csv(
            self,
            modo="exportar",
            nombre_archivo=os.path.basename(ruta),
            ruta_completa=ruta,
            cnt_fraude=cnt_fraude,
            cnt_sosp=cnt_sosp,
            cnt_legit=cnt_legit,
            total=len(filas)
        )
        if not confirmado:
            return

        try:
            with open(ruta, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "mensaje", "categoria", "origen", "subcategoria"])
                writer.writerows(filas)
            messagebox.showinfo("Exportacion Exitosa", f"Se exportaron {len(filas)} registros a:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar el dataset: {e}")

    def on_show(self):
        self._cargar_datos()
