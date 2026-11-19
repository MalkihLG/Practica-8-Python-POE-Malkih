
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from catalogo import CATALOGO, CATEGORIAS
from datos_locales import TiendaDatos, ROLES
from categorias_tienda import TARJETAS, GALERIA
BG = "#FFF9F7"
WHITE = "#FFFCFA"
CREAM = "#FFF6EF"
PINK = "#FFE0E8"
PALE_PINK = "#FFCCE3"
DEEP_PINK = "#C95F7B"
CHERRY = "#68403E"
ROSE = "#F7C7D9"
MINT = "#B9E3DD"
MINT_LIGHT = "#E8F5EE"
SKY = "#8DE2F9"
BLUE = "#E4F1FB"
LILAC = "#F0E7F4"
TEXT = "#503B3E"
MUTED = "#766269"
BORDER = "#EBD6D5"
SIDE = "#FFF4F1"
CARD_TINTS = ("#FBE6E8", "#E8F4EB", "#E3F1FD", "#F0E7F5")
CENT = Decimal("0.01")
TASA_IVA = Decimal("0.16")
ASSETS = Path(__file__).resolve().parent / "assets"


def pesos(n):
    return f"${Decimal(n).quantize(CENT, rounding=ROUND_HALF_UP):,.2f}"


def decimal_positivo(valor):
    try:
        n = Decimal(valor.strip().replace(",", "."))
        if not n.is_finite() or n <= 0:
            raise ValueError
        return n.quantize(CENT, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError, AttributeError):
        raise ValueError("escribe un precio válido mayor a cero.")


def cantidad_positiva(valor):
    try:
        n = int(valor.strip())
        if n <= 0:
            raise ValueError
        return n
    except (ValueError, AttributeError):
        raise ValueError("la cantidad debe ser un número entero mayor a cero.")



def texto_ticket(venta):
    lineas = ["=" * 54,
              "                       TIENDA",
              "                 Pastelería y postres",
              "=" * 54, f"Ticket: {venta['folio']}", f"Fecha: {venta['fecha']}",
              f"Cliente: {venta['cliente']}", f"Le atendió: {venta['vendedor']}",
              "-" * 54, f"{'PRODUCTO':23} {'CANT.':>5} {'P.U.':>9} {'IMP.':>9}", "-" * 54]
    for d in venta["detalle"]:
        lineas.append(f"{d['nombre'][:23]:23} {d['cantidad']:>5} {pesos(d['precio']):>9} {pesos(d['importe']):>9}")
    lineas += ["-" * 54, f"{'SUBTOTAL:':>43} {pesos(venta['subtotal']):>10}",
               f"{'IVA (16 %):':>43} {pesos(venta['iva']):>10}",
               f"{'TOTAL:':>43} {pesos(venta['total']):>10}",
               "=" * 54, "         ¡Gracias por su compra , que tengas un día muy bonito!", "=" * 54]
    return "\n".join(lineas)


def label(parent, text, size=11, weight="normal", bg=BG, fg=TEXT, **kw):
    return tk.Label(parent, text=text, font=("Segoe UI", size, weight), bg=bg, fg=fg, **kw)


def button(parent, text, command, primary=False, bg=None, fg=None, pady=10, **kw):
    bg = bg or (DEEP_PINK if primary else "#FCE4EA")
    fg = fg or (WHITE if primary else DEEP_PINK)
    return tk.Button(parent, text=text, command=command, bd=0, relief="flat", cursor="hand2",
                     bg=bg, fg=fg, activebackground=CHERRY if primary else PINK,
                     activeforeground=WHITE if primary else DEEP_PINK,
                     font=("Segoe UI", 10, "bold"), padx=17, pady=pady, **kw)



def rect_redondo(cv, x1, y1, x2, y2, radio, relleno, borde="", grosor=1):

    from math import cos, sin, radians
    r = min(radio, (x2-x1)/2, (y2-y1)/2)
    coords=[]
    for cx,cy,first,last in [
        (x1+r,y1+r,180,270), (x2-r,y1+r,270,360),
        (x2-r,y2-r,0,90), (x1+r,y2-r,90,180),
    ]:
        for deg in range(first,last+1,6):
            coords += [cx+r*cos(radians(deg)),cy+r*sin(radians(deg))]
    return cv.create_polygon(coords, fill=relleno, outline=borde or relleno,
                             width=grosor, smooth=False)


def dibujar_icono(cv, nombre, x, y, color):

    k={"fill":"", "width":2, "outline":color}
    def line(*p): cv.create_line(*p, fill=color, width=2, capstyle="round", joinstyle="round")
    if nombre=="Inicio":
        line(x-10,y-1,x,y-11,x+10,y-1)
        line(x-8,y-2,x-8,y+10,x+8,y+10,x+8,y-2)
        line(x-2,y+10,x-2,y+3,x+3,y+3,x+3,y+10)
    elif nombre=="Menú":
        line(x-10,y+2,x-7,y+11,x+7,y+11,x+10,y+2)
        cv.create_arc(x-10,y-11,x+11,y+5,start=0,extent=180,style="arc",outline=color,width=2)
        cv.create_arc(x-6,y-14,x+7,y+2,start=0,extent=160,style="arc",outline=color,width=2)
    elif nombre=="Clientes":
        cv.create_oval(x-5,y-11,x+5,y-1,**k)
        cv.create_arc(x-11,y-1,x+11,y+17,start=0,extent=180,style="arc",outline=color,width=2)
        cv.create_arc(x-16,y-5,x-2,y+12,start=70,extent=125,style="arc",outline=color,width=2)
        cv.create_arc(x+2,y-5,x+16,y+12,start=-15,extent=125,style="arc",outline=color,width=2)
    elif nombre=="Productos":
        line(x-10,y-7,x,y-12,x+10,y-7,x+10,y+6,x,y+12,x-10,y+6,x-10,y-7)
        line(x-10,y-7,x,y-1,x+10,y-7)
        line(x,y-1,x,y+12)
    elif nombre=="Nueva venta":
        cv.create_oval(x-11,y-11,x+11,y+11,**k)
        line(x-6,y,x+6,y);line(x,y-6,x,y+6)
    elif nombre=="Usuarios":
        cv.create_oval(x-5,y-11,x+5,y-1,**k)
        cv.create_arc(x-11,y-1,x+11,y+17,start=0,extent=180,style="arc",outline=color,width=2)
        line(x+10,y-9,x+10,y+4)
    elif nombre=="Historial":
        cv.create_rectangle(x-10,y-9,x+10,y+11,**k)
        cv.create_rectangle(x-4,y-13,x+4,y-7,**k)
        for d in [0,5]: line(x-5,y+d,x+5,y+d)


