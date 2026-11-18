"""Consulta del historial usando exclusivamente la API de database.db."""
import tkinter as tk
import logging
import sqlite3
from tkinter import messagebox, ttk

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from database.db import obtener_historial, eliminar_historial_item, limpiar_historial

COLOR_FRAUDE = "#ef4444"
COLOR_SOSPECHOSO = "#f59e0b"
COLOR_LEGITIMO = "#22c55e"
CATEGORIAS = {"Todas las categorías": None, "Fraude": "fraude",
              "Sospechoso": "sospechoso", "Legítimo": "legitimo"}
NOMBRES = {"fraude": "Fraude", "sospechoso": "Sospechoso", "legitimo": "Legítimo"}
logger = logging.getLogger(__name__)


def _porcentaje(valor):
    """SQLite ya entrega la confianza en escala 0–100."""
    try:
        numero = float(valor)
        return f"{numero:.1f}%" if 0 <= numero <= 100 else "No disponible"
    except (ValueError, TypeError):
        return "No disponible"


class SelectorCategoria(ctk.CTkComboBox):
    """Mantiene el menú de CTk y dibuja el chevrón a la escala del control."""
    def _draw(self, no_color_updates=False):
        super()._draw(no_color_updates)
        lienzo = self._canvas
        lienzo.itemconfig("dropdown_arrow", state="hidden")
        lienzo.itemconfig("border_parts_right", fill=self._apply_appearance_mode(self._border_color),
                             outline=self._apply_appearance_mode(self._border_color))
        lienzo.delete("chevron")
        escala = self._apply_widget_scaling
        x = escala(self._current_width - self._current_height / 2)
        y = escala(self._current_height / 2)
        lienzo.create_line(x-escala(4), y-escala(2), x, y+escala(2), x+escala(4), y-escala(2),
                           width=escala(1.7), fill="#172536", capstyle="round", joinstyle="round",
                           tags=("chevron", "right_parts"))

    def _on_leave(self, event=None):
        super()._on_leave(event)
        self._draw()


def _iconos_acciones(master, tamano):
    # Dibujar a mayor resolución suaviza los contornos incluso en tamaños pequeños.
    imagenes = []
    for nombre in ("ojo", "papelera"):
        imagen = Image.new("RGBA", (96, 96))
        trazo = ImageDraw.Draw(imagen)
        if nombre == "ojo":
            color = "#17345a"
            trazo.line([(5,48),(14,36),(26,26),(38,21),(48,20),(58,21),(70,26),
                        (82,36),(91,48),(82,60),(70,70),(58,75),(48,76),(38,75),
                        (26,70),(14,60),(5,48)], fill=color, width=7, joint="curve")
            trazo.ellipse((35,35,61,61), outline=color, width=7)
        else:
            color = "#a51c25"
            trazo.rounded_rectangle((24,28,72,87), radius=6, outline=color, width=7)
            trazo.line((13,25,83,25), fill=color, width=7)
            trazo.rounded_rectangle((36,10,60,26), radius=4, outline=color, width=6)
            for x in (40,56):
                trazo.line((x,39,x,73), fill=color, width=6)
        imagenes.append(ImageTk.PhotoImage(imagen.resize((tamano, tamano), Image.Resampling.LANCZOS), master=master))
    return imagenes


