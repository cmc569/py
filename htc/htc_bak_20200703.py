# encoding: UTF-8
import uuid
import MySQLdb
import re
import os
# import ftplib
import requests
import base64
import time
import urlparse
# import mysql.connector
import pandas as pd

from selenium.common.exceptions import NoSuchElementException 

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from bs4 import BeautifulSoup


def get_page_data(url):
    driver = webdriver.Chrome(executable_path='C:\py\webdriver\chromedriver.exe')
    driver.get(url)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_Confirm"]').click()
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnSearch"]').click()
    time.sleep(5)
    
    while True:
        tbs = pd.read_html(driver.page_source, attrs={'class':'resultTable'})
        get_table_data(tbs[0])
        
        driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_pagerDataList1"]/a[13]').click()
        time.sleep(5)
    
    
def get_table_data(tb):
    tb.columns = ['city', 'class', 'code', 'name', 'surgery', 'type', 'reason', 'item_cname', 'item_name', 'item', 'license', 'charge', 'group', 'desc']
    print(tb['code'])
    
def save_table_db(tb):
    try:
        engine = create_engine("mysql+mysqldb://{}:{}@{}/{}?charset=utf8".format('michliu', 'Vd134564', '61.56.209.149:3308', 'spider'))
        con = engine.connect()
    except:
        engine = create_engine("mysql+mysqldb://{}:{}@{}/{}?charset=utf8".format('michliu', 'Vd134564', '61.56.209.149:3308', 'spider'))
        con = engine.connect()
    else:
        tb.to_sql(name='tom_court_closePrice', con=con, if_exists='append', index=False)

# start
if __name__ == '__main__':
    url = 'https://www.nhi.gov.tw/SpecialMaterial/SpecialMaterial.aspx'
    result = get_page_data(url)