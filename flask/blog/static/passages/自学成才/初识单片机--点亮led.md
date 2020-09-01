---
title: 初识单片机--点亮led
categories: 自学成才
date: 2020-3-1~21:28:31
thumbnail: http://www.hificat.com/module/kc103/4.JPG
---
淘宝买了一个51单片机，今天到货开始学习。本专题将记录在学习过程中遇到的问题，本篇记录单片机的初次上手中遇到的驱动问题和烧录问题。

<!--more-->

## 1、单片机品牌型号

品牌：普中

型号：STC89C52

![](https://s2.ax1x.com/2020/03/01/32QdA0.jpg)

## 2、Windows10下烧写

- 安装CH340驱动

 CH340/CH341驱动适用于win7、win8 64位操作系统，安装后就可以进行各种参数操作了，适用于WINDOWS 98/ME/2000/XP/Vista/Linux等操作系统。CH340/CH341驱动可以用于usb转串口操作，转换后可以与各类串口监控软件和调试工具配合使用。 

下载链接：https://pan.baidu.com/s/1i4esgIh 

- 下载STC-ISP烧写程序

淘宝客服发给我的普中的烧写程序每次都超时，无法真正写入到单片机里面。搜索了大量相关问题之后，有人推荐使用STC-ISP原厂的烧写程序，果然解决了问题。

下载链接：http://www.stcisp.com/_download_stcisp_new.html 

![附图：STC-ISP烧写步骤](https://s2.ax1x.com/2020/03/01/321RfK.png)