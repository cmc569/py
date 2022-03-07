# encoding: UTF-8
import uuid
import MySQLdb
import re
import os
# import ftplib
import requests
import base64
import urllib

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from time import sleep

# def capture_ba(myid, myaddr):
def capture_ba(myid, caseNo, myaddr, lat, lng):

    driver = webdriver.Chrome(executable_path='C:\py\webdriver\chromedriver.exe')
    # driver = webdriver.Chrome(chrome_options=options, executable_path='C:\py\webdriver\chromedriver.exe')

    myUrl = 'http://building-apply.publicwork.ntpc.gov.tw/geoViewer/geoViewAction.do?infopage=1&pas=I30' ;
    driver.get(myUrl)
    
    #輸入lat, lng
    driver.find_element_by_id('TWDO').send_keys(lat)
    driver.find_element_by_id('TWDN').send_keys(lng)
    
    #送出執行
    driver.find_element_by_xpath('/html/body/div[2]/div/form/table/tbody/tr[5]/td/input[3]').click()
    
    #切換到下一視窗
    handles = driver.window_handles
    driver.switch_to_window(handles[-1])

    #檢查有無資訊
    html = driver.page_source
    # print html
    # os._exit(0)
    
    no_result = u'查無此地段地號'
    if html.find(no_result) != -1:
        print(u'查無此地段地號')
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
        for i in range(0, 3):
            sleep(2)
            try:
                driver.find_element_by_xpath('//*[@id="mapCanvas_zoom_slider"]/div[2]').click()
            except:
                driver.find_element_by_xpath('//*[@id="mapCanvas_zoom_slider"]/div[2]').click()
        # os._exit(0)

        #擷取圖面
        sleep(5)
        
        myuid = str(uuid.uuid4())
        filename = 'new-taipei_' + str(myid) + '_' + myuid + '.png'
        tf = driver.get_screenshot_as_file(r'.\ba_capture\\'+filename)
        
        #如果需要執行完自動關閉，就要加上下面這一行
        driver.close()
        driver.quit()
        
        del driver
        del myUrl
        del handles
        del myuid
        
        if tf:
            f = open('.\\ba_capture\\'+filename, 'rb')
            fdata = base64.encodestring(f.read())
            
            payload = {'id':str(myid),'cCaseNo':caseNo,'authorization':'pnxYQjT+6bxrpUC/9q0ef9AtKAbuuSh4tFi3hTSaO+U=','image':fdata}
            response = requests.post('http://hs-cms.accunix.net/api/cms/caseMapCadastral.php', payload)
            response_dic = response.json()
            
            if response_dic['status'] == 200:
                return filename
            else:
                return 'NG'
        else:
            return 'NG'

def seperate_addr(addr):
    # regex1 = re.compile(u'^(.*市)')
    # match = regex1.search(addr)
    # myCity = match.group(0)
    myCity = u'新北市'
    # del match
    
    regex2 = re.compile(u'市(\D{1,3}區)')
    match = regex2.findall(addr)
    # match = re.findall(ru'市(\D+區)',addr)
    # myArea = "".join(match)
    # myArea = list(set(match))
    myArea = "".join(list(set(match)))
    # print("".join(myArea))
    del match
    
    myAddr = addr.replace(myCity, '')
    myAddr = myAddr.replace(myArea, '')
    
    return [myCity+myArea, myAddr]

def sendFtp(fh):
    path = 'C:/py/ba_capture/' + fh
    
    ftp = ftplib.FTP('waws-prod-hk1-025.ftp.azurewebsites.windows.net', "hshouse\irs2018", "AccuHit5008!!")
    ftp.cwd('./site/wwwroot/ba')
    
    ftp.storbinary('STOR ' + fh, open(path, 'rb'))
    ftp.quit

def updateDB(myid, fh, case_id):
    db1 = MySQLdb.connect("61.56.209.149","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
    
    fh = '/ba/' + fh
    sql = 'UPDATE `case` SET cCaseBuildingApply = "' + fh + '" WHERE cCaseBuildingApply IS NULL AND id = "' + str(myid) + '";'
    print(sql)
    conn1 = db1.cursor()
    conn1.execute(sql)
    db1.commit()    
    
    sql = 'UPDATE `case_map` SET cPath = "' + fh + '" WHERE cMapLabel = "4" AND cCaseNo = "' + case_id + '";'
    print(sql)
    conn1 = db1.cursor()
    conn1.execute(sql)
    db1.commit()
    
    db1.close()


# start
if __name__ == '__main__':
    db = MySQLdb.connect("61.56.209.149","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')

    sql = 'SELECT id, cCaseNo, cAddress, cLat, cLng FROM `case_map` WHERE cAddress LIKE "新北市%" AND cAddress NOT LIKE "%地號%" AND cMapLabel = 4 AND cPath = "" ORDER BY id DESC LIMIT 1000;'
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
        print(row[3] + ', ' +row[4]),
        print(' '+"\n"),

        result = capture_ba(row[0], row[1], myArr, row[3], row[4])
        # if result == 'NG':
            # print('====== NG ======')
        # else:
            # print('====== OK ======')
            # print(' ')
        
        del arr
        del myArr
        del row
        
    # db.close()
