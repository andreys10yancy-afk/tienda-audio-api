from django.core.management.base import BaseCommand

from catalogo.models import Categoria, Marca, Producto

CATEGORIAS = [
    ("Audífonos", "audifonos"),
    ("IEMs", "iems"),
    ("Parlantes", "parlantes"),
    ("DACs y Amplificadores", "dacs-amplificadores"),
    ("Micrófonos", "microfonos"),
    ("Interfaces de audio", "interfaces-audio"),
]

MARCAS = [
    ("Sony", "Japón"),
    ("Sennheiser", "Alemania"),
    ("Audio-Technica", "Japón"),
    ("Focusrite", "Reino Unido"),
    ("JBL", "Estados Unidos"),
    ("FiiO", "China"),
    ("Shure", "Estados Unidos"),
    ("Kiwi Ears", "China"),
]

# (nombre, descripcion, precio COP, stock, categoria_slug, marca, destacado)
PRODUCTOS = [
    ("WH-1000XM5", "Audífonos inalámbricos con cancelación de ruido líder en su clase.", 1450000, 12, "audifonos", "Sony", True),
    ("HD 600", "Audífonos abiertos de referencia para escucha crítica.", 1250000, 8, "audifonos", "Sennheiser", True),
    ("ATH-M50x", "Audífonos de estudio cerrados, el estándar para monitoreo.", 640000, 20, "audifonos", "Audio-Technica", False),
    ("Quartet", "IEM de 4 drivers balanceados con sonido neutro y detallado.", 380000, 15, "iems", "Kiwi Ears", True),
    ("FiiO KA11", "DAC dongle USB-C con salida balanceada de 3.5 mm.", 210000, 30, "dacs-amplificadores", "FiiO", False),
    ("FiiO K7", "DAC/amplificador de escritorio con salida balanceada 4.4 mm.", 980000, 5, "dacs-amplificadores", "FiiO", True),
    ("Flip 6", "Parlante Bluetooth portátil, resistente al agua IP67.", 520000, 25, "parlantes", "JBL", False),
    ("PartyBox 110", "Parlante de fiesta con luces y hasta 12 horas de batería.", 1390000, 0, "parlantes", "JBL", False),
    ("SM58", "Micrófono dinámico vocal, un clásico de los escenarios.", 450000, 18, "microfonos", "Shure", False),
    ("SM7B", "Micrófono dinámico de estudio para voz, podcast y locución.", 2300000, 6, "microfonos", "Shure", True),
    ("Scarlett 2i2 (4ta gen)", "Interfaz de audio USB de 2 entradas y 2 salidas.", 890000, 14, "interfaces-audio", "Focusrite", True),
    ("Scarlett Solo (4ta gen)", "Interfaz de audio USB para grabar voz y guitarra.", 640000, 0, "interfaces-audio", "Focusrite", False),
    ("MDR-7506", "Audífonos de monitoreo profesional, plegables y resistentes.", 610000, 10, "audifonos", "Sony", False),
    ("HD 560S", "Audífonos abiertos con sonido natural y escenario amplio.", 780000, 9, "audifonos", "Sennheiser", False),
]


class Command(BaseCommand):
    help = "Carga categorías, marcas y productos de ejemplo (idempotente)."

    def handle(self, *args, **options):
        cats = {}
        for nombre, slug in CATEGORIAS:
            cats[slug], _ = Categoria.objects.get_or_create(
                slug=slug, defaults={"nombre": nombre}
            )
        marcas = {}
        for nombre, pais in MARCAS:
            marcas[nombre], _ = Marca.objects.get_or_create(
                nombre=nombre, defaults={"pais": pais}
            )
        creados = 0
        for nombre, desc, precio, stock, cat, marca, dest in PRODUCTOS:
            _, nuevo = Producto.objects.get_or_create(
                nombre=nombre,
                marca=marcas[marca],
                defaults={
                    "descripcion": desc,
                    "precio": precio,
                    "stock": stock,
                    "categoria": cats[cat],
                    "destacado": dest,
                },
            )
            creados += nuevo
        self.stdout.write(self.style.SUCCESS(f"Listo. Productos nuevos: {creados}"))
