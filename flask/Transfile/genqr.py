import qrcode
import socket
import os
 
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    # print(ip)
    return ip

def gen_qr(ip,port=80):
    data = ip+":"+str(port)
    # 实例化QRCode生成qr对象
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4
    )
    # 传入数据
    qr.add_data(data)
    qr.make(fit=True)
    # 生成二维码
    img = qr.make_image()
    return img

def gen(path,port=80):
    ip = get_ip()
    img = gen_qr(ip,port)
    img_file = os.path.join(path,"Qrcode.png")
    # 保存二维码
    img.save(img_file)
    return None