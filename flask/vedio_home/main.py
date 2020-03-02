#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, request, render_template, redirect,url_for,flash
import time
import os
import sqlite3 # 导入sqlit3库


# In[2]:


# 文件上传的地址
UPLOAD_FOLDER = 'static/vedios'

app = Flask(__name__)
app.secret_key = '123456'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#限制最大上传文件为1Gb
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024


# In[3]:


#  连接到一个数据库名为 records 的数据库,如果存在则直接连接,如果不存在则创建
data_base=sqlite3.connect('reocords', check_same_thread=False)
# 设置数据库光标,你之后所有对数据库进行的操作都是通过光标来执行的
cursor=data_base.cursor()
# 创建一个表名为 uploads 的数据库表,如果这个表不存在的话
# 后面括号里面的内容为这个表的属性,属性与属性之间用  ,  隔开,属性名与属性类型之间用 空格  隔开,如果不写类型的话,默认       为text类型
cursor.execute('create table if not exists uploads(info text)')
# 数据库的提交,对数据进行增删改后都需要进行数据库的提交
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
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            record = {"filename": filename, "date": date}
            # print(record)
            # 更新本地记录
            cursor.execute('insert into uploads (info) VALUES (\"%s\")'%(record))
            data_base.commit()
            return redirect(url_for('index'))
    return render_template('upload.html')


# In[7]:


@app.route("/player/<filename>", methods=['GET'])
def player(filename):
    path = "../"+app.config['UPLOAD_FOLDER']+"/"+filename
    return render_template('player.html',path=path)


# In[8]:


if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True,port=5000)

