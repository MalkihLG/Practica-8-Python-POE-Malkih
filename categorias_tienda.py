CATEGORIAS = [
    "Todas", "Bebidas", "Pasteles", "Galletas y brownies", "Panadería",
    "Desayunos", "Helados", "Postres", "Accesorios",
]

TARJETAS = [
    ("Bebidas", "Café, té y jugos", "cafe_latte", "#E8F4EB", "#91BCA7"),
    ("Pasteles y postres", "Pasteles, pays y flanes", "pastel_fresa_nuevo", "#FBE6E8", "#DDA7B0"),
    ("Galletas y brownies", "Galletas y chocolate", "galletas_nuevas", "#E5F1FA", "#8AB9D8"),
    ("Panadería", "Panes y muffins", "panes_canasta", "#F0F4E9", "#A9C79F"),
    ("Desayunos dulces", "Hot cakes y donas", "hotcakes", "#FFF2DE", "#D7B077"),
    ("Helados y fríos", "Helados y malteadas", "helado_copa", "#E4F4FC", "#8BBED9"),
    ("Especialidades", "Macarons y bocaditos", "macarons", "#F0E7F5", "#BDA4CE"),
    ("Accesorios", "Fiestas y decoración", "accesorios_fiesta", "#FCE6EB", "#DDA7B0"),
]

GALERIA = {
    "Bebidas": ("cafe_latte", "jugo_naranja", "chocolate_caliente", "te", "frappe"),
    "Pasteles y postres": ("pastel_fresa_nuevo", "flan"),
    "Galletas y brownies": ("galletas_nuevas", "brownies"),
    "Panadería": ("panes_canasta", "muffins_chocolate"),
    "Desayunos dulces": ("hotcakes", "crepas_fresa", "donas"),
    "Helados y fríos": ("helado_copa",),
    "Especialidades": ("macarons", "pay_manzana"),
    "Accesorios": ("accesorios_fiesta",),
}


NOVEDADES = [
    ("Muffin de chocolate", "Panadería", 35, 24),
    ("Crepas con fresas", "Desayunos dulces", 78, 18),
    ("Hot cakes con miel", "Desayunos dulces", 85, 18),
    ("Jugo de naranja natural", "Bebidas", 45, 22),
    ("Frappé de chocolate", "Bebidas", 68, 22),
    ("Chocolate con malvaviscos", "Bebidas", 58, 22),
    ("Té de canela", "Bebidas", 35, 20),
    ("Flan de caramelo individual", "Pasteles y postres", 48, 18),
    ("Pay de manzana porción", "Pasteles y postres", 52, 18),
    ("Helado de tres sabores", "Helados y fríos", 65, 18),
    ("Macarons surtidos (3 piezas)", "Especialidades", 60, 20),
    ("Gorro de cumpleaños", "Accesorios", 25, 25),
    ("Velas para pastel", "Accesorios", 22, 25),
    ("Topper Feliz Cumpleaños", "Accesorios", 45, 20),
    ("Platos desechables para pastel (10 piezas)", "Accesorios", 32, 15),
    ("Servilletas decoradas (20 piezas)", "Accesorios", 30, 15),
]


def clasificar_producto(nombre, categoria):

    if categoria in CATEGORIAS[1:]:
        return categoria
    n = nombre.casefold()
    if any(p in n for p in ("gorrito", "gorro", "vela", "topper", "servilleta", "plato desechable", "accesorio")):
        return "Accesorios"
    if any(p in n for p in ("helado", "malteada", "sundae")):
        return "Helados y fríos"
    if categoria == "Café y bebidas":
        return "Bebidas"
    if any(p in n for p in ("galleta", "brownie")):
        return "Galletas y brownies"
    if any(p in n for p in ("hot cake", "pancake", "waffle", "crepa", "dona")):
        return "Desayunos dulces"
    if any(p in n for p in ("panqué", "croissant", "muffin", "pan fresco", "pan dulce", "pan ", "baguette", "concha", "rol de canela")):
        return "Panadería"
    if categoria == "Pasteles":
        return "Pasteles y postres"
    if any(p in n for p in ("pastel", "tarta", "pay ", "flan", "gelatina", "cheesecake", "tiramisú")):
        return "Pasteles y postres"
    if categoria == "Panadería":
        return "Panadería"
    if categoria == "Bocaditos salados":
        return "Panadería"
    return "Especialidades"
