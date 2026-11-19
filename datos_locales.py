
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import copy
import hashlib
import hmac
import json
import os
from pathlib import Path
import shutil
import tempfile

from catalogo import CATALOGO
from categorias_tienda import NOVEDADES, clasificar_producto

CENT = Decimal("0.01")
IVA = Decimal("0.16")
ROLES = ("Administrador", "Cajero", "Inventario")
ITERACIONES = 150_000


def _moneda(v):
    return Decimal(str(v)).quantize(CENT, rounding=ROUND_HALF_UP)


def _clave_nueva(clave, minimo=6):
    if not isinstance(clave, str) or len(clave) < minimo or len(clave) > 128:
        raise ValueError("La contraseña debe tener entre 6 y 128 caracteres.")
    sal = os.urandom(16)
    resultado = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, ITERACIONES)
    return {"salt": sal.hex(), "hash": resultado.hex()}


def _verificar(clave, registro):
    try:
        valor = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"),
                                   bytes.fromhex(registro["salt"]), ITERACIONES)
        return hmac.compare_digest(valor, bytes.fromhex(registro["hash"]))
    except (KeyError, ValueError, TypeError):
        return False


class TiendaDatos:

    def __init__(self, ruta=None):
        self.ruta = Path(ruta) if ruta else Path(__file__).resolve().parent / "data" / "tienda_datos.json"
        if self.ruta.exists():
            self._cargar(self.ruta)
            self._actualizar_categorias()
        elif self.ruta.with_suffix(".bak").exists():
            self._cargar(self.ruta.with_suffix(".bak"))
            self._actualizar_categorias()
            self.guardar()
        else:
            self.usuarios = {
                "admin": {"rol": "Administrador", **_clave_nueva("1234", minimo=1)},
                "cajero": {"rol": "Cajero", **_clave_nueva("1234", minimo=1)},
                "inventario": {"rol": "Inventario", **_clave_nueva("1234", minimo=1)},
            }
            self.clientes = {
                "C001": {"nombre": "Ana García", "telefono": "7751234567"},
                "C002": {"nombre": "Luis Martínez", "telefono": "7757654321"},
            }
            self.productos = {
                f"P{i:03d}": {"nombre": nombre, "categoria": categoria,
                               "precio": _moneda(precio), "stock": int(stock)}
                for i, (nombre, categoria, precio, stock) in enumerate(CATALOGO, 1)
            }
            self.ventas = []
            self.secuencia_venta = 0
            self.edicion_catalogo = 2
            self.guardar()

    def _actualizar_categorias(self):

        if self.edicion_catalogo >= 2:
            return
        for producto in self.productos.values():
            producto["categoria"] = clasificar_producto(producto["nombre"], producto["categoria"])
        nombres = {p["nombre"].casefold() for p in self.productos.values()}
        numero = max((int(c[1:]) for c in self.productos if c.startswith("P") and c[1:].isdigit()), default=0)
        for nombre, categoria, precio, stock in NOVEDADES:
            if nombre.casefold() in nombres:
                continue
            numero += 1
            codigo = f"P{numero:03d}"
            while codigo in self.productos:
                numero += 1
                codigo = f"P{numero:03d}"
            self.productos[codigo] = {"nombre": nombre, "categoria": categoria,
                                     "precio": _moneda(precio), "stock": stock}
            nombres.add(nombre.casefold())
        self.edicion_catalogo = 2
        self.guardar()

    def _cargar(self, ruta):
        try:
            raw = json.loads(ruta.read_text(encoding="utf-8"))
            if raw.get("version") != 1:
                raise ValueError("Formato de datos desconocido")
            self.usuarios = raw["usuarios"]
            self.clientes = raw["clientes"]
            self.productos = {k: {**p, "precio": _moneda(p["precio"])}
                              for k, p in raw["productos"].items()}
            self.ventas = []
            for venta in raw["ventas"]:
                venta = dict(venta)
                venta["subtotal"] = _moneda(venta["subtotal"])
                venta["iva"] = _moneda(venta["iva"])
                venta["total"] = _moneda(venta["total"])
                venta["detalle"] = [{**item, "precio": _moneda(item["precio"]),
                                     "importe": _moneda(item["importe"])}
                                    for item in venta["detalle"]]
                self.ventas.append(venta)
            self.secuencia_venta = int(raw.get("secuencia_venta", len(self.ventas)))
            self.edicion_catalogo = int(raw.get("edicion_catalogo", 1))
        except (OSError, ValueError, TypeError, KeyError) as exc:
            raise RuntimeError(f"No se pueden leer los datos en {ruta}. No se han borrado.\n{exc}") from exc

    def _serializar(self):
        def monetizar(obj):
            if isinstance(obj, Decimal):
                return str(obj)
            if isinstance(obj, dict):
                return {k: monetizar(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [monetizar(v) for v in obj]
            return obj
        return monetizar({
            "version": 1, "edicion_catalogo": self.edicion_catalogo, "secuencia_venta": self.secuencia_venta,
            "usuarios": self.usuarios, "clientes": self.clientes,
            "productos": self.productos, "ventas": self.ventas,
        })

    def guardar(self):

        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.ruta.parent,
                                             prefix="._tienda_", suffix=".tmp", delete=False) as archivo:
                temporal = Path(archivo.name)
                json.dump(self._serializar(), archivo, ensure_ascii=False, indent=2)
                archivo.flush()
                os.fsync(archivo.fileno())
            if self.ruta.exists():
                shutil.copy2(self.ruta, self.ruta.with_suffix(".bak"))
            os.replace(temporal, self.ruta)
        finally:
            if temporal is not None and temporal.exists():
                temporal.unlink()

    def _cambio(self, accion):
        anterior = (copy.deepcopy(self.usuarios), copy.deepcopy(self.clientes),
                    copy.deepcopy(self.productos), copy.deepcopy(self.ventas), self.secuencia_venta)
        try:
            resultado = accion()
            self.guardar()
            return resultado
        except Exception:
            self.usuarios, self.clientes, self.productos, self.ventas, self.secuencia_venta = anterior
            raise

    def iniciar_sesion(self, usuario, clave):
        registro = self.usuarios.get(usuario.strip())
        return registro["rol"] if registro and _verificar(clave, registro) else None

    def crear_o_editar_usuario(self, nombre, rol, contrasena="", actual=None):
        nombre = nombre.strip().lower()
        if not nombre or not nombre.replace("_", "").isalnum():
            raise ValueError("El usuario solo puede contener letras, números y guion bajo.")
        if rol not in ROLES:
            raise ValueError("Selecciona un puesto válido.")
        if nombre in self.usuarios and not contrasena:
            nuevo = dict(self.usuarios[nombre])
        else:
            if not contrasena:
                raise ValueError("Escribe una contraseña para la cuenta nueva.")
            nuevo = _clave_nueva(contrasena)
        nuevo["rol"] = rol
        if nombre in self.usuarios and self.usuarios[nombre]["rol"] == "Administrador" and rol != "Administrador":
            if sum(u["rol"] == "Administrador" for u in self.usuarios.values()) <= 1:
                raise ValueError("Debe quedar al menos un administrador.")
        return self._cambio(lambda: self.usuarios.__setitem__(nombre, nuevo))

    def eliminar_usuario(self, nombre, usuario_actual):
        if nombre == usuario_actual:
            raise ValueError("No puedes eliminar la cuenta con la que iniciaste sesión.")
        if nombre not in self.usuarios:
            raise ValueError("Ese usuario no existe.")
        if self.usuarios[nombre]["rol"] == "Administrador" and sum(
                x["rol"] == "Administrador" for x in self.usuarios.values()) <= 1:
            raise ValueError("Debe quedar al menos un administrador.")
        return self._cambio(lambda: self.usuarios.pop(nombre))

    def cambiar_contrasena(self, usuario, anterior, nueva):
        if not self.iniciar_sesion(usuario, anterior):
            raise ValueError("La contraseña actual es incorrecta.")
        nuevo = _clave_nueva(nueva)
        return self._cambio(lambda: self.usuarios[usuario].update(nuevo))

    def guardar_cliente(self, codigo, nombre, telefono):
        codigo, nombre, telefono = codigo.strip().upper(), nombre.strip(), telefono.strip()
        if not codigo or not nombre:
            raise ValueError("Es obligatorio escribir código y nombre del cliente.")
        if telefono and (len(telefono) != 10 or not telefono.isdigit()):
            raise ValueError("El teléfono debe tener 10 dígitos o dejarse vacío.")
        return self._cambio(lambda: self.clientes.__setitem__(codigo, {"nombre": nombre, "telefono": telefono}))

    def eliminar_cliente(self, codigo):
        if codigo not in self.clientes:
            raise ValueError("Cliente no encontrado.")
        return self._cambio(lambda: self.clientes.pop(codigo))

    def guardar_producto(self, codigo, nombre, categoria, precio, stock):
        codigo, nombre = codigo.strip().upper(), nombre.strip()
        if not codigo or not nombre:
            raise ValueError("Es obligatorio escribir código y nombre del producto.")
        try:
            p = _moneda(str(precio).strip().replace(",", "."))
            if not p.is_finite() or p <= 0:
                raise ValueError
        except (InvalidOperation, ValueError):
            raise ValueError("El precio debe ser un número mayor que cero.")
        try:
            cantidad = int(str(stock).strip())
            if cantidad < 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValueError("El stock debe ser un número entero igual o mayor a cero.")
        return self._cambio(lambda: self.productos.__setitem__(codigo, {
            "nombre": nombre, "categoria": categoria or "Otros", "precio": p, "stock": cantidad,
        }))

    def eliminar_producto(self, codigo):
        if codigo not in self.productos:
            raise ValueError("Producto no encontrado.")
        return self._cambio(lambda: self.productos.pop(codigo))

    def calcular_carrito(self, carrito):
        if not carrito:
            raise ValueError("Agrega algún producto al carrito.")
        detalle = []
        for codigo, n in carrito.items():
            producto = self.productos.get(codigo)
            if not producto:
                raise ValueError(f"Producto {codigo} ya no disponible.")
            if not isinstance(n, int) or n <= 0 or n > producto["stock"]:
                raise ValueError(f"Cantidad sin existencias para {producto['nombre']}.")
            importe = _moneda(producto["precio"] * n)
            detalle.append({"codigo": codigo, "nombre": producto["nombre"],
                            "cantidad": n, "precio": producto["precio"], "importe": importe})
        subtotal = _moneda(sum((fila["importe"] for fila in detalle), Decimal(0)))
        iva = _moneda(subtotal * IVA)
        total = subtotal + iva
        return detalle, subtotal, iva, total

    def previsualizar_venta(self, carrito, cliente_id, vendedor):
        if cliente_id not in self.clientes:
            raise ValueError("Selecciona un cliente registrado.")
        detalle, subtotal, iva, total = self.calcular_carrito(carrito)
        return {"folio": "VISTA PREVIA (SIN COBRAR)", "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "cliente": self.clientes[cliente_id]["nombre"], "vendedor": vendedor,
                "detalle": detalle, "subtotal": subtotal, "iva": iva, "total": total}

    def realizar_venta(self, carrito, cliente_id, vendedor):
        previa = self.previsualizar_venta(carrito, cliente_id, vendedor)
        def accion():
            self.secuencia_venta += 1
            venta = {**previa, "folio": f"V{self.secuencia_venta:04d}"}
            for item in venta["detalle"]:
                self.productos[item["codigo"]]["stock"] -= item["cantidad"]
            self.ventas.append(venta)
            return venta
        return self._cambio(accion)
