import PyPDF2
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import concurrent.futures
import time
from alive_progress import alive_bar

class PDFReader():

	def __init__(self, pdfFile):
		format = "%(asctime)s: %(message)s"
		pdf = open(pdfFile, 'rb')
		read_pdf = PyPDF2.PdfReader(pdf)
		self.pages = read_pdf.pages

	def addCompany(self, companies, company, ticker):
		row = [company, ticker]
		companies.append(row)
		return 
	
	# Read PDF and return companies names and tickers
	def readCompanies(self) -> list:
		companies = []
		pageNumber = 0
		# Read until find end strings
		while True:
			page = self.pages[pageNumber]
			page_content = page.extract_text()
			parsed = ''.join(page_content)
			cels = parsed.split('\n')
			celNumber = 0
			cab = (cels[celNumber])
			if cab == "Company": # pageNumber != 9: # There are break lines among
				celNumber += 2
				ended = False
				while cels[celNumber] != "June 24, 2022": # Pages end string
					if cels[celNumber] == "ftserussell.com": # End string of all
						ended = True
						break
					company = cels[celNumber]
					ticker = cels[celNumber+1]
					if company != "Company": # test if cab
						self.addCompany(companies, company, ticker)

					celNumber += 2

			else: # cab = "Company Ticker" - Method to discover other pattern of page
				# No break lines in page 10
				# cabs
				headers = cels[celNumber].rsplit(maxsplit=1)
				celNumber += 1
				while cels[celNumber][:13] != "June 24, 2022":
					# split ticker at right
					subCel = cels[celNumber].rsplit(maxsplit=1)
					company = subCel[0]
					ticker = subCel[1]
					if company != "Company": # test if cab
						self.addCompany(companies, company, ticker)

					celNumber += 1

			if ended:
				break

			pageNumber += 1

		self.companies = companies
		return companies
	
	def addYFRow(self, companyRow):
		company = companyRow[0]
		ticker = companyRow[1]
		co = yf.Ticker(ticker)
		try: # Ticker ONEM raises an error, for ex.
			info = co.info
			firstUTC = info['firstTradeDateEpochUtc']
		except:
			ipo = firstValue = lastValue = lastDate = howMuchPercent = None
			row = [company, ticker, ipo, firstValue, lastValue, lastDate, howMuchPercent]
			self.yfDataRows.append(row)
			return

		ipo = datetime.utcfromtimestamp(firstUTC).date()
		history = co.history(start=ipo, end=ipo + timedelta(1))

		try:
			firstValue = history.iloc[0,0]
		except:
			# no history data for ticker
			firstValue = None

		try:
			lastValue = co.info['currentPrice'] #history.iloc[-1,0]
		except:
			# no data
			lastValue = None

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
		return row

	def readYFDataRowsThread(self,qt=0) -> list:
		self.yfDataRows = []

		if qt:
			companies = self.companies[:qt]
		else:
			companies = self.companies

		if not(qt): # if no qt then qt = total
			qt = len(self.companies)
		with concurrent.futures.ThreadPoolExecutor() as exe:
	       	# issue some tasks and collect futures
			print("Creating Threads...")
			futures = [exe.submit(self.addYFRow, companie) for companie in companies]
			print("Executing Threads...")
			with alive_bar(qt) as bar:

	        	# update bar as tasks are completed
				for future in concurrent.futures.as_completed(futures):

					bar()

    	# report that all tasks are completed
		print('Done.')
		return self.yfDataRows

	def readYFDataRowsNoThread(self, qt=0) -> list:
		self.yfDataRows = []
		if not(qt): # if no qt then qt = total
			qt = len(self.companies)
		with alive_bar(qt) as bar:
			for companie_number in range(qt):
				companie = self.companies[companie_number]
				self.addYFRow(companie)
				bar()
		return self.yfDataRows

	def readYFDataRows(self, thread=False, qt=0):
		self.yfDataRows = []
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
	qt =  0
	pdf_reader = PDFReader('ru2000_membershiplist_20220624_0.pdf')
	pdf_reader.readCompanies()
	start_time = time.perf_counter()
	pdf_reader.readYFDataRows(thread=True, qt=qt)
	end_time = time.perf_counter()
	execution_time = end_time - start_time
	execution_time_str = time.strftime("%H:%M:%S", time.gmtime(execution_time))
	print(f"The execution time is: {execution_time_str}")
	pdf_reader.saveExcel('CompaniesGrowing.xlsx')

