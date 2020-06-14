#!/usr/bin/env python
# coding: utf-8

# In[1]:


from mail import send_email
from func import database_init,update
import time


# In[2]:


# 初始化数据库
database_init(table_name='menu')


# In[ ]:


while(1):
    # 更新并且发送邮件
    update(url='https://www.ibiquge.net/84_84792/')
    time.sleep(1800)# update every half hour

