#!/usr/bin/env python
# coding: utf-8

# In[3]:


from aip import AipOcr


# In[4]:


def wordreco(path):
    appid='xxxx'
    apikey='xxxx'
    secretkey='xxxx'

    client=AipOcr(appid,apikey,secretkey)
    
    i=open(path,'rb')
    img=i.read()
    message = client.basicGeneral(img);
    word=[]
    
    for i in message.get('words_result'):
        word.append(i.get('words'))
    word="".join(word)# 合并成一句话
    return word


# In[5]:


path='C:/Users/11197/Desktop/1.png'
word=wordreco(path)
print(word)


# In[ ]:




