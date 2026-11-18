# ui/theme.py
"""
Definición centralizada de colores, fuentes, dimensiones y radios
para Bolivia Fraud Detector (CustomTkinter).
Fuente de verdad visual: 5 Mockups oficiales.
"""

# --- PALETA CROMÁTICA OFICIAL ---
AZUL            = "#1E3A8A"   # Azul institucional principal / Sidebar
AZUL_OSCURO     = "#0F1F4D"   # Títulos principales y texto de botones activos
AZUL_SELECCION  = "#CFE5FB"   # Fondo de ítem activo en sidebar y chips de dataset
FONDO           = "#F8FAFC"   # Fondo general de la ventana y paneles
BLANCO          = "#FFFFFF"   # Tarjetas, fondos de tabla, inputs
BORDE           = "#CBD5E1"   # Bordes generales de inputs y tarjetas
TEXTO           = "#1F2937"   # Texto oscuro principal
TEXTO_MUTED     = "#64748B"   # Subtítulos y textos secundarios

# Estados semafóricos de riesgo
ROJO            = "#DC2626"   # Fraude / Alerta crítica
ROJO_CLARO      = "#FEE2E2"   # Fondo de tarjeta de fraude
AMBAR           = "#D99A1E"   # Sospechoso / Advertencia
AMBAR_CLARO     = "#FEF3C7"   # Fondo de tarjeta sospechosa
VERDE           = "#16A34A"   # Legítimo / Sin indicios de fraude
VERDE_CLARO     = "#DCFCE7"   # Fondo de tarjeta legítima

# Elementos específicos
GRIS_BURBUJA    = "#7F848E"   # Burbuja de mensaje del usuario en el chat
GRIS_TABLA_HEAD = "#E5E7EB"   # Cabecera de tablas
SIDEBAR_HOVER   = "#1A3275"   # Hover sutil en botones inactivos del sidebar

# --- TIPOGRAFÍAS ---
FONT_FAMILY = "Segoe UI"
FONT_TABLES = "Segoe UI"  # Fallback nativo universal en Windows

FONT_TITULO_PAGINA = (FONT_FAMILY, 24, "bold")
FONT_SUBTITULO     = (FONT_FAMILY, 13, "normal")
FONT_SIDEBAR_TIT   = (FONT_FAMILY, 15, "bold")
FONT_SIDEBAR_BTN   = (FONT_FAMILY, 13, "normal")
FONT_CARD_TIT      = (FONT_FAMILY, 14, "bold")
FONT_BODY          = (FONT_FAMILY, 12, "normal")
FONT_BODY_BOLD     = (FONT_FAMILY, 12, "bold")
FONT_BADGE         = (FONT_FAMILY, 11, "bold")

# --- DIMENSIONES Y RADIOS ---
SIDEBAR_WIDTH = 312
WINDOW_DEFAULT_SIZE = "1408x768"
WINDOW_MIN_SIZE = (1100, 650)

RADIUS_CARD = 14
RADIUS_INPUT = 10
RADIUS_PILL = 20
RADIUS_BADGE = 6
