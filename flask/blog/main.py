#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from flask import Flask, request, render_template, redirect,url_for,make_response, send_from_directory, session, Markup
import os, time, markdown, sqlite3, math


# In[ ]:


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1.5 * 1024 * 1024 * 1024 # max_size: 1.5G
app.config['SECRET_KEY'] = os.urandom(24)
app.config['FASSAGE_PATH'] = 'static/passages/'
app.config['UPLOAD'] = 'static/uploads/'
app.config['ACCOUNT'] = 'lankning'
app.config['PASSWORD'] = '123456'


# In[ ]:


def secure_filename(filename):
    filename = filename.replace(' ','')
    return filename


# In[ ]:


#md转html的方法 
def md2html(filename):
    exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    mdcontent = ""
    with open(filename,'r',encoding='utf-8') as f:
        mdcontent = f.read()
        pass
    html = markdown.markdown(mdcontent,extensions=exts)
    content = Markup(html)
    return content


# In[ ]:


database=sqlite3.connect('database')
cursor=database.cursor()
cursor.execute('create table if not exists ttou(title text,category text,url text,time text, cover text)')
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
        title = request.form.get('delete')
        for i in records:
            if i[0]==title:
                category = i[1]
        os.remove(os.path.join(app.config['FASSAGE_PATH'],category,title+'.md'))
        # print(title,category,'deleted')
        cursor.execute('DELETE FROM ttou WHERE title=\"%s\"' % title)
        database.commit()
        return redirect(url_for("modify"))


# In[ ]:


@app.route('/admin_edit/<title>', methods=['GET','POST'])
def edit(title):
    if request.method == 'GET':
        if (session.get('username')==app.config['ACCOUNT']) and (session.get('password')==app.config['PASSWORD']):
            database=sqlite3.connect('database')
            cursor=database.cursor()
            cursor.execute('select * from ttou')
            records = cursor.fetchall()
            content = []
            for i in records:
                if i[0]==title:
                    content.append(title)
                    content.append(i[1]) # category
                    content.append(i[3]) # localtime
                    content.append(i[4]) # cover
                    break
            path = os.path.join(app.config['FASSAGE_PATH'],content[1],title+'.md')
#             print(path)
            with open(path,'r',encoding='utf-8') as f:
                mdcontent = f.read()
                content.append(mdcontent) # text area
            return render_template('new.html',content=content)
        else:
            return redirect(url_for("login"))
    elif request.method == 'POST':
        # 1. delete original file
        database=sqlite3.connect('database')
        cursor=database.cursor()
        cursor.execute('select * from ttou')
        records=cursor.fetchall()
        for i in records:
            if i[0]==title:
                category = i[1]
        os.remove(os.path.join(app.config['FASSAGE_PATH'],category,title+'.md'))
        # print(title,category,'deleted')
        cursor.execute('DELETE FROM ttou WHERE title=\"%s\"' % title)
        database.commit()
        
        # 2. save figured file
        title = secure_filename(request.form.get('title'))
        category = request.form.get('category')
        text = request.form.get('text')
        if request.form.get('time')=='':
            localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        else:
            localtime =  request.form.get('time')
        cover =  request.form.get('cover')
        context = '# '+title+'\n'+text+'\n\n'+localtime
#         print(context)
        catepath = os.path.join(app.config['FASSAGE_PATH'],category)
        if not os.path.exists(catepath):#判断存放图片的文件夹是否存在
            os.makedirs(catepath) # 若图片文件夹不存在就创建
        with open('%s.md'% (os.path.join(catepath,title)), "w+",encoding='utf-8') as m:
            m.write(context)
        target = category+'+'+title
        cursor.execute('insert into ttou (title,category,url,time,cover) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")' 
                       %(title,category,target,localtime,cover))
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
        category = request.form.get('category')
        text = request.form.get('text')
        if request.form.get('time')=='':
            localtime = time.strftime("%Y-%m-%d~%H:%M:%S", time.localtime())
        else:
            localtime =  request.form.get('time')
        cover =  request.form.get('cover')
        context = '# '+title+'\n'+text+'\n\n'+localtime
#         print(context)
        catepath = os.path.join(app.config['FASSAGE_PATH'],category)
        if not os.path.exists(catepath):#判断存放图片的文件夹是否存在
            os.makedirs(catepath) # 若图片文件夹不存在就创建
        with open('%s.md'% (os.path.join(catepath,title)), "w+",encoding='utf-8') as m:
            m.write(context)
        target = category+'+'+title
        database=sqlite3.connect('database')
        cursor=database.cursor()
        cursor.execute('insert into ttou (title,category,url,time,cover) VALUES (\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")' 
                       %(title,category,target,localtime,cover))
        database.commit()
        return redirect(url_for("read",target=target))


# In[ ]:


@app.route('/read/<target>', methods=['GET'])
def read(target):
#     print(target)
    database=sqlite3.connect('database')
    cursor=database.cursor()
    cursor.execute('select * from ttou')
    records = cursor.fetchall()
    categories = []
    for i in records:
        if i[1] not in categories:
            categories.append(i[1])
    target = target.replace('+','/')
    html = md2html('%s.md'% (os.path.join(app.config['FASSAGE_PATH'],target)))
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
        if filename!=None:
            path = app.config['UPLOAD'] + filename
            os.remove(path)
            cursor.execute('DELETE FROM upload WHERE filename=\"%s\"' % filename)
            database.commit()
        else:
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
    app.run('0.0.0.0',port)

