"""
CAPA 1 - Interfaz grafica (BOCETO NO FUNCIONAL)

Maqueta visual de ThermoPC. Los botones no ejecutan calculos ni lectura
real del equipo: los valores mostrados son de ejemplo. Esta capa solo debe
contener codigo de interfaz; la logica vive en las capas 2 a 5.
"""

import tkinter as tk
from tkinter import ttk

# Paleta de colores
BG = "#eef5fb"
CARD = "#ffffff"
TEXT = "#17324d"
MUTED = "#536b80"
ACCENT = "#1677a8"
OK = "#2e7d32"


class ThermoPCBoceto:
    def __init__(self, root):
        self.root = root
        root.title("HeatBalance | Boceto de interfaz")
        root.geometry("1100x860")
        root.minsize(950, 760)
        root.configure(bg=BG)

        self._configurar_estilos()

        outer = self._crear_contenedor_scroll(root)
        outer.columnconfigure(0, weight=1)

        self._crear_encabezado(outer)
        self._crear_fila_superior(outer)
        self._crear_fila_resultados(outer)
        self._crear_grafica(outer)
        self._crear_historial(outer)
        self._crear_pie(outer)

    # ------------------------------------------------------- contenedor scroll
    def _crear_contenedor_scroll(self, root):
        """Crea una pagina desplazable y devuelve el frame donde va el contenido."""
        contenedor = ttk.Frame(root)
        contenedor.pack(fill="both", expand=True)

        self.lienzo_pagina = tk.Canvas(contenedor, bg=BG, highlightthickness=0)
        barra = ttk.Scrollbar(contenedor, orient="vertical",
                              command=self.lienzo_pagina.yview)
        self.lienzo_pagina.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lienzo_pagina.pack(side="left", fill="both", expand=True)

        contenido = ttk.Frame(self.lienzo_pagina, padding=18)
        ventana = self.lienzo_pagina.create_window((0, 0), window=contenido, anchor="nw")

        # Actualiza la region desplazable cuando cambia el contenido
        contenido.bind(
            "<Configure>",
            lambda e: self.lienzo_pagina.configure(
                scrollregion=self.lienzo_pagina.bbox("all")))
        # El contenido ocupa todo el ancho de la ventana
        self.lienzo_pagina.bind(
            "<Configure>",
            lambda e: self.lienzo_pagina.itemconfigure(ventana, width=e.width))
        # Rueda del mouse
        self.lienzo_pagina.bind_all(
            "<MouseWheel>",
            lambda e: self.lienzo_pagina.yview_scroll(int(-e.delta / 120), "units"))
        return contenido

    # ------------------------------------------------------------------ estilos
    def _configurar_estilos(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=CARD)
        s.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("Card.TLabel", background=CARD, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("Title.TLabel", font=("Segoe UI", 20, "bold"))
        s.configure("Subtitle.TLabel", foreground=MUTED)
        s.configure("CardTitle.TLabel", background=CARD, font=("Segoe UI", 11, "bold"))
        s.configure("Result.TLabel", background=CARD, font=("Segoe UI", 18, "bold"),
                    foreground=ACCENT)
        s.configure("Ok.TLabel", background=CARD, foreground=OK,
                    font=("Segoe UI", 10, "bold"))
        s.configure("Muted.TLabel", background=CARD, foreground=MUTED)
        s.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        s.configure("Treeview", font=("Consolas", 9), rowheight=24)
        s.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    # --------------------------------------------------------------- encabezado
    def _crear_encabezado(self, parent):
        ttk.Label(parent, text="HeatBalance", style="Title.TLabel").grid(
            row=0, column=0, sticky="w")
        ttk.Label(
            parent,
            text="Temperaturas de equilibrio de CPU y GPU "
                 "mediante Gauss-Seidel",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(0, 12))

    # ---------------------------------------------- fila superior (2 tarjetas)
    def _crear_fila_superior(self, parent):
        fila = ttk.Frame(parent)
        fila.grid(row=2, column=0, sticky="ew")
        fila.columnconfigure(0, weight=1)
        fila.columnconfigure(1, weight=1)

        # --- Datos del equipo
        datos = ttk.Frame(fila, style="Card.TFrame", padding=14)
        datos.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        datos.columnconfigure(1, weight=1)
        ttk.Label(datos, text="Datos del equipo", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Button(datos, text="Leer datos del equipo").grid(
            row=1, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        campos = [("Uso de CPU (%)", "70"), ("Uso de GPU (%)", "90"),
                  ("Temperatura ambiente (°C)", "25")]
        for i, (etiqueta, valor) in enumerate(campos, start=2):
            ttk.Label(datos, text=etiqueta, style="Card.TLabel").grid(
                row=i, column=0, sticky="w", pady=5)
            ent = ttk.Entry(datos, width=12)
            ent.insert(0, valor)
            ent.grid(row=i, column=1, sticky="e", pady=5)

        ttk.Label(datos, text="Estado de lectura: ✔ datos leidos (ejemplo)",
                  style="Ok.TLabel").grid(row=5, column=0, columnspan=2,
                                          sticky="w", pady=(8, 0))
        ttk.Label(datos, text="Si un dato no esta disponible, escribelo manualmente.",
                  style="Muted.TLabel").grid(row=6, column=0, columnspan=2, sticky="w")

        # --- Parametros del metodo
        params = ttk.Frame(fila, style="Card.TFrame", padding=14)
        params.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        params.columnconfigure(1, weight=1)
        ttk.Label(params, text="Parametros del metodo", style="CardTitle.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(params, text="Tolerancia (%)", style="Card.TLabel").grid(
            row=1, column=0, sticky="w", pady=5)
        tol = ttk.Entry(params, width=12)
        tol.insert(0, "0.01")
        tol.grid(row=1, column=1, sticky="e", pady=5)

        ttk.Label(params, text="Maximo de iteraciones", style="Card.TLabel").grid(
            row=2, column=0, sticky="w", pady=5)
        it = ttk.Entry(params, width=12)
        it.insert(0, "100")
        it.grid(row=2, column=1, sticky="e", pady=5)

        botones = ttk.Frame(params, style="Card.TFrame")
        botones.grid(row=3, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Button(botones, text="Calcular equilibrio").pack(side="left")
        ttk.Button(botones, text="Restablecer").pack(side="left", padx=(8, 0))

    # ------------------------- fila de resultados (datos leidos vs estimados)
    def _crear_fila_resultados(self, parent):
        fila = ttk.Frame(parent)
        fila.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        fila.columnconfigure(0, weight=1)
        fila.columnconfigure(1, weight=1)

        leidos = ttk.Frame(fila, style="Card.TFrame", padding=14)
        leidos.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        ttk.Label(leidos, text="Datos leidos", style="CardTitle.TLabel").pack(anchor="w")
        for linea in ("Uso de CPU: 70 %", "Uso de GPU: 90 %", "Ambiente: 25 °C"):
            ttk.Label(leidos, text=linea, style="Card.TLabel").pack(anchor="w", pady=3)

        estimados = ttk.Frame(fila, style="Card.TFrame", padding=14)
        estimados.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        ttk.Label(estimados, text="Temperaturas estimadas",
                  style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(estimados, text="CPU: 60.38 °C", style="Result.TLabel").pack(
            anchor="w", pady=(6, 0))
        ttk.Label(estimados, text="GPU: 73.54 °C", style="Result.TLabel").pack(anchor="w")
        ttk.Label(estimados, text="Iteraciones: 4   |   Tiempo: 0.002 s",
                  style="Card.TLabel").pack(anchor="w", pady=(6, 0))
        ttk.Label(estimados, text="✔ Convergencia alcanzada", style="Ok.TLabel").pack(
            anchor="w")

    # ------------------------------------------------------------------ grafica
    def _crear_grafica(self, parent):
        marco = ttk.Frame(parent, style="Card.TFrame", padding=10)
        marco.grid(row=4, column=0, sticky="nsew", pady=(12, 0))

        cab = ttk.Frame(marco, style="Card.TFrame")
        cab.pack(fill="x")
        ttk.Label(cab, text="Convergencia: error vs. iteraciones",
                  style="CardTitle.TLabel").pack(side="left")
        ttk.Button(cab, text="Guardar grafica").pack(side="right")

        # Marcador de posicion (en la version final aqui va la grafica real)
        lienzo = tk.Canvas(marco, height=190, bg="#f7fafc", highlightthickness=1,
                           highlightbackground="#c9d6e2")
        lienzo.pack(fill="both", expand=True, pady=(8, 0))
        lienzo.bind("<Configure>", lambda e: self._dibujar_placeholder(lienzo))

    @staticmethod
    def _dibujar_placeholder(c):
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        c.create_line(50, 15, 50, h - 30, fill="#8aa0b3")          # eje Y
        c.create_line(50, h - 30, w - 20, h - 30, fill="#8aa0b3")  # eje X
        c.create_text(14, h // 2, text="Error (%)", angle=90, fill=MUTED)
        c.create_text(w // 2, h - 12, text="Iteracion", fill=MUTED)
        # curva decreciente de ejemplo
        pts = []
        for i in range(5):
            x = 50 + i * (w - 90) / 4
            y = (h - 40) - (h - 70) * (0.5 ** (i * 1.4))
            pts += [x, y]
        c.create_line(*pts, fill=ACCENT, width=2, smooth=True)
        c.create_text(w // 2, h // 2 - 10, text="[ Aqui va la grafica de convergencia ]",
                      fill="#a3b4c4", font=("Segoe UI", 11, "italic"))

    # ---------------------------------------------------------------- historial
    def _crear_historial(self, parent):
        marco = ttk.Frame(parent, style="Card.TFrame", padding=12)
        marco.grid(row=5, column=0, sticky="nsew", pady=(12, 0))

        cab = ttk.Frame(marco, style="Card.TFrame")
        cab.pack(fill="x", pady=(0, 8))
        ttk.Label(cab, text="Historial de iteraciones",
                  style="CardTitle.TLabel").pack(side="left")
        ttk.Button(cab, text="Exportar CSV / TXT").pack(side="right")

        cols = ("iter", "cpu", "gpu", "err")
        tabla = ttk.Treeview(marco, columns=cols, show="headings", height=10)
        for col, texto, ancho in (("iter", "Iteracion", 90), ("cpu", "CPU (°C)", 130),
                                  ("gpu", "GPU (°C)", 130), ("err", "Error maximo (%)", 160)):
            tabla.heading(col, text=texto)
            tabla.column(col, width=ancho, anchor="center")
        for fila in ((1, "56.5000", "73.1500", "65.82365"),
                     (2, "60.3520", "73.5352", "6.38256"),
                     (3, "60.3828", "73.5383", "0.05103"),
                     (4, "60.3831", "73.5383", "0.00041")):
            tabla.insert("", "end", values=fila)
        sb = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=sb.set)
        tabla.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    # ---------------------------------------------------------------------- pie
    def _crear_pie(self, parent):
        ttk.Label(
            parent,
            text="Nota del modelo: coeficientes ilustrativos, no calibrados con "
                 "mediciones reales del equipo.",
            style="Subtitle.TLabel", wraplength=1000,
        ).grid(row=6, column=0, sticky="w", pady=(10, 0))


if __name__ == "__main__":
    ventana = tk.Tk()
    ThermoPCBoceto(ventana)
    ventana.mainloop()