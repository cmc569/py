# encoding: UTF-8
import uuid
import MySQLdb
import re
import os
# import ftplib
import requests
import base64
import requests

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from time import sleep

# /html/body/div[5]/div[2]/div[3]/ul/li[1]/div[2]/div[1]/h2/a
# /html/body/div[5]/div[2]/div[3]/ul/li[2]/div[2]/div[1]/h2/a
def get_broker_id(url):
    driver = webdriver.Chrome(executable_path='C:\py\webdriver\chromedriver.exe')
    driver.get(url)
    
    driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[3]/ul/li[1]/div[2]/div[1]/h2/a').click()
    
    #切換到下一視窗
    handles = driver.window_handles
    # handle1 = driver.current_window_handle
    # print(driver.title)
    # driver.switch_to_window(handles[-1])
    driver.switch_to_window(handles[1])

    #仲介姓名
    sales = driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[1]/span[2]/span[1]/h3').text
    print sales

    #從業年限
    year_limit = driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[1]/span[2]/span[2]/ul/li[1]/span').text
    print year_limit

    #就職公司
    company = driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[1]/span[2]/span[2]/ul/li[2]/span[1]').text
    print company
    
    #分公司
    branch = driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[1]/span[2]/span[2]/ul/li[2]/span[2]').text
    print branch

    #行動電話
    mobile = driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[1]/span[2]/span[2]/ul/li[3]/span').text
    print mobile

    #服務區域
    service_area = driver.find_element_by_xpath('/html/body/div[4]/div[4]/div[1]/span[2]/span[2]/ul/li[4]/span').text
    print service_area
        
    #切換回上一視窗並關閉下一視窗
    # driver.close()
    print(driver.title)
    driver.switch_to_window(handles[0])
    # driver.switch_to_window(handle1)
    print(driver.title)
    #
    driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[3]/ul/li[2]/div[2]/div[1]/h2/a').click()

    
# start
if __name__ == '__main__':
    url = 'https://www.591.com.tw/broker-list.html'
    result = get_broker_id(url)