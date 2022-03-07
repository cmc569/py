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
from selenium.common.exceptions import NoSuchElementException 

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def get_web_data(url):
    driver = webdriver.Chrome(executable_path='C:\py\webdriver\chromedriver.exe')
    driver.get(url)
    # sn = driver.find_element_by_xpath('//*[@id="page"]/section/div[1]/div[1]/div/div[1]/div[1]/div[1]/app-product-summary-name/h1/span[2]').text
    el = driver.find_elements_by_class_name('product-summary-name--Original')
    
    # html = driver.page_source
    print(el)
    
    sleep(3)
    
    
# start
if __name__ == '__main__':
    url = 'https://www.arrow.com/en/products/2229293-1/te-connectivity?q=2229293-1'
    result = get_web_data(url)
    print(result)