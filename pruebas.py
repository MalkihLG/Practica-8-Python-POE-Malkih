
from pathlib import Path
from tempfile import TemporaryDirectory
from decimal import Decimal
import json
from datos_locales import TiendaDatos
from main import texto_ticket


def ejecutar():
    with TemporaryDirectory() as carpeta:
        ruta=Path(carpeta)/"data"/"tienda_datos.json"
        d=TiendaDatos(ruta)
        assert len(d.productos)==137
        assert d.iniciar_sesion("admin","1234")=="Administrador"
        assert d.iniciar_sesion("cajero","1234")=="Cajero"
        assert d.iniciar_sesion("inventario","1234")=="Inventario"
        assert d.iniciar_sesion("admin","otra") is None
        assert '"1234"' not in ruta.read_text(encoding='utf8')
        d.guardar_cliente('C010','Elena Rosales','7751234567')
        d.guardar_producto('P999','Muffin de fresa','Repostería','27.50','10')
        d.crear_o_editar_usuario('supervisor','Inventario','suClave2026')
        d.cambiar_contrasena('cajero','1234','NuevaClaveSegura')
        assert d.iniciar_sesion('cajero','1234') is None
        assert d.iniciar_sesion('cajero','NuevaClaveSegura')=='Cajero'
        carrito={'P999':2,'P001':1}
        previo=d.previsualizar_venta(carrito,'C010','cajero')
        assert previo['subtotal']==Decimal('405.00')
        assert previo['iva']==Decimal('64.80')
        assert previo['total']==Decimal('469.80')
        assert len(d.ventas)==0
        stock_orig=d.productos['P999']['stock']
        venta=d.realizar_venta(carrito,'C010','cajero')
        assert venta['folio']=='V0001'
        assert d.productos['P999']['stock']==stock_orig-2
        ticket=texto_ticket(venta)
        assert 'IVA (16 %)' in ticket and '$469.80' in ticket
        d2=TiendaDatos(ruta)
        assert d2.clientes['C010']['nombre']=='Elena Rosales'
        assert d2.productos['P999']['stock']==8
        assert d2.iniciar_sesion('supervisor','suClave2026')=='Inventario'
        assert d2.iniciar_sesion('cajero','NuevaClaveSegura')=='Cajero'
        assert len(d2.ventas)==1 and d2.ventas[0]['total']==Decimal('469.80')
        assert d2.realizar_venta({'P999':1},'C010','admin')['folio']=='V0002'
        d2.eliminar_producto('P999')
        d2.eliminar_cliente('C010')
        d3=TiendaDatos(ruta)
        assert 'P999' not in d3.productos
        assert 'C010' not in d3.clientes
        assert len(d3.ventas)==2
        assert d3.iniciar_sesion('admin','1234')=='Administrador'
        assert ruta.with_suffix('.bak').exists()
        assert json.loads(ruta.read_text(encoding='utf8'))['version']==1
        try:
            d3.eliminar_usuario('admin','cajero')
        except ValueError:
            pass
        else:
            raise AssertionError('No debe eliminar al último administrador')
        print('OK: se guardan y recuperan clientes, productos, usuarios, roles, contraseñas, ventas, stock y ticket/IVA.')

if __name__=='__main__':
    ejecutar()
