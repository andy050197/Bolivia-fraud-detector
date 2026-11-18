import os
from PIL import Image, ImageDraw

ASSETS_DIR = r"C:\IA\bolivia-fraud-detector\assets"
os.makedirs(ASSETS_DIR, exist_ok=True)

def draw_shield(path):
    img = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Escudo exterior
    points = [(40, 6), (70, 16), (70, 48), (40, 74), (10, 48), (10, 16)]
    d.polygon(points, fill=(255, 255, 255, 230), outline=(220, 230, 242, 255), width=3)
    # Detalle interior
    inner = [(40, 14), (64, 22), (64, 46), (40, 66), (16, 46), (16, 22)]
    d.polygon(inner, fill=(30, 58, 138, 200))
    # Simbolo check o balanza
    d.line([(30, 40), (37, 48), (52, 32)], fill=(255, 255, 255, 255), width=4)
    img.save(path)

def draw_icon(path, kind, color=(203, 213, 225, 255)):
    img = Image.new("RGBA", (48, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if kind == "chat":
        # Burbuja de chat
        d.rounded_rectangle([(8, 10), (40, 32)], radius=6, outline=color, width=3)
        d.polygon([(14, 32), (14, 40), (22, 32)], fill=color)
    elif kind == "history":
        # Reloj
        d.ellipse([(8, 8), (40, 40)], outline=color, width=3)
        d.line([(24, 16), (24, 24), (32, 24)], fill=color, width=3)
    elif kind == "dashboard":
        # 4 cuadrados tipo grid
        d.rounded_rectangle([(8, 8), (20, 20)], radius=3, outline=color, width=2)
        d.rounded_rectangle([(28, 8), (40, 20)], radius=3, outline=color, width=2)
        d.rounded_rectangle([(8, 28), (20, 40)], radius=3, outline=color, width=2)
        d.rounded_rectangle([(28, 28), (40, 40)], radius=3, outline=color, width=2)
    elif kind == "dataset":
        # Cilindro / base de datos
        d.ellipse([(10, 8), (38, 18)], outline=color, width=3)
        d.line([(10, 13), (10, 34)], fill=color, width=3)
        d.line([(38, 13), (38, 34)], fill=color, width=3)
        d.arc([(10, 18), (38, 28)], 0, 180, fill=color, width=3)
        d.arc([(10, 28), (38, 38)], 0, 180, fill=color, width=3)
    elif kind == "training":
        # Engranaje / sliders
        d.line([(10, 14), (38, 14)], fill=color, width=3)
        d.rectangle([(16, 10), (22, 18)], fill=color)
        d.line([(10, 24), (38, 24)], fill=color, width=3)
        d.rectangle([(26, 20), (32, 28)], fill=color)
        d.line([(10, 34), (38, 34)], fill=color, width=3)
        d.rectangle([(14, 30), (20, 38)], fill=color)
    img.save(path)

draw_shield(os.path.join(ASSETS_DIR, "shield_logo.png"))
draw_icon(os.path.join(ASSETS_DIR, "nav_chat.png"), "chat")
draw_icon(os.path.join(ASSETS_DIR, "nav_history.png"), "history")
draw_icon(os.path.join(ASSETS_DIR, "nav_dashboard.png"), "dashboard")
draw_icon(os.path.join(ASSETS_DIR, "nav_dataset.png"), "dataset")
draw_icon(os.path.join(ASSETS_DIR, "nav_training.png"), "training")

# Versiones activas (azul marino/blancas)
active_color = (255, 255, 255, 255)
draw_icon(os.path.join(ASSETS_DIR, "nav_chat_active.png"), "chat", active_color)
draw_icon(os.path.join(ASSETS_DIR, "nav_history_active.png"), "history", active_color)
draw_icon(os.path.join(ASSETS_DIR, "nav_dashboard_active.png"), "dashboard", active_color)
draw_icon(os.path.join(ASSETS_DIR, "nav_dataset_active.png"), "dataset", active_color)
draw_icon(os.path.join(ASSETS_DIR, "nav_training_active.png"), "training", active_color)

print("Icons generated successfully.")
