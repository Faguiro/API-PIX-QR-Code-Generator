# API PIX QR Code Generator

## 🚀 Sobre a Plataforma

A **API PIX QR Code Generator** é uma solução completa e eficiente para geração dinâmica de QR Codes para transações PIX. Desenvolvida com Python e Flask, nossa plataforma oferece uma interface RESTful intuitiva que permite a criação rápida e segura de QR Codes PIX prontos para uso em pagamentos, cobranças e transações financeiras.

---

## ✨ Funcionalidades Principais

- ✅ Geração Instantânea de QR Codes PIX
- ✅ Interface Web Intuitiva para testes e demonstração
- ✅ API RESTful com endpoints bem documentados
- ✅ Suporte a Parâmetros Personalizáveis do PIX
- ✅ Respostas em JSON estruturadas
- ✅ Base64 Encoding para fácil integração
- ✅ CORS Habilitado para consumo frontend

---

## 🌐 Acesse a Plataforma

**URL Oficial do Projeto:** [https://snakeproject.pythonanywhere.com/pix_generator](https://snakeproject.pythonanywhere.com/pix_generator)

---

## 🎯 Como Usar

### Interface Web

Acesse nosso site para utilizar a interface gráfica que facilita a geração de QR Codes PIX:

1. Preencha os campos necessários:
   - Chave PIX
   - Valor da transação
   - Nome do beneficiário
   - Cidade
2. Clique em "Gerar QRcode"
3. Visualize e baixe o QR Code gerado
4. Teste com leitores PIX para validar

### API Endpoints

#### Gerar QR Code PIX

```http
POST /generate-pix-qrcode
```

**Exemplo de requisição:**

```json
{
  "pix_key": "12345678900",
  "amount": 150.75,
  "recipient_name": "João Silva",
  "city": "São Paulo"
}
```

#### Interface Web

```http
GET /pix_generator
```

Acesse nossa interface web completa para testes e demonstração.

---

## 📊 Exemplos de Uso

### Interface de Geração

<img width="1267" alt="Interface Principal da API PIX" src="https://github.com/user-attachments/assets/27178a44-6e4c-4c2c-96e0-29f3e1b2f8a3" />

### QR Code Gerado

<img width="1006" height="863" alt="image" src="https://github.com/user-attachments/assets/e28a80ca-805b-49b7-b041-5086d4c112a6" />

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Descrição |
|------------|-----------|
| **Python 3** | Linguagem principal |
| **Flask** | Framework web |
| **qrcode** | Geração de QR Codes |
| **Pillow** | Manipulação de imagens |
| **PythonAnywhere** | Hospedagem |

---

## 🔗 Integração

Nossa API foi projetada para fácil integração com:

- 💻 Aplicações web e mobile
- 🛒 Sistemas de e-commerce
- 💳 Plataformas de pagamento
- 📱 Aplicativos financeiros
- 🏢 Sistemas empresariais

---

## 📄 Estrutura da Resposta

A API retorna um JSON estruturado contendo:

- ✅ Status da operação
- 🖼️ Dados do QR Code em base64
- 📋 Metadados da transação
- ⚠️ Mensagens de erro/sucesso

---

## 🌟 Vantagens

| Vantagem | Descrição |
|----------|-----------|
| **Fácil Integração** | API simples e documentada |
| **Confiável** | Hospedagem estável no PythonAnywhere |
| **Seguro** | Validações de dados implementadas |
| **Escalável** | Arquitetura preparada para crescimento |
| **Open Source** | Código disponível para contribuição |

---

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:

- 🐛 Reportar issues
- 💡 Sugerir melhorias
- 🔧 Enviar pull requests

---

## 📞 Suporte

Para dúvidas ou suporte:

1. 📖 Acesse nossa documentação online
2. 💻 Verifique os exemplos de uso
3. 📧 Entre em contato através do repositório

---

## ⭐ Apoie o Projeto

Se este projeto te ajudou, considere dar uma estrela no repositório!

---

## 🔗 Acesse Agora

**[https://snakeproject.pythonanywhere.com/pix_generator](https://snakeproject.pythonanywhere.com/pix_generator)**

---

## 📌 Nota

Esta API é ideal para desenvolvedores que precisam integrar funcionalidades PIX em suas aplicações de forma rápida e confiável.

---

## 📝 Licença

Este projeto está sob a licença que permite uso livre para fins educacionais e comerciais.

---

**Desenvolvido com ❤️ para facilitar integrações PIX no Brasil**
