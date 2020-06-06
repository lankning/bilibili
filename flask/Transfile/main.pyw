#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, request, render_template, redirect,url_for
import os
from gevent import pywsgi
from genqr import gen

#import win32api, win32gui

#ct = win32api.GetConsoleTitle()
#hd = win32gui.FindWindow(0,ct)
#win32gui.ShowWindow(hd,0)
# In[2]:


# 文件上传的地址
UPLOAD_FOLDER = './uploads'
app = Flask(__name__)


# In[3]:


# 安全问题
# 除了常规的CSRF防范，我们还需要重点关注这几个问题：验证文件类型、验证文件大小、过滤文件名

black_list=['exe','sh','com','pif','bat','scr','sys','dll'] # 黑名单，不允许上传这些类型的文件
def passport(filetype):
    if filetype in black_list:
        return 0 # 文件类型可疑
    else:
        return 1 # 文件类型安全

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024 # 限制最大上传文件为100Mb

def filter(file): # 过滤文件名
    filename = file.filename.rsplit('.', 1)[0]
    filetype = file.filename.rsplit('.', 1)[1]
    if passport(filetype):
        filename = filename.replace(' ','') # 将文件名中的空格去除
        filename = filename.replace('.','-') # 去除文件中的.
        filename = filename+'.'+filetype
        return filename
    else:
        return 0 # 文件不安全


# # index
# - get, index.html
# - post
#   - 多文件循环：
#     - 文件安全:save后返回index
#     - 文件不安全:error.html

# In[4]:


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':#post方法
        for file in request.files.getlist('file'):
            if file:
                filename = filter(file)
                if filename:#文件安全
                    file.save(os.path.join(UPLOAD_FOLDER, filename))
                    print('%s存储成功！'%filename)
                else:#文件不安全
                    return render_template('error.html')
            else:
                print('%s存储失败！'%filename)
        return render_template('success.html')


# In[5]:


@app.route('/statement', methods=['GET'])
def statement():
    return render_template('statement.html')


# In[6]:


@app.route('/', methods=['GET'])
def home():
    return redirect(url_for('index'))


# In[7]:


if __name__ == '__main__':
    port=5000
    gen(UPLOAD_FOLDER,port)
    server = pywsgi.WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()


# In[ ]:




