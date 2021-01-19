# Imports
from selenium import webdriver
from pymongo import MongoClient
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re, requests, io, time, random, string
from datetime import date
from credentials import email, password
from stock_list import stock_list
import pprint as pp

client = MongoClient()
db = client['stock_data']
collection = db.current_data

options = Options()
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Chrome.app/Contents/MacOS/Google Chrome"
chrome_driver_binary = "/Users/jtreeves/Desktop/SEI1019/unit_four/codealong/chromedriver"
driver = webdriver.Chrome(chrome_driver_binary, chrome_options=options)
time.sleep(3)

def log_in(email=email, password=password):
    driver.get('https://wallmine.com')
    time.sleep(2)
    driver.find_element_by_xpath('/html/body/main/header/div/ul/li[1]/ul/li[3]/a').click() # click on sign in
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="new_user"]/div[5]/div[1]/div[2]/a').click() # click on sign in with a password
    if "We're glad you're back!" in driver.page_source:
        print('On sign in page')
        # Sign into website
        driver.find_element_by_xpath('//*[@id="user_email"]').send_keys(email)
        driver.find_element_by_xpath('//*[@id="user_password"]').send_keys(password)
        time.sleep(0.1)
        driver.find_element_by_xpath('//*[@id="new_user"]/div[5]/div[2]/div[1]/button').click()
        time.sleep(3)
        # Confirm on webpage after signed in
        if "Stock market overview" in driver.page_source:
            print('Sign in successful')
    else:
        print('Start app over')

def get_data(stocks):
    for i in range(len(stock_list)):
        each_stock = stock_list[i]
        driver.get(f"https://wallmine.com/{each_stock.get('exchange')}/{each_stock.get('stock_ticker')}")
        time.sleep(3)
        company_name = driver.find_element_by_xpath('/html/body/main/section/div[2]/div/div[1]/h1/div[2]/a').text

        current_price = driver.find_element_by_xpath('/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/span[1]').text

        percentage = driver.find_element_by_xpath('/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[2]/div')
        price_increase = True
        if driver.find_elements_by_class_name('badge.badge-success'):
            price_up = driver.find_elements_by_class_name('badge.badge-success')[0].text
            if price_up == percentage:
                print('price up')
        elif driver.find_elements_by_class_name('badge.badge-danger'):
            price_down = driver.find_elements_by_class_name('badge.badge-danger')[0].text
            if price_down == percentage:
                price_movement = False
                print('price down')

        amount_change = float(driver.find_element_by_xpath('/html/body/main/section/div[3]/div/div/div/div/div[2]/div/div[1]/span[2]').text[1:])
        
        check_market_cap = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[1]/td/span').text
        if check_market_cap[-1] == 'T':
            market_cap = float(check_market_cap[1:-1]) * 1000000000000
        elif check_market_cap[-1] == 'B':
            market_cap = float(check_market_cap[1:-1]) * 1000000000
        elif check_market_cap[-1] == 'M':
            market_cap = float(check_market_cap[1:-1]) * 1000000
        else:
            market_cap = 'N/A'

        check_enterprise_value = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[1]/table/tbody/tr[2]/td/span').text
        if check_enterprise_value[-1] == 'T':
            enterprise_value = float(check_enterprise_value[1:-1]) * 1000000000000
        elif check_enterprise_value[-1] == 'B':
            enterprise_value = float(check_enterprise_value[1:-1]) * 1000000000
        elif check_enterprise_value[-1] == 'M':
            enterprise_value = float(check_enterprise_value[1:-1]) * 1000000
        else:
            enterprise_value = 'N/A'

        check_ebitda = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[2]/td/span').text
        if check_ebitda[-1] == 'T':
            ebitda = float(check_ebitda[1:-1]) * 1000000000000
        elif check_ebitda[-1] == 'B':
            ebitda = float(check_ebitda[1:-1]) * 1000000000
        elif check_ebitda[-1] == 'M':
            ebitda = float(check_ebitda[1:-1]) * 1000000
        else:
            ebitda = 'N/A'

        check_income = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[1]/div[2]/table/tbody/tr[3]/td/span').text
        if check_income[-1] == 'T':
            income = float(check_income[1:-1]) * 1000000000000
        elif check_income[-1] == 'B':
            income = float(check_income[1:-1]) * 1000000000
        elif check_income[-1] == 'M':
            income = float(check_income[1:-1]) * 1000000
        else:
            income = 'N/A'

        volume_elements = driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[2]/div[1]/table/tbody/tr[1]/td').text.split(' / ')
        volume_purchased = volume_elements[0]
        volume_outstanding = volume_elements[1]

        relative_volume = float(driver.find_element_by_xpath('/html/body/main/section/div[4]/div[1]/div[2]/div[2]/div[1]/table/tbody/tr[2]/td/span').text[:-2])

        stock_object = {
            'company_name': company_name,
            'stock_ticker': each_stock.get('stock_ticker'),
            'exchange': each_stock.get('exchange'),
            'current_price': current_price,
            'percentage': percentage,
            'price_increase': price_increase,
            'amount_change': amount_change,
            'market_cap': market_cap,
            'enterprise_value': enterprise_value,
            'ebitda': ebitda,
            'income': income,
            'volume_purchased': volume_purchased,
            'volume_outstanding': volume_outstanding,
            'relative_volume': relative_volume,
            'date': date.today()
        }
        db.current_data.insert(stock_object)
        retrieve_stock = db.current_data.find_one({'stock_ticker': each_stock.get('stock_ticker')})
        pp.pprint(retrieve_stock)

# Run the functions
log_in(email, password)
time.sleep(1)
get_data(stock_list)