class Navegacion(tk.Canvas):
    def __init__(self, parent, titulo, icono, accion):
        super().__init__(parent, width=230, height=46, bg=SIDE, bd=0, highlightthickness=0, cursor="hand2")
        self.titulo, self.icono, self.accion = titulo, icono, accion
        self.activo = False
        self.bind("<Configure>", lambda _e: self.dibujar())
        self.bind("<Button-1>", lambda _e: self.accion())
        self.bind("<Return>", lambda _e: self.accion())
        self.configure(takefocus=True)

    def set_selected(self, active):
        self.activo = active
        self.dibujar()

    def dibujar(self):
        self.delete("all")
        w = max(170, self.winfo_width())
        color = DEEP_PINK if self.activo else "#FFFAF8"
        rect_redondo(self, 2, 2, w-2, 44, 12, color,
                     DEEP_PINK if self.activo else "#E7CBC9")
        fg = WHITE if self.activo else CHERRY
        dibujar_icono(self,self.titulo,33,23,fg)
        self.create_text(69, 23, text=self.titulo, anchor="w",
                         font=("Segoe UI", 12, "bold" if self.activo else "normal"), fill=fg)


class TarjetaCategoria(tk.Canvas):

    def __init__(self, parent, titulo, subtitulo, imagen, color, acento, accion, alto=276):
        super().__init__(parent, bg=BG, height=alto, bd=0, highlightthickness=0, cursor="hand2")
        self.nombre, self.subtitulo, self.imagen = titulo, subtitulo, imagen
        self.tono, self.acento, self.accion = color, acento, accion
        self.alto = alto
        self.bind("<Configure>", lambda _e: self.dibujar())
        self.bind("<Button-1>", lambda _e: self.accion())
        self.bind("<Return>", lambda _e: self.accion())
        self.configure(takefocus=True)

    def dibujar(self):
        self.delete("all")
        w = self.winfo_width()
        if w < 10: return
        h = self.alto
        rect_redondo(self, 2, 2, w-2, h-2, 23, self.tono)
        image_y = 49 if h <= 205 else (83 if h >= 260 else 53)
        self.create_image(w/2, image_y, image=self.imagen)
        ty = 108 if h <= 205 else (h - 119 if h >= 260 else h - 108)
        self.create_text(w/2, ty, text=self.nombre, width=w-16, justify="center",
                         font=("Georgia", 11 if h <= 205 else 12, "bold"), fill=CHERRY)
        self.create_text(w/2, 134 if h <= 205 else ty+(28 if h>=260 else 37), text=self.subtitulo,
                         font=("Segoe UI", 9 if h <= 205 else 10), fill=TEXT)
        y1, y2 = (h-38, h-7) if h <= 205 else (h-62, h-18)
        rect_redondo(self, 27, y1, w-27, y2, 21, "#FFFAF9", self.acento)
        self.create_text(w/2, (y1+y2)/2, text="Ver productos  ›",
                         fill=CHERRY, font=("Segoe UI", 10, "bold"))


class PanelRedondo(tk.Canvas):

    def __init__(self, parent):
        super().__init__(parent, bg=BG, bd=0, highlightthickness=0)
        self.contenido = tk.Frame(self, bg=WHITE)
        self.indice = self.create_window(17, 16, anchor="nw", window=self.contenido)
        self.bind("<Configure>", self.redimensionar)

    def redimensionar(self, _ev=None):
        w, h = self.winfo_width(), self.winfo_height()
        if w < 30 or h < 30: return
        if hasattr(self, "_fondo"):
            self.delete(self._fondo)
        self._fondo = rect_redondo(self, 2, 2, w-2, h-2, 20, WHITE, BORDER)
        self.tag_lower(self._fondo)
        self.itemconfigure(self.indice, width=max(1, w-34), height=max(1, h-33))


class TiendaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        try:
            self.data = TiendaDatos()
        except (OSError, RuntimeError) as exc:
            messagebox.showerror("No se pueden abrir los datos",
                                 f"TIENDA no iniciará para evitar perder la información.\n\n{exc}")
            self.destroy()
            raise SystemExit(1)
        self.usuario = ""
        self.rol = ""
        self.carrito = {}
        self.title("TIENDA | Pastelería y postres")
        self.geometry("1390x940")
        self.minsize(1050, 745)
        self.configure(bg=BG)
        self.pastel_img = tk.PhotoImage(file=str(ASSETS / "pastel_fresa.png"))

        self.menu_img = {
            nombre: tk.PhotoImage(file=str(ASSETS / f"{nombre}.png"))
            for nombre in ("macarons", "panes_canasta", "muffins_chocolate", "cafe_latte", "galletas_nuevas", "pastel_fresa_nuevo")
        }
        self.menu_img_small = {nombre: foto.subsample(2, 2) for nombre, foto in self.menu_img.items()}
        self.categoria_img = {}
        for categoria, _subtitulo, imagen, _tono, _acento in TARJETAS:

            self.categoria_img[categoria] = tk.PhotoImage(file=str(ASSETS / ("categoria_" + imagen + ".png")))
        self.mini_galeria = {
            nombre: tk.PhotoImage(file=str(ASSETS / ("mini_" + nombre + ".png")))
            for grupo in GALERIA.values() for nombre in grupo
        }
        self.pasar_a_venta = None
        self.estilos()
        self.pantalla_login()

    def estilos(self):
        s = ttk.Style(self)
        if "clam" in s.theme_names():
            s.theme_use("clam")
        s.configure("TFrame", background=WHITE)
        s.configure("TLabel", background=WHITE, foreground=TEXT, font=("Segoe UI", 10))
        s.configure("TEntry", padding=9, borderwidth=1, fieldbackground=WHITE)
        s.configure("TCombobox", padding=8, borderwidth=1, fieldbackground=WHITE)
        s.map("TCombobox", fieldbackground=[("readonly", WHITE)])
        s.configure("Treeview", font=("Segoe UI", 10), rowheight=33,
                    foreground=TEXT, background=WHITE, fieldbackground=WHITE, borderwidth=0)
        s.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                    background="#F6E1E2", foreground=CHERRY, relief="flat", padding=9)
        s.map("Treeview", background=[("selected", "#F3C6D2")], foreground=[("selected", CHERRY)])
        s.configure("Vertical.TScrollbar", background=ROSE, troughcolor=WHITE)

    def limpiar(self):
        for w in self.winfo_children():
            w.destroy()

    def pantalla_login(self):
        self.limpiar()
        cont = tk.Frame(self, bg=BG)
        cont.pack(fill="both", expand=True, padx=48, pady=42)

        lado_arte = tk.Frame(cont, bg=BLUE, width=540)
        lado_arte.pack(side="left", fill="both", expand=True)
        lado_arte.pack_propagate(False)
        label(lado_arte, "Bienvenidos", 15, "bold", bg=BLUE, fg=DEEP_PINK).pack(pady=(28, 0))
        label(lado_arte, "TIENDA", 41, "bold", bg=BLUE, fg=CHERRY).pack(pady=(9, 0))
        label(lado_arte, "PASTELERÍA Y POSTRES", 11, "bold", bg=BLUE, fg=DEEP_PINK).pack()
        tk.Label(lado_arte, image=self.pastel_img, bg=BLUE).pack(expand=True, pady=(0, 0))
        label(lado_arte, "Hecho con amor y un toque de fresa", 12, bg=BLUE, fg=CHERRY).pack(pady=(0, 16))
        cinta = tk.Frame(lado_arte, height=11, bg=BLUE)
        cinta.pack(fill="x", side="bottom")
        for tono in (PINK, SKY, MINT, LILAC, CREAM):
            tk.Frame(cinta, bg=tono, height=11).pack(side="left", fill="x", expand=True)
        lado_form = tk.Frame(cont, bg=WHITE, width=490)
        lado_form.pack(side="left", fill="both", expand=True)
        central = tk.Frame(lado_form, bg=WHITE)
        central.place(relx=.5, rely=.49, anchor="center", relwidth=.78)
        label(central, "Hola, ¡qué gusto verte!", 21, "bold", bg=WHITE).pack(anchor="w")
        label(central, "Inicia sesión para comenzar a vender dulzura.", 10, bg=WHITE, fg=MUTED).pack(anchor="w", pady=(6, 30))
        label(central, "Usuario", 11, "bold", bg=WHITE).pack(anchor="w", pady=(0, 7))
        self.login_user = ttk.Entry(central, font=("Segoe UI", 12))
        self.login_user.pack(fill="x", ipady=4)
        label(central, "Contraseña", 11, "bold", bg=WHITE).pack(anchor="w", pady=(22, 7))
        self.login_password = ttk.Entry(central, show="•", font=("Segoe UI", 12))
        self.login_password.pack(fill="x", ipady=4)
        button(central, "Ingresar a Tienda    →", self.iniciar_sesion, primary=True, pady=13).pack(fill="x", pady=(30, 24))
        info = tk.Frame(central, bg=LILAC, padx=18, pady=16)
        info.pack(fill="x")
        label(info, "CUENTAS INICIALES (SOLO PRIMER USO)", 9, "bold", bg=LILAC, fg=DEEP_PINK).pack(anchor="w")
        label(info, "Administrador: admin / 1234", 10, bg=LILAC).pack(anchor="w", pady=(8, 2))
        label(info, "Cajero: cajero / 1234", 10, bg=LILAC).pack(anchor="w")
        label(info, "Inventario: inventario / 1234", 10, bg=LILAC).pack(anchor="w")
        label(info, "Cambia estas claves después de entrar.", 9, bg=LILAC, fg=MUTED).pack(anchor="w", pady=(7, 0))
        label(lado_form, "Práctica 8", 9, bg=WHITE, fg=MUTED).pack(side="bottom", pady=22)
        self.login_password.bind("<Return>", lambda _e: self.iniciar_sesion())
        self.login_user.focus_set()

    def iniciar_sesion(self):
        usuario = self.login_user.get().strip()
        rol = self.data.iniciar_sesion(usuario, self.login_password.get())
        if not rol:
            messagebox.showerror("Acceso no autorizado", "Usuario o contraseña incorrectos.")
            return
        self.usuario, self.rol = usuario, rol
        self.pantalla_app()

    def pantalla_app(self):
        self.limpiar()
        shell = tk.Frame(self, bg=BG)
        shell.pack(fill="both", expand=True)
        sidebar = tk.Frame(shell, bg=SIDE, width=262)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        toldo = tk.Canvas(sidebar, height=61, bg=SIDE, bd=0, highlightthickness=0)
        toldo.pack(fill="x")
        def dibujar_toldo(_ev=None):
            toldo.delete("all")
            w=toldo.winfo_width()
            z=w/10
            for i in range(10):
                col = "#F4A9B9" if i%2==0 else "#FFE1E7"
                toldo.create_rectangle(z*i, 0, z*(i+1)+1, 43, fill=col, outline=col)
                toldo.create_arc(z*i, 27, z*(i+1)+1, 62, start=180, extent=180,
                                  style="pieslice", fill=col, outline=col)
        toldo.bind("<Configure>", dibujar_toldo)

        self.logo_mini = self.menu_img["pastel_fresa_nuevo"].subsample(2,2)
        tk.Label(sidebar, image=self.logo_mini, bg=SIDE).pack(pady=(8, 0))
        tk.Label(sidebar, text="TIENDA",font=("Georgia",30,"bold"),
                 bg=SIDE,fg=CHERRY).pack(pady=(1,0))
        tk.Label(sidebar, text="Pastelería y Repostería",font=("Georgia",12,"italic"),
                 bg=SIDE,fg=CHERRY).pack(pady=(1,14))
        tk.Frame(sidebar, bg="#E8BDC3", height=1).pack(fill="x", padx=27, pady=(0, 24))

        self.nav_buttons = {}
        iconos = {"Inicio":"⌂", "Menú":"♧", "Clientes":"♧", "Productos":"▣",
                  "Nueva venta":"⊕", "Historial":"▤", "Usuarios":"♙"}
        secciones = ["Inicio", "Menú", "Clientes", "Productos"]
        if self.rol == "Administrador":
            secciones.append("Usuarios")
        if self.rol in ("Administrador", "Cajero"):
            secciones.extend(["Nueva venta", "Historial"])
        for titulo in secciones:
            b=Navegacion(sidebar, titulo, iconos[titulo], lambda t=titulo: self.mostrar_seccion(t))
            b.pack(fill="x", padx=16, pady=2)
            self.nav_buttons[titulo]=b
        # El pie queda al fondo independientemente de la altura de la pantalla.
        pie=tk.Frame(sidebar, bg=SIDE)
        pie.pack(side="bottom", fill="x", padx=20, pady=(2,22))
        tk.Frame(pie, height=1, bg="#E8CDD0").pack(fill="x", pady=(0,10))
        button(pie, "↪   Cerrar sesión", self.cerrar_sesion,
               bg="#FDE4E8", fg=DEEP_PINK, pady=11).pack(fill="x", pady=(0,12))
        label(pie, "Dulces momentos", 11, bg=SIDE, fg=CHERRY).pack()

        contenido=tk.Frame(shell,bg=BG)
        contenido.pack(side="left", fill="both", expand=True)
        arriba=tk.Frame(contenido,bg=BG,height=76)
        arriba.pack(fill="x")
        arriba.pack_propagate(False)
        label(arriba, "El rincón más dulce", 12, bg=BG, fg=CHERRY).pack(side="left",padx=31,pady=(0,0))
        label(arriba, f"♙  {self.usuario}  ·  {self.rol}", 11, bg=BG, fg=CHERRY).pack(side="right",padx=(5,31))
        button(arriba, "Mi contraseña", self.abrir_cambio_contrasena,
               bg=CREAM, fg=CHERRY, pady=6).pack(side="right", padx=6)
        tk.Frame(contenido,bg="#E8A9B9",height=1).pack(fill="x",padx=31)
        label(contenido, "Sistema educativo · Cambios guardados automáticamente en archivo local · Sin base de datos",
              9,bg=BG,fg=MUTED).pack(side="bottom",anchor="w",padx=31,pady=(0,16))
        self.page=tk.Frame(contenido,bg=BG)
        self.page.pack(fill="both",expand=True,padx=23,pady=(26,20))
        self.mostrar_seccion("Menú")

    def cerrar_sesion(self):
        self.usuario = self.rol = ""
        self.carrito = {}
        self.pantalla_login()

    def mostrar_seccion(self, nombre):
        if nombre not in self.nav_buttons:
            return messagebox.showwarning("Acceso", "Tu puesto no tiene acceso a esa sección.")
        for texto, b in self.nav_buttons.items():
            on = texto == nombre
            b.set_selected(on)
        for w in self.page.winfo_children():
            w.destroy()
        if nombre == "Inicio": self.inicio()
        elif nombre == "Menú": self.menu()
        elif nombre == "Clientes": self.clientes()
        elif nombre == "Productos": self.productos()
        elif nombre == "Nueva venta": self.venta()
        elif nombre == "Historial": self.historial()
        elif nombre == "Usuarios": self.usuarios()

    def page_title(self, title, subtitle):
        titular = tk.Frame(self.page, bg=BG)
        titular.pack(fill="x", pady=(0,22))
        tk.Label(titular, text=title, font=("Georgia", 28, "bold"),
                 bg=BG, fg=CHERRY).pack(anchor="w")
        label(titular,subtitle,11,bg=BG,fg=MUTED).pack(anchor="w",pady=(6,0))

    def card(self, parent, padx=20, pady=18):
        c = tk.Frame(parent, bg=WHITE, padx=padx, pady=pady, highlightthickness=1,
                     highlightbackground=BORDER)
        return c

    def counter(self, parent, number, description, tint):
        frame = tk.Frame(parent, bg=tint, padx=20, pady=18)
        frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        label(frame, str(number), 23, "bold", bg=tint, fg=CHERRY).pack(anchor="w")
        label(frame, description, 10, bg=tint, fg=TEXT).pack(anchor="w", pady=(4, 0))

    def inicio(self):
        self.page_title("Bienvenidos a Tienda", "llena de alegría tu día.")
        cifras = tk.Frame(self.page, bg=BG)
        cifras.pack(fill="x", pady=(0, 19))
        self.counter(cifras, len(self.data.productos), "Productos registrados", PINK)
        self.counter(cifras, len(self.data.clientes), "Clientes registrados", MINT_LIGHT)
        self.counter(cifras, len(self.data.ventas), "Ventas registradas", LILAC)
        self.counter(cifras, pesos(sum((v['total'] for v in self.data.ventas), Decimal('0'))), "Ingresos registrados", CREAM)
        centro = self.card(self.page, 28, 20)
        centro.pack(fill="both", expand=True)
        texto = tk.Frame(centro, bg=WHITE)
        texto.pack(side="left", fill="both", expand=True)
        label(texto, "Un poquito de dulzura en cada venta", 17, "bold", bg=WHITE, fg=CHERRY, wraplength=350).pack(anchor="w", pady=(33, 12))
        label(texto, "tenenos disponibles mas de cien productos.\nRegistra pedidos, clientes y ventas; crea tickets digitales con IVA.", 11, bg=WHITE, fg=MUTED, justify="left", wraplength=350).pack(anchor="w", pady=(0, 25))
        button(texto, "Ver menú de productos  →", lambda: self.mostrar_seccion("Menú"), primary=True).pack(anchor="w", pady=(0, 8))
        button(texto, "Comenzar una venta  →", lambda: self.mostrar_seccion("Nueva venta")).pack(anchor="w")
        # thumbnail reduced by Tk's built-in integer subsampling
        mini = self.pastel_img.subsample(2, 2)
        self._mini = mini
        tk.Label(centro, image=mini, bg=WHITE).pack(side="right", padx=(0, 5))

    def menu(self):

        self.page_title("Menú de Tienda",
                        "Repostería artesanal, pasteles, bocaditos y café  ·  Precios de ejemplo en MXN.")

        contenedor=tk.Frame(self.page, bg=BG)
        contenedor.pack(fill="both", expand=True)
        scroll=tk.Canvas(contenedor, bg=BG, highlightthickness=0, bd=0)
        sb=ttk.Scrollbar(contenedor, orient="vertical", command=scroll.yview)
        sb.pack(side="right",fill="y")
        scroll.pack(side="left",fill="both",expand=True)
        scroll.configure(yscrollcommand=sb.set)
        interior=tk.Frame(scroll,bg=BG)
        win=scroll.create_window((0,0),anchor="nw",window=interior)
        interior.bind("<Configure>",lambda _e: scroll.configure(scrollregion=scroll.bbox("all")))
        scroll.bind("<Configure>",lambda ev: scroll.itemconfigure(win,width=ev.width))
        self.scroll_menu=scroll

        altura=185
        grupo=tk.Frame(interior,bg=BG)
        grupo.pack(fill="x",pady=(0,14))
        for i in range(4):
            grupo.columnconfigure(i,weight=1,uniform="cards")
        for i,(titulo,sub,imagen,tono,accent) in enumerate(TARJETAS):
            tarjeta=TarjetaCategoria(grupo,titulo,sub,self.categoria_img[titulo],tono,accent,
                              lambda c=titulo:self.menu_elegir_categoria(c),alto=altura)
            tarjeta.grid(row=i//4,column=i%4,sticky="nsew",
                         padx=(0 if i%4==0 else 5,0 if i%4==3 else 5),
                         pady=(0 if i<4 else 6,6))
        grupo.rowconfigure(0,minsize=altura)
        grupo.rowconfigure(1,minsize=altura)

        panel=PanelRedondo(interior)
        panel.configure(height=324)
        panel.pack(fill="x",pady=(0,9))
        caja=panel.contenido
        top=tk.Frame(caja,bg=WHITE)
        top.pack(fill="x",pady=(0,9))
        tk.Label(top,text="Nuestra carta",font=("Georgia",16,"bold"),
                 bg="#F7DFE2",fg=CHERRY,padx=10,pady=5).pack(side="left",padx=(0,12))
        label(top,"Categoría:",10,bg=WHITE,fg=TEXT).pack(side="left")
        self.filtro_menu=ttk.Combobox(top,values=CATEGORIAS,state="readonly",width=19)
        self.filtro_menu.set("Todas")
        self.filtro_menu.pack(side="left",padx=(5,12))
        self.filtro_menu.bind("<<ComboboxSelected>>",lambda _evt:self.refrescar_menu())
        label(top,"Buscar:",10,bg=WHITE,fg=TEXT).pack(side="left")
        self.buscar_menu=tk.StringVar()
        entrada=ttk.Entry(top,textvariable=self.buscar_menu,width=23)
        entrada.pack(side="left",padx=(5,0),fill="x",expand=True)
        self.buscar_menu.trace_add("write",lambda *_args:self.refrescar_menu())

        footer=tk.Frame(caja,bg=WHITE)
        footer.pack(side="bottom",fill="x",pady=(7,0))
        self.menu_info=label(footer,"",10,bg=WHITE,fg=MUTED)
        self.menu_info.pack(side="left")
        button(footer,"Agregar a una venta  →",self.menu_a_venta,
               primary=True,pady=6).pack(side="right")
        self.menu_galeria=tk.Frame(caja,bg=WHITE)
        self.menu_tabla_container=tk.Frame(caja,bg=WHITE)
        self.menu_tabla_container.pack(fill="both",expand=True)
        self.t_menu=self.tabla(self.menu_tabla_container,("id","name","cat","price","stock"),
            ("Código","Producto / presentación","Categoría","Precio","Disponibles"),
            (68,254,148,85,85),height=7)
        self.t_menu.bind("<Double-1>",lambda _evt:self.menu_a_venta())
        self.refrescar_menu()

    def _galeria_categoria(self, categoria):

        for hijo in self.menu_galeria.winfo_children():
            hijo.destroy()
        if categoria == "Todas" or categoria not in GALERIA:
            self.menu_galeria.pack_forget()
            return
        self.menu_galeria.pack(fill="x",pady=(0,7),before=self.menu_tabla_container)
        label(self.menu_galeria,"Ilustraciones:",9,bg=WHITE,fg=MUTED).pack(side="left",padx=(0,8))
        for nombre in GALERIA[categoria]:
            tk.Label(self.menu_galeria,image=self.mini_galeria[nombre],
                     bg=WHITE,bd=0).pack(side="left",padx=(0,7))

    def menu_elegir_categoria(self, categoria):
        self.filtro_menu.set(categoria)
        self.refrescar_menu()

        self.scroll_menu.yview_moveto(0.35)

    def refrescar_menu(self):
        if not hasattr(self,"t_menu") or not self.t_menu.winfo_exists():
            return
        seleccion = self.filtro_menu.get()
        self._galeria_categoria(seleccion)
        consulta = self.buscar_menu.get().casefold().strip()
        self.t_menu.delete(*self.t_menu.get_children())
        contador = 0
        for codigo, producto in self.data.productos.items():
            if seleccion != "Todas" and producto["categoria"] != seleccion:
                continue
            if consulta and consulta not in (codigo + " " + producto["nombre"] + " " + producto["categoria"]).casefold():
                continue
            self.t_menu.insert("", "end", iid=codigo,
                values=(codigo, producto["nombre"], producto["categoria"], pesos(producto["precio"]),producto["stock"]),
                tags=("alternate",) if contador % 2 else ())
            contador += 1
        self.menu_info.configure(text=f"{contador} artículos · tienes que dar  doble clic en un producto para venderlo")

    def menu_a_venta(self):
        seleccion = self.t_menu.selection()
        if not seleccion:
            return messagebox.showwarning("Elige un producto", "Selecciona primero un producto de la carta.")
        self.pasar_a_venta = seleccion[0]
        self.mostrar_seccion("Nueva venta")

    def tabla(self, parent, cols, headers, widths, height=11):
        wrapper = tk.Frame(parent, bg=WHITE)
        wrapper.pack(fill="both", expand=True)
        tree = ttk.Treeview(wrapper, columns=cols, show="headings", height=height, selectmode="browse")
        for col, head, width in zip(cols, headers, widths):
            tree.heading(col, text=head)
            tree.column(col, width=width, minwidth=70, anchor="center" if col in ("id", "qty", "stock", "folio") else "w")
        tree.tag_configure("alternate", background="#FBF2F0")
        tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(wrapper, command=tree.yview, orient="vertical")
        sb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=sb.set)
        return tree

    def field(self, parent, title, readonly=False):
        label(parent, title, 10, "bold", bg=WHITE).pack(anchor="w", pady=(10, 5))
        e = ttk.Entry(parent, font=("Segoe UI", 10), state="readonly" if readonly else "normal")
        e.pack(fill="x", ipady=2)
        return e

    @staticmethod
    def set_entry(entry, value):
        entry.delete(0, "end")
        entry.insert(0, str(value))

    def clientes(self):
        self.page_title("Clientes", "Consulta y administra a quienes disfrutan nuestros postres.")
        area = tk.Frame(self.page, bg=BG)
        area.pack(fill="both", expand=True)
        left = self.card(area)
        left.pack(side="left", fill="both", expand=True, padx=(0, 13))
        label(left, "Lista de clientes", 14, "bold", bg=WHITE, fg=CHERRY).pack(anchor="w", pady=(0, 13))
        self.t_client = self.tabla(left, ("id", "name", "phone"), ("Código", "Nombre completo", "Teléfono"), (90, 220, 155))
        self.t_client.bind("<<TreeviewSelect>>", self.seleccionar_cliente)
        self.refrescar_clientes()
        if self.rol == "Administrador":
            right = self.card(area)
            right.pack(side="right", fill="y")
            right.configure(width=260)
            right.pack_propagate(False)
            label(right, "Datos del cliente", 14, "bold", bg=WHITE, fg=CHERRY).pack(anchor="w")
            self.c_id = self.field(right, "Código (ej. C003)")
            self.c_name = self.field(right, "Nombre completo")
            self.c_phone = self.field(right, "Teléfono (10 dígitos)")
            button(right, "Guardar / actualizar", self.guardar_cliente, primary=True).pack(fill="x", pady=(25, 8))
            button(right, "Eliminar seleccionado", self.borrar_cliente).pack(fill="x")
            button(right, "Limpiar formulario", lambda: [self.set_entry(e, "") for e in (self.c_id,self.c_name,self.c_phone)], bg=WHITE).pack(fill="x", pady=8)
        else:
            label(left, "Este puesto tiene acceso de consulta.", 10, bg=WHITE, fg=MUTED).pack(anchor="w", pady=10)

    def refrescar_clientes(self):
        self.t_client.delete(*self.t_client.get_children())
        for i,(k,v) in enumerate(sorted(self.data.clientes.items())):
            self.t_client.insert("", "end", iid=k, values=(k, v["nombre"], v["telefono"]), tags=("alternate",) if i%2 else ())

    def seleccionar_cliente(self, _evt=None):
        if self.rol != "Administrador": return
        sel = self.t_client.selection()
        if sel:
            c = self.data.clientes[sel[0]]
            for e, v in ((self.c_id, sel[0]), (self.c_name,c["nombre"]), (self.c_phone,c["telefono"])): self.set_entry(e,v)

    def guardar_cliente(self):
        try: self.data.guardar_cliente(self.c_id.get(), self.c_name.get(), self.c_phone.get())
        except ValueError as exc: return messagebox.showwarning("Datos incorrectos", str(exc))
        except OSError as exc: return messagebox.showerror("No se pudo guardar",str(exc))
        self.refrescar_clientes()
        for e in (self.c_id,self.c_name,self.c_phone): self.set_entry(e,"")
        messagebox.showinfo("Guardado", "Cliente guardado correctamente.")

    def borrar_cliente(self):
        sel = self.t_client.selection()
        if not sel: return messagebox.showwarning("Selecciona", "Elige un cliente.")
        if messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
            try: self.data.eliminar_cliente(sel[0])
            except (ValueError, OSError) as exc: return messagebox.showerror("No se pudo guardar",str(exc))
            self.refrescar_clientes()

    def productos(self):
        self.page_title("Productos dulces", "Organiza el inventario de la pastelería.")
        area = tk.Frame(self.page, bg=BG)
        area.pack(fill="both", expand=True)
        left = self.card(area)
        left.pack(side="left", fill="both", expand=True, padx=(0, 13))
        label(left, "Inventario de delicias", 14, "bold", bg=WHITE, fg=CHERRY).pack(anchor="w", pady=(0, 8))
        filtros = tk.Frame(left, bg=WHITE)
        filtros.pack(fill="x", pady=(0, 10))
        self.p_busqueda = tk.StringVar()
        ttk.Entry(filtros, textvariable=self.p_busqueda, width=24).pack(side="left", padx=(0,10))
        self.p_categoria_filtro = ttk.Combobox(filtros, values=CATEGORIAS, state="readonly",width=18)
        self.p_categoria_filtro.set("Todas")
        self.p_categoria_filtro.pack(side="left")
        self.p_busqueda.trace_add("write", lambda *_args: self.refrescar_productos())
        self.p_categoria_filtro.bind("<<ComboboxSelected>>",lambda _evt: self.refrescar_productos())
        self.t_products = self.tabla(left, ("id","name","cat","price","stock"),
                                    ("Código", "Producto", "Categoría", "Precio", "Stock"), (78,238,92,89,65))
        self.t_products.bind("<<TreeviewSelect>>", self.seleccionar_producto)
        self.refrescar_productos()
        if self.rol in ("Administrador", "Inventario"):
            right = self.card(area, 17, 15)
            right.pack(side="right", fill="y")
            right.configure(width=260)
            right.pack_propagate(False)
            label(right, "Datos del producto", 13, "bold", bg=WHITE, fg=CHERRY).pack(anchor="w")
            self.p_id = self.field(right, "Código (ej. P122)")
            self.p_name = self.field(right, "Nombre del producto")
            label(right, "Categoría", 10, "bold", bg=WHITE).pack(anchor="w", pady=(10,5))
            self.p_category = ttk.Combobox(right, state="readonly", values=CATEGORIAS[1:])
            self.p_category.pack(fill="x")
            self.p_category.set("Pasteles")
            self.p_price = self.field(right, "Precio ($)")
            self.p_stock = self.field(right, "Existencias")
            button(right, "Guardar / actualizar", self.guardar_producto, primary=True).pack(fill="x", pady=(20,6))
            button(right, "Eliminar seleccionado", self.borrar_producto).pack(fill="x")
        else:
            label(left, "Este puesto puede consultar el inventario.", 10, bg=WHITE, fg=MUTED).pack(anchor="w", pady=10)

    def refrescar_productos(self):
        self.t_products.delete(*self.t_products.get_children())
        filtro = self.p_categoria_filtro.get() if hasattr(self, "p_categoria_filtro") else "Todas"
        busqueda = self.p_busqueda.get().strip().casefold() if hasattr(self, "p_busqueda") else ""
        i = 0
        for k,p in sorted(self.data.productos.items()):
            if filtro != "Todas" and p["categoria"] != filtro: continue
            if busqueda and busqueda not in (k + " " + p["nombre"]).casefold(): continue
            self.t_products.insert("", "end", iid=k, values=(k,p["nombre"],p["categoria"],pesos(p["precio"]),p["stock"]),tags=("alternate",) if i%2 else ())
            i+=1

    def seleccionar_producto(self,_evt=None):
        if self.rol not in ("Administrador", "Inventario"): return
        sel=self.t_products.selection()
        if sel:
            p=self.data.productos[sel[0]]
            for e,v in ((self.p_id,sel[0]),(self.p_name,p["nombre"]),(self.p_price,p["precio"]),(self.p_stock,p["stock"])): self.set_entry(e,v)
            self.p_category.set(p["categoria"])

    def guardar_producto(self):
        try: self.data.guardar_producto(self.p_id.get(),self.p_name.get(),self.p_category.get(),self.p_price.get(),self.p_stock.get())
        except ValueError as exc: return messagebox.showwarning("Datos incorrectos",str(exc))
        except OSError as exc: return messagebox.showerror("No se pudo guardar",str(exc))
        self.refrescar_productos()
        for e in (self.p_id,self.p_name,self.p_price,self.p_stock):self.set_entry(e,"")
        self.p_category.set("Pasteles")
        messagebox.showinfo("Guardado", "Producto guardado correctamente.")

    def borrar_producto(self):
        sel=self.t_products.selection()
        if not sel: return messagebox.showwarning("Selecciona", "Elige un producto.")
        if sel[0] in self.carrito:return messagebox.showwarning("En carrito", "Quita primero ese producto del carrito.")
        if messagebox.askyesno("Confirmar", "¿Eliminar este producto?"):
            try: self.data.eliminar_producto(sel[0])
            except (ValueError, OSError) as exc: return messagebox.showerror("No se pudo guardar",str(exc))
            self.refrescar_productos()

    def venta(self):
        self.page_title("Nueva venta", "Prepara una compra y genera un bonito ticket digital.")
        form = self.card(self.page, 20, 12)
        form.pack(fill="x", pady=(0,15))
        label(form, "Selecciona los productos", 13, "bold", bg=WHITE, fg=CHERRY).pack(anchor="w", pady=(0,8))
        row1 = tk.Frame(form, bg=WHITE)
        row1.pack(fill="x", pady=(0,10))
        label(row1, "Cliente", 10, "bold", bg=WHITE).pack(side="left", padx=(0,9))
        self.v_client=ttk.Combobox(row1, state="readonly", width=33)
        self.v_client.pack(side="left", padx=(0,23))
        self.v_client["values"]=[f"{k} - {v['nombre']}" for k,v in sorted(self.data.clientes.items())]
        if self.v_client["values"]:self.v_client.current(0)
        label(row1, "Cantidad", 10, "bold", bg=WHITE).pack(side="left", padx=(0,9))
        self.v_qty=ttk.Entry(row1,width=9)
        self.v_qty.insert(0,"1")
        self.v_qty.pack(side="left",padx=(0,16))
        label(row1,"Categoría",10,"bold",bg=WHITE).pack(side="left",padx=(0,7))
        self.v_category = ttk.Combobox(row1,state="readonly",values=CATEGORIAS,width=19)
        self.v_category.set("Todas")
        self.v_category.pack(side="left")
        self.v_category.bind("<<ComboboxSelected>>",lambda _evt:self.refrescar_combo_venta())
        row2=tk.Frame(form,bg=WHITE)
        row2.pack(fill="x")
        label(row2,"Producto",10,"bold",bg=WHITE).pack(side="left",padx=(0,9))
        self.v_product=ttk.Combobox(row2, state="readonly",width=58)
        self.v_product.pack(side="left",padx=(0,13))
        self.refrescar_combo_venta()
        if self.pasar_a_venta:
            elegido = self.data.productos.get(self.pasar_a_venta)
            if elegido:
                self.v_category.set(elegido["categoria"])
                self.refrescar_combo_venta()
                for opcion in self.v_product["values"]:
                    if opcion.startswith(self.pasar_a_venta + " - "):
                        self.v_product.set(opcion)
                        break
            self.pasar_a_venta = None
        button(row2,"+ Agregar al carrito",self.agregar_carrito,primary=True,pady=8).pack(side="left")
        middle = tk.Frame(self.page, bg=BG)
        middle.pack(fill="both",expand=True)
        left=self.card(middle,16,15)
        left.pack(side="left",fill="both",expand=True,padx=(0,13))
        label(left,"Mi carrito",13,"bold",bg=WHITE,fg=CHERRY).pack(anchor="w",pady=(0,12))
        controls=tk.Frame(left,bg=WHITE)
        controls.pack(side="bottom",fill="x",pady=(10,0))
        button(controls,"Quitar producto",self.quitar_carrito).pack(side="left",padx=(0,8))
        button(controls,"Vaciar carrito",self.vaciar_carrito,bg=WHITE,fg=MUTED).pack(side="left")
        self.t_cart=self.tabla(left,("id","name","qty","price","amount"),
                               ("Código","Producto","Cant.","P. unitario","Importe"),(73,225,59,106,110),height=6)
        right=self.card(middle,18,19)
        right.pack(side="right",fill="y")
        right.configure(width=225)
        right.pack_propagate(False)
        label(right,"Resumen de compra",13,"bold",bg=WHITE,fg=CHERRY).pack(anchor="w",pady=(0,12))
        label(right,"Subtotal",10,bg=WHITE,fg=MUTED).pack(anchor="w")
        self.sub_lbl=label(right,"$0.00",17,"bold",bg=WHITE)
        self.sub_lbl.pack(anchor="w",pady=(3,9))
        label(right,"IVA (16 %)",10,bg=WHITE,fg=MUTED).pack(anchor="w")
        self.iva_lbl=label(right,"$0.00",17,"bold",bg=WHITE)
        self.iva_lbl.pack(anchor="w",pady=(3,9))
        tk.Frame(right,bg=BORDER,height=1).pack(fill="x",pady=(4,8))
        label(right,"Total a pagar",11,"bold",bg=WHITE,fg=DEEP_PINK).pack(anchor="w")
        self.total_lbl=label(right,"$0.00",23,"bold",bg=WHITE,fg=CHERRY)
        self.total_lbl.pack(anchor="w",pady=(3,9))
        button(right,"Ver para el cliente",self.vista_cliente,
               bg=BLUE,fg=CHERRY,pady=7).pack(fill="x", pady=(3,8))
        button(right,"Cobrar y crear ticket  →",self.cobrar,primary=True,pady=9,wraplength=185).pack(fill="x")
        self.refrescar_carrito()

    def refrescar_combo_venta(self):
        categoria = self.v_category.get()
        self.v_product["values"] = [
            f"{k} - {p['nombre']} · {pesos(p['precio'])} ({p['stock']} disponibles)"
            for k,p in self.data.productos.items()
            if p['stock']>0 and (categoria == "Todas" or categoria == p["categoria"])
        ]
        if self.v_product["values"]: self.v_product.current(0)
        else: self.v_product.set("")

    def agregar_carrito(self):
        code=self.v_product.get().split(" - ")[0]
        if code not in self.data.productos:return messagebox.showwarning("Producto", "Selecciona un producto.")
        try:qty=cantidad_positiva(self.v_qty.get())
        except ValueError as exc:return messagebox.showwarning("Cantidad",str(exc))
        nuevo=self.carrito.get(code,0)+qty
        if nuevo>self.data.productos[code]["stock"]:
            return messagebox.showwarning("Sin existencias", "No hay suficientes unidades disponibles.")
        self.carrito[code]=nuevo
        self.refrescar_carrito()

    def quitar_carrito(self):
        sel=self.t_cart.selection()
        if not sel:return messagebox.showwarning("Producto", "Selecciona un producto del carrito.")
        self.carrito.pop(sel[0],None)
        self.refrescar_carrito()

    def vaciar_carrito(self):
        self.carrito.clear()
        self.refrescar_carrito()

    def refrescar_carrito(self):
        self.t_cart.delete(*self.t_cart.get_children())
        for i,(code,qty) in enumerate(self.carrito.items()):
            p=self.data.productos[code]
            imp=p["precio"]*qty
            self.t_cart.insert("","end",iid=code,values=(code,p["nombre"],qty,pesos(p["precio"]),pesos(imp)),tags=("alternate",) if i%2 else ())
        if self.carrito:
            try:
                _detalle, subtotal, iva, total = self.data.calcular_carrito(self.carrito)
            except ValueError as exc:
                return messagebox.showerror("Carrito", str(exc))
        else:
            subtotal = iva = total = Decimal("0.00")
        self.sub_lbl.configure(text=pesos(subtotal))
        self.iva_lbl.configure(text=pesos(iva))
        self.total_lbl.configure(text=pesos(total))

    def vista_cliente(self):
        if self.rol not in ("Administrador", "Cajero"):
            return messagebox.showwarning("Acceso", "Este puesto no puede realizar ventas.")
        client=self.v_client.get().split(" - ")[0]
        try:
            previa=self.data.previsualizar_venta(self.carrito,client,self.usuario)
        except ValueError as exc:
            return messagebox.showwarning("Revisa el carrito",str(exc))
        self.mostrar_ticket(previa, previa=True)

    def cobrar(self):
        if self.rol not in ("Administrador", "Cajero"):
            return messagebox.showwarning("Acceso", "Este puesto no puede registrar ventas.")
        client=self.v_client.get().split(" - ")[0]
        try: venta=self.data.realizar_venta(self.carrito,client,self.usuario)
        except ValueError as exc:return messagebox.showwarning("No se puede cobrar",str(exc))
        except OSError as exc:return messagebox.showerror("No se guardó la venta",str(exc))
        self.carrito={}
        self.mostrar_seccion("Nueva venta")
        self.mostrar_ticket(venta)

    def abrir_cambio_contrasena(self):
        top=tk.Toplevel(self)
        top.title("TIENDA · Cambiar mi contraseña")
        top.geometry("440x385")
        top.configure(bg=WHITE)
        top.transient(self)
        top.grab_set()
        frame=tk.Frame(top,bg=WHITE,padx=30,pady=23)
        frame.pack(fill="both",expand=True)
        label(frame, "Cambiar mi contraseña", 17, "bold", bg=WHITE, fg=CHERRY).pack(anchor="w",pady=(0,13))
        label(frame, f"Usuario: {self.usuario}", 10, bg=WHITE, fg=MUTED).pack(anchor="w")
        entradas=[]
        for titulo in ("Contraseña actual", "Nueva contraseña (mínimo 6 caracteres)", "Repite la nueva contraseña"):
            label(frame, titulo, 10, bg=WHITE).pack(anchor="w",pady=(13,4))
            campo=ttk.Entry(frame,show="•")
            campo.pack(fill="x")
            entradas.append(campo)
        def aplicar():
            if entradas[1].get()!=entradas[2].get():
                return messagebox.showwarning("Contraseñas", "Las contraseñas nuevas no coinciden.", parent=top)
            try:
                self.data.cambiar_contrasena(self.usuario,entradas[0].get(),entradas[1].get())
            except (ValueError,OSError) as exc:
                return messagebox.showwarning("No se pudo cambiar",str(exc),parent=top)
            messagebox.showinfo("Contraseña actualizada", "El cambio se guardó. La próxima vez usa la nueva contraseña.",parent=top)
            top.destroy()
        button(frame, "Guardar nueva contraseña", aplicar, primary=True).pack(fill="x",pady=(22,0))
        entradas[0].focus_set()

    def usuarios(self):
        if self.rol != "Administrador":
            return messagebox.showwarning("Acceso", "Solo el administrador gestiona cuentas.")
        self.page_title("Usuarios y puestos", "Administra las cuentas de TIENDA y los permisos por puesto.")
        area=tk.Frame(self.page,bg=BG)
        area.pack(fill="both",expand=True)
        left=self.card(area)
        left.pack(side="left",fill="both",expand=True,padx=(0,13))
        label(left,"Personal registrado",14,"bold",bg=WHITE,fg=CHERRY).pack(anchor="w",pady=(0,14))
        self.t_users=self.tabla(left,("user","role"),("Usuario","Puesto"),(155,205))
        self.t_users.bind("<<TreeviewSelect>>", self.seleccionar_usuario)
        right=self.card(area,15,15)
        right.pack(side="right",fill="y")
        right.configure(width=285)
        right.pack_propagate(False)
        label(right,"Agregar o editar cuenta",13,"bold",bg=WHITE,fg=CHERRY).pack(anchor="w")
        self.u_name=self.field(right,"Nombre de usuario")
        label(right,"Puesto",10,"bold",bg=WHITE).pack(anchor="w",pady=(12,4))
        self.u_role=ttk.Combobox(right,values=ROLES,state="readonly")
        self.u_role.pack(fill="x")
        self.u_role.set("Cajero")
        label(right,"Contraseña nueva",10,"bold",bg=WHITE).pack(anchor="w",pady=(12,4))
        self.u_pass=ttk.Entry(right,show="•")
        self.u_pass.pack(fill="x")
        label(right,"Para cambiar solo el puesto, deja la clave vacía. Para crear cuenta, escribe mínimo 6 caracteres.",
              9,bg=WHITE,fg=MUTED,wraplength=235,justify="left").pack(anchor="w",pady=(10,13))
        button(right,"Guardar cuenta", self.guardar_usuario,primary=True).pack(fill="x",pady=(6,7))
        button(right,"Eliminar seleccionada",self.borrar_usuario).pack(fill="x",pady=4)
        button(right,"Limpiar formulario", self.limpiar_usuario,bg=CREAM,fg=CHERRY).pack(fill="x",pady=4)
        self.refrescar_usuarios()

    def refrescar_usuarios(self):
        self.t_users.delete(*self.t_users.get_children())
        for i,(nombre,registro) in enumerate(sorted(self.data.usuarios.items())):
            self.t_users.insert("","end",iid=nombre,values=(nombre,registro["rol"]),
                                tags=("alternate",) if i%2 else ())

    def seleccionar_usuario(self,_evt=None):
        sel=self.t_users.selection()
        if sel:
            self.set_entry(self.u_name,sel[0])
            self.u_role.set(self.data.usuarios[sel[0]]["rol"])
            self.u_pass.delete(0,"end")

    def limpiar_usuario(self):
        self.set_entry(self.u_name,"")
        self.u_role.set("Cajero")
        self.u_pass.delete(0,"end")

    def guardar_usuario(self):
        nombre=self.u_name.get().strip().lower()
        rol=self.u_role.get()
        if nombre == self.usuario and rol != "Administrador":
            return messagebox.showwarning("Puesto", "No puedes cambiar tu propio puesto mientras tienes la sesión abierta.")
        try:
            self.data.crear_o_editar_usuario(nombre,rol,self.u_pass.get())
        except (ValueError,OSError) as exc:
            return messagebox.showwarning("Cuenta no guardada",str(exc))
        self.refrescar_usuarios()
        self.limpiar_usuario()
        messagebox.showinfo("Cuenta guardada", "Los cambios se guardaron y estarán disponibles al volver a entrar.")

    def borrar_usuario(self):
        sel=self.t_users.selection()
        if not sel: return messagebox.showwarning("Usuario", "Selecciona una cuenta.")
        if not messagebox.askyesno("Confirmación",f"¿Eliminar la cuenta {sel[0]}?"):
            return
        try:
            self.data.eliminar_usuario(sel[0],self.usuario)
        except (ValueError,OSError) as exc:
            return messagebox.showwarning("No se pudo eliminar",str(exc))
        self.refrescar_usuarios()
        self.limpiar_usuario()

    def historial(self):
        self.page_title("Historial de ventas", "Consulta los tickets guardados, incluso después de cerrar la aplicación.")
        p=self.card(self.page)
        p.pack(fill="both",expand=True)
        label(p,"Tickets registrados",14,"bold",bg=WHITE,fg=CHERRY).pack(anchor="w",pady=(0,12))
        self.t_history=self.tabla(p,("folio","date","client","seller","total"),
                                  ("Folio","Fecha y hora","Cliente","Cajero","Total"),(90,165,220,110,100))
        for i,v in enumerate(reversed(self.data.ventas)):
            self.t_history.insert("","end",iid=v["folio"],values=(v["folio"],v["fecha"],v["cliente"],v["vendedor"],pesos(v["total"])),tags=("alternate",) if i%2 else ())
        button(p,"Ver ticket seleccionado",self.ver_ticket,primary=True).pack(anchor="w",pady=(14,0))

    def ver_ticket(self):
        sel=self.t_history.selection()
        if not sel:return messagebox.showwarning("Selecciona", "Selecciona un ticket del historial.")
        v=next((x for x in self.data.ventas if x["folio"]==sel[0]),None)
        if v:self.mostrar_ticket(v)

    def mostrar_ticket(self, v, previa=False):
        top=tk.Toplevel(self)
        top.title(("Tienda | Vista para cliente" if previa else "Tienda | Ticket ") + ("" if previa else v["folio"]))
        top.geometry("650x690")
        top.configure(bg=BG)
        top.transient(self)
        label(top,"TIENDA",25,"bold",fg=CHERRY).pack(pady=(18,0))
        label(top,"Vista previa para el cliente · Sin cobrar" if previa else "Ticket digital · Pastelería y postres",
              11,fg=DEEP_PINK).pack(pady=(0,14))
        body=tk.Text(top,font=("Consolas",10),bg=WHITE,fg=TEXT,bd=0,padx=22,pady=21,wrap="none")
        body.insert("1.0",texto_ticket(v))
        body.configure(state="disabled")
        body.pack(fill="both",expand=True,padx=23,pady=(0,12))
        foot=tk.Frame(top,bg=BG)
        foot.pack(fill="x",padx=23,pady=(0,22))
        def guardar():
            ruta=filedialog.asksaveasfilename(parent=top,defaultextension=".txt",initialfile=f"ticket_{v['folio']}.txt",filetypes=[("Documento de texto","*.txt")])
            if ruta:
                try:
                    Path(ruta).write_text(texto_ticket(v),encoding="utf-8")
                    messagebox.showinfo("Ticket guardado","Tu ticket digital se guardó correctamente.",parent=top)
                except OSError as e:messagebox.showerror("No se pudo guardar",str(e),parent=top)
        if not previa:
            button(foot,"Guardar ticket (.txt)",guardar,primary=True).pack(side="left")
        else:
            label(foot,"Este resumen NO registra la venta.",10,bg=BG,fg=DEEP_PINK).pack(side="left")
        button(foot,"Cerrar",top.destroy).pack(side="right")


if __name__ == "__main__":
    TiendaApp().mainloop()
