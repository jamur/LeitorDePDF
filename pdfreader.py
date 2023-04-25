import PyPDF2
import re


pdf_file = open('ru2000_membershiplist_20220624_0.pdf', 'rb')

read_pdf = PyPDF2.PdfReader(pdf_file)

pages = read_pdf.pages

p = 0

# Lê até encontrar as strings que indicam final
while True:

	page = pages[p]

	page_content = page.extract_text()

	parsed = ''.join(page_content)
	
	splited = parsed.split('\n')

	print("\n\n---------------------")
	print("Página " + str(p+1))
	print("---------------------\n")


	if p != 9:

		c = 0

		#cabeçalhos
		print(splited[c] + " | " + splited[c+1])

		c += 2

		ended = False

		while splited[c] != "June 24, 2022":

			if splited[c] == "ftserussell.com":
				print("----------------\nTerminou\n----------------")
				ended = True
				break

			print(splited[c] + " | " + splited[c+1])
			c += 2

	else:

		# Na página 10 o PDF fica sem quebra de linhas entre colunas
		#cabeçalhos

		c = 0

		subsplited = splited[c].rsplit(maxsplit=1)

		print(subsplited[0] + " | " + subsplited[1])

		c += 1

		while splited[c][:13] != "June 24, 2022":

			subsplited = splited[c].rsplit(maxsplit=1)

			print(subsplited[0] + " | " + subsplited[1])
			c += 1


	if ended:
		print("----------------\nTerminou Mesmo\n----------------")
		break

	p += 1

















#print("Sem eliminar as quebras")
#print(parsed)

#parsed = re.sub('n', '', parsed)
#print("Após eliminar as quebras")
#print(parsed)

#print("Pegando apenas as 20 primeiras posições")
#novastring = parsed[0:20]
#print(novastring)
