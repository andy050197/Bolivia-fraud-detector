# ui/components.py
"""
Componentes reutilizables de CustomTkinter para Bolivia Fraud Detector.
Diseñados siguiendo estrictamente las Reglas Globales de Uniformidad (Prompt 2).
"""

import os
import customtkinter as ctk
from PIL import Image

from ui.theme import (
    AZUL, AZUL_OSCURO, AZUL_SELECCION, FONDO, BLANCO, BORDE, TEXTO, TEXTO_MUTED,
    ROJO, ROJO_CLARO, AMBAR, AMBAR_CLARO, VERDE, VERDE_CLARO, GRIS_TABLA_HEAD,
    SIDEBAR_HOVER, FONT_FAMILY, FONT_PAGE_TITLE, FONT_SUBTITLE, FONT_BODY,
    FONT_BODY_BOLD, FONT_TABLE_HEAD, FONT_TABLE_CELL, FONT_TABLE_CELL_BOLD,
    FONT_BUTTON, FONT_BADGE, BORDER_WIDTH, BORDER_COLOR, RADIUS_CARD, RADIUS_INPUT,
    RADIUS_BUTTON, RADIUS_PILL, RADIUS_BADGE, BTN_HEIGHT_TOOL, BTN_HEIGHT_TRAIN,
    BADGE_HEIGHT_TABLE, BADGE_HEIGHT_CHAT, BADGE_MIN_WIDTH
)

ICONS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")

def cargar_icono_ctk(nombre_archivo: str, size: tuple = (20, 20)):
    """Carga un icono PNG desde assets/icons adaptado para CustomTkinter."""
    ruta = os.path.join(ICONS_DIR, nombre_archivo)
    if os.path.exists(ruta):
        try:
            img = Image.open(ruta)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception:
            return None
    return None

# =====================================================================
# 1. ENCABEZADO DE PÁGINA ESTANDARIZADO (Sección 1.5)
# =====================================================================
class PageHeader(ctk.CTkFrame):
    """Encabezado oficial unificado para todas las vistas."""
    def __init__(self, parent, titulo: str, subtitulo: str = None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.pack(fill="x", padx=40, pady=(32, 20))

        lbl_tit = ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(family=FONT_PAGE_TITLE[0], size=FONT_PAGE_TITLE[1], weight=FONT_PAGE_TITLE[2]),
            text_color=AZUL_OSCURO
        )
        lbl_tit.pack(anchor="w")

        if subtitulo:
            lbl_sub = ctk.CTkLabel(
                self,
                text=subtitulo,
                font=ctk.CTkFont(family=FONT_SUBTITLE[0], size=FONT_SUBTITLE[1]),
                text_color=TEXTO_MUTED
            )
            lbl_sub.pack(anchor="w", pady=(6, 0))

def crear_header_vista(parent, titulo: str, subtitulo: str = None):
    """Función de compatibilidad que instancia PageHeader."""
    return PageHeader(parent, titulo, subtitulo)

# =====================================================================
# 2. BADGE CURVO ESTANDARIZADO (Sección 1.4)
# =====================================================================
class Badge(ctk.CTkFrame):
    """
    Badge de píldora oficial (Fraude, Sospechoso, Legítimo, Operativo, ACTIVO).
    Alto: 30px en tablas, 36px en chat.
    Ancho mínimo uniforme: 110px.
    """
    def __init__(self, parent, categoria: str, alto: int = BADGE_HEIGHT_TABLE, ancho: int = BADGE_MIN_WIDTH, **kwargs):
        cat_raw = str(categoria).strip()
        cat_lower = cat_raw.lower()

        if "fraude" in cat_lower:
            color_fondo = ROJO
            texto = "Fraude"
        elif "sospechoso" in cat_lower:
            color_fondo = AMBAR
            texto = "Sospechoso"
        elif "legitimo" in cat_lower or "legítimo" in cat_lower:
            color_fondo = VERDE
            texto = "Legítimo"
        elif "activo" in cat_lower:
            color_fondo = VERDE
            texto = "ACTIVO"
        elif "operativo" in cat_lower:
            color_fondo = VERDE
            texto = "Operativo"
        elif "sin entrenar" in cat_lower:
            color_fondo = "#94A3B8"
            texto = "Sin entrenar"
        else:
            color_fondo = AZUL
            texto = cat_raw

        radio = alto // 2
        super().__init__(
            parent,
            fg_color=color_fondo,
            corner_radius=radio,
            width=ancho,
            height=alto,
            **kwargs
        )
        self.pack_propagate(False)

        self.lbl = ctk.CTkLabel(
            self,
            text=texto,
            font=ctk.CTkFont(family=FONT_BADGE[0], size=FONT_BADGE[1], weight=FONT_BADGE[2]),
            text_color=BLANCO
        )
        self.lbl.place(relx=0.5, rely=0.5, anchor="center")

