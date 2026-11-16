"""
API REST de CONSULTA (solo GET) para la tienda de equipos de audio.

Endpoints:
    GET /api/categorias/
    GET /api/marcas/
    GET /api/productos/            (con filtros, orden y paginación)
    GET /api/productos/<id>/
"""
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET

from .models import Categoria, Marca, Producto


# ---------- Serializadores (convierten objetos Django -> diccionarios) ----------

def serializar_categoria(c):
    return {"id": c.id, "nombre": c.nombre, "slug": c.slug}


def serializar_marca(m):
    return {"id": m.id, "nombre": m.nombre, "pais": m.pais}


def serializar_producto(p):
    return {
        "id": p.id,
        "nombre": p.nombre,
        "descripcion": p.descripcion,
        "precio": float(p.precio),
        "stock": p.stock,
        "disponible": p.stock > 0,
        "imagen_url": p.imagen_url,
        "destacado": p.destacado,
        "categoria": serializar_categoria(p.categoria),
        "marca": serializar_marca(p.marca),
    }


def error(mensaje, status):
    return JsonResponse({"error": mensaje}, status=status)


# ---------- Endpoints ----------

@require_GET
def categorias(request):
    datos = [serializar_categoria(c) for c in Categoria.objects.all()]
    return JsonResponse({"count": len(datos), "results": datos})


@require_GET
def marcas(request):
    datos = [serializar_marca(m) for m in Marca.objects.all()]
    return JsonResponse({"count": len(datos), "results": datos})


ORDENES = {
    "nombre": "nombre",
    "precio_asc": "precio",
    "precio_desc": "-precio",
    "recientes": "-creado",
}


@require_GET
def productos(request):
    qs = Producto.objects.select_related("categoria", "marca")
    g = request.GET

    # Filtros
    if g.get("categoria"):
        qs = qs.filter(categoria__slug=g["categoria"])
    if g.get("marca"):
        qs = qs.filter(marca__id=g["marca"]) if g["marca"].isdigit() else qs.filter(
            marca__nombre__iexact=g["marca"]
        )
    if g.get("q"):
        qs = qs.filter(
            Q(nombre__icontains=g["q"])
            | Q(descripcion__icontains=g["q"])
            | Q(marca__nombre__icontains=g["q"])
        )
    if g.get("destacado") in ("1", "true"):
        qs = qs.filter(destacado=True)
    if g.get("disponible") in ("1", "true"):
        qs = qs.filter(stock__gt=0)
    try:
        if g.get("precio_min"):
            qs = qs.filter(precio__gte=float(g["precio_min"]))
        if g.get("precio_max"):
            qs = qs.filter(precio__lte=float(g["precio_max"]))
    except ValueError:
        return error("precio_min y precio_max deben ser números", 400)

    # Orden
    orden = g.get("orden", "nombre")
    if orden not in ORDENES:
        return error(f"orden inválido. Opciones: {', '.join(ORDENES)}", 400)
    qs = qs.order_by(ORDENES[orden])

    # Paginación
    try:
        tam = min(max(int(g.get("tam", 6)), 1), 50)
        pagina = max(int(g.get("page", 1)), 1)
    except ValueError:
        return error("page y tam deben ser enteros", 400)
    pag = Paginator(qs, tam)
    if pagina > pag.num_pages:
        pagina = pag.num_pages
    obj = pag.page(pagina)

    return JsonResponse(
        {
            "count": pag.count,
            "page": obj.number,
            "total_pages": pag.num_pages,
            "results": [serializar_producto(p) for p in obj.object_list],
        }
    )


@require_GET
def producto_detalle(request, pk):
    try:
        p = Producto.objects.select_related("categoria", "marca").get(pk=pk)
    except Producto.DoesNotExist:
        return error("Producto no encontrado", 404)
    return JsonResponse(serializar_producto(p))


# ---------- Frontend (página HTML que consume la API) ----------

def inicio(request):
    return render(request, "catalogo/index.html")
