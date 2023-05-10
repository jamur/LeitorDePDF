import PyPDF2
import re
import pandas as pd
import yfinance as yf

def addRow(rows, company, ticker):
	co = yf.Ticker(ticker)
	history = co.history(period="max", interval="3mo")
	try:
		ipo = history.index[0].tz_localize(None) # removed timezone because excel don't support
		firstValue = history.iloc[0,0]
		lastValue = history.iloc[-1,0]
		lastDate = history.index[-1].tz_localize(None)  # removed timezone because excel don't support
		howMuchPercent = ((lastValue - firstValue) / firstValue) * 100
	except: # there is no values for ticker
		ipo = None
		firstValue = None
		lastValue = None
		lastDate = None
		howMuchPercent = None
	row = [company, ticker, ipo, firstValue, lastValue, lastDate, howMuchPercent]
	# add row in the dataframe
	rows.append(row)
	print( company + " | " + ticker + " | ̭̭" + str(ipo) + " | ̭̭" + str(firstValue) + " | ̭̭" + str(lastValue) + " | ̭̭" + str(lastDate) + " | ̭̭" + str(howMuchPercent))

	return 

pdf_file = open('ru2000_membershiplist_20220624_0.pdf', 'rb')
read_pdf = PyPDF2.PdfReader(pdf_file)
pages = read_pdf.pages
p = 0
columns = ['Company', 'Ticker', 'IPO', 'First Value', 'Last Value',
	   		 'Last Date', 'How Much']
rows = []

# Lê até encontrar as strings que indicam final
while True:
	page = pages[p]
	page_content = page.extract_text()
	parsed = ''.join(page_content)
	splited = parsed.split('\n')
	print("\n\n---------------------")
	print("Página " + str(p+1))
	print("---------------------\n")
	if p != 9: # Tratamento normal - a não ser a página 10 (no else) que está fora do padrão
		c = 0
		#cabeçalhos
		print(splited[c] + " | " + splited[c+1])
		c += 2
		ended = False
		while splited[c] != "June 24, 2022": #String do fim de cada página
			if splited[c] == "ftserussell.com": #String no final de toda a lista
				print("----------------\nTerminou\n----------------")
				ended = True
				break
			company = splited[c]
			ticker = splited[c+1]
			addRow(rows, company, ticker)
			#df.loc[len(df.index)] = [company, ticker, ipo, firstValue, lastValue, lastDate, howMuchPercent]
			c += 2
			df = pd.DataFrame(rows, columns = columns)
			print(df)
			df.to_excel('SuperTempShares.xlsx')


	else:
		# Na página 10 o PDF fica sem quebra de linhas entre colunas
		
		c = 0
		# cabeçalhos
		headers = splited[c].rsplit(maxsplit=1)
		print(headers[0] + " | " + headers[1])
		c += 1
		while splited[c][:13] != "June 24, 2022":
			# separa o ticker, que está a direita
			subsplited = splited[c].rsplit(maxsplit=1)
			company = subsplited[0]
			ticker = subsplited[1]
			addRow(rows, ticker)
			#df.loc[len(df.index)] = [company, ticker, ipo, firstValue, lastValue, lastDate, howMuchPercent]
			c += 1

	if ended:
		print("----------------\nTerminou Mesmo\n----------------")
		break

	p += 1
	df = pd.DataFrame(rows, columns = columns)
	
	#print(df)
	#df.to_excel('TempShares.xlsx')

print(df)
df.to_excel('Shares.xlsx')

#print("Sem eliminar as quebras")
#print(parsed)

#parsed = re.sub('n', '', parsed)
#print("Após eliminar as quebras")
#print(parsed)

#print("Pegando apenas as 20 primeiras posições")
#novastring = parsed[0:20]
#print(novastring)