def crear_badge_categoria(parent, categoria: str, alto: int = BADGE_HEIGHT_TABLE, ancho: int = BADGE_MIN_WIDTH):
    """Crea y devuelve un Badge empaquetable."""
    return Badge(parent, categoria, alto=alto, ancho=ancho)

# =====================================================================
# 3. BOTONES ESTANDARIZADOS (Sección 1.3 - Tres Variantes Únicas)
# =====================================================================
class BotonPrimario(ctk.CTkButton):
    """Variante 1: fg AZUL, hover SIDEBAR_HOVER, texto blanco bold 16px."""
    def __init__(self, parent, text: str, command=None, icon=None, width=None, height=BTN_HEIGHT_TOOL, **kwargs):
        img = cargar_icono_ctk(icon, size=(20, 20)) if isinstance(icon, str) else icon
        super().__init__(
            parent,
            text=text,
            command=command,
            image=img,
            compound="left",
            width=width or 140,
            height=height,
            corner_radius=RADIUS_BUTTON,
            fg_color=AZUL,
            hover_color=SIDEBAR_HOVER,
            text_color=BLANCO,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
            **kwargs
        )

class BotonContorno(ctk.CTkButton):
    """Variante 2: fg transparente, border 2px AZUL, texto AZUL_OSCURO bold 16px."""
    def __init__(self, parent, text: str, command=None, icon=None, width=None, height=BTN_HEIGHT_TOOL, **kwargs):
        img = cargar_icono_ctk(icon, size=(20, 20)) if isinstance(icon, str) else icon
        super().__init__(
            parent,
            text=text,
            command=command,
            image=img,
            compound="left",
            width=width or 120,
            height=height,
            corner_radius=RADIUS_BUTTON,
            fg_color="transparent",
            border_width=BORDER_WIDTH,
            border_color=AZUL,
            hover_color="#E0E7FF",
            text_color=AZUL_OSCURO,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
            **kwargs
        )

class BotonPeligro(ctk.CTkButton):
    """Variante 3: fg transparente, border 2px ROJO, texto ROJO bold 16px."""
    def __init__(self, parent, text: str, command=None, icon=None, width=None, height=BTN_HEIGHT_TOOL, **kwargs):
        img = cargar_icono_ctk(icon, size=(20, 20)) if isinstance(icon, str) else icon
        super().__init__(
            parent,
            text=text,
            command=command,
            image=img,
            compound="left",
            width=width or 140,
            height=height,
            corner_radius=RADIUS_BUTTON,
            fg_color="transparent",
            border_width=BORDER_WIDTH,
            border_color=ROJO,
            hover_color=ROJO_CLARO,
            text_color=ROJO,
            font=ctk.CTkFont(family=FONT_BUTTON[0], size=FONT_BUTTON[1], weight=FONT_BUTTON[2]),
            **kwargs
        )

# =====================================================================
# 4. CHIP DE RESUMEN ESTADÍSTICO (Sección 1.4 y 4)
# =====================================================================
def crear_chip_resumen(parent, texto: str):
    """Chip ovalado celeste (AZUL_SELECCION) con texto AZUL_OSCURO 15px bold."""
    chip = ctk.CTkFrame(parent, fg_color=AZUL_SELECCION, corner_radius=RADIUS_PILL, height=36)
    lbl = ctk.CTkLabel(
        chip,
        text=texto,
        font=ctk.CTkFont(family=FONT_BADGE[0], size=FONT_BADGE[1], weight=FONT_BADGE[2]),
        text_color=AZUL_OSCURO
    )
    lbl.pack(padx=16, pady=6)
    chip.lbl = lbl
    return chip

