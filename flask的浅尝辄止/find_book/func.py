#定义所有的函数
from bs4 import BeautifulSoup as bs
import requests
import time
from retrying import retry
import os

base_path='./books/'

def search(bn,wn):
    #https://www.biquge5200.cc/modules/article/search.php?searchkey=bn
    url = 'https://www.biquge5200.cc/modules/article/search.php?searchkey='+bn
    html = requests.get(url)
    soup = bs(html.text,"html.parser")
    #menu = soup.find_all('a')
    text = soup.find_all("td", { "class" : "odd" })
    
    #通过书名查找符合条件的urls和作者
    urls = []
    writor = []
    bookname=[]
    for i,con in enumerate(text):
        if i%3==0:#得到链接
            tag_a = con.find('a')
            urls.append(tag_a.get('href'))
            bookname.append(tag_a.get_text())
            #print(tag_a.get('href'))
        if i%3==1:#得到作者
            writor.append(con.get_text())
            #print(con.get_text())
    #如果没有这本书：返回None;有这本书，正常返回url和wn
    if urls==[]:
        return url,None,wn
    else:
        #判断作者是否一致,作者为None的情况:取第一种
        if wn=='':#没有写作者
            url = urls[0]
            print('没有输入作者,自动选择最佳匹配的.')
            wn = writor[0]
            bn = bookname[0]
        else:#寻找匹配的作者,如果用户输入错误,就么有了?
            try:#有这个作者
                where = writor.index(wn)
                url = urls[where]
                wn = writor[where]
                bn = bookname[where]
            except:#没有这个作者
                bn = ''
                wn = None
    return url,bn,wn

@retry(stop_max_attempt_number=100) #最大重试100次，100次全部报错，才会报错
def _open_url(url):
    response = requests.get(url, headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'
    }, timeout=10) #超时的时候回报错并重试
    assert response.status_code == 200 #状态码不是200，也会报错并充实
    return response

def load_on_cloud(url,wn):
    html = requests.get(url)
    soup = bs(html.text,"html.parser")
    menu = soup.find_all('a')
    bookname=soup.find('h1').get_text()
    filename=bookname+'_'+wn
    href_list = []
    count = 0
    print('%s-开始存储...'%bookname)
    for r in menu:
        h = r.get('href')
        if h != None:
            if url in h:
                count = count+1
                if count>=10:#去除前面的杂章
                    href_list.append(h)
    print("%s-章节url读取完毕！"%bookname)
    
    content = []
    for c,chap in enumerate(href_list):#章节内容加入txt
        try:
            html = _open_url(chap)
        except Exception as e:
            print(e)
        soup = bs(html.text,"html.parser")#bs煮过
        title = soup.find('h1').get_text()
        #txt更新部分
        with open(base_path+'./%s.txt' % filename,'a') as f:
            f.write(title+'\n')
        text = soup.find_all('p')
        with open(base_path+'./%s.txt' % filename,'a') as f:
            for i in range(len(text)):
                f.write(text[i].get_text()+'\n')
        time.sleep(2)#防止网站访问过热
        if c%50==0:
            print("%s-已储存%.1f%%" % (bookname,100*c/len(href_list)))
    print("%s-储存完成！" % bookname)
    return None

def check_on_cloud(bn,wn):
    if wn=='' and bn=='':
        return 1
    elif wn=='':
        book_storaged = os.listdir(base_path)
        for book in book_storaged:
            if bn in book:
                return book
        return 0
    elif bn=='':
        book_storaged = os.listdir(base_path)
        for book in book_storaged:
            if wn in book:
                return book
        return 0
    else:
        filename=bn+'_'+wn+'.txt'
        book_storaged = os.listdir(base_path)
        if filename in book_storaged:
            print('此书已经储存.')
            return filename
        else:
            print('仓库没有此书.')
            return 0