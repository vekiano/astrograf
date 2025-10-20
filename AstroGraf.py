# -*- coding: utf-8 -*-
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from io import BytesIO

app = Flask(__name__)

try:
    from kerykeion import AstrologicalSubject, KerykeionChartSVG
except Exception as e:
    print(f"Erro ao importar Kerykeion: {e}")

# Mapeamento de UTC offset para timezone válido
TZ_MAP = {
    -12.0: 'Etc/GMT+12', -11.0: 'Etc/GMT+11', -10.0: 'Etc/GMT+10',
    -9.5: 'Australia/Darwin', -9.0: 'Etc/GMT+9', -8.0: 'Etc/GMT+8',
    -7.0: 'America/Denver', -6.0: 'America/Chicago', -5.0: 'America/New_York',
    -4.5: 'America/Caracas', -4.0: 'America/Santiago', -3.5: 'Canada/Newfoundland',
    -3.0: 'America/Sao_Paulo', -2.0: 'Etc/GMT+2', -1.0: 'Atlantic/Azores',
    0.0: 'UTC', 1.0: 'Europe/London', 2.0: 'Europe/Cairo', 3.0: 'Europe/Moscow',
    3.5: 'Asia/Tehran', 4.0: 'Asia/Dubai', 4.5: 'Asia/Kabul', 5.0: 'Asia/Karachi',
    5.5: 'Asia/Kolkata', 5.75: 'Asia/Kathmandu', 6.0: 'Asia/Dhaka', 6.5: 'Asia/Yangon',
    7.0: 'Asia/Bangkok', 8.0: 'Asia/Singapore', 9.0: 'Asia/Tokyo', 9.5: 'Australia/Darwin',
    10.0: 'Australia/Sydney', 10.5: 'Australia/Adelaide', 11.0: 'Asia/Bangkok',
    12.0: 'Pacific/Auckland', 12.75: 'Pacific/Chatham', 13.0: 'Pacific/Tongatapu'
}


@app.route('/api/cidades')
def cidades():
    q = request.args.get('q', '').lower()
    cidmundo = os.path.join(os.path.dirname(__file__), 'CidMundo.txt')
    result = []
    if os.path.exists(cidmundo):
        try:
            with open(cidmundo, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    p = line.split('|')
                    if len(p) >= 9:
                        try:
                            city = p[3].lower()
                            if q in city:
                                result.append({
                                    'city': p[3],
                                    'state': p[2],
                                    'country': p[1],
                                    'lat': float(p[4]),
                                    'lon': float(p[5]),
                                    'tz': float(p[8])
                                })
                                if len(result) >= 20:
                                    break
                        except:
                            pass
        except:
            pass
    return jsonify(result)


@app.route('/')
def index():
    now = datetime.utcnow()
    timezone_padrao = -3
    hora_ajustada = (now.hour + timezone_padrao + 24) % 24

    html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AstroGraf - Mapa Astral Gráfico</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:20px}
