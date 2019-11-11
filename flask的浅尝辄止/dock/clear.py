# 清楚原来的不规范命名
import os

# -txt记录中
records=[]
with open('records.txt','r+',encoding='utf-8') as s:
    for line in s:
        records.append(eval(line))# 这里打开所有记录
for record in records:
    filename = record['filename'].rsplit('.', 1)[0]
    filetype = record['filename'].rsplit('.', 1)[1]
    filename = filename.replace(' ','')
    filename = filename.replace('.','-')
    newname = filename+'.'+filetype
    record['filename']=newname
print('记录文件纠正完成！')

# -书名中

path='./uploads/'
fileList = os.listdir(path)
for file in fileList:
    filename = file.rsplit('.', 1)[0]
    filetype = file.rsplit('.', 1)[1]
    filename = filename.replace(' ','')
    filename = filename.replace('.','-')
    newname = filename+'.'+filetype
    os.rename(path+file,path+newname)
print('书名改好了!')

# 查询是否所有的记录都对应一本书
newrecords = []
for record in records:
    filename = record['filename']
    #print(filename)
    r = 0
    for file in fileList:
        if filename == file:
            r+=1
    if r == 1:
        newrecords.append(record)

with open('records.txt','w+',encoding='utf-8') as s:
    for line in newrecords:
        s.write(str(line))
        s.write('\n')
print('清理无效数据完成！')