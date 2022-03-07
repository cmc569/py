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

def get_broker_data(url):
    driver = webdriver.Chrome(executable_path='C:\py\webdriver\chromedriver.exe')
    driver.get(url)
    
    #最大頁數
    max_page = int(driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[4]/div/a[4]').text)
    print 'max page = ' + str(max_page)
    #
    el = driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[3]/ul')
    options = el.find_elements_by_tag_name("li")
    
    for i in range(max_page):
        # i = 1579
        #下一頁
        print 'page = ' + str(i+1)
        driver.find_element_by_id('gotoPage').clear()
        driver.find_element_by_id('gotoPage').send_keys(i+1)
        driver.find_element_by_xpath('/html/body/div[5]/div[2]/div[4]/div/input').click()
        time.sleep(1)
        
        for idx in range(15):
            tag = '/html/body/div[5]/div[2]/div[3]/ul/li['+ str(idx + 1)+']/div[2]/div[1]/h2/a'
            # print tag
            driver.find_element_by_xpath(tag).click()
        
            #切換到下一視窗
            window_1 = driver.current_window_handle
            handles = driver.window_handles
            driver.switch_to_window(handles[1])

            detail = get_broker_detail(driver)
                    
            #切換回上一視窗並關閉下一視窗
            # print(driver.title)
            driver.close()
            driver.switch_to_window(window_1)
            time.sleep(3)


    
def get_broker_detail(driver):
    if check_exists_by_xpath(driver, '/html/body/div[4]/div[4]/div[1]/span[2]/span[1]/h3'):
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
        
        #目前網址
        current_url = driver.current_url
        print current_url
        
        #取得sales id
        parsed_url = urlparse.urlparse(current_url)
        sales_id = parsed_url.path.replace('/', '')
        print sales_id
        
        save_data(sales, year_limit, company, branch, mobile, service_area, current_url, sales_id)
        
        print ""
    
    
def save_data(sales, year_limit, company, branch, mobile, service_area, current_url, sales_id):
    # db = MySQLdb.connect("accu-qa.mysql.database.azure.com","coder", "AccuHit5008!!", "wending", port=3306, charset='utf8')
    db = MySQLdb.connect("61.56.209.149","coder", "AccuHit5008!!", "spider", port=3308, charset='utf8')
    # db = mysql.connector.connect(host="61.56.209.149",user="coder", passwd="AccuHit5008!!", database="spider", port=3308, charset='utf8')

    sql = 'SELECT * FROM 591_broker WHERE broker_id = "' + sales_id + '" AND broker_status = "Y";'
    # print sql
    
    conn = db.cursor()
    conn.execute(sql)
    
    row = conn.fetchall()
    if (row):
        sql = 'UPDATE 591_broker SET broker_name = "' + sales + '", broker_store = "' + company + '", broker_branch = "' + branch + '", broker_mobile = "' + mobile + '", broker_area = "' + service_area + '", broker_service_year = "' + service_area + '", broker_url = "' + current_url + '" WHERE broker_id = "' + sales_id + '";'
        print 'UPDATE DB Row: ' + sales_id
    else:
        sql = 'INSERT INTO 591_broker SET broker_id = "' + sales_id + '", broker_name = "' + sales + '", broker_store = "' + company + '", broker_branch = "' + branch + '", broker_mobile = "' + mobile + '", broker_area = "' + service_area + '", broker_service_year = "' + service_area + '", broker_url = "' + current_url + '";'
        print 'INSERT DB Row: ' + sales_id
        
    if (conn.execute(sql)):
        db.commit()
    
    db.close()
    
        
def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

# start
if __name__ == '__main__':
    url = 'https://www.591.com.tw/broker-list.html'
    # url = 'https://www.591.com.tw/index.php?firstRow=3645&totalRows=23692&?&m=0&o=12&module=shop&action=list'   #page 244
    result = get_broker_data(url)