import os
from PIL import Image, ImageDraw

ICONS_DIR = r"C:\IA\bolivia-fraud-detector\assets\icons"
os.makedirs(ICONS_DIR, exist_ok=True)

def hex_to_rgba(hex_color, alpha=255):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4)) + (alpha,)

COLOR_WHITE = (255, 255, 255, 255)
COLOR_DARK_BLUE = hex_to_rgba("#0F1F4D")
COLOR_BLUE = hex_to_rgba("#1E3A8A")
COLOR_RED = hex_to_rgba("#DC2626")
COLOR_MUTED = hex_to_rgba("#64748B")

def draw_plus(path, color=COLOR_WHITE):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.line([(24, 12), (24, 36)], fill=color, width=4)
    d.line([(12, 24), (36, 24)], fill=color, width=4)
    img.save(path)

def draw_download(path, color=COLOR_WHITE):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Flecha abajo
    d.line([(24, 10), (24, 28)], fill=color, width=4)
    d.polygon([(16, 26), (32, 26), (24, 34)], fill=color)
    # Bandeja
    d.line([(10, 32), (10, 38), (38, 38), (38, 32)], fill=color, width=4)
    img.save(path)

def draw_upload(path, color=COLOR_WHITE):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Flecha arriba
    d.line([(24, 30), (24, 14)], fill=color, width=4)
    d.polygon([(16, 16), (32, 16), (24, 8)], fill=color)
    # Bandeja
    d.line([(10, 32), (10, 38), (38, 38), (38, 32)], fill=color, width=4)
    img.save(path)

def draw_eye(path, color=COLOR_BLUE):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.arc([(8, 14), (40, 34)], 0, 360, fill=color, width=3)
    d.ellipse([(20, 20), (28, 28)], fill=color)
    img.save(path)

def draw_trash(path, color=COLOR_RED):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Tapa
    d.line([(12, 16), (36, 16)], fill=color, width=3)
    d.line([(20, 12), (28, 12)], fill=color, width=3)
    # Cuerpo
    d.line([(15, 16), (17, 38), (31, 38), (33, 16)], fill=color, width=3)
    d.line([(21, 20), (21, 34)], fill=color, width=2)
    d.line([(27, 20), (27, 34)], fill=color, width=2)
    img.save(path)

def draw_edit(path, color=COLOR_BLUE):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(14, 34), (12, 36), (10, 38), (14, 38)], fill=color)
    d.line([(14, 34), (32, 16), (36, 20), (18, 38)], fill=color, width=3)
    d.line([(32, 16), (35, 13), (39, 17), (36, 20)], fill=color, width=3)
    img.save(path)

def draw_search(path, color=COLOR_MUTED):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([(10, 10), (28, 28)], outline=color, width=4)
    d.line([(25, 25), (38, 38)], fill=color, width=4)
    img.save(path)

def draw_play(path, color=COLOR_WHITE):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.polygon([(16, 12), (36, 24), (16, 36)], fill=color)
    img.save(path)

# Generar iconos nuevos
draw_plus(os.path.join(ICONS_DIR, "plus_white.png"), COLOR_WHITE)
draw_download(os.path.join(ICONS_DIR, "download_white.png"), COLOR_WHITE)
draw_upload(os.path.join(ICONS_DIR, "upload_white.png"), COLOR_WHITE)
draw_eye(os.path.join(ICONS_DIR, "eye_blue.png"), COLOR_DARK_BLUE)
draw_eye(os.path.join(ICONS_DIR, "eye_white.png"), COLOR_WHITE)
draw_trash(os.path.join(ICONS_DIR, "trash_red.png"), COLOR_RED)
draw_edit(os.path.join(ICONS_DIR, "edit_blue.png"), COLOR_DARK_BLUE)
draw_search(os.path.join(ICONS_DIR, "search_muted.png"), COLOR_MUTED)
draw_play(os.path.join(ICONS_DIR, "play_white.png"), COLOR_WHITE)

print("Iconos adicionales generados exitosamente.")
