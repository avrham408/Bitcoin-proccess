import requests
from bs4 import BeautifulSoup
import os
import ctypes
import time
import logging
import datetime
import analyze 

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
LOG_FILENAME = 'logging.log'
s_handler = logging.StreamHandler()
f_handler = logging.FileHandler(LOG_FILENAME)
s_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
s_handler.setFormatter(formatter)
f_handler.setFormatter(formatter)
logger.addHandler(s_handler)
logger.addHandler(f_handler)





URL = 'https://il.investing.com/crypto/bitcoin/btc-usd'
SLEEPING_TIME = 60 * 30
TITLE = "Bitcoin Scrapper"
TEST_FILE_CSV = 'test.csv'

def raise_message(msg, ):
	MessageBox = ctypes.windll.user32.MessageBoxW
	MessageBox(None, msg, TITLE, 0)


def get_data(url: str):
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
	logger.debug("starting get data from {}".format(url))
	try:
		page = requests.get(url, headers=headers)
	except requests.exceptions.ConnectionError:
		logging.debug("internet not connected")
		return "restart"
	if page.status_code != 200:
		logger.error("URL {} answer with {}".format(URL, page.status_code))
		raise_message("URL {} answer with {}".format(URL, page.status_code))
		return None
	return page


def scrap(page):
	soup = BeautifulSoup(page.content, 'html.parser')
	class_data = soup.find_all(class_='top bold inlineblock')
	if not class_data:
		logger.info("spliting to class_data 'top bold inlineblock' failed")
		return False
	logger.debug("data split to top bold inlineblock class")
	id_data = soup.find_all(id='last_last')[0]
	if not id_data:
		logger.info("spliting to id = last_id failed")
		return False
	logger.debug("data split to last_last div id")
	price = id_data.contents[0]
	float_price = change_price_to_float(price)
	if not float_price:
		logger.info("changing price from string to float failed price value is = {}", float_price)
	return float_price	


def change_price_to_float(price: str):
	p = price.replace(',', '')
	try:
		return float(p)
	except ValueError as e:
		return False


def scrap_price():
	while True:
		logger.debug("starting ")
		page = get_data(URL)
		if not page: #SOMTHING HAPPEND TO URL
			logger.error("scrapping failed the url not stable")
			break
		if page == "restart":
			time.sleep(SLEEPING_TIME)
			logger.debug('restart')
			continue
		else:
			price = scrap(page)
			if not price:
				logger.info("scrapping price failed")
				break
			return price 
	return False


def add_price(price: float, file_name="data.csv"):
	row = "{},{}".format(str(datetime.datetime.today()), price)


	with open(file_name, 'a') as f:
		try:
			f.write('\n' + row)
			logger.info("data write to the csv")
		except Exception as e:
			logger.error("writing to file failed", exc_info=True)


def manage_gap(gap_list):
	if not gap_list:
		logger.info("nothing interesting happend")
		return
	if len(gap_list) == 1:
		raise_message(f"gap found {gap_list[0][0]} - {format(gap_list[0][1], '.4f')}% changed {gap_list[0][2]}$")		
	else:
		raise_message("more then one change happend go to log and to web to see what changed")

print("adar")

if __name__ == "__main__":
	price = scrap_price()
	if not price:
		exit()
	logger.info("server back with {} bitcoin to dolar".format(price))
	add_price(price)
	gap_list = analyze.run_analyze()
	manage_gap(gap_list)




