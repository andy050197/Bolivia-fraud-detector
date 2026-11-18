import sys
import os

# Para que funcione el .exe generado por PyInstaller
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

import customtkinter as ctk
from database.db import inicializar_db, cargar_csv_a_dataset, obtener_dataset
from views.chat_detector   import ChatDetectorView
from views.historial        import HistorialView
from views.panel_general    import PanelGeneralView
from views.dataset          import DatasetView
from views.entrenar_modelo  import EntrenarModeloView

# Configuración de apariencia
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

SIDEBAR_COLOR  = "#1e293b"   # Azul oscuro del mockup
SIDEBAR_HOVER  = "#334155"
SIDEBAR_ACTIVE = "#1e40af"
ICON_COLOR     = "#94a3b8"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bolivia Fraud Detector")
        self.geometry("1100x680")
        self.minsize(900, 580)
        self.configure(fg_color="#f8fafc")

        # Inicializar base de datos y cargar CSV inicial
        inicializar_db()
        self._cargar_dataset_inicial()

        self._vista_activa = None
        self._botones_nav  = {}
        self._build_layout()
        self._navegar("chat")

    def _cargar_dataset_inicial(self):
        """Carga el CSV inicial solo si el dataset está vacío."""
        if len(obtener_dataset()) == 0:
            csv_path = os.path.join(BASE_DIR, "data", "mensajes.csv")
            if os.path.exists(csv_path):
                cargar_csv_a_dataset(csv_path)

    def _build_layout(self):
        # ── Sidebar ──────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_COLOR, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo / título
        frame_logo = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        frame_logo.pack(fill="x", padx=15, pady=(20, 25))
        ctk.CTkLabel(frame_logo, text="🛡", font=ctk.CTkFont(size=28), text_color="white").pack(side="left")
        ctk.CTkLabel(frame_logo, text="Bolivia Fraud\nDetector",
                     font=ctk.CTkFont(size=13, weight="bold"),
                     text_color="white", justify="left").pack(side="left", padx=8)

        # Ítems de navegación
        nav_items = [
            ("chat",      "💬", "Chat Detector"),
            ("historial", "🕐", "Historial de Análisis"),
            ("panel",     "📊", "Panel General"),
            ("dataset",   "🗂", "Dataset de Mensajes"),
            ("entrenar",  "🤖", "Entrenar Modelo"),
        ]
        for key, icon, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=f" {icon}  {label}",
                anchor="w",
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                text_color="#cbd5e1",
                hover_color=SIDEBAR_HOVER,
                height=42,
                corner_radius=8,
                command=lambda k=key: self._navegar(k)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._botones_nav[key] = btn

        # ── Área de contenido ─────────────────────────────────────
        self.frame_contenido = ctk.CTkFrame(self, fg_color="white", corner_radius=0)
        self.frame_contenido.pack(side="right", fill="both", expand=True)

        # Instanciar todas las vistas
        self._vistas = {
            "chat":      ChatDetectorView(self.frame_contenido),
            "historial": HistorialView(self.frame_contenido),
            "panel":     PanelGeneralView(self.frame_contenido),
            "dataset":   DatasetView(self.frame_contenido),
            "entrenar":  EntrenarModeloView(self.frame_contenido),
        }

    def _navegar(self, key: str):
        # Ocultar vista actual
        if self._vista_activa and self._vista_activa in self._vistas:
            self._vistas[self._vista_activa].pack_forget()

        # Resetear estilos de botones
        for k, btn in self._botones_nav.items():
            btn.configure(fg_color="transparent", text_color="#cbd5e1")

        # Activar nuevo botón
        self._botones_nav[key].configure(fg_color=SIDEBAR_ACTIVE, text_color="white")

        # Mostrar nueva vista
        self._vistas[key].pack(fill="both", expand=True)

        # Llamar hook on_show si existe (para actualizar datos)
        vista = self._vistas[key]
        if hasattr(vista, "on_show"):
            vista.on_show()

        self._vista_activa = key


if __name__ == "__main__":
    app = App()
    app.mainloop()
