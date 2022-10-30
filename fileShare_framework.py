#!encoding=utf-8
import requests
import json
import argparse
import os
import random
import string
import base64
import time
import hashlib
from requests_toolbelt import MultipartEncoder
requests.packages.urllib3.disable_warnings()
## 配置类，包含公共配置相关信息
class Config:
    ## banner
    banner = r'''
 ___  ___  ___ _____ ___ ___ 
/ __|/ _ \| __|_   _/ _ ( _ )
\__ \ (_) | _|  | | \_, / _ \
|___/\___/|_|   |_|  /_/\___/
      fileShare by Soft98    
       QQ群: 775916840                          
    '''
    custom_mix = False
    custom_encode = "base64"
    mix_str = "".join(random.sample(string.ascii_letters + string.digits,22))
    fix_size = 1073741824
    mix = False
    dis_demix = False

## 文件类，文件相关信息
class File:
    file_name = None
    file_path = None
    file_data = None
    file_size = None
    file_object = None
    download_url = None
    mix = False

## 工具类
class Util:
    ## 输出
    def stdout(message:str,end=None):
        start = "[*] "
        if message.startswith("\r"):
            start = "\r" + start
            message = message[1:]
        if message.startswith("\n"):
            start = "\n" + start
            message = message[1:]
        print(start,message,end=end)
    ## 输出异常信息并退出
    def error(message:str):
        print("[*] Error: ",message)
        os._exit(0)
    ## 混淆字节获取方法
    def get_mix_bytes():
        data = Config.mix_str.encode("utf-8")
        if Config.custom_encode.lower() == "md5":
            h = hashlib.md5(data)
            data = h.hexdigest().encode("utf-8")
        if Config.custom_encode.lower() == "sha1":
            h = hashlib.sha1(data)
            data = h.hexdigest().encode("utf-8")
        if Config.custom_encode.lower() == "sha256":
            h = hashlib.sha256(data)
            data = h.hexdigest().encode("utf-8")
        if Config.custom_encode.lower() == "sha512":
            h = hashlib.sha512(data)
            data = h.hexdigest().encode("utf-8")
        encode_pass = base64.b64encode(data)
        return encode_pass*100

## 文件处理类
class FileHandle:
    def get_file_data(file:File,read_size):
        mix_bytes = Util.get_mix_bytes()
        mix_length = len(mix_bytes)
        file.file_data = b''
        if file.mix:
            Util.stdout("文件混淆中...")
            if read_size < mix_length:
                mix_length = read_size
            if mix_length > Config.fix_size:
                mix_length = Config.fix_size
            file.file_data = file.file_object.read(mix_length)
            temp = b''
            for i in range(mix_length):
                temp = temp + (mix_bytes[i] ^ file.file_data[i]).to_bytes(1,"big")
            file.file_data = temp
            read_size = read_size - mix_length
        if read_size > 0:
            if file.file_data == b'':
                file.file_data = file.file_object.read(read_size)
            file.file_data = file.file_data + file.file_object.read(read_size)

    def demix_file(file:File):
        Util.stdout("文件反混淆中...")
        mix_bytes = Util.get_mix_bytes()
        mix_length = len(mix_bytes)
        real_size = file.file_size
        if real_size < mix_length:
            mix_length = real_size
        if mix_length > Config.fix_size:
                mix_bytes = Config.fix_size
        de_file = open(file.file_path + file.file_name + ".dec","wb+")
        de_mix_data = file.file_object.read(mix_length)
        temp = b''
        for i in range(mix_length):
            temp = temp + (mix_bytes[i]^ de_mix_data[i]).to_bytes(1,"big")
        de_file.write(temp + file.file_object.read(real_size - mix_length))
        file.file_object.close()
        de_file.close()
        os.remove(file.file_path + file.file_name)
        os.rename(file.file_path + file.file_name + ".dec",file.file_path + file.file_name)
        Util.stdout("文件反混淆结束...")
        
        
## 云存储类，包含云存储和下载相关函数
class CloudService:
    ## 上传文件函数，并生成分享码
    def upload(file:File):
        Util.stdout("文件上传中...")
        ## 文件上传方法具体实现
        ## code...
        ## code...
        ## code...
        scode = {
            ## 自行实现的shareCode组成
            "mix":file.mix
        }
        return base64.b64encode(json.dumps(scode).encode("utf-8")).decode("utf-8")
        # 如果错误可以用error方法输出
        # Util.error("文件上传失败")
    
    ## 获取文件下载地址函数
    def get_download_url(scode):
        ## 根据scode获取下载地址
        download_url = ""
        ## code...
        ## code...
        ## code...
        return download_url
        # 如果错误可以用error方法输出
        # Util.error("获取下载地址失败")
            
    ## 下载文件函数
    def download(file:File):
        response = requests.get(file.download_url,verify=False,stream=True)
        size = 0
        chunk_size = 1024
        start = time.time()
        try:
            content_size = int(response.headers["content-length"])
            Util.stdout("*"*70)
            Util.stdout("[文件名]: " + file.file_name)
            Util.stdout("[文件夹]: " + file.file_path)
            Util.stdout("[文件大小]: {:.2f} MB".format(content_size/chunk_size/1024))
            for data in response.iter_content(chunk_size=chunk_size):
                file.file_object.write(data)
                size += len(data)
                Util.stdout("\r[下载进度]: %s%.2f%%" % (">"*int(size*50/content_size),float(size/content_size*100)),end=" ")
            end = time.time()
            Util.stdout("\n[下载时间]: {:.2f}秒".format(end-start))
            Util.stdout("*"*70)
        except:
            Util.stdout("*"*70)
            Util.stdout("[文件名]: " + file.file_name)
            Util.stdout("[文件夹]: " + file.file_path)
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                size += len(data)
                Util.stdout("\r[下载进度]: %.2f MB" % (size/chunk_size/1024),end=" ")
            end = time.time()
            Util.stdout("\n[下载时间]: {:.2f}秒".format(end-start))
            Util.stdout("*"*70)

