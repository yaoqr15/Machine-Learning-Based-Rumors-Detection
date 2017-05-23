#-*-coding=utf-8-*-
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )
import time            
import re            
import os    
import sys  
import codecs
import io
import shutil
import urllib
import urllib2
import json
import rsa
import binascii
import base64
import lxml
import random
import datetime
from datetime import timedelta
import xlwt
from lxml import etree
import xlrd
from xlutils.copy import copy
import cookielib
import csv

key=""
#********************************************************************************
#                            登陆weibo.cn
#********************************************************************************
def enableCookies():
            #获取一个保存cookies的对象
            cj = cookielib.CookieJar()
            #将一个保存cookies对象和一个HTTP的cookie的处理器绑定
            cookie_support = urllib2.HTTPCookieProcessor(cj)
            #创建一个opener,设置一个handler用于处理http的url打开
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
            #安装opener，此后调用urlopen()时会使用安装过的opener对象
            urllib2.install_opener(opener)

    #预登陆获得 servertime, nonce, pubkey, rsakv
def getServerData():
            url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=ZW5nbGFuZHNldSU0MDE2My5jb20%3D&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)&_=1442991685270'
            data = urllib2.urlopen(url).read()
            p = re.compile('\((.*)\)')
            try:
                    json_data = p.search(data).group(1)
                    data = json.loads(json_data)
                    servertime = str(data['servertime'])
                    nonce = data['nonce']
                    pubkey = data['pubkey']
                    rsakv = data['rsakv']
                    return servertime, nonce, pubkey, rsakv
            except:
                    print 'Get severtime error!'
                    return None


    #获取加密的密码
def getPassword(password, servertime, nonce, pubkey):
            rsaPublickey = int(pubkey, 16)
            key = rsa.PublicKey(rsaPublickey, 65537) #创建公钥
            message = str(servertime) + '\t' + str(nonce) + '\n' + str(password) #拼接明文js加密文件中得到
            passwd = rsa.encrypt(message, key) #加密
            passwd = binascii.b2a_hex(passwd) #将加密信息转换为16进制。
            return passwd

    #获取加密的用户名
def getUsername(username):
            username_ = urllib.quote(username)
            username = base64.encodestring(username_)[:-1]
            return username

     #获取需要提交的表单数据
def getFormData(userName,password,servertime,nonce,pubkey,rsakv):
        userName = getUsername(userName)
        psw = getPassword(password,servertime,nonce,pubkey)

        form_data = {
            'entry':'weibo',
            'gateway':'1',
            'from':'',
            'savestate':'7',
            'useticket':'1',
            'pagerefer':'http://weibo.com/p/1005052679342531/home?from=page_100505&mod=TAB&pids=plc_main',
            'vsnf':'1',
            'su':userName,
            'service':'miniblog',
            'servertime':servertime,
            'nonce':nonce,
            'pwencode':'rsa2',
            'rsakv':rsakv,
            'sp':psw,
            'sr':'1366*768',
            'encoding':'UTF-8',
            'prelt':'115',
            'url':'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype':'META'
            }
        formData = urllib.urlencode(form_data)
        return formData

    #登陆函数
def login(username,psw):
            enableCookies()
            url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
            servertime,nonce,pubkey,rsakv = getServerData()
            formData = getFormData(username,psw,servertime,nonce,pubkey,rsakv)
            headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0'}
            req  = urllib2.Request(
                    url = url,
                    data = formData,
                    headers = headers
            )
            result = urllib2.urlopen(req)
            text = result.read()
            #print text
            #还没完！！！这边有一个重定位网址，包含在脚本中，获取到之后才能真正地登陆
            p = re.compile('location\.replace\(\'(.*?)\'\)')
            try:
                    login_url = p.search(text).group(1)
                    #print login_url
                    #由于之前的绑定，cookies信息会直接写入
                    urllib2.urlopen(login_url)
                    print "Login success!"
            except:
                    print 'Login error!'
                    return 0

            #访问主页，把主页写入到文件中
            url = 'http://weibo.com/u/2679342531/home?topnav=1&wvr=6'
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            text = response.read()
            fp_raw = open("weibo.html","w+")
            fp_raw.write(text)
            fp_raw.close()
            #print text
