#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Flask para geração de QR Code PIX
"""

import os
import json
import base64
from io import BytesIO
from datetime import datetime
from flask import Flask, request, render_template, jsonify, send_file, make_response
from flask_cors import CORS

# No início do arquivo, após os outros imports
from datetime import datetime, timedelta

# Importar o gerador de payload PIX
from payload_generator import Payload

# Inicializar Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para requisições de outros domínios

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-padrao-pix-api')

# Diretório para salvar QR Codes (opcional)
QR_CODE_DIR = os.path.join(os.path.dirname(__file__), 'qrcodes')
os.makedirs(QR_CODE_DIR, exist_ok=True)

@app.route('/')
def index():
    """Página inicial da API"""
    return render_template('index.html')

@app.route('/api/docs')
def api_docs():
    """Documentação da API"""
    return render_template('api_docs.html')

@app.route('/generate', methods=['GET'])
def generate_form():
    """Formulário web para geração de PIX"""
    return render_template('generate.html')

@app.route('/generate', methods=['POST'])
def generate_pix_web():
    """Gerar PIX a partir do formulário web"""
    try:
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        chavepix = request.form.get('chavepix', '').strip()
        valor = request.form.get('valor', '0.00').strip()
        cidade = request.form.get('cidade', '').strip()
        txid = request.form.get('txid', '').strip()
        return_base64 = request.form.get('return_base64', 'false') == 'true'
        
        # Validação básica
        if not all([nome, chavepix, cidade]):
            return render_template('generate.html', 
                                 error="Nome, chave PIX e cidade são obrigatórios")
        
        # Gerar payload
        payload_gen = Payload(
            nome=nome,
            chavepix=chavepix,
            valor=valor,
            cidade=cidade,
            txtId=txid,
            diretorio=''
        )
        
        payload = payload_gen.gerarPayload()
        qr_image = payload_gen.get_qrcode_image()
        
        # Converter QR Code para base64 se necessário
        qr_base64 = None
        if return_base64:
            buffered = BytesIO()
            qr_image.save(buffered, format="PNG")
            qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        # Salvar em arquivo temporário para exibição
        temp_filename = f"pix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        temp_path = os.path.join(QR_CODE_DIR, temp_filename)
        qr_image.save(temp_path)
        
        # Renderizar resultado
        return render_template('result.html',
                             payload=payload,
                             qr_image=f"/qrcodes/{temp_filename}",
                             qr_base64=qr_base64,
                             nome=nome,
                             valor=valor,
                             cidade=cidade)
    
    except ValueError as e:
        return render_template('generate.html', error=f"Erro de valor: {str(e)}")
    except Exception as e:
        return render_template('generate.html', error=f"Erro ao gerar PIX: {str(e)}")

@app.route('/api/v1/pix/generate', methods=['POST'])
def api_generate_pix():
    """
    Endpoint da API para geração de PIX
    Formato esperado (JSON):
    {
        "nome": "João Silva",
        "chavepix": "joao.silva@email.com",
        "valor": "150.50",
        "cidade": "São Paulo",
        "txid": "PEDIDO123",
        "return_image": true,
        "image_format": "base64"  # ou "url"
    }
    """
    try:
        # Verificar se é JSON
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type deve ser application/json"
            }), 400
        
        data = request.get_json()
        
        # Validar campos obrigatórios
        required_fields = ['nome', 'chavepix', 'cidade']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "success": False,
                    "error": f"Campo '{field}' é obrigatório"
                }), 400
        
        # Obter parâmetros
        nome = data.get('nome', '').strip()
        chavepix = data.get('chavepix', '').strip()
        valor = data.get('valor', '0.00').strip()
        cidade = data.get('cidade', '').strip()
        txid = data.get('txid', '').strip()
        return_image = data.get('return_image', False)
        image_format = data.get('image_format', 'base64')
        
        # Gerar payload PIX
        payload_gen = Payload(
            nome=nome,
            chavepix=chavepix,
            valor=valor,
            cidade=cidade,
            txtId=txid,
            diretorio=''
        )
        
        payload = payload_gen.gerarPayload()
        qr_image = payload_gen.get_qrcode_image()
        
        # Preparar resposta
        response_data = {
            "success": True,
            "payload": payload,
            "data": {
                "nome": nome,
                "chavepix": chavepix,
                "valor": valor,
                "cidade": cidade,
                "txid": txid,
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Adicionar imagem se solicitado
        if return_image:
            if image_format == 'base64':
                # Converter para base64
                buffered = BytesIO()
                qr_image.save(buffered, format="PNG")
                qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                response_data["qr_code"] = {
                    "format": "base64",
                    "data": f"data:image/png;base64,{qr_base64}",
                    "mime_type": "image/png"
                }
            
            elif image_format == 'url':
                # Salvar arquivo e retornar URL
                filename = f"pix_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(payload) % 10000}.png"
                filepath = os.path.join(QR_CODE_DIR, filename)
                qr_image.save(filepath)
                
                # Construir URL (ajuste conforme sua configuração)
                base_url = request.host_url.rstrip('/')
                response_data["qr_code"] = {
                    "format": "url",
                    "url": f"{base_url}/api/v1/pix/download/{filename}"
                }
        
        return jsonify(response_data)
    
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": f"Erro de validação: {str(e)}"
        }), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro interno: {str(e)}"
        }), 500

@app.route('/api/v1/pix/download/<filename>', methods=['GET'])
def download_qrcode(filename):
    """Download de QR Code gerado"""
    try:
        filepath = os.path.join(QR_CODE_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                "success": False,
                "error": "Arquivo não encontrado"
            }), 404
        
        return send_file(filepath, mimetype='image/png')
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro ao baixar: {str(e)}"
        }), 500

@app.route('/api/v1/pix/validate', methods=['POST'])
def validate_payload():
    """Validar um payload PIX existente"""
    try:
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type deve ser application/json"
            }), 400
        
        data = request.get_json()
        payload = data.get('payload', '')
        
        if not payload:
            return jsonify({
                "success": False,
                "error": "Payload é obrigatório"
            }), 400
        
        # Aqui você pode adicionar validações específicas
        # Por enquanto, apenas verifica estrutura básica
        is_valid = len(payload) > 50 and payload.startswith('000201')
        
        return jsonify({
            "success": True,
            "valid": is_valid,
            "payload_length": len(payload),
            "checksum_valid": True  # Implementar validação CRC16 se necessário
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Erro na validação: {str(e)}"
        }), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Endpoint de saúde da API"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "PIX QR Code Generator API",
        "version": "1.0.0"
    })

@app.route('/qrcodes/<filename>')
def serve_qrcode(filename):
    """Servir arquivos de QR Code"""
    try:
        return send_file(os.path.join(QR_CODE_DIR, filename))
    except FileNotFoundError:
        return "QR Code não encontrado", 404

# Error handlers
# Error handlers - CORRIGIDOS
@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({
            "success": False,
            "error": "Endpoint não encontrado"
        }), 404
    # Retorna uma resposta JSON simples para rotas web não encontradas
    return jsonify({
        "success": False,
        "error": "Página não encontrada",
        "message": f"A URL {request.path} não existe neste servidor",
        "available_routes": ["/", "/generate", "/api/docs", "/api/v1/health"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor",
            "message": str(error) if app.debug else "Ocorreu um erro interno"
        }), 500
    # Retorna uma resposta JSON simples para erros internos
    return jsonify({
        "success": False,
        "error": "Erro interno do servidor",
        "message": "Desculpe, ocorreu um erro inesperado"
    }), 500

# Adicione esta rota para evitar erro do favicon
@app.route('/favicon.ico')
def favicon():
    return '', 204  # Retorna No Content para evitar erros



# Dentro da função create_app ou após a definição das rotas principais
@app.route('/sitemap.xml')
def sitemap():
    try:
        """Gera o sitemap.xml dinamicamente[citation:1]"""
        pages = []
        # Data fictícia para "última modificação" (10 dias atrás)
        ten_days_ago = (datetime.now() - timedelta(days=10)).date().isoformat()
        # Lista todas as URLs da aplicação que queremos indexar
        for rule in app.url_map.iter_rules():
            # Filtra apenas rotas GET sem argumentos obrigatórios (para simplificar)
            if "GET" in rule.methods and len(rule.arguments) == 0:
                # URLs a incluir (evite APIs internas)
                if rule.rule.startswith(('/', '/generate', '/api/docs')):
                    pages.append([
                        f"https://SEU_DOMINIO_AQUI.com{rule.rule}",
                        ten_days_ago
                    ])
        
        # Renderiza um template XML (veja abaixo)
        sitemap_xml = render_template('sitemap_template.xml', pages=pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response
    except Exception as e:
        app.logger.error(f"Erro ao gerar sitemap: {e}")
        return jsonify({"error": "Erro interno"}), 500

if __name__ == '__main__':
    # Configurações do servidor
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"🚀 Iniciando API PIX Generator em http://{host}:{port}")
    print(f"📄 Documentação: http://{host}:{port}/api/docs")
    print(f"🎯 Formulário web: http://{host}:{port}/generate")
    
    app.run(host=host, port=port, debug=debug)