#!/usr/bin/python
from __future__ import print_function
import os, sys
import time 
import shutil
import urllib
import urllib2
from Queue import Queue
import threading
from lxml import etree

print = lambda x: sys.stdout.write("%s\n" % x)
queue = Queue()

THREADS_COUNT = 10
SITE = 'http://www.inmyroom.ru'
cookievalue = 'comments_view_token=0ef719421a90f6bfe930806a25cc8f73; __utma=268774953.159504125.1422995349.1423251330.1423251330.1; __utmc=268774953; __utmz=268774953.1423251330.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _gat_UA-26535798-1=1; _dc_gtm_UA-26535798-1=1; _ym_visorc_10521778=b; _ga=GA1.2.159504125.1422995349; the_comment_cookies=JustTheCommentsCookies; _marvin_project_session=b1hMcVN3M0Z1TXhHUU45RzlEUUFkUlFnUmVGcHNCL1oybkppSzkrUm0rWEQ3bEYvQm5RR0x6Ri9rQjdIVk9ickthbkZUMGZJSGRNMjdxdUNvcjVob1lnZk5QSVI2TFlLZ0p4YTd0dHJyTnNDMUJBazBwSG5ucEQxbEhBSk9YTjNYcEw3QW53OHVmanZqODY0MjJnRE9uTHNZaEhhK3BuN2hsRVhkWlhWN0t2NnRYUjhqK0R4NWo1S1pJUmM0bWQ2VXRJTXZyMDYycXJyMnVGeXRkSUhYUHdhR1ZBRTJRcXNVUm1aT0dTN2Q5R3dFNjRYcmZ2d1VBd1RyN0ZVdy9HY0I4L2pNYmNoS0gzdHF5dTNTSWZRTWNNcWhTQXllRmE5UnRsOEJKb0VkcEJVRDFkWnJXdVNpeGRQdzd0eDZyUnlWRXg1NGQyaGZFc0NvbE8rMVZ3QkZMTnNFRUR5WG1FRC9ib2l0MnZlVit1NTlyTm5KUk5vZXBmNFZGOEFXckN0Z1l6ZGN0QjF3a3dvdGZrMThhaEdGRmtmUjlTa3dQUndqSVBqVVBrbER6QUVKQzUrempYK2xXcUdpamFuVDBCQWNGc0ZUb0Q3U2dsTUoyNnVGSGxSTUE9PS0tVndkWDFXZXFxUDRqWWZwQ3hMVUViZz09--f16933a228370fb4f2ff0203dbedf7098e02f1d9'

opener = urllib2.build_opener()
opener.addheaders.append(('Cookie', 'cookiename=' + cookievalue))

def getPageTree(url):
	page = opener.open(url).read()
	return etree.HTML(page)

def getPageCount(link):
	tree = getPageTree(link)
	r = tree.xpath('.//*[@class="pagination"]/span/a')
	return r[len(r) - 1].text

def getPageList():
	tree = getPageTree(SITE + '/photos')
	r = tree.xpath('.//*[@class="page-index-aside"]//*[@data-role="filter-section"][1]/ul/li')
	links = []
	for x in r:
		elem = x.xpath('./a')[0]
		link = SITE + elem.attrib['href']
		name = elem.text
		links.append({
			'link' : link, 
			'name' : name,
			'pages': int(getPageCount(link))})
	return links

def getPreviewList(url):
	tree = getPageTree(url)
	r = tree.xpath('.//div[@class="photo"]/div[@class="photo-pic photo-pic-square"]/a')
	links = []
	for i in range(1, len(r)):
		links.append(SITE + r[i].attrib['href'])
	return links

def getImgLink(url):
	tree = getPageTree(url)
	r = tree.xpath('.//div[@class="photo-show-pic is-loading"]/div/div/img')
	return r[0].attrib['data-src']

def downloadImgs(folder):
	print('start download')

	print('clear folder')
	if os.path.exists(folder):
		shutil.rmtree(folder)
	os.makedirs(folder)
	
	print('load pages ...')
	pl = getPageList()
	print('pages loaded')
	for p in pl:
		print('"' + p['name'] + '" ' + str(p['pages']))
	
	print('start downloading images')

	folderCount = 0
	for i in range(3, 4):
		folderPath = folder + str(folderCount) + '. ' + pl[i]['name']
		os.makedirs(folderPath)
		folderCount = folderCount + 1
		name = 1

		for j in range(1, pl[i]['pages']):
			pageUrl = pl[i]['link'] + '/page/' + str(j)
			arr = [pageUrl, folderPath + '/', name]
			queue.put(arr)
			name = name + 20

	print('images downloaded :)')

def worker():
	while True:
		try:
			arg = queue.get()
			pageUrl = arg[0]
			folderPath = arg[1]
			name = arg[2]

			i = 0
			imgPageList = getPreviewList(pageUrl)
			for ip in imgPageList:
				imgLink = getImgLink(ip)
				k = imgLink.rfind(".")
				ext = imgLink[k:]
				urllib.urlretrieve(imgLink, folderPath + str(name + i) + ext)
				i = i + 1
		except Exception, error:
			print(error)

downloadImgs('/home/diego/inmyroom/')

#f = file('list.txt', 'w')
#f.open()
#for item in getPageList():
#  f.write("%s\n" % item)
#f.close()

for j in xrange(THREADS_COUNT):
	thread_ = threading.Thread(target=worker)
	thread_.start()

while threading.active_count() > 1:
    time.sleep(1)

	