#********************************************************************************
#                            爬取数据
#********************************************************************************
class CollectData():
    def __init__(self,keyword, startTime, interval, flag=True, begin_url_per = "http://s.weibo.com/weibo/"):
        self.begin_url_per = begin_url_per  #设置固定地址部分
        self.setKeyword(keyword)    #设置关键字
        self.setStartTimescope(startTime)   #设置搜索的开始时间
        #self.setRegion(region)  #设置搜索区域
        self.setInterval(interval)  #设置邻近网页请求之间的基础时间间隔（注意：过于频繁会被认为是机器人）
        self.setFlag(flag)

    ##设置关键字
    ##关键字需解码后编码为utf-8
    def setKeyword(self,keyword):
        self.keyword= unicode(keyword)#keyword.decode('GBK','ignore').encode("utf-8")

        print 'twice encode:',self.getKeyWord()

    ##关键字需要进行两次urlencode
    def getKeyWord(self):
        once = urllib.urlencode({"kw":self.keyword})[3:]
        return urllib.urlencode({"kw":once})[3:]

    ##设置起始范围，间隔为1天
    ##格式为：yyyy-mm-dd
    def setStartTimescope(self, startTime):
        if not (startTime == '-'):
            self.timescope = startTime + ":" + startTime
        else:
            self.timescope = '-'

    ##设置搜索地区
    #def setRegion(self, region):
    #    self.region = region

    ##设置邻近网页请求之间的基础时间间隔
    def setInterval(self, interval):
        self.interval = int(interval)

    ##设置是否被认为机器人的标志。若为False，需要进入页面，手动输入验证码
    def setFlag(self, flag):
        self.flag = flag

    ##构建URL
    def getURL(self):
        return self.begin_url_per+self.getKeyWord()+"&typeall=1&suball=1×cope=custom:"+self.timescope+"&page="

    ##爬取一次请求中的所有网页，最多返回50页
    def download(self, url, maxTryNum=4):
        hasMore = True  #某次请求可能少于50页，设置标记，判断是否还有下一页
        isCaught = False    #某次请求被认为是机器人，设置标记，判断是否被抓住。抓住后，需要，进入页面，输入验证码
        name_filter = set([])    #过滤重复的微博ID

        i = 1   #记录本次请求所返回的页数
        while hasMore and i < 51 and (not isCaught):    #最多返回50页，对每页进行解析，并写入结果文件
            source_url = url + str(i)   #构建某页的URL
            data = ''   #存储该页的网页数据
            goon = True #网络中断标记
            ##网络不好的情况，试着尝试请求三次
            for tryNum in range(maxTryNum):
                try:
                    print source_url
                    html = urllib2.urlopen(source_url, timeout=12)

                    data = html.read()
                    break
                except:
                    if tryNum < (maxTryNum-1):
                        time.sleep(10)
                    else:
                        print 'Internet Connect Error!'
                        self.flag = False
                        goon = False
                        break
            if goon:
                lines = data.splitlines()
                isCaught = True
                for line in lines:
                    ## 判断是否有微博内容，出现这一行，则说明没有被认为是机器人
                    if line.startswith('<script>STK && STK.pageletM && STK.pageletM.view({"pid":"pl_weibo_direct"'):
                        isCaught = False
                        n = line.find('html":"')
                        if n > 0:
                            j = line[n + 7: -12].encode('utf-8').decode('unicode_escape').encode("utf-8").replace("\\", "")
                                 #去掉所有的\
                            ## 没有更多结果页面
                            if (j.find('<div class="search_noresult">') > 0):
                                hasMore = False
                            ## 有结果的页面
                            else:
                                #此处j要decode，因为上面j被encode成utf-8了
                                page = lxml.etree.HTML(j.decode('utf-8'))
                                ps = page.xpath("//p[@node-type='feed_list_content']")   #使用xpath解析得到微博内容
                                addrs = page.xpath("//a[@class='W_texta W_fb']")   #使用xpath解析得到博主地址
                                pulltimes = page.xpath("//div[@class='feed_from W_textb']/a")
                                #print pulltimes
                                addri = 0
                                #获取昵称和微博内容

                                for p in ps:
                                    #print p.attrib
                                    name = (p.attrib.get('nick-name')).strip()    #获取昵称
                                    txt = (str(p.xpath('string(.)'))).strip()          #获取微博内容
                                    addr = addrs[addri].attrib.get('href')
                                    pulltime=pulltimes[addri].attrib.get('title')#获取微博时间
                                    addri += 1
                                    #print name,txt
                                    csvfile=io.open(unicode(key)+".csv", 'a+b')
                                    csvfile.write(codecs.BOM_UTF8)
                                    writer=csv.writer(csvfile,dialect='excel')
                                      #writer.writerow(['作者','内容','时间'])
                                    data = (txt,name,pulltime)
                                    writer.writerow(data)
                                    csvfile.close()
                        break
                lines = None
                ## 处理被认为是机器人的情况
                if isCaught:
                    print 'Be Caught!'
                    data = None
                    self.flag = False
                    break
                ## 没有更多结果，结束该次请求，跳到下一个请求
                if not hasMore:
                    print 'No More Results!'
                    if i == 1:
                        time.sleep(random.randint(3,8))
                    else:
                        time.sleep(10)
                    data = None
                    break
                i += 1
                ## 设置两个邻近URL请求之间的随机休眠时间，防止Be Caught
                sleeptime_one = random.randint(self.interval-25,self.interval-15)
                sleeptime_two = random.randint(self.interval-15,self.interval)
                if i%2 == 0:
                    sleeptime = sleeptime_two
                else:
                    sleeptime = sleeptime_one
                print 'sleeping ' + str(sleeptime) + ' seconds...'
                time.sleep(sleeptime)
            else:
                break

    ##改变搜索的时间范围，有利于获取最多的数据
    def getTimescope(self, perTimescope):
        if not (perTimescope=='-'):
            times_list = perTimescope.split(':')#2017-05-17
            #print int(times_list[-1][0:4]),int(times_list[-1][5:7]),int(times_list[-1][8:10])
            start_date = datetime.datetime(int(times_list[-1][0:4]),  int(times_list[-1][5:7]), int(times_list[-1][8:10]) )
            print start_date
            start_new_date = start_date + timedelta(days = 1)
            start_str = start_new_date.strftime("%Y-%m-%d")
            return start_str + ":" + start_str
        else:
            return '-'
if __name__ == '__main__':
    #定义变量
    username = 'yqr2007@hotmail.com'#'18794816141'             #输入你的用户名
    password = 'yqr82903998.'#'woaini14..'               #输入你的密码
    login(username,password)
    while True:
        ## 接受键盘输入
        key=keyword ="月经洗头会加速患癌"
        #keyword=unicode(keyword)
        startTime = '2010-05-01'
        #region = raw_input('Enter the region([BJ]11:1000,[SH]31:1000,[GZ]44:1,[CD]51:1):')
        interval = '30'

        ##实例化收集类，收集指定关键字和起始时间的微博
        cd = CollectData(keyword, startTime, interval)

        #print cd.timecope
        while cd.flag:
            print cd.timescope
            #cd.timescope = cd.getTimescope(cd.timescope)
            url = cd.getURL()
            cd.download(url)
            cd.timescope = cd.getTimescope(cd.timescope)  #改变搜索的时间，到下一天
        else:
            cd = None
            print '-----------------------------------------------------'
            print '-----------------------------------------------------'
    

    
