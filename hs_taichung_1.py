# encoding: UTF-8
import uuid
import MySQLdb
import re
import os
import ftplib

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from time import sleep


def capture_ba(myid, myaddr):
    # driver = webdriver.Chrome(executable_path='.\webdriver\chromedriver.exe')
    driver = webdriver.Chrome(executable_path='C:\py\webdriver\chromedriver.exe')
    
    myUrl = 'http://mcgbm.taichung.gov.tw/geoViewer/geoViewAction.do?infopage=1&pas=I80' ;
    driver.get(myUrl)

    #選擇縣市區域
    myaddr[0] = myaddr[0].replace(u'台中市', u'臺中市')
    s1 = Select(driver.find_element_by_id('ZON2'))
    s1.select_by_value(myaddr[0])

    #輸入地址
    driver.find_element_by_id('addr').send_keys(myaddr[1])

    #送出執行
    driver.find_element_by_xpath('/html/body/div[2]/div/form/table/tbody/tr[5]/td/input[3]').click()

    #切換到下一視窗
    handles = driver.window_handles
    driver.switch_to_window(handles[-1])

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
        return filename
    else:
        return 'NG'

def seperate_addr(addr):
    # regex1 = re.compile(u'^(.*市)')
    # match = regex1.search(addr)
    # myCity = match.group(0)
    myCity = u'台中市'
    # del match
    
    regex2 = re.compile(u'台中市(\D{1,3}區)')
    match = regex2.findall(addr)
    myArea = "".join(match)
    del match
    
    myAddr = addr.replace(myCity, '')
    myAddr = myAddr.replace(myArea, '')
    
    return [myCity+myArea, myAddr]

def sendFtp(fh):
    path = 'C:/py/ba_capture/' + fh
    
    ftp = ftplib.FTP('waws-prod-hk1-025.ftp.azurewebsites.windows.net', "hshouse\irs2018", "AccuHit5008!!")
    ftp.cwd('./site/wwwroot/ba')
    # files = ftp.dir()
    
    ftp.storbinary('STOR ' + fh, open(path, 'rb'))
    ftp.quit

def updateDB(myid, fh, case_id):
    # db1 = MySQLdb.connect("218.32.3.105","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
    db1 = MySQLdb.connect("61.56.209.149","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
    
    fh = '/ba/' + fh
    # sql = 'UPDATE `case` SET cCaseBuildingApply = %s WHERE cCaseBuildingApply IS NULL AND id = %s;'
    sql = 'UPDATE `case` SET cCaseBuildingApply = "' + fh + '" WHERE cCaseBuildingApply IS NULL AND id = "' + str(myid) + '";'
    print(sql)
    conn1 = db1.cursor()
    conn1.execute(sql)
    db1.commit()
    
    
    sql = 'UPDATE `case_map` SET cPath = "' + fh + '" WHERE cMapLabel = "4" AND cCaseNo = "' + case_id + '";'
    print(sql)
    conn1 = db1.cursor()
    # conn1 = db1.cursor('UPDATE `case` SET cCaseBuildingApply = %s WHERE cCaseBuildingApply IS NULL AND id = %s;', (fh, str(myid))
    # conn1.execute(sql, (fh, myid))
    conn1.execute(sql)
    db1.commit()
    
    db1.close()



# start
if __name__ == '__main__':
    # result = capture_ba('15238', [u'台中市太平區', u'福隆段小段31號'])
    # updateDB('15236', 'new-taipei_15236_f821e869-63a4-4ca2-9cba-81ce582db588.png')
    # db = MySQLdb.connect("218.32.3.105","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
    db = MySQLdb.connect("61.56.209.149","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
 
    sql = 'SELECT id, cCaseNo, cCaseAddr FROM `case` WHERE cCaseAddr LIKE "台中市%" AND cCaseBuildingApply IS NULL ORDER BY id DESC LIMIT 1000;'
    # sql = 'SELECT id, cCaseNo, cCaseAddr FROM `case` WHERE cCaseAddr LIKE "台中市%" AND cCaseBuildingApply IS NULL ORDER BY id DESC LIMIT 1;'
    conn = db.cursor()
    conn.execute(sql)

    for row in conn.fetchall():
        arr = row[2].split(',')
        
        myArr = seperate_addr(arr[0])
        print(row[0]),
        print(' '),
        print(row[1]),
        print(' '),
        print(row[2]),
        print(' '),
        # print(",".join(myArr))
        
        result = capture_ba(row[0], myArr)
        if result == 'NG':
            print('====== NG ======')
        else:
            sendFtp(result)
            updateDB(row[0], result, row[1])
            print('====== OK ======')
            print(' ')
        
        del arr
        del myArr
        del row
        
    db.close()
