from dataclasses import dataclass
import datetime
import logging
import os

logger = logging.getLogger()

FILE_NAME = "data.csv"

@dataclass
class Price():
	date: datetime.datetime
	price: float


	@classmethod
	def create_price(cls, date, price):
		date_time_date = cls.__valid_date__(date)
		price = cls.__valid__price_float__(price)
		return cls(date_time_date, price)

	@staticmethod
	def __valid_date__(date: str):
		try:
			return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
		except ValueError:
			logger.error(f"creating Price object failed the date is not valid '{date}'", exc_info=True)
			raise NotInFormatError("row from the data in the csv not in the format")

	@staticmethod
	def __valid__price_float__(price: str):
		try: 
			return float(price)
		except ValueError:
			logger.error(f"creating Price object failed the date is not valid '{price}'", exc_info=True)
			raise NotInFormatError("row from the data in the csv not in the format")


class NotInFormatError(Exception):
	pass


def read_data(file_name: str) -> list :
	with open(file_name, 'r') as f:
		try:
			raw_data = f.read().split('\n')[1:]
		except Exception as e:
			logger.error(f"read data from {file_name} failed", exc_info=True)			
	return raw_data


def create_prices(raw_data: list):
	list_of_prices = []
	for row in raw_data:
		if row == '': #empty row in the end
			continue
		row_split = row.split(',')
		if len(row_split) != 2:
			logger.error(f"row from the data in the csv not in the format {len(row_split)} items in rows: {row}")
			raise NotInFormatError("row from the data in the csv not in the format")
		date, raw_price = row_split
		price = Price.create_price(date, raw_price)
		list_of_prices.append(price)
		logger.debug(f"{price} add to list_of_prices list")
	logger.debug(f"{len(list_of_prices)} row add to list_of_prices")
	return list_of_prices


def run_analyze_for_today(prices_list):
	today_price = prices_list.pop()
	if today_price.date.date() != datetime.datetime.now().date():
		logger.error("in run_analyze_for_today the day that poped not today")
		raise Exception("run_analyze_for_today must be for today price")

	analize_parmeters = [[1, 0.10, "Yesterday"], [7, 0.15, "Last Week"], [30, 0.20, "Last Month"], [90, 0.30, "3 Month Ago"]]

	gap_list = list()
	for parmeters in analize_parmeters:
		logger.debug("comparing start")
		days, precent, compare_name  = parmeters
		date_price_to_compare = get_compare_date(prices_list, today_price, days)
		if date_price_to_compare:
			gap_amount = int(today_price.price - date_price_to_compare.price)
			gap_in_precent = compare_prices(today_price, date_price_to_compare, precent)
			if gap_in_precent: #if the gap relevant for allerting
				logger.info(f"gap found {compare_name} - {format(gap_in_precent, '.4f')}% changed {gap_amount}$")
				gap_list.append((compare_name, gap_in_precent, gap_amount))
			else:
				logger.debug("no gap in this compration")
	return gap_list




def get_compare_date(prices, today_price, days):
	for price in prices[::-1]:
		if today_price.date.date() - datetime.timedelta(days=days) == price.date.date():
			return price


def compare_prices(today, price_to_compare, precent):
	change_in_currency_in_precent = today.price / price_to_compare.price - 1
	if change_in_currency_in_precent > 0:
		if change_in_currency_in_precent > precent:
			return change_in_currency_in_precent
	else:
		if change_in_currency_in_precent < precent * -1:
			return change_in_currency_in_precent
	return None



def run_analyze(file_name=FILE_NAME):
	raw_data = read_data(file_name)
	prices_list = create_prices(raw_data)
	return run_analyze_for_today(prices_list)


if __name__ == "__main__":
	pass