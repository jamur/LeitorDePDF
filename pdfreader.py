import PyPDF2
import re

def processa9():
	# Depois da página 9 (página 10) o PDF fica sem quebra de linhas entre colunas
	while p == 9:

		page = read_pdf.pages[p]

		page_content = page.extract_text()

		parsed = ''.join(page_content)
		
		splited = parsed.split('\n')

		print("\n\n---------------------")
		print("Página " + str(p+1))
		print("---------------------\n")

		c = 0

		#cabeçalhos
		subsplited = splited[c].rsplit(maxsplit=1)

		print(subsplited[0] + " | " + subsplited[1])

		c = 1

		ended = False

		while splited[c][:13] != "June 24, 2022":

			if splited[c][:14] == "ftserussel.com":
				print("----------------\nTerminou\n----------------")
				break
				ended = True

			subsplited = splited[c].rsplit(maxsplit=1)

			print(subsplited[0] + " | " + subsplited[1])
			c += 2

		if ended:
			break

		p += 1


pdf_file = open('ru2000_membershiplist_20220624_0.pdf', 'rb')
read_pdf = PyPDF2.PdfReader(pdf_file)
number_of_pages = read_pdf.pages
page = read_pdf.pages[0]
page_content = page.extract_text()

parsed = ''.join(page_content)
print("Sem eliminar as quebras")
print(parsed)

parsed = re.sub('n', '', parsed)
print("Após eliminar as quebras")
print(parsed)

print("Pegando apenas as 20 primeiras posições")
novastring = parsed[0:20]
print(novastring)

splited = parsed.split('\n')
type(splited)

p = 0

def processa10():
	# Na página 10 o PDF fica sem quebra de linhas entre colunas

	global p

	page = read_pdf.pages[p]

	page_content = page.extract_text()

	parsed = ''.join(page_content)

	print(parsed)
	
	splited = parsed.split('\n')

	print("\n\n---------------------")
	print("Página " + str(p+1))
	print("---------------------\n")

	c = 0

	#cabeçalhos
	subsplited = splited[c].rsplit(maxsplit=1)

	print(subsplited[0] + " | " + subsplited[1])

	c = 1

	ended = False

	while splited[c][:13] != "June 24, 2022":

		subsplited = splited[c].rsplit(maxsplit=1)

		print(subsplited[0] + " | " + subsplited[1])
		c += 2

	p += 1


#Com quebras de linha entre colunas
while p <= 23:

	if p == 9:
		processa10()
		continue

	page = read_pdf.pages[p]

	page_content = page.extract_text()

	parsed = ''.join(page_content)
	
	splited = parsed.split('\n')

	print("\n\n---------------------")
	print("Página " + str(p+1))
	print("---------------------\n")

	#cabeçalhos
	print(splited[0] + " | " + splited[1])

	c = 2

	ended = False

	while splited[c] != "June 24, 2022":

		if splited[c] == "ftserussell.com":
			print("----------------\nTerminou\n----------------")
			ended = True
			break

		print(splited[c] + " | " + splited[c+1])
		c += 2

	if ended:
		break

	p += 1
