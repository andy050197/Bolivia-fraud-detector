import os
from PIL import Image, ImageDraw

ICONS_DIR = r"C:\IA\bolivia-fraud-detector\assets\icons"
os.makedirs(ICONS_DIR, exist_ok=True)

def hex_to_rgba(hex_color, alpha=255):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)

COLOR_WHITE = (255, 255, 255, 255)
COLOR_DARK_BLUE = hex_to_rgba("#0F1F4D")

def draw_lucide_shield(path, size=80, stroke_color=COLOR_WHITE):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Escudo outline
    pad = 8
    w, h = size - pad * 2, size - pad * 2
    points = [
        (size/2, pad),
        (size - pad, pad + h * 0.18),
        (size - pad, pad + h * 0.58),
        (size/2, size - pad),
        (pad, pad + h * 0.58),
        (pad, pad + h * 0.18)
    ]
    d.polygon(points, outline=stroke_color, fill=(0, 0, 0, 0), width=4)
    img.save(path)

def draw_message_circle(path, color):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([(8, 8), (40, 36)], outline=color, width=3)
    d.polygon([(12, 32), (10, 42), (22, 36)], fill=color)
    img.save(path)

def draw_history(path, color):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.arc([(8, 8), (40, 40)], 45, 360, fill=color, width=3)
    # Manecillas
    d.line([(24, 15), (24, 24), (32, 24)], fill=color, width=3)
    # Flecha
    d.polygon([(36, 12), (44, 18), (34, 22)], fill=color)
    img.save(path)

def draw_layout_grid(path, color):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r = 3
    d.rounded_rectangle([(8, 8), (21, 21)], radius=r, outline=color, width=3)
    d.rounded_rectangle([(27, 8), (40, 21)], radius=r, outline=color, width=3)
    d.rounded_rectangle([(8, 27), (21, 40)], radius=r, outline=color, width=3)
    d.rounded_rectangle([(27, 27), (40, 40)], radius=r, outline=color, width=3)
    img.save(path)

def draw_database(path, color):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([(10, 8), (38, 18)], outline=color, width=3)
    d.line([(10, 13), (10, 35)], fill=color, width=3)
    d.line([(38, 13), (38, 35)], fill=color, width=3)
    d.arc([(10, 17), (38, 27)], 0, 180, fill=color, width=3)
    d.arc([(10, 25), (38, 35)], 0, 180, fill=color, width=3)
    img.save(path)

def draw_users(path, color):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Cabeza central
    d.ellipse([(18, 8), (30, 20)], outline=color, width=3)
    # Torso central
    d.arc([(12, 24), (36, 42)], 180, 360, fill=color, width=3)
    d.line([(12, 33), (12, 40)], fill=color, width=3)
    d.line([(36, 33), (36, 40)], fill=color, width=3)
    img.save(path)

def draw_avatar_shield(path):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([(4, 4), (60, 60)], fill=(240, 243, 246, 255), outline=(203, 213, 225, 255), width=2)
    # Escudo interior negro
    points = [(32, 16), (46, 22), (46, 38), (32, 48), (18, 38), (18, 22)]
    d.polygon(points, fill=(31, 41, 55, 255))
    img.save(path)

# Generar iconos
draw_lucide_shield(os.path.join(ICONS_DIR, "shield_main.png"), size=60)
draw_avatar_shield(os.path.join(ICONS_DIR, "avatar_shield.png"))

# Iconos blancos (inactivos) y azul oscuro (activos)
tipos = [
    ("message-circle", draw_message_circle),
    ("history", draw_history),
    ("layout-grid", draw_layout_grid),
    ("database", draw_database),
    ("users", draw_users)
]

for name, func in tipos:
    func(os.path.join(ICONS_DIR, f"{name}_white.png"), COLOR_WHITE)
    func(os.path.join(ICONS_DIR, f"{name}_active.png"), COLOR_DARK_BLUE)

print("Iconos Lucide generados con éxito.")
