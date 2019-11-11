from flask import Flask, request, render_template, redirect, url_for
import time

app = Flask(__name__)

@app.route('/')
def index():#登录页
    return render_template('index.html')
        
     
@app.route('/register',methods=['GET', 'POST'])
def register():#注册页面
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name=[]
        sub_name=request.form.get('name')
        with open('name.txt','r+', encoding="utf-8") as f:
            name = f.readlines()
        name.append(sub_name+'\n')
        with open('name.txt','w+', encoding="utf-8") as f:
            for line in name:
                f.write(line)

        mail=[]
        sub_mail=request.form.get('mail')
        with open('mail.txt','r+', encoding="utf-8") as m:
            mail = m.readlines()
        mail.append(sub_mail+'\n')
        with open('mail.txt','w+', encoding="utf-8") as m:
            for line in mail:
                m.write(line)
        
        pwd=[]
        sub_pwd=request.form.get('pwd')
        with open('pwd.txt','r+', encoding="utf-8") as p:
            pwd = p.readlines()
        pwd.append(sub_pwd+'\n')
        with open('pwd.txt','w+', encoding="utf-8") as p:
            for line in pwd:
                p.write(line)
        return redirect(url_for('index'))
        
@app.route('/home', methods=['GET', 'POST'])
def home():#登录之后的界面
    if request.method == 'GET':
        return redirect(url_for('index'))
    #如果用户名不存在，返回到index页面。如果密码不正确，返回到index页面。用户名密码正确，返回到home页面。
    if request.method == 'POST':
        #判断用户名密码是否正确
        with open('name.txt', 'r+', encoding="utf8") as f:
            with open('pwd.txt','r+', encoding="utf8") as p:
                name=request.form.get('name')
                pwd=request.form.get('pwd')
                i=0
                j=0
                est=0
                for line in f:#寻找账号对应的索引
                    i = i+1
                    if line==(name+'\n'):
                        est = est+1
                        break
                if est==0:#不存在这样的账户
                    #flash('name输入错误','flag')
                    return redirect(url_for('index'))
                for line in p:#寻找对应的密码
                    j = j+1
                    if j==i:
                        password=line
                        break
                if password==(pwd+'\n'):#用户名密码匹配成功
                    #flash('pwd输入正确','flag')
                    sub_name=request.form.get('name')
                    return render_template('home.html',username=str(sub_name))
                else:#密码输入错误
                    return redirect(url_for('index'))
        

@app.route('/comment',methods=['GET', 'POST'])
def comment():#评论区
    if request.method == 'GET':
        says=[]
        with open('says.txt', 'r+' ,encoding="utf8") as s:
            for line in s:
                says.append(eval(line))# 这里打开存放所有的留言
        return render_template('comment.html', says=says)
    else:
        title = request.form.get('say_title')
        text = request.form.get('say')
        user = request.form.get('say_user')
        date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        says=[]
        with open('says.txt','w+', encoding="utf8") as s:
            for line in s:
                says.append(eval(line))# 这里打开存放所有的留言
        says.append({"title": title,
                     "text": text,
                     "user": user,
                     "date": date})
        with open('says.txt','w') as s:
            for line in says:
                s.write(str(line))
                s.write('\n')
        return redirect(url_for('comment'))

@app.route('/moive/zdg')
def zdg():
    return render_template('zdg.html')

@app.route('/moive/bcq')
def bcq():
    return render_template('bcq.html')

@app.route('/moive/mg')
def mg():
    return render_template('mg.html')

if __name__ == '__main__':
    app.run(port=2333)#host='0.0.0.0',
