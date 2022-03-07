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
    driver = webdriver.Chrome(executable_path='.\webdriver\chromedriver.exe')

    myUrl = 'http://building-apply.publicwork.ntpc.gov.tw/geoViewer/geoViewAction.do?infopage=1&pas=I30' ;
    driver.get(myUrl)

    #選擇縣市區域
    s1 = Select(driver.find_element_by_id('ZON2'))  # 实例化Select
    s1.select_by_value(myaddr[0])

    #輸入地址
    driver.find_element_by_id('addr').send_keys(myaddr[1])

    #送出執行
    driver.find_element_by_xpath('/html/body/div[2]/div/form/table/tbody/tr[6]/td/input[3]').click()

    #切換到下一視窗
    handles = driver.window_handles
    driver.switch_to_window(handles[-1])

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
    myCity = u'新北市'
    # del match
    
    regex2 = re.compile(u'市(\D{1,3}區)')
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
    files = ftp.dir()
    
    ftp.storbinary('STOR ' + fh, open(path, 'rb'))
    ftp.quit

def updateDB(myid, fh):
    db1 = MySQLdb.connect("218.32.3.105","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')
    
    fh = '/ba/' + fh
    sql = 'UPDATE `case` SET cCaseBuildingApply = "' + fh + '" WHERE cCaseBuildingApply IS NULL AND id = "' + str(myid) + '";'
    print(sql)
    conn1 = db1.cursor()
    conn1.execute(sql)
    db1.commit()
    db1.close()



# start
if __name__ == '__main__':
    db = MySQLdb.connect("218.32.3.105","coder", "AccuHit5008!!", "foreclosure", port=3308, charset='utf8')

    sql = 'SELECT id, cCaseAddr FROM `case` WHERE cCaseAddr LIKE "新北市%" AND cCaseBuildingApply IS NULL ORDER BY id DESC LIMIT 1000;'
    conn = db.cursor()
    conn.execute(sql)

    for row in conn.fetchall():
        arr = row[1].split(',')
        myArr = seperate_addr(arr[0])
        
        print(row[0]),
        print(' '),
        print(",".join(myArr))
        
        result = capture_ba(row[0], myArr)
        if result == 'NG':
            print('====== NG ======')
        else:
            # sendFtp('new-taipei_4b463705-0ba6-4b18-80ca-32ff4fa878b2.png')
            sendFtp(result)
            updateDB(row[0], result)
            print('====== OK ======')
            print(' ')
        
        del arr
        del myArr
        del row
        
    db.close()
