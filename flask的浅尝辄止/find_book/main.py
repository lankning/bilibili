from flask import Flask, request, render_template, redirect,url_for,make_response,send_from_directory,flash
from func import *
import _thread

app = Flask(__name__)
app.secret_key = '123456'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    else:#post方法
        bn = request.form.get('book_name')
        wn = request.form.get('writor')
        print('书名',bn)
        print('作者',wn)
        exist = check_on_cloud(bn,wn)#没有，返回0；有，返回书名
        if exist==1:
            flash('书名和作者必须要填哦！')
            return redirect(url_for('index'))
        elif exist==0:
            url,bn,wn=search(bn,wn)
            if bn==None:#没有这本书
                flash('书名不准确或者后台进程已满。')
                return redirect(url_for('index'))
            elif wn==None:#没有这个作者
                flash('作者名不准确或者后台进程已满。')
                return redirect(url_for('index'))
            else:#网上搜到了这本书
                with open('url.txt','w') as u:
                    u.write(url)
                with open('bn.txt','w') as b:
                    b.write(bn)
                with open('wn.txt','w') as w:
                    w.write(wn)
                return redirect(url_for('loading'))
        else:#云端已经有了
            return redirect(url_for('download',filename = exist))
        

@app.route('/loading', methods=['GET'])
def loading():
    print('loading')
    with open('url.txt','r') as u:
        url = u.read()
    with open('bn.txt','r') as b:
        bn = b.read()
    with open('wn.txt','r') as w:
        wn = w.read()
    _thread.start_new_thread(load_on_cloud,(url,wn,))
    return render_template('loading.html',bn=bn,wn=wn)

@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = './books/'  # 假设在当前目录
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response
    
if __name__ == '__main__':
    app.run(threaded=True,host='0.0.0.0')