import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import re
import pandas as pd

# Configure o caminho do Tesseract, se necessário
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# pytesseract.pytesseract.tesseract_cmd = '/usr/local/bin/tesseract'  # Mac/Linux

def pdf_to_lines_with_ocr(pdf_path, zoom=4):  # Aumentamos o fator de zoom para 4
    doc = fitz.open(pdf_path)
    data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # Aumentar a resolução da imagem
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Converte a página do PDF em imagem
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Usa OCR para extrair texto da imagem
        page_text = pytesseract.image_to_string(img, lang="por", config='--psm 6 --oem 3 -c preserve_interword_spaces=1')  # Usando o idioma português
        
        # Separa o texto em linhas
        page_lines = page_text.split('\n')
        
        for i, line in enumerate(page_lines):
            # Verifica se é a última linha da página
            if i == len(page_lines) - 1:
                # Adiciona uma marcação à última linha
                data.append(['*** ' + line])
            else:
                # Divide cada linha em campos - 3 espaços ou mais, entende como delimitador
                fields = re.split(r'\s{3,}', line)  # Aqui você pode precisar ajustar a expressão regular (3 espaços)
                if len(fields) == 5:  # Verifica se a linha tem 5 campos
                    data.append(fields)

    return data

# Caminho para o seu arquivo PDF
pdf_path = 'listagem.pdf'

# Extrair linhas de texto
extracted_lines = pdf_to_lines_with_ocr(pdf_path, zoom=4)  # Aumentamos o fator de zoom para 4

# Cria um DataFrame pandas com os dados extraídos
df = pd.DataFrame(extracted_lines, columns=['Data', 'Hora', 'Tipo de Evento', 'Nome', 'Nº SNS'])

# Salva o DataFrame como uma planilha do Excel
df.to_excel('dados_extraidos.xlsx', index=False)

print("Os dados foram salvos com sucesso na planilha 'dados_extraidos.xlsx'.")
