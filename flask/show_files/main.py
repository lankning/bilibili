#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, request, render_template, redirect,url_for,flash
import time
import os
import sqlite3 # 导入sqlit3库


# In[2]:


# 文件上传的地址
saved_path = 'static/files'
app = Flask(__name__)


# In[3]:


data_base=sqlite3.connect('reocords', check_same_thread=False)
cursor=data_base.cursor()
cursor.execute('create table if not exists uploads(info text)')
data_base.commit()


# In[4]:


def getrecords():
    cursor.execute('select * from uploads')
    results=cursor.fetchall()
    records=[]
    for r in results:
        records.append(eval(r[0]))
    return records


# In[5]:


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        records=getrecords()
        # print(records)
        return render_template('index.html',records=records[::-1])

    else:#post方法
        scon = request.form.get('scon')
        target = []
        # 搜索云端是否有该文件，罗列所有相关的
        records=getrecords()
        for record in records:
            # print(record['filename'])
            if scon in record['filename']:
                target.append(record)
        if target==[]:#没有找到相关文件
            flash('没有找到相关文件！')
            return render_template('index.html',records=records[::-1])
        else:
            return render_template('index.html',records=target[::-1])


# In[6]:


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = file.filename.rsplit('.', 1)[0]
            filetype = file.filename.rsplit('.', 1)[1]
            filename = filename.replace(' ','') # 将文件名中的空格去除
            filename = filename.replace('.','-') # 去除文件中的.
            filename = filename+'.'+filetype
            # 解决命名冲突的问题
            records=getrecords()
            for record in records:
                if filename==record['filename']:
                    flash('该文件已经存在！')
                    return render_template('upload.html')
            # ----------
            file.save(os.path.join(saved_path, filename))
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            record = {"filename": filename, "date": date}
            # print(record)
            # 更新本地记录
            cursor.execute('insert into uploads (info) VALUES (\"%s\")'%(record))
            data_base.commit()
            return redirect(url_for('index'))
    return render_template('upload.html')


# In[7]:


@app.route("/<filename>", methods=['GET'])
def classify(filename):
    path = "../"+saved_path+"/"+filename
    filetype=filename.split(".",-1)[-1]
    if filetype == 'pdf':
        return render_template('pdf.html',path=path)
    elif filetype in {'png','jpg','jpeg','tiff'}:
        return render_template('img.html',path=path)
    elif filetype == 'mp4':
        return render_template('vedio.html',path=path)
    elif filetype == {'mp3','m4a'}:
        return render_template('audio.html',path=path)
    else:
        return render_template('player.html',path=path)


# In[8]:


if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True,port=5000)


# In[ ]:




