# SonidoPro — API REST de consulta (tienda de equipos de audio)

**Stack:** Django (backend) · PostgreSQL (base de datos) · Foundation (CSS) · JavaScript `fetch` (frontend)

## 1. ¿Qué es una API REST de consulta?
Un "mesero" entre el frontend y la base de datos. El frontend **pide** datos por una URL
(método **GET**) y el backend responde en **JSON**. "De consulta" = solo lee (no crea ni borra).

```
Navegador (Foundation + JS) --GET /api/productos/--> Django --SQL--> PostgreSQL
                           <------- JSON ----------        <-------- filas
```

## 2. Endpoints

| Método | URL | Descripción |
|---|---|---|
| GET | `/api/categorias/` | Lista de categorías |
| GET | `/api/marcas/` | Lista de marcas |
| GET | `/api/productos/` | Lista de productos (filtros, orden, paginación) |
| GET | `/api/productos/<id>/` | Detalle de un producto |

Parámetros de `/api/productos/`:

| Parámetro | Ejemplo | Qué hace |
|---|---|---|
| `q` | `?q=sony` | Busca en nombre, descripción y marca |
| `categoria` | `?categoria=audifonos` | Filtra por slug de categoría |
| `marca` | `?marca=3` o `?marca=Sony` | Filtra por id o nombre de marca |
| `precio_min`, `precio_max` | `?precio_max=500000` | Rango de precio (COP) |
| `disponible` | `?disponible=1` | Solo con stock |
| `destacado` | `?destacado=1` | Solo destacados |
| `orden` | `?orden=precio_desc` | `nombre`, `precio_asc`, `precio_desc`, `recientes` |
| `page`, `tam` | `?page=2&tam=6` | Paginación |

Códigos de respuesta: `200` OK · `400` parámetro inválido · `404` producto no existe.

Ejemplo de respuesta (`/api/productos/3/`):
```json
{
  "id": 3, "nombre": "ATH-M50x", "precio": 640000.0, "stock": 20, "disponible": true,
  "categoria": {"id": 1, "nombre": "Audífonos", "slug": "audifonos"},
  "marca": {"id": 3, "nombre": "Audio-Technica", "pais": "Japón"}
}
```

## 3. Estructura del proyecto
```
config/settings.py        -> configuración (conexión a PostgreSQL)
catalogo/models.py        -> tablas: Categoria, Marca, Producto
catalogo/views.py         -> los endpoints de la API (devuelven JSON)
catalogo/urls.py          -> rutas /api/...
catalogo/templates/...    -> index.html (frontend con Foundation)
catalogo/static/...       -> app.js (fetch a la API) y styles.css
catalogo/management/commands/cargar_datos.py -> datos de ejemplo
```

## 4. Cómo correrlo

### a) Crear la base de datos en PostgreSQL
```sql
CREATE DATABASE tienda_audio;
```
(con pgAdmin o `psql -U postgres`). Si tu usuario/contraseña no son `postgres`/`postgres`,
cambia las variables de entorno `DB_USER` y `DB_PASSWORD` (o edita `config/settings.py`).

### b) Instalar y arrancar
```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt

python manage.py migrate        # crea las tablas en PostgreSQL
python manage.py cargar_datos   # inserta 14 productos de ejemplo
python manage.py createsuperuser  # (opcional) para entrar a /admin/
python manage.py runserver
```
Abre http://127.0.0.1:8000/ (frontend) y http://127.0.0.1:8000/api/productos/ (JSON).

> Para probar sin PostgreSQL: define `USE_SQLITE=1` antes de correr los comandos.

## 5. Pruebas rápidas del backend
```bash
curl "http://127.0.0.1:8000/api/productos/?categoria=audifonos&orden=precio_desc"
curl "http://127.0.0.1:8000/api/productos/?q=shure&disponible=1"
curl "http://127.0.0.1:8000/api/productos/999/"      # 404
```
