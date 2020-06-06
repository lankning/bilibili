#!/usr/bin/env python
# coding: utf-8

# In[12]:


from aip import AipOcr
import re
import pandas as pd
from pandas import DataFrame


# In[2]:


appid='xxxxxxxx'
apikey='xxxxxxxxxxxxxxx'
secretkey='xxxxxxxxxxxxxxxxxxxxxxxxx'

client=AipOcr(appid,apikey,secretkey)


# In[5]:


i=open(r'C:\Users\11197\Desktop\2.jpg','rb')
img=i.read()


# In[8]:


message = client.basicGeneral(img);
# print(message)
word=[]
for i in message.get('words_result'):
    word.append(i.get('words'))


# In[10]:


print(word)


# In[13]:


dic = {}
dic['姓名']=word

df = pd.DataFrame(dic)
df.to_excel('2.xlsx', index=False)

