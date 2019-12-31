#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import matplotlib.pyplot as plt


# In[2]:


def getlr(index):# 得到每个零点的左右索引，然后取其中值
    newindex=[]
    for i in index[0]:
        if i == index[0,0]:
            lasti=i
            newindex.append(i)
            continue
        else:
            if i==lasti+1:#如果是连贯的
                lasti=i
            else:#如果已经断开了，就取上一个
                newindex.append(lasti)
                lasti = i
                newindex.append(i)
    newindex.append(index[0,-1])
    newindex = np.array(newindex)
    newindex = newindex.reshape((-1,2))
    new = []
    for i in newindex:
        new.append(int((i[0]+i[1])/2))
    return new


# In[3]:


def getroot(r=np.linspace(-30,30,10000),f = pow(np.linspace(-30,30,10000),2)-5):
    zero = r*0
    plt.plot(r,f,r,zero)
    plt.show()
    index = np.array(np.where(abs(f)<0.1))
    new = getlr(index)
    print('零点坐标为',r[new])
    return r[new]

a=getroot()

