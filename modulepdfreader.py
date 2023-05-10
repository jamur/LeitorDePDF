import PyPDF2
import re
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
#import logging
#import concurrent.futures
import threading
import time
from progressbar import progressbar
from alive_progress import alive_bar

# TODO Threads

class PDFReader():

	def __init__(self, pdfFile):
		format = "%(asctime)s: %(message)s"
		#logging.basicConfig(format=format, level=logging.INFO,
		#					datefmt="%H:%M:%S")
		pdf = open(pdfFile, 'rb')
		read_pdf = PyPDF2.PdfReader(pdf)
		self.pages = read_pdf.pages

	def addCompany(self, companies, company, ticker):
		row = [company, ticker]
		companies.append(row)
		#logging.info( company + " | " + ticker )
		return 
	
	# Lê o PDF e retorna uma lista de listas: [Nome da Empresa, Ticker]
	def readCompanies(self) -> list:
		companies = []
		pageNumber = 0
		# Lê até encontrar as strings que indicam final
		while True:
			page = self.pages[pageNumber]
			page_content = page.extract_text()
			parsed = ''.join(page_content)
			cels = parsed.split('\n')
			#print("\n\n---------------------")
			#print("Página " + str(pageNumber+1))
			#print("---------------------\n")
			celNumber = 0
			cab = (cels[celNumber])
			if cab == "Company": # pageNumber != 9: # Tratamento normal - a não ser a página 10 (no else) que está fora do padrão
				#cabs
				celNumber += 2
				ended = False
				while cels[celNumber] != "June 24, 2022": #String do fim de cada página
					if cels[celNumber] == "ftserussell.com": #String no final de toda a lista
						#print("----------------\nTerminou\n----------------")
						ended = True
						break
					company = cels[celNumber]
					ticker = cels[celNumber+1]
					if company != "Company": # test if cab
						self.addCompany(companies, company, ticker)

					#df.loc[len(df.index)] = [company, ticker, ipo, firstValue, lastValue, lastDate, howMuchPercent]
					celNumber += 2
					#df = pd.DataFrame(self.rows, columns = columns)
					#print(df)
					#df.to_excel('SuperTempShares.xlsx')
			else: # if cab = "Company Ticker" - Nem method to discover other pattern of page
				# Na página 10 o PDF fica sem quebra de linhas entre colunas
				# cabeçalhos
				headers = cels[celNumber].rsplit(maxsplit=1)
				#print(headers[0] + " | " + headers[1])
				celNumber += 1
				while cels[celNumber][:13] != "June 24, 2022":
					# separa o ticker, que está a direita
					subCel = cels[celNumber].rsplit(maxsplit=1)
					company = subCel[0]
					ticker = subCel[1]
					if company != "Company": # test if cab
						self.addCompany(companies, company, ticker)
					#df.loc[len(df.index)] = [company, ticker, ipo, firstValue, lastValue, lastDate, howMuchPercent]
					celNumber += 1

			if ended:
				#print("----------------\nTerminou Mesmo\n----------------")
				break

			pageNumber += 1
			#df = pd.DataFrame(rows, columns = columns)
			
			#print(df)
			#df.to_excel('TempShares.xlsx')

		self.companies = companies
		return companies
	
	def getFirstValue(self, co, ipo):
		limit = 1
		day = ipo
		while limit < 180:
			history = co.history(start=day, end=day + timedelta(1))
			firstValue = history.iloc[0,0]
			if firstValue:
				return firsValue
			day += timedelta(1)
			limit += 1

	def addYFRow(self, companyRow):
		company = companyRow[0]
		ticker = companyRow[1]
		#print(ticker, end=".")
		co = yf.Ticker(ticker)
		#history = co.history(period="max", interval="3mo")
		try: # Ticker ONEM raises an error, for ex.
			info = co.info
			firstUTC = info['firstTradeDateEpochUtc']
		except:
			ipo = firstValue = lastValue = lastDate = howMuchPercent = None
			row = [company, ticker, ipo, firstValue, lastValue, lastDate, howMuchPercent]
			self.yfDataRows.append(row)
			return

		ipo = datetime.utcfromtimestamp(firstUTC).date()
		# ipo = history.index[0].date() # .tz_localize(None).date() # removed timezone because excel don't support
		history = co.history(start=ipo, end=ipo + timedelta(1))

		try:
			firstValue = history.iloc[0,0]
		except:
			firstValue = None

		#if firstValue == 0:
		#	firstValue = self.getFirstValue(co, ipo)

		try:
			lastValue = co.info['currentPrice'] #history.iloc[-1,0]
		except:
			#history = co.history(period = "1d")
			lastValue = None

		#history = co.history(period="1m")
		#try:
		#	lastDate = history.index[-1].date()  # removed timezone because excel don't support
		#	lastDate = lastDate.strftime("%d/%m/%Y")
		#except:
		#	lastDate = None
		lastDate = None

		if firstValue and lastValue:
			howMuchPercent = ((lastValue - firstValue) / firstValue) * 100
			howMuchPercent = f"{howMuchPercent:.0f}%"
			firstValue = f"{firstValue:.2f}"
			lastValue = f"{lastValue:.2f}"
		else:
			howMuchPercent = None

		ipo = ipo.strftime("%d/%m/%Y")
		row = [company, ticker, ipo, firstValue, lastValue, lastDate, howMuchPercent]
		self.yfDataRows.append(row)
		#logging.info( company + " | " + ticker + " | ̭̭" + str(ipo) + " | ̭̭" +
		#		str(firstValue) + " | ̭̭" + str(lastValue) + " | ̭̭" + 
		#		str(lastDate) + " | ̭̭" + str(howMuchPercent))
		#ipo = "N/D"
		#firstValue = "N/D"
		#lastValue = "N/D"
		#lastDate = "N/D"
		#howMuchPercent = "N/D"
		# add row in the list
		return row

	# based on self.
	def readYFDataRowsThread(self,qt=0) -> list:
		self.yfDataRows = []
		threads = list()
		#logging.info("Runing threads")
		if not(qt): # if no qt then qt = total
			qt = len(self.companies)
		print("Creating Threads...")
		with alive_bar(qt) as bar:
			for companie_number in range(qt):
				companie = self.companies[companie_number]
				#print(".", end="")
				#logging.info(f"Main    : before creating thread {t}")
				x = threading.Thread(target=self.addYFRow, args=(companie,))
				threads.append(x)
				#logging.info(f"Main    : before running thread {t}")
				x.start()
				#logging.info(f"Main    : wait for the thread to finish {t}")
				#x.join()
				bar()

		threads_qt = len(threads)
		print("Waiting Threads...")
		with alive_bar(qt) as bar:
			while threads_qt > 0:
				time.sleep(5)
				for thread in threads:
					if not(thread.is_alive()):
						threads_qt -= 1
						bar()

		# Só pra garantir
		for thread in threads:
			thread.join()

		#logging.info("Main    : all done")
		#with concurrent.futures.ThreadPoolExecutor as executor:
		#	executor.map(self.addYFRow, companyTupleOfTuples)
		#for company in companies:
		#	self.addYFRow(yfDataRows, company)
		return self.yfDataRows

	def readYFDataRowsNoThread(self, qt=0) -> list:
		self.yfDataRows = []
		#logging.info(self.companies)
		if not(qt): # if no qt then qt = total
			qt = len(self.companies)
		with alive_bar(qt) as bar:
			for companie_number in range(qt):
				companie = self.companies[companie_number]
				self.addYFRow(companie)
				#print(".", end="")
				#logging.info(companie[1])
				bar()
		#logging.info("Main    : all done")
		#with concurrent.futures.ThreadPoolExecutor as executor:
		#	executor.map(self.addYFRow, companyTupleOfTuples)
		#for company in companies:
		#	self.addYFRow(yfDataRows, company)
		return self.yfDataRows

	def readYFDataRows(self, thread=False, qt=0):
		self.yfDataRows = []
		#self.readYFDataRowsThread()
		if thread:
			self.readYFDataRowsThread(qt)
		else:
			self.readYFDataRowsNoThread(qt)
		columns = ['Company', 'Ticker', 'IPO', 'First Value', 'Last Value',
	   		 'Last Date', 'How Much']
		self.df = pd.DataFrame(self.yfDataRows, columns = columns)
		return self.yfDataRows
		

	def saveExcel(self, arqName):
		self.df.to_excel(arqName)


if __name__ == "__main__":
	qt =  15
	pdf_reader = PDFReader('ru2000_membershiplist_20220624_0.pdf')
	companies = pdf_reader.readCompanies()
	start_time = time.perf_counter()
	df_yf_data = pdf_reader.readYFDataRows(qt=qt)
	end_time = time.perf_counter()
	execution_time = end_time - start_time
	print(f"The execution time is: {execution_time}")
	pdf_reader.saveExcel('CompaniesGrowing.xlsx')

	# More than half more time
	#start_time = time.perf_counter()
	#df_yf_data = pdf_reader.readYFDataRows(qt, thread=False)
	#end_time = time.perf_counter()
	#execution_time = end_time - start_time
	#print(f"The execution time with no thread is: {execution_time}")
	#pdf_reader.saveExcel('NoThread.xlsx')

#print("Sem eliminar as quebras")
#print(parsed)

#parsed = re.sub('n', '', parsed)
#print("Após eliminar as quebras")
#print(parsed)

#print("Pegando apenas as 20 primeiras posições")
#novastring = parsed[0:20]
#print(novastring)




