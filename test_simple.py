# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

print("\n" + "=" * 80)
print("TESTE: Script está sendo executado")
print("=" * 80 + "\n")


@app.route('/')
def index():
    print("TESTE: Rota / foi chamada")
    return "OK - Index"


@app.route('/api/teste')
def teste():
    print("TESTE: Rota /api/teste foi chamada")
    return jsonify({'status': 'ok', 'msg': 'Sistema funcionando'})


@app.route('/api/info', methods=['POST'])
def info():
    print("\n" + "=" * 80)
    print("TESTE: Rota /api/info foi chamada")
    print("=" * 80)

    try:
        d = request.json
        print(f"JSON recebido: {d}")
        print(f"Tipos: {[(k, type(v).__name__) for k, v in d.items()]}")

        # Teste simples de conversão
        tz = float(d.get('timezone', -3.0))
        print(f"tz recebido: {tz} (type={type(tz).__name__})")

        hora = int(d.get('hora', 14))
        print(f"hora recebido: {hora} (type={type(hora).__name__})")

        hora_utc = int(hora - tz)
        print(f"hora_utc calculado: {hora_utc} (type={type(hora_utc).__name__})")

        print("=" * 80 + "\n")
        return jsonify({'status': 'ok', 'dados': d})
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80 + "\n")
        return jsonify({'status': 'erro', 'msg': str(e)}), 400


@app.route('/api/gerar-grafico', methods=['POST'])
def gerar_grafico():
    print("\n" + "=" * 80)
    print("GERAR GRÁFICO: Função chamada")
    print("=" * 80)

    try:
        d = request.json
        print(f"JSON: {d}")

        # Teste básico
        print("Testando conversões...")
        ano = int(d['ano'])
        print(f"✓ ano={ano}")

        tz = float(d['timezone'])
        print(f"✓ tz={tz}")

        print("Tudo OK até aqui!")

        # Se chegou aqui, o problema está depois
        print("Tentando importar Kerykeion...")
        from kerykeion import AstrologicalSubject
        print("✓ Kerykeion importado")

        print("=" * 80 + "\n")
        return jsonify({'status': 'ok', 'msg': 'Teste passou'})

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 80 + "\n")
        return jsonify({'status': 'erro', 'msg': str(e)}), 400


if __name__ == '__main__':
    print("Iniciando Flask em http://localhost:5000")
    print("Ctrl+C para parar\n")
    app.run(debug=True)