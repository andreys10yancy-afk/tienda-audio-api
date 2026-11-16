from django.urls import path

from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("api/categorias/", views.categorias, name="api_categorias"),
    path("api/marcas/", views.marcas, name="api_marcas"),
    path("api/productos/", views.productos, name="api_productos"),
    path("api/productos/<int:pk>/", views.producto_detalle, name="api_producto"),
]
