#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask, request, render_template, redirect,url_for,make_response,send_from_directory
import os, fitz, zipfile, random
from gevent import pywsgi
from skimage.io import imread
from skimage.transform import resize
import matplotlib.pyplot as plt


# In[2]:


app = Flask(__name__)
UPLOAD_FLODER = './uploads'

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

def download(filename,directory = './'):# 假设在当前目录
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    response = make_response(send_from_directory(directory, filename, as_attachment=True))
    response.headers["Content-Disposition"] = "attachment; filename={}".format(filename.encode().decode('latin-1'))
    return response

def pyMuPDF_fitz(pdfPath, imagePath, acc):# 将pdf转化为图片，放入相应的文件夹
    print("imagePath="+imagePath)
    pdfDoc = fitz.open(pdfPath)
    for pg in range(pdfDoc.pageCount):
        page = pdfDoc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        zoom_x = 1.33333333*acc #(1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 1.33333333*acc
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)
        
        if not os.path.exists(imagePath):#判断存放图片的文件夹是否存在
            os.makedirs(imagePath) # 若图片文件夹不存在就创建
        
        pix.writePNG(imagePath+'/'+'images_%s.png' % pg)#将图片写入指定的文件夹内
    pdfDoc.close()
    return 1

def zip_ya(startdir, file_news): # 将文件压缩
    z = zipfile.ZipFile(file_news,'w',zipfile.ZIP_DEFLATED) #参数一：文件夹名
    for dirpath, dirnames, filenames in os.walk(startdir):
        fpath = dirpath.replace(startdir,'') #这一句很重要，不replace的话，就从根目录开始复制
        fpath = fpath and fpath + os.sep or ''#这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename),fpath+filename)
        print ('%s压缩成功' % file_news)
    z.close()

def pic2pdf(path,name):
    doc = fitz.open()
    for img in os.listdir(path): # 读取图片，确保按文件名排序
        # print(img)
        imgdoc = fitz.open(os.path.join(path,img))         # 打开图片
        pdfbytes = imgdoc.convertToPDF()    # 使用图片创建单页的 PDF
        imgpdf = fitz.open("pdf", pdfbytes)
        doc.insertPDF(imgpdf)          # 将当前页插入文档
    newpath = os.path.join(path, name)
    if os.path.exists("%s.pdf" % newpath):
        os.remove("%s.pdf" % newpath)
    doc.save("%s.pdf" % newpath)          # 保存pdf文件
    doc.close()

def combine_pdf_files(path,name):
    doc = fitz.open()
    for pdf in os.listdir(path): # 读取图片，确保按文件名排序
        # print(img)
        pdfbytes = fitz.open(os.path.join(path,pdf))         # 打开图片
        doc.insertPDF(pdfbytes)          # 将当前页插入文档
    newpath = os.path.join(path, name)
    if os.path.exists("%s.pdf" % newpath):
        os.remove("%s.pdf" % newpath)
    doc.save("%s.pdf" % newpath)          # 保存pdf文件
    doc.close()


# In[3]:


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')


# In[4]:


@app.route('/Compress-picture', methods=['GET', 'POST'])
def Compress_picture():
    if request.method == 'GET':
        return render_template('Compress-picture.html')

    elif request.method == 'POST':#post方法
        file = request.files.get('file')
        rate = float(request.form.get('rate'))
        dpi = int(request.form.get('dpi'))
        if dpi > 500:
            return redirect(url_for("index"))
        
        filename = os.path.join(UPLOAD_FLODER,file.filename)
        file.save(filename)
        
        img = imread(filename)
        # print(img.shape)
        x = int(img.shape[0]*rate)
        y = int(img.shape[1]*rate)
        # print(x,y)
        img = resize(img,(x,y))
        print(img.shape)
        plt.axis('off')
        plt.imshow(img)
        plt.savefig(filename,bbox_inches='tight',pad_inches=0.0,dpi=dpi)#,dpi=800
        
        # get file size
        file.seek(0, os.SEEK_END)
        size1 = file.tell()/1024/1024
        size2 = os.stat('%s'%filename).st_size/1024
        print(filename,'原大小%.2fMb, ' % size1,'压缩后大小为%.2fkb' % size2)
        # print('分辨率比率为%s' % rate, '实际压缩比率为%.4f' % (size2/(1024*size1)))
        
        response = download(file.filename,UPLOAD_FLODER)
        return response


# In[5]:


@app.route('/pdf-to-pic', methods=['GET', 'POST'])
def pdf_to_pic():
    if request.method == 'GET':
        return render_template('pdf-to-pic.html')

    elif request.method == 'POST':#post方法
        file = request.files.get('file')
        acc = int(request.form.get('acc'))
        
        filename = os.path.join(UPLOAD_FLODER,file.filename)
        file.save(filename)
        
        name = file.filename.rsplit('.', 1)[0]
        img_path = os.path.join(UPLOAD_FLODER, name)
        pyMuPDF_fitz(filename, img_path, acc)
        file_news = os.path.join(UPLOAD_FLODER, '%s.zip' % name) # 压缩后文件夹的名字
        zip_ya(img_path, file_news)
        
        response = download('%s.zip' % name, UPLOAD_FLODER)
        return response


# In[6]:


@app.route('/pic-to-pdf', methods=['GET', 'POST'])
def pic_to_pdf():
    if request.method == 'GET':
        return render_template('pic-to-pdf.html')

    elif request.method == 'POST':#post方法
        temp_fold = os.path.join(UPLOAD_FLODER, str(random.randint(0,9999)))
        if not os.path.exists(temp_fold):#判断存放图片的文件夹是否存在
            os.makedirs(temp_fold) # 若图片文件夹不存在就创建
        for file in request.files.getlist('file'):
            filename = os.path.join(temp_fold, file.filename)
            file.save(filename)
        name = request.form.get('name')
        
        pic2pdf(temp_fold, name)
        
        response = download(name+".pdf", temp_fold)
        return response


# In[7]:


@app.route('/combine-pdf', methods=['GET', 'POST'])
def combine_pdf():
    if request.method == 'GET':
        return render_template('combine-pdf.html')

    elif request.method == 'POST':#post方法
        temp_fold = os.path.join(UPLOAD_FLODER, str(random.randint(0,9999)))
        if not os.path.exists(temp_fold):#判断存放图片的文件夹是否存在
            os.makedirs(temp_fold) # 若图片文件夹不存在就创建
        for file in request.files.getlist('file'):
            filename = os.path.join(temp_fold, file.filename)
            file.save(filename)
        name = request.form.get('name')
        
        combine_pdf_files(temp_fold, name)
        
        response = download(name+".pdf", temp_fold)
        return response


# In[ ]:


if __name__ == '__main__':
    port=5000
    server = pywsgi.WSGIServer(('0.0.0.0', port), app)
    server.serve_forever()


# In[ ]:




