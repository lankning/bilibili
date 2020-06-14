import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def send_email(subject,mess,to_addr='your_destination@163.com'):
# SMTP服务器以及相关配置信息
    smtp_server = 'smtp.163.com'    #163邮箱用到的SMTP服务器
    from_addr = 'your_account@163.com'
    password = 'Authorization code'      #上面代码中发送方是163邮箱，所以密码不是邮箱的登录密码，而是手动开启SMTP协议后设置或分配的授权码！，
    #但如果是Gmail则使用的密码是登录密码

    msg = MIMEText(mess, 'html', 'utf-8')
# 如果没有加入如下代码，则会被识别为垃圾邮件
# 1.创建邮件(写好邮件内容、发送人、收件人和标题等)
    msg['From'] = format_addr('Lankning小说管家 <%s>' % from_addr)  # 发件人昵称和邮箱
    msg['To'] = format_addr('管理员 <%s>' % to_addr)  # 收件人昵称和邮箱
    msg['Subject'] = Header('%s'%subject, 'utf-8').encode()  # 邮件标题
# 2.登录账号
    #server = smtplib.SMTP_SSL(smtp_server,465)
    server = smtplib.SMTP(smtp_server,25)
    #server.set_debuglevel(1)#打印出交互信息
    server.helo(smtp_server)
    server.ehlo(smtp_server)
    server.login(from_addr, password)
# 3.发送邮件
    server.sendmail(from_addr, to_addr.split(","), msg.as_string())
    server.quit()
    return None