# =====================================================================
# 5. BUSCADOR ESTANDARIZADO (Con debounce y bordes 2px completos)
# =====================================================================
class Buscador(ctk.CTkFrame):
    """
    Componente oficial de buscador con icono de lupa, bordes 2px completos
    y debounce automático para búsquedas fluidas sin bloqueos ni distorsión de UI.
    """
    def __init__(self, parent, placeholder_text: str = "Buscar...", command=None, debounce_ms: int = 220, height=BTN_HEIGHT_TOOL, **kwargs):
        super().__init__(
            parent,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDER_COLOR,
            corner_radius=RADIUS_INPUT,
            height=height,
            **kwargs
        )
        self.pack_propagate(False)
        self._command = command
        self._debounce_ms = debounce_ms
        self._timer_id = None
        self._last_query = ""

        img_search = cargar_icono_ctk("search_muted.png", size=(18, 18))
        if img_search:
            self.lbl_ico = ctk.CTkLabel(self, text="", image=img_search, width=28)
            self.lbl_ico.pack(side="left", padx=(10, 2))

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder_text,
            font=ctk.CTkFont(family=FONT_BODY[0], size=FONT_BODY[1]),
            fg_color="transparent",
            text_color=TEXTO,
            border_width=0
        )
        # Margen derecho de 12px para asegurar que no tape el borde derecho curvo
        self.entry.pack(side="left", fill="both", expand=True, padx=(2, 12), pady=3)

        self.entry.bind("<KeyRelease>", self._on_key_release, add="+")
        self.entry.bind("<Return>", self._on_return, add="+")

    def _on_key_release(self, event=None):
        if not self._command:
            return
        if event and event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock", "Up", "Down", "Left", "Right"):
            return
        current = self.get().strip()
        if current == self._last_query:
            return
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
        self._timer_id = self.after(self._debounce_ms, self._ejecutar_busqueda)

    def _on_return(self, event=None):
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        self._ejecutar_busqueda()

    def _ejecutar_busqueda(self):
        self._timer_id = None
        self._last_query = self.get().strip()
        if self._command:
            self._command()

    def get(self) -> str:
        return self.entry.get()

    def delete(self, first, last=None):
        self.entry.delete(first, last)
        self._last_query = ""

    def insert(self, index, string):
        self.entry.insert(index, string)

    def bind(self, sequence=None, command=None, add="+"):
        return self.entry.bind(sequence, command, add=add)

# =====================================================================
# 6. COMPONENTE REUTILIZABLE: DataTable
# =====================================================================
ROW_HEIGHT = 54  # Altura mínima de cada fila de datos (garantiza que badges no se partan)

