# ============================================
# PuriPOS Server v2.0
# Dashboard móvil con datos completos
# ============================================

import os, json
from datetime import datetime
from flask import Flask, jsonify, request, render_template_string, abort

app = Flask(__name__)
SECRET_KEY = os.environ.get("PURIPOS_SECRET", "puripos2026")
datos_locales = {}

HTML = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<title>PuriPOS Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
     background:#0f172a;color:#f1f5f9;padding:12px;min-height:100vh;
     max-width:430px;margin:0 auto}
.local{font-size:18px;font-weight:600}
.fecha{font-size:11px;color:#64748b;margin-top:2px}
/* Período */
.periodo{display:flex;gap:6px;margin:10px 0}
.pbtn{flex:1;padding:7px;border-radius:8px;border:none;font-size:12px;
      font-weight:500;cursor:pointer;background:#1e293b;color:#64748b}
.pbtn.active{background:#10b981;color:white}
/* Turno */
.turno{display:flex;align-items:center;gap:10px;background:#1e293b;
       border-radius:10px;padding:10px 12px;margin-bottom:10px}
.avatar{width:34px;height:34px;border-radius:50%;background:#3b82f6;
        display:flex;align-items:center;justify-content:center;
        font-size:13px;font-weight:600;flex-shrink:0}
.turno-cajero{font-size:13px;font-weight:500}
.turno-sub{font-size:11px;color:#64748b;margin-top:1px}
/* Cards */
.card{background:#1e293b;border-radius:12px;padding:13px;margin-bottom:8px}
.sec{font-size:10px;color:#64748b;text-transform:uppercase;
     letter-spacing:.5px;margin-bottom:8px}
/* Total */
.total-lbl{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.5px}
.total-val{font-size:38px;font-weight:700;color:#10b981;margin:3px 0 2px}
.total-sub{font-size:11px;color:#64748b}
/* Rosca métodos */
.metodos-wrap{display:flex;align-items:center;gap:12px}
.rosca-cont{position:relative;width:72px;height:72px;flex-shrink:0}
.rosca-cont svg{width:72px;height:72px}
.rosca-centro{position:absolute;top:50%;left:50%;
              transform:translate(-50%,-50%);text-align:center}
.rosca-txt{font-size:11px;font-weight:700}
.metodo-item{display:flex;align-items:center;gap:5px;margin-bottom:5px}
.dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.met-nom{font-size:11px;color:#94a3b8;flex:1}
.met-val{font-size:11px;font-weight:600}
/* Grid */
.grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px}
.gcard{background:#1e293b;border-radius:10px;padding:10px 12px}
.gcard-lbl{font-size:10px;color:#64748b;text-transform:uppercase;
           letter-spacing:.3px;margin-bottom:3px}
.gcard-val{font-size:16px;font-weight:600}
/* Resumen */
.res-row{display:flex;justify-content:space-between;padding:5px 0;
         border-bottom:.5px solid #334155;font-size:12px}
.res-row:last-child{border-bottom:none}
.res-lbl{color:#94a3b8}
.res-val{font-weight:600}
.res-neto{display:flex;justify-content:space-between;align-items:center;
          margin-top:8px;padding-top:8px;border-top:1px solid #10b981}
.res-neto-lbl{font-size:13px;font-weight:600}
.res-neto-val{font-size:22px;font-weight:700}
.nota{font-size:10px;color:#475569;margin-top:5px}
/* Top */
.top-item{display:flex;align-items:center;gap:6px;padding:5px 0;
          border-bottom:.5px solid #334155}
.top-item:last-child{border-bottom:none}
.top-n{font-size:10px;color:#64748b;width:14px}
.top-bw{flex:1}
.top-nom{font-size:12px;margin-bottom:2px}
.bar-bg{background:#334155;border-radius:2px;height:3px}
.bar{height:3px;border-radius:2px}
.top-uds{font-size:11px;font-weight:500;color:#10b981;white-space:nowrap}
/* Alertas */
.alerta-item{display:flex;align-items:center;gap:8px;padding:6px 0;
             border-bottom:.5px solid #334155}
.alerta-item:last-child{border-bottom:none}
.dot-r{width:7px;height:7px;border-radius:50%;background:#ef4444;flex-shrink:0}
.dot-o{width:7px;height:7px;border-radius:50%;background:#f59e0b;flex-shrink:0}
.dot-g{width:7px;height:7px;border-radius:50%;background:#10b981;flex-shrink:0}
/* Inventario */
.inv-header{display:flex;justify-content:space-between;
            align-items:center;cursor:pointer}
.inv-body{display:none;margin-top:10px}
.inv-body.open{display:block}
.inv-item{display:flex;justify-content:space-between;padding:4px 0;
          border-bottom:.5px solid #334155;font-size:11px}
.inv-item:last-child{border-bottom:none}
.inv-val{font-weight:500}
.footer{text-align:center;font-size:10px;color:#334155;
        margin-top:12px;padding-bottom:8px}
.offline{background:#fef2f2;border:1px solid #fecaca;border-radius:8px;
         padding:12px;margin-bottom:12px;font-size:13px;
         color:#dc2626;text-align:center}
</style>
</head>
<body>
<div id="app">Cargando...</div>
<script>
const LOCAL = "{{local_id}}";
let PERIODO = "hoy";
let DATA_HOY = null;

function fmt(n){return '$'+Math.round(n||0).toLocaleString('es-CL')}

function renderPeriodo(d){
  if(!d||d.error){
    document.getElementById('app').innerHTML=
      '<div class="offline">Sin datos.<br>El POS puede estar offline.</div>';
    return;
  }

  const cols = {
    'Efectivo':'#10b981','Debito/Tarjeta':'#3b82f6',
    'Débito/Tarjeta':'#3b82f6','Transferencia':'#8b5cf6','Mixto':'#f59e0b'
  };

  // Totales por método
  const tot = Object.values(d.totales||{}).reduce((a,b)=>a+b,0)||1;
  let ang = 0;
  const arcs = [];
  const metList = [];
  Object.entries(d.totales||{}).forEach(([m,v])=>{
    if(v<=0) return;
    const c = cols[m]||'#64748b';
    const pct = v/tot;
    const ext = pct*360;
    arcs.push({color:c,start:ang,ext});
    ang+=ext;
    metList.push(`<div class="metodo-item">
      <div class="dot" style="background:${c}"></div>
      <span class="met-nom">${m}</span>
      <span class="met-val" style="color:${c}">${fmt(v)}</span>
    </div>`);
  });

  // SVG rosca
  function polarToXY(cx,cy,r,deg){
    const rad=(deg-90)*Math.PI/180;
    return{x:cx+r*Math.cos(rad),y:cy+r*Math.sin(rad)};
  }
  let svgArcs='';
  if(arcs.length===1){
    svgArcs=`<circle cx="18" cy="18" r="14" fill="none" 
      stroke="${arcs[0].color}" stroke-width="4"/>`;
  } else {
    arcs.forEach(a=>{
      const r=14,cx=18,cy=18;
      const s=polarToXY(cx,cy,r,a.start);
      const e=polarToXY(cx,cy,r,a.start+a.ext);
      const lg=a.ext>180?1:0;
      svgArcs+=`<path d="M${s.x.toFixed(2)},${s.y.toFixed(2)} 
        A${r},${r} 0 ${lg} 1 ${e.x.toFixed(2)},${e.y.toFixed(2)}"
        fill="none" stroke="${a.color}" stroke-width="4"/>`;
    });
  }
  const rosca=`<div class="rosca-cont">
    <svg viewBox="0 0 36 36">
      <circle cx="18" cy="18" r="14" fill="none" stroke="#334155" stroke-width="4"/>
      ${svgArcs}
    </svg>
    <div class="rosca-centro">
      <div class="rosca-txt">${fmt(d.neto).replace('$','$')}</div>
    </div>
  </div>`;

  // Top productos
  const tc=['#10b981','#3b82f6','#8b5cf6','#f59e0b','#ef4444'];
  const mx=d.top5&&d.top5.length?d.top5[0][1]:1;
  const topHTML=d.top5&&d.top5.length?d.top5.map(([p,u],i)=>`
    <div class="top-item">
      <span class="top-n">${i+1}</span>
      <div class="top-bw">
        <div class="top-nom">${p.substring(0,24)}</div>
        <div class="bar-bg"><div class="bar" 
          style="width:${Math.round(u/mx*100)}%;background:${tc[i]}"></div></div>
      </div>
      <span class="top-uds">${u} uds</span>
    </div>`).join('')
    :'<div style="color:#64748b;font-size:12px;padding:6px 0">Sin ventas</div>';

  // Alertas
  const alertHTML=d.alertas&&d.alertas.length?d.alertas.map(a=>`
    <div class="alerta-item">
      <div class="${a.critico?'dot-r':'dot-o'}"></div>
      <div>
        <div style="font-size:12px">${a.nombre}</div>
        <div style="font-size:10px;color:#64748b">
          ${a.critico?'SIN STOCK':'Stock: '+a.stock+' '+a.unidad+' · mín: '+a.minimo}</div>
      </div>
    </div>`).join('')
    :'<div style="color:#10b981;font-size:12px;padding:6px 0">✅ Todo en stock</div>';

  // Resumen neto
  const costo = d.costo_productos||0;
  const gastos_mes_total = d.gastos_mes||0;
  // Dividir gasto mensual según período
  let gastos = gastos_mes_total;
  let notaGastos = '';
  if(gastos_mes_total > 0){
    if(PERIODO==='hoy'){
      const diasMes = new Date(new Date().getFullYear(), new Date().getMonth()+1, 0).getDate();
      gastos = Math.round(gastos_mes_total / diasMes);
      notaGastos = '* Estimado diario de gastos mensuales';
    } else if(PERIODO==='semana'){
      gastos = Math.round(gastos_mes_total / 4.33);
      notaGastos = '* Estimado semanal de gastos mensuales';
    }
    // Mes: usar valor completo sin nota
  }
  const neto = d.neto - costo - gastos;
  const netoColor = neto>=0?'#10b981':'#ef4444';
  const resumenHTML=`
    <div class="res-row"><span class="res-lbl">Vendiste</span>
      <span class="res-val" style="color:#10b981">${fmt(d.neto)}</span></div>
    ${costo>0?`<div class="res-row"><span class="res-lbl">Costo productos</span>
      <span class="res-val" style="color:#f59e0b">- ${fmt(costo)}</span></div>`:''}
    ${gastos>0?`<div class="res-row"><span class="res-lbl">Gastos fijos${notaGastos?' *':''}</span>
      <span class="res-val" style="color:#ef4444">- ${fmt(gastos)}</span></div>`:''}
    <div class="res-neto">
      <span class="res-neto-lbl">Neto</span>
      <span class="res-neto-val" style="color:${netoColor}">${fmt(Math.abs(neto))}${neto<0?' 📉':''}</span>
    </div>
    ${notaGastos?`<div class="nota">${notaGastos}</div>`:''}`;

  // Turno
  const ini=d.cajero&&d.cajero!=='—'?d.cajero.substring(0,2).toUpperCase():'?';
  const turnoHTML=`<div class="turno">
    <div class="avatar">${ini}</div>
    <div>
      <div class="turno-cajero">${d.cajero||'—'} · Turno activo</div>
      <div class="turno-sub">${d.n_pedidos||0} ventas · ${fmt(d.neto)}</div>
    </div>
  </div>`;

  // Inventario colapsable
  const valorInv = d.valor_inventario||0;
  const invHTML = d.inventario&&d.inventario.length?`
    <div class="card">
      <div class="inv-header" onclick="toggleInv()">
        <div>
          <div class="sec">📦 Inventario completo</div>
          <div style="font-size:13px;font-weight:600;color:#10b981">
            Valor total: ${fmt(valorInv)}</div>
        </div>
        <span style="color:#64748b;font-size:18px" id="inv-arrow">▾</span>
      </div>
      <div class="inv-body" id="inv-body">
        ${d.inventario.map(p=>{
          const col=p.critico?'#ef4444':p.bajo?'#f59e0b':'#10b981';
          return`<div class="inv-item">
            <span>${p.nombre.substring(0,22)}</span>
            <span class="inv-val" style="color:${col}">
              ${p.critico?'SIN STOCK':p.stock+' '+p.unidad}</span>
          </div>`;
        }).join('')}
      </div>
    </div>`:'';

  const sync = d.ultima_actualizacion||'—';
  document.getElementById('app').innerHTML=`
    <div class="local">🏭 ${d.local||LOCAL}</div>
    <div class="fecha">${d.fecha||'—'} · Sync: ${sync}</div>
    <div class="periodo">
      <button class="pbtn${PERIODO==='hoy'?' active':''}" onclick="setPeriodo('hoy')">Hoy</button>
      <button class="pbtn${PERIODO==='semana'?' active':''}" onclick="setPeriodo('semana')">Semana</button>
      <button class="pbtn${PERIODO==='mes'?' active':''}" onclick="setPeriodo('mes')">Mes</button>
    </div>
    ${turnoHTML}
    <div class="card">
      <div class="total-lbl">Total vendido</div>
      <div class="total-val">${fmt(d.neto)}</div>
      <div class="total-sub">${d.n_pedidos||0} ventas · ${PERIODO==='hoy'?'Hoy':PERIODO==='semana'?'Esta semana':'Este mes'}</div>
    </div>
    <div class="card">
      <div class="sec">Métodos de pago</div>
      <div class="metodos-wrap">${rosca}
        <div style="flex:1">${metList.join('')}</div>
      </div>
    </div>
    <div class="grid">
      <div class="gcard"><div class="gcard-lbl">Ventas</div>
        <div class="gcard-val" style="color:#8b5cf6">${d.n_pedidos||0}</div></div>
      <div class="gcard"><div class="gcard-lbl">Venta promedio</div>
        <div class="gcard-val" style="color:#f59e0b">${fmt(d.ticket_prom)}</div></div>
      <div class="gcard"><div class="gcard-lbl">Venta mayor</div>
        <div class="gcard-val">${fmt(d.ticket_max)}</div></div>
      <div class="gcard"><div class="gcard-lbl">Descuentos</div>
        <div class="gcard-val" style="color:#ef4444">- ${fmt(d.total_desc)}</div></div>
    </div>
    <div class="card"><div class="sec">Resumen</div>${resumenHTML}</div>
    <div class="card"><div class="sec">Lo que más se vende</div>${topHTML}</div>
    <div class="card" style="${d.alertas&&d.alertas.length?'border:.5px solid #ef4444':''}">
      <div class="sec" style="${d.alertas&&d.alertas.length?'color:#ef4444':''}">
        ${d.alertas&&d.alertas.length?'⚠️ Productos por agotarse':'Stock'}
      </div>${alertHTML}
    </div>
    ${invHTML}
    <div class="footer">PuriPOS v2.0 · Se actualiza cada 5 min</div>`;
}

function toggleInv(){
  const b=document.getElementById('inv-body');
  const a=document.getElementById('inv-arrow');
  if(b){b.classList.toggle('open');if(a)a.textContent=b.classList.contains('open')?'▴':'▾';}
}

function setPeriodo(p){
  PERIODO=p;
  cargar();
}

function cargar(){
  fetch('/api/'+LOCAL+'?periodo='+PERIODO)
    .then(r=>r.json())
    .then(d=>renderPeriodo(d))
    .catch(()=>renderPeriodo(null));
}

cargar();
setInterval(cargar,300000);
</script>
</body>
</html>"""

@app.route('/<local_id>')
def dashboard(local_id):
    return render_template_string(HTML, local_id=local_id.upper())

@app.route('/api/<local_id>')
def get_datos(local_id):
    local_id = local_id.upper()
    periodo  = request.args.get('periodo','hoy')
    datos    = datos_locales.get(local_id)
    if not datos:
        return jsonify({"error":"sin datos","local":local_id})

    # Para semana y mes, acumular datos de los últimos N días
    if periodo in ('semana','mes'):
        from datetime import date, timedelta
        dias = 7 if periodo=='semana' else 30
        hoy  = date.today()

        neto_total   = 0
        n_pedidos    = 0
        ticket_prom  = 0
        ticket_max   = 0
        ticket_min   = 0
        total_desc   = 0
        totales_acc  = {}
        prod_cnt_acc = {}
        costo_acc    = 0

        # Acumular desde los CSVs guardados en datos
        historial = datos.get('historial', {})
        for i in range(dias):
            fecha_str = (hoy - timedelta(days=i)).strftime('%Y-%m-%d')
            d_dia = historial.get(fecha_str, {})
            neto_total  += d_dia.get('neto', 0)
            n_pedidos   += d_dia.get('n_pedidos', 0)
            total_desc  += d_dia.get('total_desc', 0)
            costo_acc   += d_dia.get('costo_productos', 0)
            for m,v in d_dia.get('totales',{}).items():
                totales_acc[m] = totales_acc.get(m,0)+v
            for p,u in d_dia.get('top5',[]):
                prod_cnt_acc[p] = prod_cnt_acc.get(p,0)+u

        top5_acc = sorted(prod_cnt_acc.items(),
                          key=lambda x:x[1], reverse=True)[:5]
        montos_dias = [d.get('neto',0) for d in historial.values()
                       if d.get('neto',0)>0]

        return jsonify({
            **datos,
            "neto":            neto_total,
            "n_pedidos":       n_pedidos,
            "total_desc":      total_desc,
            "ticket_prom":     sum(montos_dias)//len(montos_dias) if montos_dias else 0,
            "ticket_max":      max(montos_dias) if montos_dias else 0,
            "ticket_min":      min(montos_dias) if montos_dias else 0,
            "totales":         totales_acc,
            "top5":            top5_acc,
            "costo_productos": costo_acc,
            "gastos_mes":      datos.get("gastos_mes",0),
            "ultima_actualizacion": datos.get("ultima_actualizacion","—"),
        })

    return jsonify(datos)

@app.route('/api/<local_id>/push', methods=['POST'])
def push_datos(local_id):
    local_id = local_id.upper()
    auth = request.headers.get("X-PuriPOS-Key","")
    if auth != SECRET_KEY:
        abort(401)
    try:
        datos = request.get_json()
        datos["ultima_actualizacion"] = datetime.now().strftime("%H:%M")

        # Guardar en historial por fecha
        fecha_str = datos.get("fecha","")
        if local_id not in datos_locales:
            datos_locales[local_id] = {}
        datos_locales[local_id].update(datos)

        # Guardar snapshot del día en historial
        hoy_key = datetime.now().strftime("%Y-%m-%d")
        if "historial" not in datos_locales[local_id]:
            datos_locales[local_id]["historial"] = {}
        datos_locales[local_id]["historial"][hoy_key] = {
            "neto":            datos.get("neto",0),
            "n_pedidos":       datos.get("n_pedidos",0),
            "total_desc":      datos.get("total_desc",0),
            "totales":         datos.get("totales",{}),
            "top5":            datos.get("top5",[]),
            "costo_productos": datos.get("costo_productos",0),
        }
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/ping')
def ping():
    return jsonify({"ok":True,"locales":list(datos_locales.keys())})

@app.route('/')
def index():
    return jsonify({"sistema":"PuriPOS Server v2.0"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=False)
