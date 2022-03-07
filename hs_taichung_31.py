# encoding: UTF-8
import uuid
import MySQLdb
import re
import os
# import ftplib
import requests
import base64

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep
from bs4 import BeautifulSoup

# def capture_ba(myid, myaddr):
def capture_ba(db, myid, caseNo, myaddr):
    # options = Options()
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(executable_path='C:\py\webdriver\chromedriver.exe')
    # driver = webdriver.Chrome(chrome_options=options, executable_path='C:\py\webdriver\chromedriver.exe')

    myUrl = 'http://mcgbm.taichung.gov.tw/geoViewer/geoViewAction.do?infopage=1&pas=I80' ;
    driver.get(myUrl)

    #選擇縣市區域
    s1 = Select(driver.find_element_by_id('ZON'))
    pattern = re.compile(myaddr[0]) 
    
    for option in s1.options: 
        value = option.get_attribute('text') 
        # if pattern.search(value): 
        if pattern.match(value): 
            print value
            option.click()
            break
    del s1
    
    #選擇段小段
    sleep(2)
    s1 = Select(driver.find_element_by_id('SECTNO'))
    pattern = re.compile(myaddr[2]) 
    for option in s1.options: 
        value = option.get_attribute('text') 
        # if pattern.search(value): 
        if pattern.match(value): 
            print value
            option.click()
            break
    
    #輸入地號
    driver.find_element_by_id('lno1').send_keys(myaddr[4])
    driver.find_element_by_id('lno2').send_keys(myaddr[5])

    #送出執行
    driver.find_element_by_xpath('/html/body/div[2]/div/form/table/tbody/tr[5]/td/input[3]').click()

    #切換到下一視窗
    handles = driver.window_handles
    driver.switch_to_window(handles[-1])

    #檢查有無資訊
    html = driver.page_source
    # print html
    
    no_result = u'查無此地段地號'
    if html.find(no_result) != -1:
        print u'查無此地段地號'
        # os._exit(0)
        
        db1 = MySQLdb.connect("61.56.209.149","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
 
        sql = 'UPDATE `case_map` SET `cPath` = "N" WHERE `id` = "' + str(myid) + '";'
        # print sql
        # os._exit(0)
        
        conn1 = db1.cursor()
        conn1.execute(sql)
        db1.commit()
        db1.close()
        
        driver.close()
        driver.quit()
        
        return 'N'
    else:
        
        #縮小比例尺
        sleep(2)
        driver.find_element_by_xpath('//*[@id="mapCanvas_zoom_slider"]/div[2]/span').click()
        sleep(2)
        driver.find_element_by_xpath('//*[@id="mapCanvas_zoom_slider"]/div[2]/span').click()
        sleep(2)
        driver.find_element_by_xpath('//*[@id="mapCanvas_zoom_slider"]/div[2]/span').click()

        #擷取圖面
        sleep(5)
        
        myuid = str(uuid.uuid4())
        filename = 'taichung_' + str(myid) + '_' + myuid + '.png'
        # print(filename)
        tf = driver.get_screenshot_as_file(r'.\ba_capture\\'+filename)
        
        # driver.get('https://www.accuhit.net') ;
        # driver.save_screenshot('aaa.png')
        #如果需要執行完自動關閉，就要加上下面這一行
        driver.close()
        driver.quit()
        
        del driver
        del myUrl
        del s1
        del handles
        del myuid
        
        if tf:
            f = open('.\\ba_capture\\'+filename, 'rb')
            # fdata = base64.b64encode(f.read())
            fdata = base64.encodestring(f.read())
            # print(fdata)
            
            payload = {'id':str(myid),'cCaseNo':caseNo,'authorization':'pnxYQjT+6bxrpUC/9q0ef9AtKAbuuSh4tFi3hTSaO+U=','image':fdata}
            response = requests.post('http://hs-cms.accunix.net/api/cms/caseMapCadastral.php', payload)
            response_dic = response.json()
            # print(response_dic)
            
            if response_dic['status'] == 200:
                return filename
            else:
                return 'NG'
        else:
            return 'NG'

def seperate_addr(addr):
    myCity = u'臺中市'
    
    #濾除段小段
    addr = addr.replace(u'段小段', u'段')
    
    #distinct
    regex2 = re.compile(u'市(\D{1,3}區)')
    match = regex2.findall(addr)

    myArea = "".join(list(set(match)))
    del match
    
    #session
    regex2 = re.compile(u'區(\D+段)')
    match = regex2.findall(addr)
    
    mySec = "".join(list(set(match)))
    del match
    print mySec
    #no
    regex2 = re.compile(u'段(.*)地號$')
    match = regex2.findall(addr)

    myNo = "".join(list(set(match)))
    del match
    
    regex2 = re.compile(u'段(.*)$')
    match = regex2.findall(myNo)
    
    if match:
        myNo = "".join(list(set(match)))
        
    del match
    
    no1 = myNo
    no2 = ''
    regex2 = re.compile(u'-')
    match = regex2.findall(myNo)
    if match:
        _arr = myNo.split(u'-')
        no1 = _arr[0]
        no2 = _arr[1]
        del _arr
    
    myAddr = addr.replace(myCity, '')
    myAddr = myAddr.replace(myArea, '')
    
    return [myCity+myArea, myAddr, mySec, myNo, no1, no2]

# def sendFtp(fh):
    # path = 'C:/py/ba_capture/' + fh
    
    # ftp = ftplib.FTP('waws-prod-hk1-025.ftp.azurewebsites.windows.net', "hshouse\irs2018", "AccuHit5008!!")
    # ftp.cwd('./site/wwwroot/ba')
    
    # ftp.storbinary('STOR ' + fh, open(path, 'rb'))
    # ftp.quit

# def updateDB(myid, fh, case_id):
    # db1 = MySQLdb.connect("61.56.209.149","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
    
    # fh = '/ba/' + fh
    # sql = 'UPDATE `case` SET cCaseBuildingApply = "' + fh + '" WHERE cCaseBuildingApply IS NULL AND id = "' + str(myid) + '";'
    # print(sql)
    # conn1 = db1.cursor()
    # conn1.execute(sql)
    # db1.commit()
    
    
    # sql = 'UPDATE `case_map` SET cPath = "' + fh + '" WHERE cMapLabel = "4" AND cCaseNo = "' + case_id + '";'
    # print(sql)
    # conn1 = db1.cursor()
    # conn1.execute(sql)
    # db1.commit()
    
    # db1.close()



# start
if __name__ == '__main__':
    db = MySQLdb.connect("61.56.209.149","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
 
    # sql = 'SELECT id, cCaseNo, cAddress FROM `case_map` WHERE cAddress LIKE "台中市%" AND cMapLabel = 4 AND cPath = "" ORDER BY id DESC LIMIT 1000;'
    sql = 'SELECT id, cCaseNo, cAddress FROM `case_map` WHERE cAddress LIKE "台中市%" AND cAddress LIKE "%地號%" AND cMapLabel = 4 AND cPath = "" ORDER BY id DESC LIMIT 1000;'
    # sql = 'SELECT id, cCaseNo, cAddress FROM `case_map` WHERE id = 192042;'
    conn = db.cursor()
    conn.execute(sql)
    db.close()
    
    for row in conn.fetchall():
        arr = row[2].split(',')
        
        myArr = seperate_addr(arr[0])
        
        print(row[0]),
        print(' '),
        print(row[1]),
        print(' '),
        print(row[2]),
        print(' '),
        # os._exit(0)
        
        result = capture_ba(db, row[0], row[1], myArr)
        if result == 'NG':
            print('====== NG ======')
        else:
            print('====== OK ======')
            print(' ')
        
        del arr
        del myArr
        del row
    # db.close()
