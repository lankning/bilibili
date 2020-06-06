## Statements:



- Attention:

  1、the path in `autorun.bat` should be modified by the current path of program

  2、put `autorun.bat` into `C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`
  [`Administrator` should be modified by your name of computer]

  3、the `UPLOAD_FOLDER` in `main.py` and `main.pyw` can be modified by your Absolute path

- Referrence：

  1、python之qrcode模块生成二维码：https://www.jianshu.com/p/c0073c6aa544

  2、Python 优雅获取本机 IP 方法](https://www.cnblogs.com/xxpythonxx/p/11826491.html)



## 说明：

- 功能

  - 扫码上传文件到主机

  - 开机自启动（后台）

- 注意

  1、`autorun.bat`里面的路径要改成实际程序路径

  2、Windows系统下，把`autorun.bat` 放入目录`C:\Users\Administrator\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`内
  [`Administrator`需要被替换成电脑用户的实际名称]

  3、`main.py` 和`main.pyw` 里面的`UPLOAD_FOLDER`路径可以考虑修改为绝对路径