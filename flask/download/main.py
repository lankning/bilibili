#!/usr/bin/env python
# coding: utf-8

# # 可视化的链接文件下载
# - 默认下载路径：./static/download
# - 链接格式要求：以xxx.文件名结尾，结尾没有/

# In[1]:


from flask import Flask, request, render_template, flash
import requests
from urllib.request import unquote
import threading
import sqlite3 # 导入sqlit3库
import time


# In[2]:


def getrecords():
    data_base=sqlite3.connect('database')
    cursor=data_base.cursor()
    cursor.execute('create table if not exists records(filename text,time text)')
    data_base.commit()
    cursor.execute('select * from records')
    results=cursor.fetchall()
    records=[]
    for r in results:
        records.append({"filename": list(r)[0], "time": list(r)[1]})
    return records


# In[3]:


def split(text):# text最后不可以加‘/’，要以str输入
    text = str(text)
    stext = text.split("/",-1)
    # print(stext)
    filename=stext[-1]
    filename=unquote(filename, encoding='utf-8')#转码
    return filename


# In[4]:


def download(path,url):
    try:
        print('正在下载...%s'%split(url))
        r = requests.get(url,stream=True) 
        content_size = int(r.headers['content-length'])
        print('总大小%.2fMb'%(content_size/1024/1024))
        with open("%s/%s"%(path,split(url)), "wb") as f:
            n=0
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    loaded = n*1024*1024/content_size
                    f.write(chunk)
                    print('已下载%.2f%%...%s'%(loaded*100,split(url)))
                    n=n+1
        print('下载成功...%s'%split(url))
        data_base=sqlite3.connect('database')
        cursor=data_base.cursor()
        cursor.execute('create table if not exists records(filename text,time text)')
        data_base.commit()
        cursor.execute('insert into records (filename,time) VALUES (\"%s\",\"%s\")'%(split(url),time.ctime()))
        data_base.commit()
        print('数据库提交成功...%s'%split(url))
        return 1
    except:
        print('下载失败！')
        return 0


# In[5]:


app = Flask(__name__)


# In[6]:


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        records=getrecords()
        return render_template('index.html',records=records)
    else:#post方法
        url = request.form.get('url')
        url = str(url)
        path='./static/download'
        threading.Thread(target=download,args=(path,url)).start()#并行下载进程
        return render_template('downloading.html')


# In[7]:


if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True,port=5000)