.container{max-width:900px;margin:0 auto;background:white;border-radius:12px;padding:25px;box-shadow:0 20px 60px rgba(0,0,0,0.3)}
h1{text-align:center;color:#333;margin-bottom:18px;font-size:24px}
.content{display:grid;grid-template-columns:1fr 1fr;gap:20px}
.form-section{padding-right:20px;border-right:1px solid #ddd}
.chart-section{padding-left:20px}
fieldset{border:1px solid #ddd;border-radius:8px;padding:12px;margin-bottom:15px}
legend{padding:0 8px;color:#667eea;font-weight:bold;font-size:13px}
input,select{padding:4px;border:1px solid #ddd;border-radius:4px;font-size:12px;width:100%}
label{font-size:10px;color:#555;display:block;margin-top:3px;margin-bottom:1px}
.row-2{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}
.row-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:8px}
.row-4{display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:6px;margin-bottom:8px}
.dms-group{display:grid;grid-template-columns:60px 50px 50px 50px;gap:4px;align-items:flex-end}
.dms-group input{font-size:9px}
.dms-group select{font-size:9px}
.row-horiz{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px}
.chart-container{display:none;text-align:center;padding:15px;background:#f0f9ff;border-radius:8px;min-height:600px}
.chart-container img{max-width:90%;height:auto;border-radius:8px}
.loading{display:none;text-align:center;color:#667eea;font-weight:bold;font-size:12px;margin:20px 0}
.modal-header{background:#667eea;color:white;padding:10px;border-radius:8px 8px 0 0;cursor:move;display:flex;justify-content:space-between;align-items:center}
.modal-content{padding:15px;text-align:center}
.modal-buttons{margin-top:10px;display:flex;gap:10px;justify-content:center}
.modal-buttons button{width:auto;padding:8px 16px;font-size:12px}
#modalGrafico{display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:80%;max-width:900px;max-height:90vh;background:white;border-radius:8px;box-shadow:0 20px 60px rgba(0,0,0,0.5);z-index:2000;overflow:auto;flex-direction:column}
#modalGrafico.show{display:flex}
@media (max-width:768px){
  .content{grid-template-columns:1fr}
  .form-section{padding-right:0;border-right:none;border-bottom:1px solid #ddd;padding-bottom:20px}
  .chart-section{padding-left:0}
  #modalGrafico{width:95%;max-width:none}
}
</style>
</head>
<body>
<div class="container">
<h1>🌙 AstroGraf - Mapa Astral Gráfico</h1>
<div class="content">
  <div class="form-section">
    <form id="f">
      <fieldset>
        <legend>Identificacao</legend>
        <input type="text" id="nome" value="Meu Mapa" required style="width:100%">

        <div class="row-2">
          <div>
            <label>Dia / Mês / Ano</label>
            <div class="row-3">
              <input type="number" id="dia" min="1" max="31" value="''' + str(now.day) + '''" required>
              <input type="number" id="mes" min="1" max="12" value="''' + str(now.month) + '''" required>
              <input type="number" id="ano" value="''' + str(now.year) + '''" required>
            </div>
          </div>
          <div>
            <label>Hora / Min / Seg</label>
            <div class="row-3">
              <input type="number" id="hora" min="0" max="23" value="''' + str(hora_ajustada) + '''" required>
              <input type="number" id="minuto" min="0" max="59" value="''' + str(now.minute) + '''" required>
              <input type="number" id="segundo" min="0" max="59" value="''' + str(now.second) + '''" required>
            </div>
          </div>
        </div>
      </fieldset>

      <fieldset>
        <legend>Localizacao</legend>

        <label>Cidade / Estado / País</label>
        <div class="row-4">
          <input type="text" id="cidade" value="Brasilia" required placeholder="Cidade">
          <input type="text" id="estado" value="DF" required placeholder="Estado">
          <input type="text" id="pais" value="Brasil" required placeholder="Pais">
          <button type="button" onclick="abrirBusca()" style="width:auto;padding:4px 8px;font-size:10px">🔍 Buscar</button>
        </div>

        <label>Latitude (Graus Minutos Segundos)</label>
        <div class="dms-group">
          <div><label style="margin:0">Graus</label><input type="number" id="latg" min="0" max="90" value="15"></div>
          <div><label style="margin:0">Min</label><input type="number" id="latm" min="0" max="59" value="46"></div>
          <div><label style="margin:0">Seg</label><input type="number" id="lats" min="0" max="59" value="12"></div>
          <select id="lath" style="width:auto"><option>N</option><option selected>S</option></select>
        </div>

        <label>Longitude (Graus Minutos Segundos)</label>
        <div class="dms-group">
          <div><label style="margin:0">Graus</label><input type="number" id="long" min="0" max="180" value="47"></div>
          <div><label style="margin:0">Min</label><input type="number" id="lonm" min="0" max="59" value="55"></div>
          <div><label style="margin:0">Seg</label><input type="number" id="lons" min="0" max="59" value="12"></div>
          <select id="lonh" style="width:auto"><option>E</option><option selected>W</option></select>
        </div>

        <div class="row-2">
          <div>
            <label>Zona de Tempo (UTC)</label>
            <input type="number" id="tz" step="0.5" value="-3">
          </div>
          <div>
            <label>Casas Terrestres</label>
            <select id="houseSys">
              <option>Regiomontanus</option>
              <option>Placidus</option>
              <option>Campanus</option>
              <option>Koch</option>
            </select>
          </div>
        </div>
      </fieldset>

      <button type="submit">GERAR GRÁFICO</button>
    </form>
  </div>

  <div class="loading" id="load">⏳ Gerando gráfico...</div>
  <div id="modalGrafico">
    <div class="modal-header">
      <span>Mapa Astral</span>
      <button type="button" onclick="abrirNovaAba()" style="background:none;border:none;color:white;cursor:pointer;font-size:16px">↗ Nova Aba</button>
    </div>
    <div class="modal-content">
      <img id="chartImage" src="" alt="Mapa Astral" style="max-width:100%;height:auto;border-radius:8px;cursor:pointer" title="Duplo clique para copiar para a área de transferência">
      <div class="modal-buttons">
        <button type="button" onclick="baixarImagem()" style="background:#667eea">📥 Baixar</button>
        <button type="button" onclick="document.getElementById('modalGrafico').classList.remove('show')" style="background:#999">✕ Fechar</button>
      </div>
    </div>
  </div>
</div>

<div id="modalBusca" style="display:none;position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);width:400px;background:white;border:2px solid #667eea;border-radius:8px;box-shadow:0 20px 60px rgba(0,0,0,0.5);z-index:3000;padding:20px">
  <h3 style="margin-bottom:10px">Buscar Cidade</h3>
  <input type="text" id="searchCidade" placeholder="Digite a cidade..." style="width:100%;padding:8px;margin-bottom:10px;border:1px solid #ddd;border-radius:4px">
  <div id="listaCidades" style="max-height:300px;overflow-y:auto;border:1px solid #ddd;border-radius:4px"></div>
  <button type="button" onclick="fecharBusca()" style="width:100%;margin-top:10px;padding:6px">Fechar</button>
</div>
</div>

<script>
function dmsToDecimal(g, m, s, h) {
  let d = Math.abs(g) + Math.abs(m)/60 + Math.abs(s)/3600;
  return (h == 'S' || h == 'W') ? -d : d;
}

function abrirGrafico(url) {
  document.getElementById('chartImage').src = url;
  document.getElementById('modalGrafico').classList.add('show');
  document.getElementById('load').style.display = 'none';
}

function abrirNovaAba() {
  let url = document.getElementById('chartImage').src;
  window.open(url, '_blank');
}

function baixarImagem() {
  let img = document.getElementById('chartImage');
  let src = img.src;
  let nome = document.getElementById('nome').value || 'mapa_astral';

  let link = document.createElement('a');
  link.href = src;
  link.download = nome + '.svg';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function copiarImagemClipboard() {
  let img = document.getElementById('chartImage');
  let src = img.src;

  // Criar um canvas com tamanho 700x1000
  let canvas = document.createElement('canvas');
  canvas.width = 700;
  canvas.height = 1000;
  let context = canvas.getContext('2d');

  // Preencher com fundo branco
  context.fillStyle = '#ffffff';
  context.fillRect(0, 0, 700, 1000);

  let imgElement = new Image();
  imgElement.crossOrigin = 'anonymous';

  imgElement.onload = function() {
    // Calcular escala para caber em 700x1000 mantendo proporção
    let scale = Math.min(700 / imgElement.width, 1000 / imgElement.height);
    let newWidth = imgElement.width * scale;
    let newHeight = imgElement.height * scale;

    // Centralizar a imagem no canvas
    let x = (700 - newWidth) / 2;
    let y = (1000 - newHeight) / 2;

    context.drawImage(imgElement, x, y, newWidth, newHeight);

    // Converter canvas para blob e copiar para clipboard
    canvas.toBlob(function(blob) {
      let item = new ClipboardItem({'image/png': blob});
      navigator.clipboard.write([item]).then(function() {
        alert('✓ Imagem (700x1000) copiada para a área de transferência!');
      }).catch(function(err) {
        alert('Erro ao copiar: ' + err);
      });
    });
  };

  imgElement.onerror = function() {
    alert('Erro ao carregar a imagem para copiar');
  };

  imgElement.src = src;
}

// Event listener para duplo clique na imagem
document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('chartImage').addEventListener('dblclick', function() {
    copiarImagemClipboard();
  });
});

function fecharBusca() {
  document.getElementById('modalBusca').style.display = 'none';
}

function abrirBusca() {
  let cidadeAtual = document.getElementById('cidade').value;
  document.getElementById('searchCidade').value = cidadeAtual;
  document.getElementById('modalBusca').style.display = 'block';
  document.getElementById('searchCidade').focus();
  if (cidadeAtual.length >= 2) {
    buscarCidades(cidadeAtual);
  }
}

async function buscarCidades(q) {
  console.log("Buscando:", q);
  if (q.length < 2) {
    document.getElementById('listaCidades').innerHTML = '';
    return;
  }
  try {
    let r = await fetch('/api/cidades?q=' + encodeURIComponent(q));
    console.log("Response status:", r.status);
    let c = await r.json();
    console.log("Cidades encontradas:", c);
    document.getElementById('listaCidades').innerHTML = '';
    if (c.length === 0) {
      document.getElementById('listaCidades').innerHTML = '<div style="padding:8px;text-align:center;color:#999">Nenhuma cidade encontrada</div>';
      return;
    }
    c.forEach(function(d) {
      let div = document.createElement('div');
      div.style.cssText = 'padding:8px;border-bottom:1px solid #eee;cursor:pointer;font-size:11px';
      div.textContent = d.city + ', ' + d.state + ' - ' + d.country;
      div.onmouseover = function() { this.style.background = '#f0f9ff'; };
      div.onmouseout = function() { this.style.background = 'white'; };
      div.onclick = function() {
        document.getElementById('cidade').value = d.city;
        document.getElementById('estado').value = d.state;
        document.getElementById('pais').value = d.country;
        let latD = Math.abs(d.lat);
        let latG = Math.floor(latD);
        let latM = Math.floor((latD - latG) * 60);
        let latS = Math.round(((latD - latG) * 60 - latM) * 60);
        document.getElementById('latg').value = latG;
        document.getElementById('latm').value = latM;
        document.getElementById('lats').value = latS;
        document.getElementById('lath').value = (d.lat < 0 ? 'S' : 'N');
        let lonD = Math.abs(d.lon);
        let lonG = Math.floor(lonD);
        let lonM = Math.floor((lonD - lonG) * 60);
        let lonS = Math.round(((lonD - lonG) * 60 - lonM) * 60);
        document.getElementById('long').value = lonG;
        document.getElementById('lonm').value = lonM;
        document.getElementById('lons').value = lonS;
        document.getElementById('lonh').value = (d.lon < 0 ? 'W' : 'E');
        document.getElementById('tz').value = d.tz;
        fecharBusca();
      };
      document.getElementById('listaCidades').appendChild(div);
    });
  } catch (error) {
    console.error('Erro na busca:', error);
    document.getElementById('listaCidades').innerHTML = '<div style="padding:8px;color:red">Erro ao buscar cidades</div>';
  }
}

document.getElementById('searchCidade').addEventListener('input', function(e) {
  buscarCidades(e.target.value);
});

// Fechar modal ao clicar fora
window.onclick = function(event) {
  let modal = document.getElementById('modalGrafico');
  if (event.target == modal) {
    modal.classList.remove('show');
  }
}

// Draggable modal
let isDragging = false;
let offsetX = 0;
let offsetY = 0;

let header = document.querySelector('.modal-header');
if (header) {
  header.addEventListener('mousedown', function(e) {
    if (e.target.tagName === 'BUTTON') return;
    isDragging = true;
    let modal = document.getElementById('modalGrafico');
    offsetX = e.clientX - modal.offsetLeft;
    offsetY = e.clientY - modal.offsetTop;
  });
}

document.addEventListener('mousemove', function(e) {
  if (isDragging) {
    let modal = document.getElementById('modalGrafico');
    modal.style.left = (e.clientX - offsetX) + 'px';
    modal.style.top = (e.clientY - offsetY) + 'px';
  }
});

document.addEventListener('mouseup', function() {
  isDragging = false;
});

document.getElementById('f').addEventListener('submit', async function(e) {
  e.preventDefault();

  let lat = dmsToDecimal(parseInt(document.getElementById('latg').value), 
                         parseInt(document.getElementById('latm').value), 
                         parseInt(document.getElementById('lats').value), 
                         document.getElementById('lath').value);
  let lon = dmsToDecimal(parseInt(document.getElementById('long').value), 
                         parseInt(document.getElementById('lonm').value), 
                         parseInt(document.getElementById('lons').value), 
                         document.getElementById('lonh').value);

  let dados = {
    nome: document.getElementById('nome').value,
    dia: parseInt(document.getElementById('dia').value),
    mes: parseInt(document.getElementById('mes').value),
    ano: parseInt(document.getElementById('ano').value),
    hora: parseInt(document.getElementById('hora').value),
    minuto: parseInt(document.getElementById('minuto').value),
    segundo: parseInt(document.getElementById('segundo').value),
    latitude: lat,
    longitude: lon,
    timezone: parseFloat(document.getElementById('tz').value),
    cidade: document.getElementById('cidade').value,
    pais: document.getElementById('pais').value
  };

  document.getElementById('load').style.display = 'block';

  try {
    let res = await fetch('/api/gerar-grafico', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(dados)
    });

    if (res.ok) {
      let blob = await res.blob();
      let url = window.URL.createObjectURL(blob);
      abrirGrafico(url);
    } else {
      let j = await res.json();
      alert('Erro: ' + j.msg);
      document.getElementById('load').style.display = 'none';
    }
  } catch (error) {
    console.error('Erro:', error);
    alert('Erro: ' + error.message);
    document.getElementById('load').style.display = 'none';
  }
});
</script>
</body>
</html>'''
    return html


@app.route('/api/gerar-grafico', methods=['POST'])
def gerar_grafico():
    print("\n" + "=" * 80)
    print("GERAR GRÁFICO: Função chamada")
    print("=" * 80)

    import tempfile
    import glob

    try:
        d = request.json
        print(f"JSON recebido: {d}")

        # Conversões
        ano = int(d['ano'])
        mes = int(d['mes'])
        dia = int(d['dia'])
        hora = int(d['hora'])
        minuto = int(d['minuto'])
        segundo = int(d['segundo'])
        lat = float(d['latitude'])
        lon = float(d['longitude'])
        tz = float(d['timezone'])
        nome = d.get('nome', 'Mapa Astral')
        cidade = d.get('cidade', 'Brasilia')
        pais = d.get('pais', 'Brasil')

        print(f"✓ Dados: {ano}-{mes:02d}-{dia:02d} {hora:02d}:{minuto:02d}:{segundo:02d}")
        print(f"✓ Hora LOCAL: {hora:02d}:{minuto:02d}:{segundo:02d}")

        # Criar diretório temporário
        temp_dir = tempfile.gettempdir()
        print(f"✓ Usando diretório temporário: {temp_dir}")

        # Criar AstrologicalSubject
        print("\nCriando AstrologicalSubject...")

        # Obter timezone válido
        tz_str = TZ_MAP.get(tz, 'UTC')
        print(f"✓ Timezone mapeado: {tz} → {tz_str}")
        print(f"✓ País: {pais}")

        subj = AstrologicalSubject(
            nome,
            ano,
            mes,
            dia,
            hora,
            minuto,
            lat=lat,
            lng=lon,
            tz_str=tz_str,
            city=cidade,
            nation=pais
        )
        print(f"✓ Criado com sucesso!")

        # Gerar SVG
        print("Gerando SVG com makeSVG()...")
        chart = KerykeionChartSVG(
            subj,
            new_output_directory=temp_dir
        )
        chart.makeSVG()
        print(f"✓ SVG gerado!")

        # Procurar o arquivo SVG gerado
        print("Procurando arquivo SVG...")
        svg_files = glob.glob(os.path.join(temp_dir, f"{nome}*.svg"))

        if not svg_files:
            print(f"❌ Nenhum arquivo SVG encontrado em {temp_dir}")
            print(f"Arquivos encontrados: {os.listdir(temp_dir)[:10]}")
            return jsonify({'status': 'erro', 'msg': 'SVG não foi gerado'}), 400

        svg_file = svg_files[0]
        print(f"✓ Arquivo encontrado: {svg_file}")

        # Ler o arquivo
        with open(svg_file, 'r', encoding='utf-8') as f:
            svg_str = f.read()

        print(f"✓ SVG lido! ({len(svg_str)} bytes)")

        # Limpar o arquivo temporário
        try:
            os.remove(svg_file)
            print(f"✓ Arquivo temporário deletado")
        except:
            pass

        svg_bytes = svg_str.encode('utf-8')

        print("=" * 80)
        print("✓ SUCESSO!")
        print("=" * 80 + "\n")

        return send_file(
            BytesIO(svg_bytes),
            mimetype='image/svg+xml',
            as_attachment=False
        )

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80 + "\n")
        return jsonify({'status': 'erro', 'msg': str(e)}), 400


if __name__ == '__main__':
    print("\nIniciando AstroGraf em http://localhost:5000")
    print("Pressione Ctrl+C para parar\n")
    app.run(debug=True)