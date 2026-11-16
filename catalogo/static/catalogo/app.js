/*
 * FRONTEND: consulta la API REST con fetch() y pinta los resultados.
 * No toca la base de datos: solo habla con /api/...
 */
const el = (id) => document.getElementById(id);
const ICONOS = {
  audifonos: "🎧", iems: "🎵", parlantes: "🔊",
  "dacs-amplificadores": "🔌", microfonos: "🎙️", "interfaces-audio": "🎚️",
};
const cop = (n) =>
  new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(n);

let paginaActual = 1;

// Función genérica: hace GET a la API y devuelve el JSON
async function api(url) {
  const resp = await fetch(url);
  const datos = await resp.json();
  if (!resp.ok) throw new Error(datos.error || "Error en la API");
  return datos;
}

function mostrarEstado(msg) {
  const e = el("estado");
  e.textContent = msg;
  e.hidden = !msg;
}

// 1) Llenar los <select> con /api/categorias/ y /api/marcas/
async function cargarFiltros() {
  const [cats, marcas] = await Promise.all([api("/api/categorias/"), api("/api/marcas/")]);
  cats.results.forEach((c) => el("categoria").add(new Option(c.nombre, c.slug)));
  marcas.results.forEach((m) => el("marca").add(new Option(m.nombre, m.id)));
}

// 2) Construir la URL con los filtros y consultar /api/productos/
async function cargarProductos(pagina = 1) {
  paginaActual = pagina;
  const params = new URLSearchParams({ page: pagina, orden: el("orden").value });
  if (el("q").value.trim()) params.set("q", el("q").value.trim());
  if (el("categoria").value) params.set("categoria", el("categoria").value);
  if (el("marca").value) params.set("marca", el("marca").value);
  if (el("precio_max").value) params.set("precio_max", el("precio_max").value);
  if (el("disponible").checked) params.set("disponible", "1");
  if (el("destacado").checked) params.set("destacado", "1");

  mostrarEstado("Cargando…");
  try {
    const data = await api("/api/productos/?" + params.toString());
    mostrarEstado("");
    pintarProductos(data);
    pintarPaginacion(data);
  } catch (err) {
    mostrarEstado("⚠️ " + err.message);
  }
}

function pintarProductos(data) {
  el("resumen").textContent = `${data.count} producto(s) encontrado(s)`;
  const cont = el("productos");
  if (data.results.length === 0) {
    cont.innerHTML = "";
    mostrarEstado("No hay productos con esos filtros.");
    return;
  }
  cont.innerHTML = data.results.map((p) => `
    <div class="cell">
      <article class="tarjeta">
        <div class="img">${ICONOS[p.categoria.slug] || "🎧"}</div>
        <div class="cuerpo">
          <span class="marca-nombre">${p.marca.nombre} · ${p.categoria.nombre}</span>
          <h3>${p.nombre}${p.destacado ? '<span class="etiqueta-dest">Destacado</span>' : ""}</h3>
          <p class="desc">${p.descripcion}</p>
          <div class="precio">${cop(p.precio)}</div>
          <p><span class="label ${p.disponible ? "success" : "alert"}">
            ${p.disponible ? p.stock + " en stock" : "Agotado"}</span></p>
          <button class="button expanded" data-id="${p.id}">Ver detalle</button>
        </div>
      </article>
    </div>`).join("");
}

function pintarPaginacion(data) {
  const ul = el("paginacion");
  let html = "";
  for (let i = 1; i <= data.total_pages; i++) {
    html += i === data.page
      ? `<li class="current"><span>${i}</span></li>`
      : `<li><a href="#" data-pag="${i}">${i}</a></li>`;
  }
  ul.innerHTML = data.total_pages > 1 ? html : "";
}

// 3) Detalle: GET /api/productos/<id>/
async function verDetalle(id) {
  try {
    const p = await api(`/api/productos/${id}/`);
    el("detalle-contenido").innerHTML = `
      <h2>${p.nombre}</h2>
      <p><strong>Marca:</strong> ${p.marca.nombre} (${p.marca.pais})<br>
         <strong>Categoría:</strong> ${p.categoria.nombre}</p>
      <p>${p.descripcion}</p>
      <p class="precio"><strong>${cop(p.precio)}</strong></p>
      <p>${p.disponible ? p.stock + " unidades disponibles" : "Producto agotado"}</p>`;
    jQuery("#modal-detalle").foundation("open");
  } catch (err) {
    mostrarEstado("⚠️ " + err.message);
  }
}

// ---- Eventos ----
let temporizador;
function consultarConRetraso() {
  clearTimeout(temporizador);
  temporizador = setTimeout(() => cargarProductos(1), 300);
}

document.addEventListener("DOMContentLoaded", async () => {
  el("filtros").addEventListener("submit", (e) => e.preventDefault());
  el("q").addEventListener("input", consultarConRetraso);
  el("precio_max").addEventListener("input", consultarConRetraso);
  ["categoria", "marca", "orden", "disponible", "destacado"].forEach((id) =>
    el(id).addEventListener("change", () => cargarProductos(1))
  );
  el("limpiar").addEventListener("click", () => {
    el("filtros").reset();
    cargarProductos(1);
  });
  el("paginacion").addEventListener("click", (e) => {
    const a = e.target.closest("a[data-pag]");
    if (a) { e.preventDefault(); cargarProductos(Number(a.dataset.pag)); window.scrollTo(0, 0); }
  });
  el("productos").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-id]");
    if (b) verDetalle(b.dataset.id);
  });

  await cargarFiltros();
  await cargarProductos(1);
});

// Foundation (jQuery) se inicializa al cargar
if (window.jQuery) jQuery(document).foundation();
