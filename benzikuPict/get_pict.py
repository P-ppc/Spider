#!/usr/bin/env python
#! -*- coding: utf-8

import os
import urllib, urllib2
import re
from sgmllib import SGMLParser

download_path = os.path.dirname(os.path.abspath(__file__))
headers = [('Host','http://www.benziku.cc/shaonv'),
('Connection', 'keep-alive'),
('Cache-Control', 'max-age=0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'),
('Accept-Encoding','gzip,deflate,sdch'),
('Accept-Language', 'zh-CN,zh;q=0.8'),
('If-None-Match', '90101f995236651aa74454922de2ad74'),
('Referer','http://www.benziku.cc/shaonv'),
('If-Modified-Since', 'Thu, 01 Jan 1970 00:00:00 GMT')]

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
        self.urls = []

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
    
    def end_a(self):
        pass
    
    def get_urls(self):
        return self.urls        

class Spider(object):
    def __init__(self, base_url, url_id):
        self.url = base_url + '/' +  url_id + '.html'
        self.url_id = url_id
        self.base_url = base_url
    
    def get_content(self, urls):
        for url in urls:
            fd = urllib.urlopen(url)
            list_page = fd.read()
            fd.close()
            urlParser = UrlParser()
            urlParser.feed(list_page)
            content_urls = urlParser.get_urls()
            for u in content_urls:
                print u
    
    def parse(self, content):
        pattern = r'共(\d+?)页'
        matchs = re.findall(pattern, content)
        urls = []
        urls.append(self.url)
        for index in range(2, int(matchs[0]) + 1):
            url = self.base_url + '/' + self.url_id + '_' + str(index) + '.html'
            urls.append(url)
        
        return urls        

    def downloads(self, urls):
        d_path = download_path + "/test"
        if not os.path.exists(d_path):
            os.mkdir(d_path)

        for url in urls:
            imgParser = ImgParser()
            page = urllib.urlopen(url).read() 
            imgParser.feed(page)
            img_url = myParser.get_url()
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

    def run(self):
        fd = urllib.urlopen(self.url)
        try:
            content = fd.read()
            urls = self.parse(content)
            #self.downloads(urls)
        finally:
            fd.close()    
        


if __name__ == '__main__':
    sp = Spider('http://www.benziku.cc/shaonv', '6048')
    urls = ['http://www.benziku.cc/shaonv']
    for i in range(1, 378):
        url = 'http://www.benziku.cc/zuixin/list_56_%s.html' % str(i)
        urls.append(url)
         
    sp.get_content(urls)
    #sp.run()
    
