# ============================================
# PuriPOS Server v1.0
# Servidor central para dashboard movil
# ============================================

import os, json
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string, abort

app = Flask(__name__)

# Clave secreta para autenticar el POS
SECRET_KEY = os.environ.get("PURIPOS_SECRET", "puripos2026")

# Almacenamiento en memoria — datos por local
datos_locales = {}

# ── HTML Dashboard ──────────────────────────
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PuriPOS Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
     background:#0f172a;color:#f1f5f9;padding:16px;min-height:100vh}
.local{font-size:20px;font-weight:600}
.fecha{font-size:13px;color:#64748b;margin-top:2px}
.neto{font-size:42px;font-weight:700;color:#10b981;margin:16px 0 4px}
.neto-lbl{font-size:12px;color:#64748b;text-transform:uppercase;letter-spacing:.5px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:16px 0}
.card{background:#1e293b;border-radius:10px;padding:14px}
.card-lbl{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px}
.card-val{font-size:20px;font-weight:600}
.seccion{background:#1e293b;border-radius:10px;padding:14px;margin-bottom:10px}
.sec-title{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.5px;margin-bottom:10px}
.fila{display:flex;justify-content:space-between;align-items:center;
      padding:7px 0;border-bottom:0.5px solid #334155;font-size:14px}
.fila:last-child{border-bottom:none}
.bar-bg{background:#334155;border-radius:3px;height:4px;margin-top:4px}
.bar{height:4px;border-radius:3px}
.alerta-item{display:flex;align-items:center;gap:8px;
             padding:7px 0;border-bottom:0.5px solid #334155;font-size:13px}
.alerta-item:last-child{border-bottom:none}
.dot-r{width:8px;height:8px;border-radius:50%;background:#ef4444;flex-shrink:0}
.dot-o{width:8px;height:8px;border-radius:50%;background:#f59e0b;flex-shrink:0}
.cajero{display:flex;align-items:center;gap:10px}
.avatar{width:36px;height:36px;border-radius:50%;background:#3b82f6;
        display:flex;align-items:center;justify-content:center;
        font-size:14px;font-weight:600}
.footer{text-align:center;font-size:11px;color:#475569;margin-top:16px}
.offline{background:#fef2f2;border:1px solid #fecaca;border-radius:8px;
         padding:12px;margin-bottom:12px;font-size:13px;color:#dc2626;
         text-align:center}
.stock-item{display:flex;justify-content:space-between;align-items:center;
            padding:8px 0;border-bottom:0.5px solid #334155;font-size:13px}
.stock-item:last-child{border-bottom:none}
.stock-sym{width:20px;text-align:center;flex-shrink:0}
</style>
</head>
<body>
<div id="app">Cargando...</div>
<script>
const LOCAL = "{{local_id}}";
function fmt(n){return '$'+Math.round(n).toLocaleString('es-CL')}
function render(d){
  if(!d||d.error){
    document.getElementById('app').innerHTML=
      '<div class="offline">Sin datos disponibles.<br>El POS puede estar offline.</div>';
    return;
  }
  const cols={'Efectivo':'#10b981','Debito/Tarjeta':'#3b82f6',
              'Debito':'#3b82f6','Transferencia':'#8b5cf6','Mixto':'#f59e0b'};
  const tot=Object.values(d.totales||{}).reduce((a,b)=>a+b,0)||1;
  let mHTML=Object.entries(d.totales||{}).map(([m,v])=>{
    const c=cols[m]||'#64748b',p=Math.round(v/tot*100);
    return`<div class="fila"><span>${m}</span><div style="text-align:right">
    <span style="color:${c};font-weight:500">${fmt(v)}</span>
    <span style="color:#64748b;font-size:12px"> ${p}%</span>
    <div class="bar-bg"><div class="bar" style="width:${p}%;background:${c}"></div></div>
    </div></div>`;}).join('') || '<div style="color:#64748b;font-size:13px">Sin ventas</div>';
  const tc=['#10b981','#3b82f6','#8b5cf6','#f59e0b','#ef4444'];
  const mx=d.top5&&d.top5.length>0?d.top5[0][1]:1;
  let tHTML=d.top5&&d.top5.length>0?d.top5.map(([p,u],i)=>{
    const pct=Math.round(u/mx*100);
    return`<div class="fila"><div>
    <span style="color:${tc[i]};font-weight:500;margin-right:6px">${i+1}.</span>${p.substring(0,22)}
    <div class="bar-bg"><div class="bar" style="width:${pct}%;background:${tc[i]}"></div></div>
    </div><span style="color:${tc[i]};font-weight:500">${u} uds</span></div>`;}).join('')
    :'<div style="color:#64748b;font-size:13px;padding:8px 0">Sin ventas hoy</div>';
  let aHTML=d.alertas&&d.alertas.length>0?d.alertas.map(a=>
    `<div class="alerta-item"><div class="${a.critico?'dot-r':'dot-o'}"></div>
    <div><div>${a.nombre}</div>
    <div style="font-size:11px;color:#64748b">${a.critico?'SIN STOCK':'Stock: '+a.stock+' '+a.unidad+' (min: '+a.minimo+')'}</div>
    </div></div>`).join('')
    :'<div style="color:#10b981;font-size:13px;padding:8px 0">&#10003; Sin alertas</div>';
  const ini=d.cajero&&d.cajero!=='—'?d.cajero.substring(0,2).toUpperCase():'?';
  const ultima=d.ultima_actualizacion||'—';
  document.getElementById('app').innerHTML=`
    <div class="local">&#127981; ${d.local||LOCAL}</div>
    <div class="fecha">${d.fecha||'—'} &middot; Ultima sync: ${ultima}</div>
    <div class="neto-lbl" style="margin-top:16px">neto del dia</div>
    <div class="neto">${fmt(d.neto||0)}</div>
    <div class="grid">
      <div class="card"><div class="card-lbl">pedidos</div>
        <div class="card-val" style="color:#8b5cf6">${d.n_pedidos||0}</div></div>
      <div class="card"><div class="card-lbl">ticket prom.</div>
        <div class="card-val" style="color:#f59e0b">${fmt(d.ticket_prom||0)}</div></div>
    </div>
    <div class="seccion"><div class="sec-title">ventas por metodo</div>${mHTML}</div>
    <div class="seccion"><div class="sec-title">top productos</div>${tHTML}</div>
    <div class="seccion"><div class="sec-title">cajero activo</div>
      <div class="cajero"><div class="avatar">${ini}</div>
      <span>${d.cajero||'—'}</span></div></div>
    ${d.alertas&&d.alertas.length>0?
      `<div class="seccion" style="border:0.5px solid #ef4444">
        <div class="sec-title" style="color:#ef4444">alertas stock</div>${aHTML}</div>`
      :`<div class="seccion"><div class="sec-title">stock</div>${aHTML}</div>`}
    ${d.inventario&&d.inventario.length>0?`
    <div class="seccion">
      <div class="sec-title">stock bodega</div>
      ${d.inventario.map(p=>{
        const sym = p.critico ? '&#10060;' : p.bajo ? '&#9888;' : '&#10003;';
        const col = p.critico ? '#ef4444' : p.bajo ? '#f59e0b' : '#10b981';
        const mn  = p.minimo>0 ? ` <span style="color:#64748b;font-size:11px">mín:${p.minimo}${p.unidad}</span>` : '';
        return \`<div class="stock-item">
          <div><span class="stock-sym" style="color:\${col}">\${sym}</span> \${p.nombre}</div>
          <div style="text-align:right">
            <span style="color:\${col};font-weight:500">\${p.stock} \${p.unidad}</span>\${mn}
          </div></div>\`;
      }).join('')}
    </div>`:''}
    <div class="footer">Puri_POS v1.0</div>
    <div style="text-align:center;font-size:11px;color:#334155;margin-top:4px">
      Se actualiza cada 5 min</div>`;
}
function cargar(){
  fetch('/api/'+LOCAL)
    .then(r=>r.json())
    .then(d=>render(d))
    .catch(()=>render(null));
}
cargar();
setInterval(cargar,300000);
</script>
</body>
</html>"""

# ── Rutas ────────────────────────────────────

@app.route('/<local_id>')
def dashboard(local_id):
    local_id = local_id.upper()
    return render_template_string(HTML, local_id=local_id)

@app.route('/api/<local_id>')
def get_datos(local_id):
    local_id = local_id.upper()
    datos = datos_locales.get(local_id)
    if not datos:
        return jsonify({"error": "sin datos", "local": local_id})
    return jsonify(datos)

@app.route('/api/<local_id>/push', methods=['POST'])
def push_datos(local_id):
    local_id = local_id.upper()
    # Verificar clave secreta
    auth = request.headers.get("X-PuriPOS-Key","")
    if auth != SECRET_KEY:
        abort(401)
    try:
        datos = request.get_json()
        datos["ultima_actualizacion"] = datetime.now().strftime("%H:%M")
        datos_locales[local_id] = datos
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/ping')
def ping():
    return jsonify({"ok": True, "locales": list(datos_locales.keys())})

@app.route('/')
def index():
    return jsonify({
        "sistema": "PuriPOS Server v1.0",
        "uso": "Accede a /<codigo_local> para ver el dashboard"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
