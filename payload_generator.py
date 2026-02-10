#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador de payload PIX para QR Code estático, seguindo o padrão do Banco Central do Brasil.
Inclui funções para normalização de texto, formatação de campos e cálculo do CRC16.
"""

import crcmod
import qrcode
import os


class Payload():
    def __init__(self, nome, chavepix, valor, cidade, txtId, diretorio=''):
        
        self.nome = nome
        self.chavepix = chavepix
        self.valor = valor.replace(',', '.')
        self.cidade = cidade
        self.txtId = txtId
        self.diretorioQrCode = diretorio

        self.nome_tam = len(self.nome)
        self.chavepix_tam = len(self.chavepix)
        self.valor_tam = len(self.valor)
        self.cidade_tam = len(self.cidade)
        self.txtId_tam = len(self.txtId)

        self.merchantAccount_tam = f'0014BR.GOV.BCB.PIX01{self.chavepix_tam:02}{self.chavepix}'
        self.transactionAmount_tam = f'{self.valor_tam:02}{float(self.valor):.2f}'

        self.addDataField_tam = f'05{self.txtId_tam:02}{self.txtId}'

        self.nome_tam = f'{self.nome_tam:02}'

        self.cidade_tam = f'{self.cidade_tam:02}'

        self.payloadFormat = '000201'
        self.merchantAccount = f'26{len(self.merchantAccount_tam):02}{self.merchantAccount_tam}'
        self.merchantCategCode = '52040000'
        self.transactionCurrency = '5303986'
        self.transactionAmount = f'54{self.transactionAmount_tam}'
        self.countryCode = '5802BR'
        self.merchantName = f'59{self.nome_tam:02}{self.nome}'
        self.merchantCity = f'60{self.cidade_tam:02}{self.cidade}'
        self.addDataField = f'62{len(self.addDataField_tam):02}{self.addDataField_tam}'
        self.crc16 = '6304'

        # Variáveis para armazenar resultados
        self.payload_completa = None
        self.qrcode = None
  
    def gerarPayload(self):
        self.payload = f'{self.payloadFormat}{self.merchantAccount}{self.merchantCategCode}{self.transactionCurrency}{self.transactionAmount}{self.countryCode}{self.merchantName}{self.merchantCity}{self.addDataField}{self.crc16}'

        self.gerarCrc16(self.payload)
        return self.payload_completa

    
    def gerarCrc16(self, payload):
        crc16 = crcmod.mkCrcFun(poly=0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)

        self.crc16Code = hex(crc16(str(payload).encode('utf-8')))

        self.crc16Code_formatado = str(self.crc16Code).replace('0x', '').upper().zfill(4)

        self.payload_completa = f'{payload}{self.crc16Code_formatado}'

        self.gerarQrCode(self.payload_completa, self.diretorioQrCode)
        return self.payload_completa

    
    def gerarQrCode(self, payload, diretorio):
        dir = os.path.expanduser(diretorio)
        self.qrcode = qrcode.make(payload)
        
        # Salvar apenas se diretório for especificado
        if dir and os.path.exists(dir):
            self.qrcode.save(os.path.join(dir, 'pixqrcodegen.png'))
        
        return self.qrcode
    
    def get_qrcode_image(self):
        """Retorna o objeto QR Code PIL Image"""
        return self.qrcode
    
    def get_payload(self):
        """Retorna o payload completo"""
        return self.payload_completa


if __name__ == '__main__':
    # Teste da classe
    payload = Payload('Nome Sobrenome', '12345678900', '1.00', 'Cidade Ficticia', 'LOJA01')
    resultado = payload.gerarPayload()
    print(f"Payload gerado: {resultado[:50]}...")