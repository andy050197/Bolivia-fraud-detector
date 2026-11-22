# ui/theme.py
"""
Definición centralizada de colores, fuentes, dimensiones y radios
para Bolivia Fraud Detector (CustomTkinter).
Fuente de verdad visual: 5 Mockups oficiales + Reglas globales de uniformidad.
"""

# --- PALETA CROMÁTICA OFICIAL ---
AZUL            = "#1E3A8A"   # Azul institucional principal / Botones primarios
AZUL_OSCURO     = "#0F1F4D"   # Títulos principales y texto de botones activos
AZUL_SELECCION  = "#CFE5FB"   # Fondo de ítem activo en sidebar, chips y filas destacadas
FONDO           = "#F8FAFC"   # Fondo general de la ventana y paneles
BLANCO          = "#FFFFFF"   # Tarjetas, fondos de tabla, inputs
BORDE           = "#CBD5E1"   # Bordes generales de inputs, tablas y tarjetas (2px)
TEXTO           = "#1F2937"   # Texto oscuro principal (16px)
TEXTO_MUTED     = "#64748B"   # Subtítulos y textos secundarios

# Estados semafóricos de riesgo
ROJO            = "#DC2626"   # Fraude / Alerta crítica
ROJO_CLARO      = "#FEE2E2"   # Fondo de tarjeta de fraude
AMBAR           = "#D99A1E"   # Sospechoso / Advertencia
AMBAR_CLARO     = "#FEF3C7"   # Fondo de tarjeta sospechosa
VERDE           = "#16A34A"   # Legítimo / Sin indicios de fraude / Operativo
VERDE_CLARO     = "#DCFCE7"   # Fondo de tarjeta legítima

# Elementos específicos
GRIS_BURBUJA    = "#7F848E"   # Burbuja de mensaje del usuario en el chat
GRIS_TABLA_HEAD = "#F1F5F9"   # Cabecera de tablas
SIDEBAR_HOVER   = "#1A3275"   # Hover sutil en botones del sidebar

# --- TIPOGRAFÍAS (Reglas Globales Sección 1.1) ---
FONT_FAMILY = "Segoe UI"

FONT_PAGE_TITLE      = (FONT_FAMILY, 32, "bold")    # Título de página: 32px, bold, AZUL_OSCURO
FONT_SUBTITLE        = (FONT_FAMILY, 16, "normal")  # Subtítulo: 16px, regular, gris oscuro
FONT_BODY            = (FONT_FAMILY, 16, "normal")  # Texto general: 16px
FONT_BODY_BOLD       = (FONT_FAMILY, 16, "bold")    # Texto general enfático
FONT_TABLE_HEAD      = (FONT_FAMILY, 15, "bold")    # Cabecera de tabla: 15px, bold (evita desbordes)
FONT_TABLE_CELL      = (FONT_FAMILY, 15, "normal")  # Celdas de tabla: 15px, regular
FONT_TABLE_CELL_BOLD = (FONT_FAMILY, 15, "bold")    # Celdas destacadas
FONT_BUTTON          = (FONT_FAMILY, 16, "bold")    # Texto de botones: 16px, bold
FONT_BADGE           = (FONT_FAMILY, 15, "bold")    # Texto de badges/etiquetas: 15px, bold, blanco
FONT_CARD_TITLE      = (FONT_FAMILY, 20, "bold")    # Títulos de tarjetas: 20px, bold
FONT_STAT_NUM        = (FONT_FAMILY, 46, "bold")    # Número grande de tarjetas: 46px, bold

# Específicos para navegación
FONT_SIDEBAR_TIT     = (FONT_FAMILY, 16, "bold")
FONT_SIDEBAR_BTN     = (FONT_FAMILY, 15, "normal")
FONT_SIDEBAR_BTN_ACT = (FONT_FAMILY, 15, "bold")

# Fallbacks retrocompatibles
FONT_TITULO_PAGINA   = FONT_PAGE_TITLE
FONT_SUBTITULO       = FONT_SUBTITLE
FONT_CARD_TIT        = FONT_CARD_TITLE

# --- DIMENSIONES, BORDES Y RADIOS (Reglas Globales Sección 1.2 y 1.3) ---
SIDEBAR_WIDTH       = 312
WINDOW_DEFAULT_SIZE = "1408x768"
WINDOW_MIN_SIZE     = (1100, 650)

BORDER_WIDTH        = 2     # Bordes gruesos de 2px
BORDER_COLOR        = BORDE

RADIUS_CARD         = 12    # Radio de tarjetas y contenedores de tablas
RADIUS_INPUT        = 10    # Radio de inputs y botones
RADIUS_BUTTON       = 10    # Radio de botones
RADIUS_PILL         = 20    # Radio de píldoras grandes
RADIUS_BADGE        = 15    # Radio de badges píldora (alto 30 / 2 = 15)

# Alturas estándar de controles
BTN_HEIGHT_TOOL     = 44    # 44px en barras de herramientas
BTN_HEIGHT_TRAIN    = 56    # 56px solo para "Iniciar Entrenamiento"
INPUT_HEIGHT_TOOL   = 44    # Mismo alto que botones de barra
BADGE_HEIGHT_TABLE  = 30    # 30px en tablas
BADGE_HEIGHT_CHAT   = 36    # 36px en la tarjeta del chat
BADGE_MIN_WIDTH     = 110   # Ancho uniforme de 110px en tablas