class HistorialView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#eef3f8")
        self._pendiente = None
        self._filas = {}
        self._detalle = None
        self._build_ui()
        self._cargar_datos()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        ctk.CTkLabel(self, text="Historial de Análisis - Registro de Consultas",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#1e293b",
                     anchor="w").grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 4))
        ctk.CTkLabel(self, text="Consulta los mensajes evaluados y almacenados de forma anonimizada.",
                     text_color="#64748b", anchor="w").grid(row=1, column=0, sticky="ew", padx=24)
        filtros = ctk.CTkFrame(self, fg_color="transparent")
        filtros.grid(row=2, column=0, sticky="ew", padx=24, pady=16)
        filtros.grid_columnconfigure(0, weight=1)
        self.entry_busqueda = ctk.CTkEntry(filtros, placeholder_text="Buscar por palabra clave...", height=36)
        self.entry_busqueda.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_busqueda.bind("<KeyRelease>", self._programar_busqueda)
        self.entry_busqueda.bind("<Return>", lambda event: self._cargar_datos())
        self.combo_cat = SelectorCategoria(filtros, fg_color="#f9f9fa", button_color="#f9f9fa", values=list(CATEGORIAS), state="readonly",
                                       width=180, height=36, command=lambda value: self._cargar_datos())
        self.combo_cat.set("Todas las categorías")
        self.combo_cat.grid(row=0, column=1)
        ctk.CTkButton(filtros, text="Restablecer", width=110, height=36,
                       command=self._restablecer).grid(row=1, column=0, sticky="w", pady=(10, 0))
        ctk.CTkButton(filtros, text="Actualizar", width=110, height=36,
                       command=self._cargar_datos).grid(row=1, column=1, sticky="e", pady=(10, 0))

        self.btn_limpiar = ctk.CTkButton(filtros, text="Limpiar historial", width=130,
            fg_color="white", border_width=1, border_color="#b91c1c", text_color="#b91c1c",
            hover_color="#fee2e2", command=self._limpiar)
        self.btn_limpiar.grid(row=0, column=3, sticky="e")
        filtros.grid_columnconfigure(0, weight=0)
        filtros.grid_columnconfigure(2, weight=1)
        self.entry_busqueda.configure(width=235)
        self.canvas = tk.Canvas(self, bg="#eef3f8", highlightthickness=0)
        self.canvas.grid(row=3, column=0, sticky="nsew", padx=24)
        self.scroll = ttk.Scrollbar(self, command=self.canvas.yview)
        self.scroll.grid(row=3, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self._scroll)
        self.tabla = tk.Frame(self.canvas, bg="#aab4c2")
        ventana = self.canvas.create_window(0, 0, anchor="nw", window=self.tabla)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(ventana, width=e.width))
        self.tabla.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.seleccion = None
        self._iconos = {}
        self.celdas = {}
        self.canvas.bind("<MouseWheel>", self._rueda)
        for col, (titulo, peso) in enumerate(zip(
                ("Fecha y hora", "Mensaje anonimizado", "Categoría", "Nivel de riesgo", "Confianza", "Acciones"),
                (16, 30, 16, 13, 13, 12))):
            self.tabla.grid_columnconfigure(col, weight=peso, uniform="col")
            self._celda(0, col, titulo, encabezado=True)
        self.lbl_estado = ctk.CTkLabel(self, text="", text_color="#64748b", anchor="w", wraplength=620)
        self.lbl_estado.grid(row=4, column=0, sticky="ew", padx=24, pady=8)
    def _scroll(self, inicio, fin):
        self.scroll.set(inicio, fin)
        if float(inicio) <= 0 and float(fin) >= 1:
            self.scroll.grid_remove()
        else:
            self.scroll.grid()

    def _rueda(self, evento):
        if self.scroll.winfo_ismapped():
            direccion = -1 if getattr(evento, "num", None) == 4 or evento.delta > 0 else 1
            self.canvas.yview_scroll(direccion * 3, "units")
        return "break"

    def _celda(self, fila, col, texto, clave=None, color=None, encabezado=False):
        fondo = "#e4eaf0" if encabezado else "#f3f7fb"
        celda = tk.Frame(self.tabla, bg=fondo)
        celda.grid(row=fila, column=col, sticky="nsew", padx=(1, 0), pady=(1, 0))
        if col == 5 and not encabezado:
            tamano = round(self._apply_widget_scaling(19))
            if tamano not in self._iconos:
                self._iconos[tamano] = _iconos_acciones(self, tamano)
            celda.grid_anchor("center")
            for i, accion in enumerate((self._ver_detalles, self._eliminar)):
                tk.Button(celda, image=self._iconos[tamano][i], relief="flat", bg=fondo,
                          activebackground="#dbeafe", borderwidth=0, cursor="hand2",
                          command=lambda fn=accion: (self._seleccionar(clave), fn())).grid(
                              row=0, column=i, padx=round(self._apply_widget_scaling(3)))
        else:
            etiqueta = tk.Label(celda, text=texto, font=("Segoe UI", -round(self._apply_widget_scaling(17)), "bold" if encabezado else "normal"),
                                fg="white" if color else "#111e32", bg=color or fondo, justify="left",
                                anchor="w", wraplength=90, padx=0, pady=0)
            etiqueta.pack(anchor="w", expand=True, fill="x" if not color else "none", padx=5, pady=9)
            celda.bind("<Configure>", lambda e: etiqueta.configure(wraplength=max(20,e.width-10)))
        for widget in (celda, *celda.winfo_children()):
            for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                widget.bind(evento, self._rueda)
            if clave and not isinstance(widget, tk.Button):
                widget.bind("<Button-1>", lambda e: self._seleccionar(clave))
                widget.bind("<Double-1>", lambda e: (self._seleccionar(clave), self._ver_detalles()))
        if clave:
            self.celdas.setdefault(clave, []).append(celda)

    def _seleccionar(self, clave):
        for anterior, fondo in ((self.seleccion, "#f3f7fb"), (clave, "#dbeafe")):
            for celda in self.celdas.get(anterior, []):
                celda.configure(bg=fondo)
                for hijo in celda.winfo_children():
                    if hijo.cget("bg") in ("#f3f7fb", "#dbeafe"):
                        hijo.configure(bg=fondo)
        self.seleccion = clave

    def _cancelar_busqueda(self):
        if self._pendiente is not None:
            self.after_cancel(self._pendiente)
            self._pendiente = None

    def _programar_busqueda(self, event=None):
        self._cancelar_busqueda()
        self._pendiente = self.after(250, self._cargar_datos)

    def _restablecer(self):
        self.entry_busqueda.delete(0, "end")
        self.combo_cat.set("Todas las categorías")
        self._cargar_datos()

    def _cargar_datos(self):
        self._cancelar_busqueda()
        busqueda = self.entry_busqueda.get().strip()
        categoria = CATEGORIAS[self.combo_cat.get()]
        seleccion = (self.seleccion,) if self.seleccion else ()
        try:
            filas = obtener_historial(filtro_categoria=categoria, busqueda=busqueda or None)
        except sqlite3.Error:
            logger.exception("No se pudo consultar el historial")
            self._vaciar_tabla()
            self.btn_limpiar.configure(state="disabled")
            self.lbl_estado.configure(text="No se pudo consultar el historial. Pulsa Actualizar para reintentar.", text_color="#b91c1c")
            return
        self._vaciar_tabla()
        for fila in filas:
            id_, fecha, mensaje, cat, riesgo, confianza = fila
            clave = str(id_)
            self._filas[clave] = fila
            valores = (fecha.replace(" ", "\n", 1), mensaje, NOMBRES.get(cat, cat), riesgo, _porcentaje(confianza), "")
            colores = {"fraude": "#b72e34", "sospechoso": "#956612", "legitimo": "#338348"}
            for col, valor in enumerate(valores):
                self._celda(len(self._filas), col, valor, clave, colores.get(cat) if col == 2 else None)
        if seleccion and seleccion[0] in self._filas:
            self._seleccionar(seleccion[0])
        # Una consulta filtrada vacía no implica que el historial completo esté vacío.
        self.btn_limpiar.configure(state="normal")
        texto = (f"{len(filas)} registro(s). Selecciona uno para ver sus detalles."
                 if filas else "No hay coincidencias con estos filtros." if busqueda or categoria
                 else "Aún no hay registros. Analiza un mensaje en Chat Detector.")
        self.lbl_estado.configure(text=texto, text_color="#64748b")

    def _vaciar_tabla(self):
        for fila in self.celdas.values():
            for celda in fila:
                celda.destroy()
        self.celdas.clear()
        self._filas.clear()
        self.seleccion = None

    def _ver_detalles(self):
        seleccion = (self.seleccion,) if self.seleccion else ()
        if not seleccion or seleccion[0] not in self._filas:
            return
        if self._detalle is not None and self._detalle.winfo_exists():
            self._detalle.destroy()
        id_, fecha, mensaje, cat, riesgo, confianza = self._filas[seleccion[0]]
        ventana = self._detalle = ctk.CTkToplevel(self)
        ventana.title(f"Detalle del análisis #{id_}")
        ventana.geometry("580x460")
        ventana.minsize(440, 360)
        ventana.transient(self.winfo_toplevel())
        ventana.grid_columnconfigure(0, weight=1)
        ventana.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(ventana, text=f"Análisis #{id_} - {fecha}", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        ctk.CTkLabel(ventana, text=f"{NOMBRES.get(cat, cat)}  |  Riesgo: {riesgo}  |  Confianza: {_porcentaje(confianza)}").grid(row=1, column=0, padx=20, sticky="w")
        contenido = ctk.CTkTextbox(ventana, wrap="word")
        contenido.grid(row=2, column=0, padx=20, pady=14, sticky="nsew")
        contenido.insert("1.0", mensaje)
        contenido.configure(state="disabled")
        ctk.CTkLabel(ventana, text="Se muestra solo el texto guardado: anonimizado y limitado a 80 caracteres\n(más puntos suspensivos). El mensaje original no se conserva.",
                     justify="left", wraplength=500, text_color="#64748b").grid(row=3, column=0, padx=20, sticky="w")
        ctk.CTkButton(ventana, text="Cerrar", command=ventana.destroy).grid(row=4, column=0, padx=20, pady=16, sticky="e")
        ventana.bind("<Escape>", lambda event: ventana.destroy())

    def _eliminar(self):
        seleccion = (self.seleccion,) if self.seleccion else ()
        if not seleccion:
            return
        item_id = self._filas[seleccion[0]][0]
        if not messagebox.askyesno("Eliminar registro", f"¿Eliminar el análisis #{item_id}?\nEsta acción no se puede deshacer.", parent=self, default="no", icon="warning"):
            return
        try:
            eliminar_historial_item(item_id)
        except sqlite3.Error:
            logger.exception("No se pudo eliminar el análisis")
            messagebox.showerror("Error", "No se pudo eliminar el registro. Intenta nuevamente.", parent=self)
            return
        self._cerrar_detalle()
        self._cargar_datos()

    def _limpiar(self):
        if not messagebox.askyesno("Limpiar todo el historial", "¿Eliminar TODOS los análisis, incluidos los ocultos por los filtros?\nEsta acción no se puede deshacer.", parent=self, default="no", icon="warning"):
            return
        try:
            limpiar_historial()
        except sqlite3.Error:
            logger.exception("No se pudo limpiar el historial")
            messagebox.showerror("Error", "No se pudo limpiar el historial. Intenta nuevamente.", parent=self)
            return
        self._cerrar_detalle()
        self._cargar_datos()

    def _cerrar_detalle(self):
        if self._detalle is not None and self._detalle.winfo_exists():
            self._detalle.destroy()
        self._detalle = None

    def on_show(self):
        self._cargar_datos()

    def destroy(self):
        self._cancelar_busqueda()
        self._cerrar_detalle()
        super().destroy()
