#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de PIX com QR Code usando Tkinter
Classe Payload fornecida integrada com interface gráfica
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import crcmod
import qrcode
import os
import sys

# ============================================================================
# CLASSE PAYLOAD - Geradora do código PIX
# ============================================================================
class Payload():
    """Classe para geração do payload PIX seguindo padrão do Banco Central"""
    
    def __init__(self, nome, chavepix, valor, cidade, txtId, diretorio=''):
        """
        Inicializa o gerador de payload PIX
        
        Args:
            nome: Nome do beneficiário (até 25 caracteres)
            chavepix: Chave PIX (CPF, CNPJ, telefone, email ou chave aleatória)
            valor: Valor da transação (formato string com '.' como separador decimal)
            cidade: Cidade do beneficiário (até 15 caracteres)
            txtId: Identificador da transação (opcional)
            diretorio: Diretório para salvar QR Code (opcional)
        """
        self.nome = nome
        self.chavepix = chavepix
        self.valor = valor.replace(',', '.')
        self.cidade = cidade
        self.txtId = txtId
        self.diretorioQrCode = diretorio

        # Calcula tamanhos dos campos
        self.nome_tam = len(self.nome)
        self.chavepix_tam = len(self.chavepix)
        self.valor_tam = len(self.valor)
        self.cidade_tam = len(self.cidade)
        self.txtId_tam = len(self.txtId)

        # Constrói campos formatados
        self.merchantAccount_tam = f'0014BR.GOV.BCB.PIX01{self.chavepix_tam:02}{self.chavepix}'
        self.transactionAmount_tam = f'{self.valor_tam:02}{float(self.valor):.2f}'
        
        # Campo adicional (TXID) - se vazio, usa padrão
        if self.txtId_tam > 0:
            self.addDataField_tam = f'05{self.txtId_tam:02}{self.txtId}'
        else:
            self.addDataField_tam = '0503***'
        
        # Formata tamanhos para strings de 2 dígitos
        self.nome_tam_fmt = f'{self.nome_tam:02}'
        self.cidade_tam_fmt = f'{self.cidade_tam:02}'

        # Campos fixos do padrão PIX
        self.payloadFormat = '000201'
        self.merchantAccount = f'26{len(self.merchantAccount_tam):02}{self.merchantAccount_tam}'
        self.merchantCategCode = '52040000'
        self.transactionCurrency = '5303986'
        self.transactionAmount = f'54{self.transactionAmount_tam}'
        self.countryCode = '5802BR'
        self.merchantName = f'59{self.nome_tam_fmt}{self.nome}'
        self.merchantCity = f'60{self.cidade_tam_fmt}{self.cidade}'
        self.addDataField = f'62{len(self.addDataField_tam):02}{self.addDataField_tam}'
        self.crc16 = '6304'
        
        # Variáveis para resultados
        self.payload_completa = None
        self.qrcode = None

    def gerarPayload(self):
        """Gera o payload completo do PIX"""
        # Constrói payload sem CRC
        self.payload = f'{self.payloadFormat}{self.merchantAccount}{self.merchantCategCode}{self.transactionCurrency}{self.transactionAmount}{self.countryCode}{self.merchantName}{self.merchantCity}{self.addDataField}{self.crc16}'
        
        # Calcula CRC16
        self.gerarCrc16(self.payload)
        
        return self.payload_completa

    def gerarCrc16(self, payload):
        """Calcula o CRC16 do payload"""
        # Função CRC16 com parâmetros específicos do PIX
        crc16 = crcmod.mkCrcFun(poly=0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
        
        # Calcula CRC
        self.crc16Code = hex(crc16(str(payload).encode('utf-8')))
        
        # Formata CRC (4 dígitos hex, maiúsculos)
        self.crc16Code_formatado = str(self.crc16Code).replace('0x', '').upper().zfill(4)
        
        # Payload completo com CRC
        self.payload_completa = f'{payload}{self.crc16Code_formatado}'
        
        # Gera QR Code
        self.gerarQrCode(self.payload_completa, self.diretorioQrCode)
        
        return self.payload_completa

    def gerarQrCode(self, payload, diretorio):
        """Gera imagem do QR Code a partir do payload"""
        # Gera QR Code
        self.qrcode = qrcode.make(payload)
        
        # Salva em arquivo se diretório foi especificado
        if diretorio and os.path.exists(diretorio):
            dir_path = os.path.expanduser(diretorio)
            file_path = os.path.join(dir_path, 'pixqrcodegen.png')
            self.qrcode.save(file_path)
            print(f"QR Code salvo em: {file_path}")
        
        return self.qrcode
    
    def get_qrcode_image(self):
        """Retorna o objeto QR Code PIL Image"""
        return self.qrcode
    
    def get_payload(self):
        """Retorna o payload completo"""
        return self.payload_completa


# ============================================================================
# INTERFACE GRÁFICA Tkinter
# ============================================================================
class PixGeneratorApp:
    """Interface gráfica para geração de PIX com QR Code"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de PIX com QR Code v2.0")
        self.root.geometry("900x700")
        self.root.configure(bg="#f5f7fa")
        
        # Configurar ícone (opcional)
        try:
            self.root.iconbitmap('pix_icon.ico')  # Se tiver um ícone
        except:
            pass
        
        # Variáveis de controle
        self.chave_var = tk.StringVar()
        self.valor_var = tk.StringVar(value="1.00")
        self.nome_var = tk.StringVar()
        self.cidade_var = tk.StringVar()
        self.txid_var = tk.StringVar()
        
        # Estado do QR Code
        self.qr_image = None
        self.current_payload = None
        
        # Configurar interface
        self.setup_ui()
        
        # Exemplo de dados (opcional - para testes)
        self.preencher_exemplo()
    
    def preencher_exemplo(self):
        """Preenche campos com dados de exemplo (opcional)"""
        self.nome_var.set("João da Silva")
        self.chave_var.set("joao.silva@email.com")
        self.cidade_var.set("São Paulo")
        self.txid_var.set("PEDIDO001")
    
    def setup_ui(self):
        """Configura todos os elementos da interface"""
        # Frame principal com rolagem
        main_frame = tk.Frame(self.root, bg="#f5f7fa")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_frame = tk.Frame(main_frame, bg="#f5f7fa")
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text="💰 GERADOR DE PIX", 
                              font=("Arial", 28, "bold"), 
                              bg="#f5f7fa", fg="#2c3e50")
        title_label.pack()
        
        subtitle_label = tk.Label(title_frame, 
                                 text="Gere QR Codes PIX estáticos para pagamentos",
                                 font=("Arial", 12), 
                                 bg="#f5f7fa", fg="#7f8c8d")
        subtitle_label.pack()
        
        # Frame de entrada de dados
        input_frame = tk.LabelFrame(main_frame, text=" DADOS DO PAGAMENTO ", 
                                   font=("Arial", 13, "bold"), 
                                   bg="#ffffff", fg="#2c3e50",
                                   relief=tk.GROOVE, bd=2,
                                   padx=20, pady=20)
        input_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Grid para campos de entrada
        campos = [
            ("Nome do Recebedor*:", self.nome_var, "Ex: João da Silva (até 25 caracteres)"),
            ("Chave PIX*:", self.chave_var, "CPF, CNPJ, telefone, email ou chave aleatória"),
            ("Valor (R$)*:", self.valor_var, "Ex: 150.50 ou 200,00"),
            ("Cidade*:", self.cidade_var, "Ex: São Paulo (até 15 caracteres)"),
            ("Identificador (TXID):", self.txid_var, "Opcional - Ex: PEDIDO123, NOTA001")
        ]
        
        for i, (label_text, var, tooltip) in enumerate(campos):
            # Frame para cada campo
            campo_frame = tk.Frame(input_frame, bg="#ffffff")
            campo_frame.grid(row=i, column=0, columnspan=2, 
                           sticky="ew", pady=8)
            
            # Label
            label = tk.Label(campo_frame, text=label_text, 
                           width=22, anchor="w",
                           font=("Arial", 11), bg="#ffffff")
            label.grid(row=0, column=0, padx=(0, 10), sticky="w")
            
            # Campo de entrada
            if label_text.startswith("Valor"):
                entry = tk.Entry(campo_frame, textvariable=var, 
                               width=40, font=("Arial", 11),
                               justify="right")
                entry.grid(row=0, column=1, sticky="ew")
            else:
                entry = tk.Entry(campo_frame, textvariable=var, 
                               width=40, font=("Arial", 11))
                entry.grid(row=0, column=1, sticky="ew")
            
            # Tooltip (label de ajuda)
            help_label = tk.Label(campo_frame, text=tooltip,
                                font=("Arial", 9), fg="#7f8c8d",
                                bg="#ffffff", justify="left")
            help_label.grid(row=1, column=1, sticky="w", pady=(2, 0))
        
        # Configurar expansão das colunas
        input_frame.columnconfigure(1, weight=1)
        
        # Frame de botões de ação
        button_frame = tk.Frame(main_frame, bg="#f5f7fa")
        button_frame.pack(pady=(10, 20))
        
        # Botões com estilos
        button_style = {'font': ("Arial", 11, "bold"), 'padx': 25, 'pady': 10}
        
        btn_generate = tk.Button(button_frame, text="🔸 GERAR PIX", 
                                command=self.generate_pix,
                                bg="#e74c3c", fg="white",
                                activebackground="#c0392b",
                                cursor="hand2", **button_style)
        btn_generate.pack(side=tk.LEFT, padx=5)
        
        btn_clear = tk.Button(button_frame, text="🗑️ LIMPAR", 
                             command=self.clear_fields,
                             bg="#95a5a6", fg="white",
                             activebackground="#7f8c8d",
                             cursor="hand2", **button_style)
        btn_clear.pack(side=tk.LEFT, padx=5)
        
        btn_save = tk.Button(button_frame, text="💾 SALVAR QR CODE", 
                            command=self.save_qrcode,
                            bg="#2ecc71", fg="white",
                            activebackground="#27ae60",
                            cursor="hand2", **button_style,
                            state=tk.DISABLED)
        btn_save.pack(side=tk.LEFT, padx=5)
        self.btn_save = btn_save
        
        btn_copy = tk.Button(button_frame, text="📋 COPIAR CÓDIGO", 
                            command=self.copy_to_clipboard,
                            bg="#9b59b6", fg="white",
                            activebackground="#8e44ad",
                            cursor="hand2", **button_style)
        btn_copy.pack(side=tk.LEFT, padx=5)
        
        # Frame de resultado (dividido em duas partes)
        result_frame = tk.LabelFrame(main_frame, text=" RESULTADO ", 
                                    font=("Arial", 13, "bold"), 
                                    bg="#ffffff", fg="#2c3e50",
                                    relief=tk.GROOVE, bd=2,
                                    padx=20, pady=20)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame esquerdo - QR Code
        left_frame = tk.Frame(result_frame, bg="#ffffff")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        qr_title = tk.Label(left_frame, text="QR CODE PIX", 
                           font=("Arial", 12, "bold"),
                           bg="#ffffff", fg="#2c3e50")
        qr_title.pack(pady=(0, 10))
        
        # Container para QR Code com borda
        qr_container = tk.Frame(left_frame, bg="white", 
                               relief=tk.SUNKEN, bd=2)
        qr_container.pack(fill=tk.BOTH, expand=True)
        
        self.qr_label = tk.Label(qr_container, 
                                text="O QR Code aparecerá aqui\napós gerar o PIX",
                                font=("Arial", 10), 
                                bg="white", fg="#7f8c8d",
                                justify=tk.CENTER)
        self.qr_label.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)
        
        # Frame direito - Código PIX
        right_frame = tk.Frame(result_frame, bg="#ffffff")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        code_title = tk.Label(right_frame, text="CÓDIGO PIX (COPIA E COLA)", 
                             font=("Arial", 12, "bold"),
                             bg="#ffffff", fg="#2c3e50")
        code_title.pack(pady=(0, 10))
        
        # Container para código PIX com scrollbar
        code_container = tk.Frame(right_frame, bg="#ecf0f1")
        code_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar vertical
        scrollbar = tk.Scrollbar(code_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget para código PIX
        self.pix_text = tk.Text(code_container, 
                               height=12, 
                               font=("Courier", 10),
                               wrap=tk.WORD,
                               yscrollcommand=scrollbar.set,
                               bg="#2c3e50", fg="#ecf0f1",
                               state=tk.DISABLED,
                               padx=10, pady=10)
        self.pix_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configurar scrollbar
        scrollbar.config(command=self.pix_text.yview)
        
        # Frame de status (rodapé)
        status_frame = tk.Frame(main_frame, bg="#34495e", height=30)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = tk.Label(status_frame, 
                                    text="Preencha os dados e clique em GERAR PIX",
                                    font=("Arial", 10),
                                    bg="#34495e", fg="#ecf0f1")
        self.status_label.pack(pady=5)
    
    def validate_fields(self):
        """Valida os campos de entrada"""
        errors = []
        
        # Nome
        nome = self.nome_var.get().strip()
        if not nome:
            errors.append("O nome do recebedor é obrigatório")
        elif len(nome) > 25:
            errors.append("Nome deve ter no máximo 25 caracteres")
        
        # Chave PIX
        chave = self.chave_var.get().strip()
        if not chave:
            errors.append("A chave PIX é obrigatória")
        
        # Valor
        valor_text = self.valor_var.get().replace(",", ".").strip()
        try:
            valor = float(valor_text)
            if valor <= 0:
                errors.append("O valor deve ser maior que zero")
            elif valor > 999999.99:
                errors.append("Valor máximo é R$ 999.999,99")
        except ValueError:
            errors.append("Valor inválido. Use números (ex: 10.50 ou 10,50)")
        
        # Cidade
        cidade = self.cidade_var.get().strip()
        if not cidade:
            errors.append("A cidade é obrigatória")
        elif len(cidade) > 15:
            errors.append("Cidade deve ter no máximo 15 caracteres")
        
        return errors
    
    def generate_pix(self):
        """Gera o código PIX e o QR Code usando a classe Payload"""
        # Validar campos
        errors = self.validate_fields()
        if errors:
            messagebox.showerror("Erros de Validação", 
                               "Corrija os seguintes erros:\n\n• " + "\n• ".join(errors))
            return
        
        # Obter dados validados
        nome = self.nome_var.get().strip()
        chave = self.chave_var.get().strip()
        valor_text = self.valor_var.get().replace(",", ".")
        cidade = self.cidade_var.get().strip()
        txid = self.txid_var.get().strip()
        
        try:
            # Converter valor para string com 2 casas decimais
            valor_float = float(valor_text)
            valor_str = f"{valor_float:.2f}"
            
            # Gerar payload usando a classe fornecida
            payload_gen = Payload(
                nome=nome,
                chavepix=chave,
                valor=valor_str,
                cidade=cidade,
                txtId=txid if txid else "",
                diretorio=''  # Não salvar automaticamente
            )
            
            # Gerar payload completo
            payload_completa = payload_gen.gerarPayload()
            self.current_payload = payload_completa
            
            # Obter objeto QR Code
            qr_obj = payload_gen.get_qrcode_image()
            
            # Exibir QR Code na interface
            self.display_qrcode(qr_obj)
            
            # Exibir código PIX
            self.display_payload(payload_completa)
            
            # Atualizar status e habilitar botão de salvar
            self.status_label.config(text="✅ PIX gerado com sucesso! Escaneie o QR Code ou copie o código.")
            self.btn_save.config(state=tk.NORMAL)
            
            # Exibir payload no console para debug
            print("\n" + "="*60)
            print("PAYLOAD PIX GERADO:")
            print(payload_completa)
            print("="*60 + "\n")
            
        except ValueError as ve:
            messagebox.showerror("Erro de Valor", f"Erro no valor: {str(ve)}")
        except Exception as e:
            messagebox.showerror("Erro na Geração", 
                               f"Erro ao gerar PIX:\n\n{str(e)}\n\nVerifique os dados e tente novamente.")
    
    def display_qrcode(self, qr_obj):
        """Exibe o QR Code na interface"""
        try:
            # Redimensionar para exibição
            qr_img = qr_obj.resize((300, 300), Image.Resampling.LANCZOS)
            
            # Converter para formato Tkinter
            self.qr_image = ImageTk.PhotoImage(qr_img)
            
            # Atualizar label
            self.qr_label.config(image=self.qr_image, text="")
            
        except Exception as e:
            messagebox.showerror("Erro de Exibição", f"Erro ao exibir QR Code: {str(e)}")
    
    def display_payload(self, payload):
        """Exibe o código PIX na caixa de texto"""
        self.pix_text.config(state=tk.NORMAL)
        self.pix_text.delete(1.0, tk.END)
        
        # Formatar payload para melhor visualização
        formatted_payload = ""
        for i in range(0, len(payload), 50):
            formatted_payload += payload[i:i+50] + "\n"
        
        self.pix_text.insert(1.0, formatted_payload.strip())
        self.pix_text.config(state=tk.DISABLED)
    
    def save_qrcode(self):
        """Salva o QR Code em um arquivo"""
        if not self.current_payload:
            messagebox.showerror("Erro", "Nenhum QR Code para salvar. Gere um PIX primeiro.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("All Files", "*.*")
            ],
            title="Salvar QR Code como",
            initialfile="pix_qrcode.png"
        )
        
        if file_path:
            try:
                # Gerar QR Code em alta resolução
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=10,
                    border=4,
                )
                qr.add_data(self.current_payload)
                qr.make(fit=True)
                
                # Criar e salvar imagem
                img = qr.make_image(fill_color="black", back_color="white")
                
                # Converter para RGB se necessário
                if img.mode != 'RGB' and file_path.lower().endswith('.jpg'):
                    img = img.convert('RGB')
                
                img.save(file_path)
                
                messagebox.showinfo("Sucesso", 
                                  f"QR Code salvo com sucesso!\n\nLocal: {file_path}")
                
                self.status_label.config(text=f"✅ QR Code salvo em: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n\n{str(e)}")
    
    def copy_to_clipboard(self):
        """Copia o código PIX para a área de transferência"""
        if not self.current_payload:
            messagebox.showwarning("Aviso", "Nenhum código PIX para copiar. Gere um PIX primeiro.")
            return
        
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.current_payload)
            
            # Manter conteúdo na área de transferência
            self.root.update()
            
            messagebox.showinfo("Copiado", "✅ Código PIX copiado para a área de transferência!")
            self.status_label.config(text="✅ Código PIX copiado para a área de transferência")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível copiar:\n\n{str(e)}")
    
    def clear_fields(self):
        """Limpa todos os campos e resultados"""
        # Limpar campos de entrada
        self.nome_var.set("")
        self.chave_var.set("")
        self.valor_var.set("1.00")
        self.cidade_var.set("")
        self.txid_var.set("")
        
        # Limpar resultados
        self.pix_text.config(state=tk.NORMAL)
        self.pix_text.delete(1.0, tk.END)
        self.pix_text.config(state=tk.DISABLED)
        
        # Limpar QR Code
        if hasattr(self, 'qr_image'):
            self.qr_label.config(image="", 
                               text="O QR Code aparecerá aqui\napós gerar o PIX")
            self.qr_image = None
        
        # Resetar estado
        self.current_payload = None
        self.btn_save.config(state=tk.DISABLED)
        self.status_label.config(text="Campos limpos. Preencha os dados para gerar um novo PIX.")


# ============================================================================
# FUNÇÃO PRINCIPAL E INSTALAÇÃO DE DEPENDÊNCIAS
# ============================================================================
def check_dependencies():
    """Verifica e instala dependências necessárias"""
    required = {
        'Pillow': 'PIL',
        'qrcode': 'qrcode',
        'crcmod': 'crcmod'
    }
    
    missing = []
    
    for package, import_name in required.items():
        try:
            if import_name == 'PIL':
                from PIL import Image
            else:
                __import__(import_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print("🔄 Instalando dependências faltantes...")
        import subprocess
        import sys
        
        for package in missing:
            print(f"  Instalando {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"  ✅ {package} instalado com sucesso!")
            except subprocess.CalledProcessError:
                print(f"  ❌ Falha ao instalar {package}")
                return False
        
        print("\n✅ Todas as dependências foram instaladas!")
    
    return True


def main():
    """Função principal da aplicação"""
    print("="*60)
    print("       GERADOR DE PIX COM QR CODE v2.0")
    print("="*60)
    print("\nVerificando dependências...")
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Não foi possível instalar todas as dependências.")
        print("Por favor, instale manualmente:")
        print("  pip install pillow qrcode[pil] crcmod")
        input("\nPressione Enter para sair...")
        return
    
    print("\n✅ Dependências verificadas. Iniciando aplicação...")
    
    try:
        # Criar janela principal
        root = tk.Tk()
        
        # Configurar tema básico
        root.style = ttk.Style()
        root.style.theme_use('clam')
        
        # Criar aplicação
        app = PixGeneratorApp(root)
        
        # Configurar para fechar corretamente
        def on_closing():
            print("\n👋 Aplicação finalizada.")
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Iniciar loop principal
        print("✅ Aplicação iniciada com sucesso!")
        print("\n💡 Dica: Use dados reais de PIX para testes.")
        root.mainloop()
        
    except Exception as e:
        print(f"\n❌ Erro ao iniciar aplicação: {e}")
        print("\nTente executar: pip install pillow qrcode[pil] crcmod")
        input("Pressione Enter para sair...")


# ============================================================================
# EXECUÇÃO DO SCRIPT
# ============================================================================
if __name__ == "__main__":
    main()