class DataTable(ctk.CTkFrame):
    """
    Tabla centralizada para Historial, Dataset y Entrenar.
    - Fila de cabecera sticky en row=0, celdas de datos desde row=1.
    - ROW_HEIGHT=54 garantiza que los Badge nunca se recorten.
    - Columnas con align='w' muestran texto completo con wraplength calculado por ancho de columna.
    - finalize_rows() agrega relleno blanco para evitar slate gris al fondo.
    """
    def __init__(self, parent, columnas: list, empty_message: str = "Sin registros", **kwargs):
        super().__init__(
            parent,
            fg_color=BLANCO,
            border_width=BORDER_WIDTH,
            border_color=BORDER_COLOR,
            corner_radius=RADIUS_CARD,
            **kwargs
        )
        self.columnas = columnas
        self.empty_message = empty_message
        self._row_count = 0
        self._rows_widgets = []
        self._header_widgets = []
        self._filler_widget = None
        self._build_table_structure()

    def _build_table_structure(self):
        self.scroll_body = ctk.CTkScrollableFrame(
            self,
            fg_color=BORDER_COLOR,
            corner_radius=RADIUS_CARD - 2,
            scrollbar_button_color="#94A3B8",
            scrollbar_button_hover_color=AZUL
        )
        self.scroll_body.pack(fill="both", expand=True, padx=2, pady=2)

        for idx, col in enumerate(self.columnas):
            peso = col[1]
            min_ancho = col[3] if len(col) > 3 else 0
            self.scroll_body.grid_columnconfigure(idx, weight=peso, minsize=min_ancho)

        self._render_header()

    def _render_header(self):
        for w in self._header_widgets:
            try:
                w.destroy()
            except Exception:
                pass
        self._header_widgets.clear()

        for idx, col in enumerate(self.columnas):
            nombre = col[0]
            align = col[2] if len(col) > 2 else "center"
            min_ancho = col[3] if len(col) > 3 else 0

            cell = ctk.CTkFrame(
                self.scroll_body,
                fg_color=GRIS_TABLA_HEAD,
                corner_radius=0,
                height=44,
                width=min_ancho
            )
            cell.grid(row=0, column=idx, sticky="nsew", padx=1, pady=(1, 1))
            cell.pack_propagate(False)
            cell.grid_propagate(False)

            anchor_pos = "w" if align == "w" else ("center" if align == "center" else "e")
            lbl = ctk.CTkLabel(
                cell,
                text=nombre,
                font=ctk.CTkFont(family=FONT_TABLE_HEAD[0], size=FONT_TABLE_HEAD[1], weight=FONT_TABLE_HEAD[2]),
                text_color=AZUL_OSCURO,
                anchor=anchor_pos
            )
            lbl.pack(anchor=anchor_pos, padx=4, pady=6, fill="both", expand=True)
            self._header_widgets.append(cell)

    def scroll_to_top(self):
        try:
            self.scroll_body._parent_canvas.yview_moveto(0)
        except Exception:
            pass

    def clear(self):
        self.scroll_to_top()
        if self._filler_widget:
            try:
                self._filler_widget.destroy()
            except Exception:
                pass
            self._filler_widget = None

        for widget in self._rows_widgets:
            try:
                widget.destroy()
            except Exception:
                pass
        self._rows_widgets.clear()
        self._row_count = 0

    def finalize_rows(self):
        if self._filler_widget:
            try:
                self._filler_widget.destroy()
            except Exception:
                pass
            self._filler_widget = None

        last_row = self._row_count + 1
        self._filler_widget = ctk.CTkFrame(self.scroll_body, fg_color=BLANCO, corner_radius=0, height=1)
        self._filler_widget.grid(row=last_row, column=0, columnspan=len(self.columnas), sticky="nsew", padx=1, pady=(0, 1))
        self.scroll_body.grid_rowconfigure(last_row, weight=1)

    def show_empty(self, message: str = None):
        self.clear()
        texto = message or self.empty_message
        empty_cell = ctk.CTkFrame(self.scroll_body, fg_color=BLANCO, corner_radius=0)
        empty_cell.grid(row=1, column=0, columnspan=len(self.columnas), sticky="nsew", padx=1, pady=1)
        ctk.CTkLabel(
            empty_cell,
            text=texto,
            font=ctk.CTkFont(family=FONT_BODY[0], size=FONT_BODY[1]),
            text_color=TEXTO_MUTED
        ).pack(pady=60)
        self._rows_widgets.append(empty_cell)
        self.finalize_rows()

    def add_row(self, cell_items: list, is_highlighted: bool = False, on_click=None):
        """
        Agrega una fila de celdas con altura adaptable según el tamaño del texto.
        - grid_rowconfigure asegura altura mínima de 52px.
        - Celdas con align='w' expanden verticalmente la fila para mostrar el texto completo.
        - Badges y botones se centran verticalmente en su celda sin cortarse.
        """
        bg_color = AZUL_SELECCION if is_highlighted else BLANCO
        actual_row = self._row_count + 1

        # Altura mínima para la fila completa en el grid
        self.scroll_body.grid_rowconfigure(actual_row, minsize=52)

        for col_idx, item in enumerate(cell_items):
            col_info = self.columnas[col_idx]
            peso = col_info[1] if len(col_info) > 1 else 0
            align = col_info[2] if len(col_info) > 2 else "center"
            min_ancho = col_info[3] if len(col_info) > 3 else 80

            cell_frame = ctk.CTkFrame(
                self.scroll_body,
                fg_color=bg_color,
                corner_radius=0,
                width=min_ancho
            )
            cell_frame.grid(row=actual_row, column=col_idx, sticky="nsew", padx=1, pady=1)

            if on_click:
                cell_frame.bind("<Button-1>", lambda e, cb=on_click: cb())

            if callable(item):
                # Widget creado por factory function (Badge, botones de acciones)
                widget = item(cell_frame)
                if widget is not None and not widget.winfo_manager():
                    widget.pack(expand=True, padx=4, pady=8)
            elif isinstance(item, ctk.CTkBaseClass):
                item.master = cell_frame
                if not item.winfo_manager():
                    item.pack(expand=True, padx=4, pady=8)
            else:
                font_cell = FONT_TABLE_CELL_BOLD if is_highlighted else FONT_TABLE_CELL
                es_texto_largo = (align == "w" or peso > 0)

                if es_texto_largo:
                    lbl = ctk.CTkLabel(
                        cell_frame,
                        text=str(item),
                        font=ctk.CTkFont(family=font_cell[0], size=font_cell[1], weight=font_cell[2]),
                        text_color=AZUL_OSCURO if is_highlighted else TEXTO,
                        anchor="w",
                        justify="left",
                        wraplength=450
                    )
                    if on_click:
                        lbl.bind("<Button-1>", lambda e, cb=on_click: cb())
                    lbl.pack(fill="both", expand=True, padx=12, pady=10)
                else:
                    lbl = ctk.CTkLabel(
                        cell_frame,
                        text=str(item),
                        font=ctk.CTkFont(family=font_cell[0], size=font_cell[1], weight=font_cell[2]),
                        text_color=AZUL_OSCURO if is_highlighted else TEXTO,
                        anchor="center" if align == "center" else "e",
                        justify="center"
                    )
                    if on_click:
                        lbl.bind("<Button-1>", lambda e, cb=on_click: cb())
                    lbl.pack(fill="both", expand=True, padx=6, pady=8)

            self._rows_widgets.append(cell_frame)

        self._row_count += 1
