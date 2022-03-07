cd D:\project\py
REM call activate dev
chcp 65001
set PYTHONIOENCODING=UTF-8

call c:\xampp\php\php.exe D:\project\py\addr2latlng.php
call C:\Python27\python.exe D:\project\py\hs_new_taipei_4.py
call C:\Python27\python.exe D:\project\py\hs_new_taipei_31.py
call C:\Python27\python.exe D:\project\py\hs_taichung_3.py
call C:\Python27\python.exe D:\project\py\hs_taichung_31.py
REM pause
timeout /t 5