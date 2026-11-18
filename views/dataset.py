import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from database.db import obtener_dataset, agregar_mensaje_dataset, eliminar_mensaje_dataset, cargar_csv_a_dataset

COLOR_FRAUDE     = "#ef4444"
COLOR_SOSPECHOSO = "#f59e0b"
COLOR_LEGITIMO   = "#22c55e"

class DatasetView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Dataset de Mensajes - Corpus de Entrenamiento",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#1e293b"
                     ).pack(anchor="w", padx=30, pady=(25, 2))

        # Botones acción
        frame_acciones = ctk.CTkFrame(self, fg_color="transparent")
        frame_acciones.pack(anchor="w", padx=30, pady=(0, 15))
        ctk.CTkButton(frame_acciones, text="+ Nuevo Mensaje", width=150, height=36,
                      fg_color="#1e40af", command=self._nuevo_mensaje).pack(side="left", padx=5)
        ctk.CTkButton(frame_acciones, text="⬇ Importar CSV", width=140, height=36,
                      fg_color="white", text_color="#374151", border_width=1, border_color="#d1d5db",
                      hover_color="#f3f4f6", command=self._importar_csv).pack(side="left", padx=5)
        ctk.CTkButton(frame_acciones, text="⬆ Exportar CSV", width=140, height=36,
                      fg_color="white", text_color="#374151", border_width=1, border_color="#d1d5db",
                      hover_color="#f3f4f6", command=self._exportar_csv).pack(side="left", padx=5)

        # Filtros
        frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtros.pack(fill="x", padx=30, pady=(0, 10))
        self.entry_busqueda = ctk.CTkEntry(frame_filtros, placeholder_text="🔍 Buscar...", width=300, height=36)
        self.entry_busqueda.pack(side="left", padx=(0,10))
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self._cargar_datos())
        self.combo_cat = ctk.CTkComboBox(frame_filtros, values=["Todas las categorías","fraude","sospechoso","legitimo"],
                                          width=180, height=36, command=lambda v: self._cargar_datos())
        self.combo_cat.pack(side="left")

        # Stats rápidas
        self.frame_stats = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_stats.pack(fill="x", padx=30, pady=(0, 5))

        # Cabecera tabla
        cab = ctk.CTkFrame(self, fg_color="#f1f5f9", corner_radius=0)
        cab.pack(fill="x", padx=30)
        for texto, ancho in [("ID",50),("Texto del mensaje",350),("Categoría",100),("Origen",120),("Subcategoría",120),("",70)]:
            ctk.CTkLabel(cab, text=texto, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#374151", width=ancho, anchor="w").pack(side="left", padx=5, pady=8)

        self.frame_tabla = ctk.CTkScrollableFrame(self, fg_color="white")
        self.frame_tabla.pack(fill="both", expand=True, padx=30, pady=(0,20))
        self._cargar_datos()

    def _cargar_datos(self):
        for w in self.frame_tabla.winfo_children():
            w.destroy()
        for w in self.frame_stats.winfo_children():
            w.destroy()

        filas = obtener_dataset()
        busqueda = self.entry_busqueda.get().strip().lower()
        cat_sel  = self.combo_cat.get()

        if cat_sel != "Todas las categorías":
            filas = [f for f in filas if f[2] == cat_sel]
        if busqueda:
            filas = [f for f in filas if busqueda in f[1].lower()]

        # Stats
        total = len(filas)
        fraudes   = sum(1 for f in filas if f[2]=="fraude")
        sosp      = sum(1 for f in filas if f[2]=="sospechoso")
        legit     = sum(1 for f in filas if f[2]=="legitimo")
        for texto, color in [(f"Total Registros: {total}","#374151"),
                             (f"Fraude: {fraudes}", COLOR_FRAUDE),
                             (f"Sospechoso: {sosp}", COLOR_SOSPECHOSO),
                             (f"Legítimo: {legit}", COLOR_LEGITIMO)]:
            ctk.CTkLabel(self.frame_stats, text=texto, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color=color).pack(side="left", padx=15)

        for fila in filas:
            self._agregar_fila(*fila)

    def _agregar_fila(self, id_, mensaje, cat, origen, subcat):
        color_cat = {"fraude": COLOR_FRAUDE, "sospechoso": COLOR_SOSPECHOSO, "legitimo": COLOR_LEGITIMO}.get(cat, "#64748b")
        frame_fila = ctk.CTkFrame(self.frame_tabla, fg_color="white")
        frame_fila.pack(fill="x", pady=1)
        ctk.CTkFrame(frame_fila, fg_color="#f1f5f9", height=1).pack(fill="x")
        f = ctk.CTkFrame(frame_fila, fg_color="white")
        f.pack(fill="x")

        ctk.CTkLabel(f, text=str(id_), width=50, font=ctk.CTkFont(size=11), text_color="#94a3b8", anchor="w").pack(side="left", padx=5, pady=5)
        ctk.CTkLabel(f, text=mensaje[:60]+("..." if len(mensaje)>60 else ""), width=350,
                     font=ctk.CTkFont(size=11), text_color="#1e293b", anchor="w").pack(side="left", padx=5)

        badge = ctk.CTkFrame(f, fg_color=color_cat, corner_radius=5, width=80, height=22)
        badge.pack(side="left", padx=5)
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=cat.capitalize(), font=ctk.CTkFont(size=10, weight="bold"), text_color="white").place(relx=0.5,rely=0.5,anchor="center")

        ctk.CTkLabel(f, text=origen or "-", width=120, font=ctk.CTkFont(size=11), text_color="#64748b", anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(f, text=subcat or "-", width=120, font=ctk.CTkFont(size=11), text_color="#64748b", anchor="w").pack(side="left", padx=5)
        ctk.CTkButton(f, text="🗑", width=30, height=24, fg_color="white", text_color=COLOR_FRAUDE,
                      hover_color="#fef2f2", command=lambda i=id_: self._eliminar(i)).pack(side="left", padx=5)

    def _nuevo_mensaje(self):
        ventana = ctk.CTkToplevel(self)
        ventana.title("Agregar Mensaje al Dataset")
        ventana.geometry("500x350")
        ventana.grab_set()

        ctk.CTkLabel(ventana, text="Texto del mensaje:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(20,5))
        txt = ctk.CTkTextbox(ventana, height=100)
        txt.pack(fill="x", padx=20)

        ctk.CTkLabel(ventana, text="Categoría:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10,5))
        combo = ctk.CTkComboBox(ventana, values=["fraude","sospechoso","legitimo"])
        combo.pack(anchor="w", padx=20)

        ctk.CTkLabel(ventana, text="Origen:", font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=20, pady=(10,5))
        entry_origen = ctk.CTkEntry(ventana, placeholder_text="WhatsApp, SMS, Facebook...")
        entry_origen.pack(anchor="w", padx=20)

        def guardar():
            mensaje = txt.get("0.0","end").strip()
            cat     = combo.get()
            origen  = entry_origen.get().strip() or "Manual"
            if not mensaje:
                return
            agregar_mensaje_dataset(mensaje, cat, origen)
            ventana.destroy()
            self._cargar_datos()

        ctk.CTkButton(ventana, text="Guardar", fg_color="#1e40af", command=guardar).pack(pady=15)

    def _eliminar(self, item_id):
        eliminar_mensaje_dataset(item_id)
        self._cargar_datos()

    def _importar_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
        if filepath:
            n = cargar_csv_a_dataset(filepath)
            messagebox.showinfo("Importación exitosa", f"Se importaron {n} mensajes.")
            self._cargar_datos()

    def _exportar_csv(self):
        import csv
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if filepath:
            filas = obtener_dataset()
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["id","mensaje","categoria","origen","subcategoria"])
                writer.writerows(filas)
            messagebox.showinfo("Exportación exitosa", f"Dataset exportado correctamente.")

    def on_show(self):
        self._cargar_datos()
