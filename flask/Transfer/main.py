#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, request, render_template, redirect,url_for,make_response,send_from_directory,flash
import time,os,re
from aip import AipOcr
import pandas as pd
from pandas import DataFrame


# In[2]:


# 文件上传、下载的地址、文件名
UPLOAD_FOLDER = './uploads'
DOWNLOAD_FOLDER = './results/'
FILENAME = 'result.xlsx'

app = Flask(__name__)


# In[ ]:


def wordreco(path):
    appid='xxxx'
    apikey='xxxx'
    secretkey='xxxx'

    client=AipOcr(appid,apikey,secretkey)
    
    i=open(path,'rb')
    img=i.read()
    message = client.basicGeneral(img);
    word=[]
    
    for i in message.get('words_result'):
        word.append(i.get('words'))
    return word


# In[3]:


# 文字转表格功能
def transfer(path):
    dic = {}
    dic['标题名']=wordreco(path)

    df = pd.DataFrame(dic)
    df.to_excel(os.path.join(DOWNLOAD_FOLDER,FILENAME), index=False)
    return None


# In[4]:


def download(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = DOWNLOAD_FOLDER  # 假设在当前目录
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response


# In[5]:


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    else:#post方法
        if request.method == 'POST':
            file = request.files['file']
        if file:
            filename = file.filename.rsplit('.', 1)[0]
            filetype = file.filename.rsplit('.', 1)[1]
            filename = filename.replace(' ','') # 将文件名中的空格去除
            filename = filename.replace('.','-') # 去除文件中的.
            filename = filename+'.'+filetype
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            transfer(os.path.join(UPLOAD_FOLDER, filename))
            response = download(FILENAME)
            return response
        return redirect(url_for('index'))


# In[ ]:


if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True,port=5000)

