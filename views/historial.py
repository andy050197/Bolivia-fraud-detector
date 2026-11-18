import customtkinter as ctk
from database.db import obtener_historial, eliminar_historial_item, limpiar_historial

COLOR_FRAUDE     = "#ef4444"
COLOR_SOSPECHOSO = "#f59e0b"
COLOR_LEGITIMO   = "#22c55e"

class HistorialView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="white")
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="Historial de Análisis - Registro de Consultas",
                     font=ctk.CTkFont(size=22, weight="bold"), text_color="#1e293b"
                     ).pack(anchor="w", padx=30, pady=(25, 2))
        ctk.CTkLabel(self, text="Consulta los mensajes evaluados previamente almacenados de forma anonimizada en SQLite",
                     font=ctk.CTkFont(size=13), text_color="#64748b"
                     ).pack(anchor="w", padx=30, pady=(0, 15))

        # Barra de filtros
        frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtros.pack(fill="x", padx=30, pady=(0, 10))

        self.entry_busqueda = ctk.CTkEntry(frame_filtros, placeholder_text="🔍 Buscar por palabra clave...",
                                            width=280, height=36)
        self.entry_busqueda.pack(side="left", padx=(0, 10))
        self.entry_busqueda.bind("<KeyRelease>", lambda e: self._cargar_datos())

        self.combo_cat = ctk.CTkComboBox(frame_filtros, values=["Todas las categorías", "fraude", "sospechoso", "legitimo"],
                                          width=180, height=36, command=lambda v: self._cargar_datos())
        self.combo_cat.pack(side="left", padx=(0, 10))

        ctk.CTkButton(frame_filtros, text="Limpiar Historial", width=140, height=36,
                      fg_color="white", text_color=COLOR_FRAUDE, border_width=1, border_color=COLOR_FRAUDE,
                      hover_color="#fef2f2", command=self._limpiar).pack(side="right")

        # Cabecera de tabla
        self._build_cabecera()

        # Tabla scrollable
        self.frame_tabla = ctk.CTkScrollableFrame(self, fg_color="white")
        self.frame_tabla.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self._cargar_datos()

    def _build_cabecera(self):
        cab = ctk.CTkFrame(self, fg_color="#f1f5f9", corner_radius=0)
        cab.pack(fill="x", padx=30)
        for texto, ancho in [("Fecha y Hora",120),("Mensaje Anonimizado",310),("Categoría",100),("Nivel de Riesgo",110),("Confianza",90),("Acciones",80)]:
            ctk.CTkLabel(cab, text=texto, font=ctk.CTkFont(size=12, weight="bold"),
                         text_color="#374151", width=ancho, anchor="w"
                         ).pack(side="left", padx=5, pady=8)

    def _cargar_datos(self):
        for w in self.frame_tabla.winfo_children():
            w.destroy()

        busqueda = self.entry_busqueda.get().strip()
        cat_sel = self.combo_cat.get()
        filtro = None if cat_sel == "Todas las categorías" else cat_sel

        filas = obtener_historial(filtro_categoria=filtro, busqueda=busqueda if busqueda else None)

        if not filas:
            ctk.CTkLabel(self.frame_tabla, text="No hay registros aún. Analiza mensajes en Chat Detector.",
                         text_color="#94a3b8", font=ctk.CTkFont(size=13)).pack(pady=40)
            return

        for fila in filas:
            id_, fecha, msg, cat, nivel, confianza = fila
            self._agregar_fila(id_, fecha, msg, cat, nivel, confianza)

    def _agregar_fila(self, id_, fecha, msg, cat, nivel, confianza):
        color_cat = {"fraude": COLOR_FRAUDE, "sospechoso": COLOR_SOSPECHOSO, "legitimo": COLOR_LEGITIMO}.get(cat, "#64748b")

        frame_fila = ctk.CTkFrame(self.frame_tabla, fg_color="white", border_width=0, corner_radius=0)
        frame_fila.pack(fill="x", pady=1)

        # Separador
        ctk.CTkFrame(frame_fila, fg_color="#f1f5f9", height=1).pack(fill="x")

        frame_contenido = ctk.CTkFrame(frame_fila, fg_color="white")
        frame_contenido.pack(fill="x")

        ctk.CTkLabel(frame_contenido, text=fecha, width=120, font=ctk.CTkFont(size=11),
                     text_color="#64748b", anchor="w").pack(side="left", padx=5, pady=6)
        ctk.CTkLabel(frame_contenido, text=msg, width=310, font=ctk.CTkFont(size=11),
                     text_color="#1e293b", anchor="w", wraplength=300).pack(side="left", padx=5)

        # Badge categoría
        badge = ctk.CTkFrame(frame_contenido, fg_color=color_cat, corner_radius=5, width=80, height=22)
        badge.pack(side="left", padx=5)
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text=cat.capitalize(), font=ctk.CTkFont(size=11, weight="bold"),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame_contenido, text=nivel, width=110, font=ctk.CTkFont(size=11),
                     text_color="#374151", anchor="w").pack(side="left", padx=5)
        ctk.CTkLabel(frame_contenido, text=f"{confianza}%", width=90, font=ctk.CTkFont(size=11),
                     text_color="#374151", anchor="w").pack(side="left", padx=5)

        # Botón eliminar
        ctk.CTkButton(frame_contenido, text="🗑", width=30, height=24,
                      fg_color="white", text_color="#ef4444", hover_color="#fef2f2",
                      command=lambda i=id_: self._eliminar(i)).pack(side="left", padx=5)

    def _eliminar(self, item_id):
        eliminar_historial_item(item_id)
        self._cargar_datos()

    def _limpiar(self):
        limpiar_historial()
        self._cargar_datos()

    def on_show(self):
        self._cargar_datos()
