#!/usr/bin/env python
# -*- coding: utf-8

import os
import urllib
import urllib2
import re

download_path = os.path.dirname(os.path.abspath(__file__))
headers = [('Host','img0.imgtn.bdimg.com'),
('Connection', 'keep-alive'),
('Cache-Control', 'max-age=0'),
('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'),
('Accept-Encoding','gzip,deflate,sdch'),
('Accept-Language', 'zh-CN,zh;q=0.8'),
('If-None-Match', '90101f995236651aa74454922de2ad74'),
('Referer','http://image.baidu.com/i?tn=baiduimage&ps=1&ct=201326592&lm=-1&cl=2&nc=1&word=%E4%BA%A4%E9%80%9A&ie=utf-8'),
('If-Modified-Since', 'Thu, 01 Jan 1970 00:00:00 GMT')]

class spider(object):
    def __init__(self, url):
        self.url = url

    def parse(self, content):
        pattern = 'src="(http://.*\.jpg)\s*"'
        matchs = re.findall(pattern, content, re.M)
        return matchs
    
    def downloads(self, urls):
        d_path = download_path + "/test"
        if not os.path.exists(d_path):
            os.mkdir(d_path)
        
        for url in urls:
            filename = url.split("/")[-1]
            print url
            print "DownLoads %s" % (filename)
            opener = urllib2.build_opener()
            opener.addheaders = headers
            data = opener.open(url)
            try:
                f = open(d_path + "/" + filename, "w")
                f.write(data.read())
            except:
                print "丢失一张图片"
            finally:    
                f.close()

    def run(self):
        d_url = self.url
        fd = urllib.urlopen(d_url)
        
        try:
            content = fd.read()
            urls = self.parse(content)
            self.downloads(urls)
        finally:
            fd.close()

if __name__ == '__main__':
    sp = spider("http://eladies.sina.com.cn/photo/")
    sp.run()
        