class Main:
    ## 文件分享
    def share(file_path):
        nav = {}
        if os.path.isfile(file_path):
            file = File()
            if(len(file_path.split("/")) > 1):
                file.file_name = file_path.split("/")[-1]
                file.file_path = "".join(file_path.split("/")[:-1])
            elif(len(file_path.split("\\")) > 1):
                file.file_name = file_path.split("\\")[-1]
                file.file_path = "".join(file_path.split("\\")[:-1])
            else:
                file.file_name = file_path
            real_size = os.path.getsize(file_path)
            nav["filename"] = file.file_name
            nav["data"] = []
            index = 0
            file.file_object = open(file_path,"rb+")
            nav_mix_flag = Config.mix
            ## 如果文件超过1g，分段处理
            if real_size > Config.fix_size:
                while real_size > Config.fix_size:
                    file.file_size = Config.fix_size
                    file.mix = nav_mix_flag
                    FileHandle.get_file_data(file,Config.fix_size)
                    scode = CloudService.upload(file)
                    nav["data"].append(scode)
                    if nav_mix_flag:
                        nav_mix_flag = False
                    index += 1
                    real_size = real_size - Config.fix_size
            file.mix = nav_mix_flag
            file.file_size = real_size
            FileHandle.get_file_data(file,real_size)
            scode = CloudService.upload(file)
            nav["data"].append(scode)
            if index > 0:
                nav_file = File()
                nav_file.file_name = file.file_name
                nav_file.file_data = json.dumps(nav).encode("utf-8")
                nav_file.mix = Config.mix
                scode = CloudService.upload(nav_file)
                scode["mode"] = "nav"
            Util.stdout("ShareCode: " + scode)
    ## 文件下载
    def download(scode):
        scode = json.loads(base64.b64decode(scode.encode("utf-8")).decode("utf-8"))
        down_file = File()
        down_file.file_name = scode["filename"]
        down_file.file_path = get_download_folder() + "/"
        down_file.download_url = CloudService.get_download_url(scode)
        abs_file = down_file.file_path + down_file.file_name
        if os.path.isfile(abs_file):
            Util.error("下载失败，同名文件已存在: " + abs_file)
        down_file.file_object = open(abs_file,"ab+")
        if scode.get("mode") == "nav":
            Main.download_nav(down_file)
        else:
            CloudService.download(down_file)
        down_file.file_object.close()
        if scode.get("mix",False) and Config.dis_demix == False:
            down_file.file_size = os.path.getsize(abs_file)
            down_file.file_object = open(abs_file,"rb")
            FileHandle.demix_file(down_file)
        
    ## 导航下载
    def download_nav(down_file:File):
        response = requests.get(down_file.download_url,verify=False)
        nav = json.loads(response.text)
        for share in nav["data"]:
            scode = json.loads(base64.b64decode(share.encode("utf-8")).decode("utf-8"))
            down_file.download_url = CloudService.get_download_url(scode)
            CloudService.download(down_file)
        

## 获取下载目录
if os.name == 'nt':
    import ctypes
    from ctypes import windll, wintypes
    from uuid import UUID

    # ctypes GUID copied from MSDN sample code
    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8)
        ] 

        def __init__(self, uuidstr):
            uuid = UUID(uuidstr)
            ctypes.Structure.__init__(self)
            self.Data1, self.Data2, self.Data3,self.Data4[0], self.Data4[1], rest = uuid.fields
            for i in range(2, 8):
                self.Data4[i] = rest>>(8-i-1)*8 & 0xff

    SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
    SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID), wintypes.DWORD,
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
    ]

    def _get_known_folder_path(uuidstr):
        pathptr = ctypes.c_wchar_p()
        guid = GUID(uuidstr)
        if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
            raise ctypes.WinError()
        return pathptr.value

    FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'

    def get_download_folder():
        return _get_known_folder_path(FOLDERID_Download)
else:
    def get_download_folder():
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")
            
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='文件分享工具 ( 建议加密上传 )')
    parser.add_argument("-f",'--file',type=str, default= None, help="分享功能，指定要上传分享的文件;")
    parser.add_argument("-s",'--share',type=str, default= None, help="下载功能，指定下载文件的分享码;")
    parser.add_argument("-p",'--passwd',type=str, default= None, help="自定义混淆密码，起到加密的作用，需要至少10位;")
    parser.add_argument("-e",'--encode',type=str, default="base64", help="混淆密码编码方式，base64/md5/sha1/sha256/sha512;")
    parser.add_argument('-m',action='store_true', help="混淆功能，测试功能，混淆程度有限;")
    parser.add_argument('-d',action='store_true', help="关闭反混淆功能，直接下载混淆文件。")
    args = parser.parse_args()
    file_path = args.file
    scode = args.share
    pwd = args.passwd
    Config.mix = args.m
    Config.dis_demix = args.d
    Config.custom_encode = args.encode
    print(Config.banner)
    if pwd != None:
        if len(pwd) < 10:
            Util.error("使用自定义混淆密码需要10位及以上")
        else:
            Config.custom_mix = True
            Config.mix_str = pwd
            Config.mix = True
    if file_path != None and scode != None:
        Util.error("请指明使用的具体功能，多个功能不能一起使用")
    if file_path == None and scode == None:
        Util.error("请设置参数使用具体功能")
    if file_path != None:
        Main.share(file_path)
    elif scode != None:
        Main.download(scode)