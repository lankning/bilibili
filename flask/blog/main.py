#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, render_template, redirect,url_for,make_response, send_from_directory, session, Markup
from gevent import pywsgi
import os, time, markdown, sqlite3, math


# In[ ]:


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024 # max_size: 1Gb
app.config['SECRET_KEY'] = os.urandom(24)
app.config['FASSAGE_PATH'] = 'static/passages/'
app.config['UPLOAD'] = 'static/uploads/'
app.config['TEMP'] = 'static/temp/'
app.config['ACCOUNT'] = 'lankning'
app.config['PASSWORD'] = '123456'


# In[ ]:


def secure_filename(filename):
    filename = filename.replace(' ','')
    return filename


# In[ ]:


# 从md文件中读取intro和content信息
def get_content(path):
    with open(path,'r',encoding='utf-8') as f:
        mdcontent = f.read()
    info = mdcontent.split('---')[1].split('\n') # 第一个元素是空的
    info = [i for i in info if(len(str(i))!=0)] # 去除空元素
    for element in info:
        if 'title' in element:
            title = element.split(': ')[1]
        elif 'categories' in element:
            categories = element.split(': ')[1]
        elif 'date' in element:
            date = element.split(': ')[1]
            date = date.replace(' ','~')
        elif 'thumbnail' in element:
            thumbnail = element.split(': ')[1]
    
    text = ''
    for i in mdcontent.split('---')[2:]:
        text = text+i
    text = text.replace('\n\n\n\n\n','\n\n')
    text = text.replace('\n\n\n\n','\n\n')
    text = text.replace('\n\n\n','\n\n')
#     intro = text.split('<!--more-->')[0]
#     text = text.split('<!--more-->')[1]
#     intro = intro.replace('\n','')
#     text = text.replace('\n\n','\n')
    content = [title,categories,date,thumbnail,text]
    return content


# In[ ]:


#md转html的方法 
def md2html(path):
    path = path.replace('+','/')
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    content = get_content(path)
    mdcontent = '#'+content[0]+'\n'+content[4]+'\n\n提交时间：'+content[2].replace('~',' ')
    
    html = markdown.markdown(mdcontent,extensions=exts)
    content = Markup(html)
    return content


# In[ ]:


# 将md文件中的![]()代码改为<!img src=>格式
def regu_img(text):
    text = text.split('![')
    for i in range(len(text)-1):
        img_info = text[i+1].split(')')[0]
        text_info = ')'.join(text[i+1].split(')')[1:])
        # print(text[i+1])
        alt = img_info.split('](')[0]
        url = img_info.split('](')[1]
        img_html = '<br><img width=100%% src=\"%s\" alt=\"%s\" />'%(url,alt)
        text[i+1] = img_html+text_info
    return "".join(text)

# 已知content，组装成规范的md文件格式
def pack_md(content):# content = [title,categories,date,thumbnail,text]
    info = '---\n' + 'title: ' + content[0] + '\ncategories: ' + content[1]+ '\ndate: ' + content[2] + '\nthumbnail: ' + content[3] + '\n---\n'
    # 为了图片的比例，将![]()型的统一改为<img src="xxx" />
    content[4] = regu_img(content[4])
    passage = info + content[4].replace('\n\n','\n')
    return passage


# In[ ]:


database=sqlite3.connect('database')
cursor=database.cursor()
cursor.execute('create table if not exists ttou(title text,categories text,url text,date text, thumbnail text)')
cursor.execute('create table if not exists upload(filename text,path text,time text)')
database.commit()


# In[ ]:


@app.route('/', methods=['GET'])
def index():
    database=sqlite3.connect('database')
    cursor=database.cursor()
    cursor.execute('select * from ttou')
    records = cursor.fetchall()
    categories = []
    for i in records:
        if i[1] not in categories:
            categories.append(i[1])
    info = {"passage_number":len(records),"total_pages":math.ceil(len(records)/5)}
    
    page = request.args.get("page")
    if page==None or page=='1' or page=='0':
        page = 1
        records = records[0:5]
    else:
        page = int(page)
        records = records[5*page-5:5*page]
    info["current_page"] = page
    info["next_page"] = '\?page='+str(page+1)
    info["former_page"] = '\?page='+str(page-1)
    return render_template('index.html', info = info, categories=categories, records=records[::-1])


# In[ ]:


