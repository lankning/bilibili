from bs4 import BeautifulSoup
import requests
from retrying import retry
import sqlite3 # 导入sqlit3库
import time

def database_init(table_name='menu'):
    #  连接到一个数据库名为 records 的数据库,如果存在则直接连接,如果不存在则创建
    data_base=sqlite3.connect('reocords', check_same_thread=False)
    # 设置数据库光标,你之后所有对数据库进行的操作都是通过光标来执行的
    cursor=data_base.cursor()
    # 创建一个表名为 menu 的数据库表,如果这个表不存在的话
    # 后面括号里面的内容为这个表的属性,属性与属性之间用  ,  隔开,属性名与属性类型之间用 空格  隔开,如果不写类型的话,默认       为text类型
    cursor.execute('create table if not exists %s(info text)'%(table_name))
    # 数据库的提交,对数据进行增删改后都需要进行数据库的提交
    data_base.commit()
    return None

def get_records():
    data_base=sqlite3.connect('reocords', check_same_thread=False)
    cursor=data_base.cursor()
    cursor.execute('select * from menu')
    results=cursor.fetchall()
    records=[]
    for r in results:
        records.append(str(r[0]))
    return records

@retry(stop_max_attempt_number=100) #最大重试100次，100次全部报错，才会报错
def _open_url(url):
    response = requests.get(url, headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }, timeout=10) #超时的时候回报错并重试
    assert response.status_code == 200 #状态码不是200，也会报错并充实
    return response

def get_menu(url):#得到页面上的超链接目录
    response = _open_url(url)
    response.encoding = 'utf-8'
    data = response.text
    soup = BeautifulSoup(data,features="lxml")
    urls=[]
    for item in soup.find_all("a"):
        if item.string == None:
            continue
        else:
            urls.append('https://www.xxxx.net'+item.get("href"))
    
    urls_real=[]
    for line in urls:
        if url in line:
            urls_real.append(line)
        
#     for i in range(len(urls_real)):
#         print(str(urls_real[i]))
    return urls_real

def textfilter(text,title):# 注意顺序
    text = text.replace("天才一秒记住本站地址：[笔趣阁]","")
    text = text.replace("https://www.xxx.net/最快更新！无广告！","")
    text = text.replace("http://www.xxx.net/最快更新！无广告！","")
    text = text.replace("章节错误,点此报送(免注册),","")
    text = text.replace("报送后维护人员会在两分钟内校正章节内容,请耐心等待。","")
    text = text.replace("\xa0\xa0\xa0\xa0","\n")
    text = text.replace("\n\r\n\n\r\n\n\r\n            \n","")
    text = text.replace("\n\r\n                \n\r\n                \n\r\n            \n","")
    text = text.replace("           \r\n            \n\r\n                \r\n            \n","")
    text = text.replace("\xa0"," ")
    text = text.replace(title,"")# 正文里面有标题，让我们很生气地删掉！
    return text

def get_text(url): #得到页面上的目录
    response = _open_url(url)
    response.encoding = 'utf-8'
    data = response.text
    soup = BeautifulSoup(data,features="html.parser")
    title = soup.find('h1').get_text()
    text = soup.find(id='content').get_text()
    text = textfilter(text,title)# 过滤无关文字
    return [title,text]

def check_update(url):
    new_menu = get_menu(url)
    old_menu = get_records()
    # print(len(new_menu))
    # print(len(old_menu))
    update = new_menu[len(old_menu)-len(new_menu):]
    if update==[]:
        t='no update'# do nothing
    else:
        data_base=sqlite3.connect('reocords', check_same_thread=False)
        cursor=data_base.cursor()
        for url in new_menu:
            cursor.execute('insert into menu (info) VALUES (\"%s\")'%(url))
        data_base.commit()
    return update # list的差集，set()去重

def update(url):
    # 更新的章节目录
    update_menu = check_update(url)
    # 发邮件
    for url in update_menu:
        title,mess = get_text(url)
        send_email(title,mess)
        time.sleep(2)
    return None