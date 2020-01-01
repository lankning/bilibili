from flask import Flask, request, render_template, redirect, url_for
import sqlite3 # 导入sqlit3库
import time

# 连接到一个数据库名为 data 的数据库,如果存在则直接连接,如果不存在则创建
data_base=sqlite3.connect('data', check_same_thread=False)
# 设置数据库光标,你之后所有对数据库进行的操作都是通过光标来执行的
cursor=data_base.cursor()
# 创建一个表名为 accounts 的数据库表,如果这个表不存在的话
# 后面括号里面的内容为这个表的属性,属性与属性之间用  ,  隔开,属性名与属性类型之间用 空格  隔开,如果不写类型的话,默认       为text类型
cursor.execute('create table if not exists accounts(name text,mail text,pwd text)')
cursor.execute('create table if not exists comments(says text)')
# 数据库的提交,对数据进行增删改后都需要进行数据库的提交
data_base.commit()

app = Flask(__name__)

@app.route('/')
def index():
	return render_template("index.html")
		
@app.route('/register',methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template("register.html")
	else:
		name=request.form.get('name')
		mail=request.form.get('mail')
		pwd=request.form.get('pwd')
		# print('name:%s'%name,"\nmail:%s"%mail,"\npwd:%s"%pwd)
		cursor.execute('insert into accounts (name,mail,pwd) VALUES (\"%s\",\"%s\",\"%s\")'%(name,mail,pwd))
		data_base.commit()
		cursor.execute('select * from accounts')
		result=cursor.fetchall()
		print(result)
		return redirect(url_for('index'))

@app.route('/home',methods=['GET', 'POST'])
def home():
	if request.method == 'GET':
		return redirect(url_for('index'))
	else:
		name=request.form.get('name')
		pwd=request.form.get('pwd')
		cursor.execute('select * from accounts WHERE name=\"%s\"'%name)
		result=cursor.fetchall()
		# print(result[0][2])##密码
		if pwd==result[0][2]:
			return render_template("home.html",username=name)
		else:
			return redirect(url_for('index'))

@app.route('/comment',methods=['GET', 'POST'])
def comment():
	if request.method == 'GET':
		cursor.execute('select * from comments')
		records=cursor.fetchall()
		
		says=[]
		for r in records:
			says.append(eval(r[0]))
		print(says)
		return render_template("comment.html", says=says)
	else:
		username = request.form.get('username')
		title = request.form.get('title')
		content = request.form.get('content')
		date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		say={"title": title, "content": content, "username": username, "date": date}
		# 添加留言记录
		cursor.execute('insert into comments (says) VALUES (\"%s\")'%(say))
		data_base.commit()
		return redirect(url_for('comment'))


if __name__=='__main__':
    app.run(port='5000',debug=True)#host='0.0.0.0',