1、C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
[Administrator改为用户名]

2、autorun.bat里面的路径要改为程序文件路径，不要有中文

3、main.py里面的路径UPLOAD_FOLDER也要改

4、python头部加入：[已加入，需要解除注释]
import win32api, win32gui

ct = win32api.GetConsoleTitle()
hd = win32gui.FindWindow(0,ct)
win32gui.ShowWindow(hd,0)