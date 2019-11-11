from flask import Flask, request, render_template, redirect,url_for,make_response,send_from_directory,flash
from werkzeug import secure_filename
import time
import _thread
import os

# 文件上传的地址
UPLOAD_FOLDER = 'uploads'
# 允许上传的文件格式
# ALLOWED_EXTENSIONS = set(['txt','ppt','pptx','doc','docx','pdf','epub','mobi','rar','zip','png','jpg','jpeg','gif','mp3'])
app = Flask(__name__)
app.secret_key = '123456'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#限制最大上传文件为30Mb
app.config['MAX_CONTENT_LENGTH'] = 60 * 1024 * 1024

records=[]
with open('records.txt','r+') as s:
    for line in s:
        records.append(eval(line))# 这里打开所有记录

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html',records=records[::-1])

    else:#post方法
        scon = request.form.get('scon')
        target = []
        # 搜索云端是否有该文件，罗列所有相关的
        for record in records:
            # print(record['filename'])
            if scon in record['filename']:
                target.append(record)
        if target==[]:#没有找到相关文件
            flash('没有找到相关文件！')
            return render_template('index.html',records=records[::-1])
        else:
            return render_template('index.html',records=target[::-1])
        

#检查文件是否有效
def allowed_file(filename):
    return True


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)#重要的安全步骤
            filename = file.filename.rsplit('.', 1)[0]
            filetype = file.filename.rsplit('.', 1)[1]
            filename = filename.replace(' ','') # 将文件名中的空格去除
            filename = filename.replace('.','-') # 去除文件中的.
            filename = filename+'.'+filetype
            # 解决命名冲突的问题
            for record in records:
                if filename==record['filename']:
                    flash('该文件已经存在！')
                    return render_template('upload.html')
            # ----------
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # 更新本地记录
            records.append({"filename": filename,
                         "date": date})
            with open('records.txt','w+') as s:
                for line in records:
                    s.write(str(line))
                    s.write('\n')
            return redirect(url_for('index'))
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route("/download/<filename>", methods=['GET'])
def download(filename):
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    directory = './uploads/'  # 假设在当前目录
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0',threaded=True,port=8080)