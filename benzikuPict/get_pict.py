#!/usr/bin/env python
# -*- coding: utf-8

import os
import urllib, urllib2
import re
import Queue
import threading
from sgmllib import SGMLParser
from datetime import datetime
import time

import profile

download_path = os.path.dirname(os.path.abspath(__file__))
headers = [
            ('Host','http://www.benziku.cc/shaonv'),
            ('Connection', 'keep-alive'),
            ('Cache-Control', 'max-age=0'),
            ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
            ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'),
            ('Accept-Encoding','gzip,deflate'),
            ('Accept-Charset', 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'),
            ('Accept-Language', 'zh-CN,zh;q=0.8'),
            ('If-None-Match', '90101f995236651aa74454922de2ad74'),
            ('Referer','http://www.benziku.cc/shaonv'),
            ('If-Modified-Since', 'Thu, 01 Jan 1970 00:00:00 GMT')
    ]
queue = Queue.Queue()

class ImgParser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.flag = False
        self.url = ''
    
    def start_div(self, attrs):
        for k, v in attrs:
            if k == "class" and v == "m_Box12":
                self.flag = True
                return 
    
    def end_div(self):
        self.flag = False
    
    
    def start_img(self, attrs):
        if self.flag == True:
            for k, v in attrs:
                if k == "src":
                    self.url = v
                    return 
    
    def end_img(self):
        pass 

    def get_url(self):
        return self.url

class UrlParser(SGMLParser):
    def __init__(self):
        SGMLParser.__init__(self)
        self.flag = False
        self.a_flag = False
        self.b_flag = False
        self.urls = []
        self.titles = []

    def start_div(self, attrs):
        for k, v in attrs:
            #if k == 'class' and v == 'm_T2':
            if k == 'class' and v == 'm_Box1':
                self.flag = True
    
    def end_div(self):
        self.flag = False

    def start_a(self, attrs):
        if self.flag == True:
            for k, v in attrs:
                if k == 'href':
                    self.urls.append(v)
                    self.a_flag = True
    
    def end_a(self):
        self.a_flag = False
    
    def start_img(self, attrs):
        if self.a_flag:
            for k, v in attrs:
                if k == 'alt':
                    self.titles.append(v)
            
    def end_img(self):
        pass
    
    def get_urls(self):
        return self.urls, self.titles        

def get_content(urls):
    url_list = []
    for url in urls:
        fd = urllib.urlopen(url)
        list_page = fd.read()
        fd.close()
        urlParser = UrlParser()
        urlParser.feed(list_page)
        content_urls, content_titles = urlParser.get_urls()
        for u in zip(content_urls, content_titles):
            url_list.append(u)
    return url_list
    
class Spider(object):
    def __init__(self, url, title):
        self.url = url
        self.title = title
    
    def parse(self, content):
        url_sp = self.url.split('.html')
        pattern = r'共(\d+?)页'
        matchs = re.findall(pattern, content)
        urls = []
        urls.append(self.url)
        for index in range(2, int(matchs[0]) + 1):
            url = url_sp[0] + '_' + str(index) + '.html'
            urls.append(url)
        
        return urls        

    def downloads(self, urls):
        download_root_path = download_path + "/test"
        if not os.path.exists(download_root_path):
            os.mkdir(download_root_path)
        
        d_path = download_path + "/test/" + self.title
        if not os.path.exists(d_path):
            os.mkdir(d_path)
        
        print self.title + ' : DownLoad start!'
        for url in urls:
            imgParser = ImgParser()
            page = urllib.urlopen(url).read() 
            imgParser.feed(page)
            img_url = imgParser.get_url()
            filename = img_url.split("/")[-1]
            print img_url
            print "DownLoads %s" % (filename)
            opener = urllib2.build_opener()
            opener.addheaders = headers
            data = opener.open(img_url)
            try:
                f = open(d_path + "/" + filename, "w")
                f.write(data.read())
            except:
                print "丢失一张图片"
            finally:
                f.close()
        print self.title + ' : Download over!'

    def run(self):
        fd = urllib.urlopen(self.url)
        try:
            content = fd.read()
            urls = self.parse(content)
            self.downloads(urls)
        finally:
            fd.close()    

class SpiderThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    
    def run(self):
        while True:
            try:
                url_tuple = self.queue.get(True, timeout=10)
                print 'Queue Size : %d' % self.queue.qsize()
                sp = Spider('http://www.benziku.cc' + url_tuple[0], url_tuple[1])
                sp.run()
                self.queue.task_done()
            except:
                print 'Exit!'
                break

def profile_test():
    urls = ['http://www.benziku.cc/shaonv']

    #for i in range(1, 378):
    for i in range(1, 2):
        url = 'http://www.benziku.cc/zuixin/list_56_%s.html' % str(i)
        urls.append(url)

    for i in range(5):
        t = SpiderThread(queue)
        t.setDaemon(True)
        t.start()

    urls_list = get_content(urls)
    for u in urls_list:
        queue.put(u)
    #queue.join()  #采用join不能使用ctrl + c 退出，必须等到队列的任务全部完成才能退出
    while True:
        if queue.qsize() == 0:
            break
        else:
            time.sleep(5)

if __name__ == '__main__':
    print datetime.now()
    profile_test()
    print datetime.now()
