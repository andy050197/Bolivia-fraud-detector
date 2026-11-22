# main.py
import sys
import os
import customtkinter as ctk
from PIL import Image

def resource_path(relative_path):
    """Resuelve la ruta para desarrollo y para el empaquetado de PyInstaller."""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

from ui.theme import (
    AZUL, AZUL_OSCURO, AZUL_SELECCION, FONDO, BLANCO, SIDEBAR_WIDTH,
    WINDOW_DEFAULT_SIZE, WINDOW_MIN_SIZE, SIDEBAR_HOVER, FONT_FAMILY
)
from database.db import inicializar_db, cargar_csv_a_dataset, obtener_dataset
from views.chat_detector import ChatDetectorView
from views.historial import HistorialView
from views.panel_general import PanelGeneralView
from views.dataset import DatasetView
from views.entrenar_modelo import EntrenarModeloView

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bolivia Fraud Detector - Detección de Estafas Digitales")
        self.geometry(WINDOW_DEFAULT_SIZE)
        self.minsize(WINDOW_MIN_SIZE[0], WINDOW_MIN_SIZE[1])
        self.configure(fg_color=FONDO)

        # Base de datos local
        inicializar_db()
        self._verificar_dataset_inicial()

        self._vista_activa = None
        self._botones_nav = {}
        self._iconos = {}

        self._cargar_iconos()
        self._configurar_layout()
        self._navegar("chat")

    def _verificar_dataset_inicial(self):
        if len(obtener_dataset()) == 0:
            csv_path = resource_path(os.path.join("data", "mensajes.csv"))
            if os.path.exists(csv_path):
                cargar_csv_a_dataset(csv_path)

    def _cargar_iconos(self):
        icons_dir = resource_path(os.path.join("assets", "icons"))
        items = ["message-circle", "history", "layout-grid", "database", "users"]
        for item in items:
            p_w = os.path.join(icons_dir, f"{item}_white.png")
            p_a = os.path.join(icons_dir, f"{item}_active.png")
            if os.path.exists(p_w):
                self._iconos[f"{item}_white"] = ctk.CTkImage(Image.open(p_w), size=(20, 20))
            if os.path.exists(p_a):
                self._iconos[f"{item}_active"] = ctk.CTkImage(Image.open(p_a), size=(20, 20))

        p_escudo = os.path.join(icons_dir, "shield_main.png")
        if os.path.exists(p_escudo):
            self.img_escudo = ctk.CTkImage(Image.open(p_escudo), size=(44, 44))
        else:
            self.img_escudo = None

    def _configurar_layout(self):
        # Usar grid de 2 columnas: col 0 = Sidebar fijo (312px), col 1 = Contenido expandible
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=SIDEBAR_WIDTH)
        self.grid_columnconfigure(1, weight=1)

        # --- 1. SIDEBAR (Ancho exacto 312px, fondo AZUL) ---
        self.sidebar = ctk.CTkFrame(self, fg_color=AZUL, width=SIDEBAR_WIDTH, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Encabezado: Escudo y texto en dos líneas
        frame_logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_logo.pack(fill="x", padx=24, pady=(36, 40))

        if self.img_escudo:
            lbl_ico = ctk.CTkLabel(frame_logo, image=self.img_escudo, text="")
            lbl_ico.pack(side="left")
        else:
            lbl_ico = ctk.CTkLabel(frame_logo, text="BFD", font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"), text_color=BLANCO)
            lbl_ico.pack(side="left")

        lbl_tit = ctk.CTkLabel(
            frame_logo,
            text="Bolivia Fraud\nDetector",
            font=ctk.CTkFont(family=FONT_FAMILY, size=22, weight="bold"),
            text_color=BLANCO,
            justify="left"
        )
        lbl_tit.pack(side="left", padx=14)

        # 5 Ítems de navegación ordenados según mockup
        nav_defs = [
            ("chat", "message-circle", "Chat Detector"),
            ("historial", "history", "Historial de Análisis"),
            ("panel", "layout-grid", "Panel General"),
            ("dataset", "database", "Dataset de Mensajes"),
            ("entrenar", "users", "Entrenar Modelo"),
        ]

        for clave, icon_name, label in nav_defs:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {label}",
                image=self._iconos.get(f"{icon_name}_white"),
                compound="left",
                anchor="w",
                font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="normal"),
                fg_color="transparent",
                text_color=BLANCO,
                hover_color=SIDEBAR_HOVER,
                height=48,
                corner_radius=10,
                command=lambda c=clave: self._navegar(c)
            )
            btn.pack(fill="x", padx=20, pady=4)
            self._botones_nav[clave] = (btn, icon_name)

        # --- 2. CONTENEDOR DE CONTENIDO (Fondo FONDO #F8FAFC) ---
        self.contenedor_principal = ctk.CTkFrame(self, fg_color=FONDO, corner_radius=0)
        self.contenedor_principal.grid(row=0, column=1, sticky="nsew")
        self.contenedor_principal.grid_rowconfigure(0, weight=1)
        self.contenedor_principal.grid_columnconfigure(0, weight=1)

        # Inicializar vistas usando grid para preservar estado sin reconstruir
        self._vistas = {
            "chat": ChatDetectorView(self.contenedor_principal),
            "historial": HistorialView(self.contenedor_principal),
            "panel": PanelGeneralView(self.contenedor_principal),
            "dataset": DatasetView(self.contenedor_principal),
            "entrenar": EntrenarModeloView(self.contenedor_principal),
        }

        for vista in self._vistas.values():
            vista.grid(row=0, column=0, sticky="nsew")
            vista.grid_remove()  # ocultas inicialmente

    def _navegar(self, clave_vista: str):
        # 1. Ocultar la vista anterior
        if self._vista_activa and self._vista_activa in self._vistas:
            self._vistas[self._vista_activa].grid_remove()

        # 2. Desactivar estilo visual de todos los botones
        for k, (btn, icon_name) in self._botones_nav.items():
            btn.configure(
                fg_color="transparent",
                text_color=BLANCO,
                image=self._iconos.get(f"{icon_name}_white")
            )

        # 3. Resaltar botón activo con AZUL_SELECCION (#CFE5FB) y texto AZUL_OSCURO
        btn_act, icon_act = self._botones_nav[clave_vista]
        btn_act.configure(
            fg_color=AZUL_SELECCION,
            text_color=AZUL_OSCURO,
            image=self._iconos.get(f"{icon_act}_active")
        )

        # 4. Mostrar la vista seleccionada elevándola
        vista = self._vistas[clave_vista]
        vista.grid()
        vista.tkraise()

        # 5. Notificar hook on_show si la vista lo implementa
        if hasattr(vista, "on_show"):
            vista.on_show()

        self._vista_activa = clave_vista

if __name__ == "__main__":
    app = App()
    app.mainloop()