@app.route('/<category>/', methods=['GET'])
def category(category):
    database=sqlite3.connect('database')
    cursor=database.cursor()
    cursor.execute('select * from ttou')
    records = cursor.fetchall()
    passages = []
    categories = []
    for i in records:
        if i[1] == category:
            passages.append(i)
        if i[1] not in categories:
            categories.append(i[1])
    
    info = {"passage_number":len(records),"total_pages":math.ceil(len(passages)/5)}
    
    page = request.args.get("page")
    if page==None or page=='1' or page=='0':
        page = 1
        records = passages[0:5]
    else:
        page = int(page)
        records = passages[5*page-5:5*page]
    info["current_page"] = page
    info["next_page"] =  '\%s/?page=%s' % (category,str(page+1))
    info["former_page"] =  '\%s/?page=%s' % (category,str(page-1))
    return render_template('index.html', info = info, categories=categories, records=records[::-1])


# In[ ]:


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        session['username'] = username
        session['password'] = password
        if (session.get('username')==app.config['ACCOUNT']) and (session.get('password')==app.config['PASSWORD']):
            return redirect(url_for("admin"))
        else:
            return redirect(url_for("login"))


# In[ ]:


@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'GET':
        if (session.get('username')==app.config['ACCOUNT']) and (session.get('password')==app.config['PASSWORD']):
            return render_template('admin.html')
        else:
            return redirect(url_for("login"))
    elif request.method == 'POST':
        page = request.form.get('button')
        # print(page)
        return redirect(url_for(page))


# In[ ]:


@app.route('/admin/modify', methods=['GET','POST'])
def modify():
    if request.method == 'GET':
        if (session.get('username')==app.config['ACCOUNT']) and (session.get('password')==app.config['PASSWORD']):
            database=sqlite3.connect('database')
            cursor=database.cursor()
            cursor.execute('select * from ttou')
            records = cursor.fetchall()
            return render_template('modify.html',records=records[::-1])
        else:
            return redirect(url_for("login"))
    elif request.method == 'POST':
        database=sqlite3.connect('database')
        cursor=database.cursor()
        cursor.execute('select * from ttou')
        records=cursor.fetchall()
        
        if request.files.get('file')==None and request.form.get('delete')!=None:# 不是上传文章 -> 文章删除功能
            title = request.form.get('delete')
            for i in records:
                if i[0]==title:
                    categories = i[1]
            os.remove(os.path.join(app.config['FASSAGE_PATH'],categories,title+'.md'))
            # print(title,categories,'deleted')
            cursor.execute('DELETE FROM ttou WHERE title=\"%s\"' % title)
            database.commit()
            return redirect(url_for("modify"))
        elif request.form.get('button')!=None:# 有文章提交了
            title = secure_filename(request.form.get('title'))
            categories = request.form.get('categories')
            text = request.form.get('text')
            if request.form.get('date')=='':
                localtime = time.strftime("%Y-%m-%d~%H:%M:%S", time.localtime())
            else:
                localtime =  request.form.get('date')
            thumbnail =  request.form.get('thumbnail')
    #       print(context)
            catepath = os.path.join(app.config['FASSAGE_PATH'],categories)
            if not os.path.exists(catepath):#判断存放文章的文件夹是否存在
                os.makedirs(catepath) # 若分类文件夹不存在就创建
            content = [title,categories,localtime,thumbnail,text]
            passage = pack_md(content)
            with open('%s.md'% (os.path.join(catepath,title)), "w+",encoding='utf-8') as m:
                m.write(passage)
            target = categories+'+'+title
            database=sqlite3.connect('database')
            cursor=database.cursor()
            cursor.execute('insert into ttou (title,categories,url,date,thumbnail) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")' 
                           %(title,categories,target,localtime,thumbnail))
            database.commit()
            return redirect(url_for("read",target=target))
        else: # 上传文章功能 -> 跳转到预览
            file = request.files.get('file')
            filename = secure_filename(file.filename)
            temp_path = os.path.join(app.config['TEMP'],filename)
            file.save(temp_path)
            content = get_content(temp_path)
            # 1.title; 2.categories; 3.date; 4.thumbnail; 5.text area
            os.remove(temp_path)
            return render_template('new.html',content=content)


# In[ ]:


@app.route('/admin_edit/<target>', methods=['GET','POST'])
def edit(target):
    if request.method == 'GET':
        if (session.get('username')==app.config['ACCOUNT']) and (session.get('password')==app.config['PASSWORD']):
            content = get_content(os.path.join(app.config['FASSAGE_PATH'],target.replace('+','/')+'.md'))
            return render_template('new.html',content=content)
        else:
            return redirect(url_for("login"))
    elif request.method == 'POST':
        # 1. delete original file
        os.remove(os.path.join(app.config['FASSAGE_PATH'],target.replace('+','/')+'.md'))
        database=sqlite3.connect('database')
        cursor=database.cursor()
        cursor.execute('select * from ttou')
        records=cursor.fetchall()
        cursor.execute('DELETE FROM ttou WHERE title=\"%s\"' % target.split('+')[1])
        database.commit()
        # print(title,categories,'deleted')
        
        # 2. save figured file
        # print(context)
        title = secure_filename(request.form.get('title'))
        categories = request.form.get('categories')
        text = request.form.get('text')
        if request.form.get('date')=='':
            localtime = time.strftime("%Y-%m-%d~%H:%M:%S", time.localtime())
        else:
            localtime =  request.form.get('date')
        thumbnail =  request.form.get('thumbnail')
