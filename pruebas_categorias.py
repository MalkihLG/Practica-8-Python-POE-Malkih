

assert len(CATALOGO)==137
assert set(GALERIA)==set(CATEGORIAS)-{'Todas'}
assert sum(map(len,GALERIA.values()))==18

with TemporaryDirectory() as carpeta:
 ruta=Path(carpeta)/'data'/'tienda_datos.json'
 t=TiendaDatos(ruta)
 t.guardar_cliente('C999','Cliente de prueba','7710000000')
 t.guardar_producto('P001','Pastel de tres leches','Pasteles','299.99','4')
 t.cambiar_contrasena('cajero','1234','NuevaClave2026')

 t.productos={k:p for k,p in t.productos.items()
              if p['nombre'] not in {n for n,_,_,_ in NOVEDADES}}
 t.edicion_catalogo=1
 t.guardar()
 recargada=TiendaDatos(ruta)
 assert recargada.productos['P001']['precio']==Decimal('299.99')
 assert recargada.productos['P001']['stock']==4
 assert recargada.productos['P001']['categoria']=='Pasteles y postres'
 assert recargada.clientes['C999']['nombre']=='Cliente de prueba'
 assert recargada.iniciar_sesion('cajero','NuevaClave2026')=='Cajero'
 assert len(recargada.productos)==137
 assert [p['nombre'] for p in recargada.productos.values()].count('Gorro de cumpleaños')==1
 siguiente=TiendaDatos(ruta)
 assert len(siguiente.productos)==137
 assert siguiente.edicion_catalogo==2
 assert ruta.with_suffix('.bak').exists()
 print('OK: 8 categorías, 18 ilustraciones y actualización conservadora de datos antiguos.')