#       print(context)
        catepath = os.path.join(app.config['FASSAGE_PATH'],categories)
        if not os.path.exists(catepath):#判断存放文章的文件夹是否存在
            os.makedirs(catepath) # 若分类文件夹不存在就创建
        content = [title,categories,localtime,thumbnail,text]
        passage = pack_md(content)
        with open('%s.md'% (os.path.join(catepath,title)), "w+",encoding='utf-8') as m:
            m.write(passage)
        target = categories+'+'+title
        cursor.execute('insert into ttou (title,categories,url,date,thumbnail) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")' 
                       %(title,categories,target,localtime,thumbnail))
        database.commit()
        return redirect(url_for("modify"))


# In[ ]:


@app.route('/admin/new', methods=['GET','POST'])
def new():
    if request.method == 'GET':
        if (session.get('username')==app.config['ACCOUNT']) and (session.get('password')==app.config['PASSWORD']):
            content = ['','','','','']
            return render_template('new.html',content=content)
        else:
            return redirect(url_for("login"))
    elif request.method == 'POST':
        title = secure_filename(request.form.get('title'))
        categories = request.form.get('categories')
        text = request.form.get('text')
        if request.form.get('date')=='':
            localtime = time.strftime("%Y-%m-%d~%H:%M:%S", time.localtime())
        else:
            localtime =  request.form.get('date')
        thumbnail =  request.form.get('thumbnail')
#       print(context)
        catepath = os.path.join(app.config['FASSAGE_PATH'],categories)
        if not os.path.exists(catepath):#判断存放文章的文件夹是否存在
            os.makedirs(catepath) # 若分类文件夹不存在就创建
        content = [title,categories,localtime,thumbnail,text]
        passage = pack_md(content)
        with open('%s.md'% (os.path.join(catepath,title)), "w+",encoding='utf-8') as m:
            m.write(passage)
        target = categories+'+'+title
        database=sqlite3.connect('database')
        cursor=database.cursor()
        cursor.execute('insert into ttou (title,categories,url,date,thumbnail) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")' 
                       %(title,categories,target,localtime,thumbnail))
        database.commit()
        return redirect(url_for("read",target=target))


# In[ ]:


@app.route('/read/<target>', methods=['GET'])
def read(target):
    if target=='login':
        return redirect(url_for("login"))
    else:
        html = md2html('%s.md'% (os.path.join(app.config['FASSAGE_PATH'],target)))
        database=sqlite3.connect('database')
        cursor=database.cursor()
        cursor.execute('select * from ttou')
        records = cursor.fetchall()
        categories = []
        for i in records:
            if i[1] not in categories:
                categories.append(i[1])
        return render_template('read.html',content = html, category = categories, records=records)


# In[ ]:


@app.route('/admin/upload', methods=['GET','POST'])
def upload():
    if request.method == 'GET':
        if (session.get('username')==app.config['ACCOUNT']) and (session.get('password')==app.config['PASSWORD']):
            database=sqlite3.connect('database')
            cursor=database.cursor()
            cursor.execute('select * from upload')
            records = cursor.fetchall()
            return render_template('upload.html',records=records[::-1])
        else:
            return redirect(url_for("login"))
    elif request.method == 'POST':
        database=sqlite3.connect('database')
        cursor=database.cursor()
        filename = request.form.get('delete')
        if filename!=None: # 删除已经上传的文件
            path = app.config['UPLOAD'] + filename
            os.remove(path)
            cursor.execute('DELETE FROM upload WHERE filename=\"%s\"' % filename)
            database.commit()
        else: # 上传文件
            file = request.files.get('file')
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD'],filename))
            path = '/'+app.config['UPLOAD']+filename
            localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            cursor.execute('insert into upload (filename,path,time) VALUES (\"%s\",\"%s\",\"%s\")' 
                           %(filename,path,localtime))
            database.commit()
        return redirect(url_for("upload"))


# In[ ]:


if __name__ == '__main__':
    port=5000
    server = pywsgi.WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()

