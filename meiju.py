#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os, random, queue, requests, threading
from bs4 import BeautifulSoup
from faker import Factory

fake = Factory.create()
main_site = 'http://www.meijutt.com/content/meiju%s.html'

headers = {
	'Connection': 'keep-alive',
	'User-Agent': fake.user_agent()
	}

def fix_character(s):
	for i in ['<', '>', ':', '"', '/', '\\\\', '|', '?', '*']:
		s = s.replace(s, '')
	return s

class MainSpider(threading.Thread):
	def __init__(self, url, vols, queue=None):
		threading.Thread.__init__(self)
		print('[spider]')
		print('=' * 60)
		self.url = url
		self.queue = queue
		self.vol = '1'
		self.vols = vols

	def run(self):
		for vol in self.vols:
			self.spider(vol)
		print('\ncrawl end \n\n')

	def spider(self, vol):
		url = main_site %(vol)
		print('*' * 60)
		print('crawling:' + url)
		print('*' * 60)
		res = requests.get(url, headers=headers)
		if res.status_code == 200:
			soup = BeautifulSoup(res.content, 'html.parser')
			title = soup.find('div', attrs={'class': 'info-title'}).text
			print('title: ' + title)
			cover = soup.img['src']
			s = soup.find('div', attrs={'class': 'o_r_contact'})
			str = s.find_all('li')
			episodes = str[0].text													#全集数
			formerly = str[1].text													#原名
			director = str[4].text													#导演
			main_performer = str[5].text											        #主演
			release_date = str[6].text												#上映日期
			country = str[9].text													#国家
			down_list = soup.find('div', attrs={'class': 'down_list'})				                                #获取下载列表
			episode_names = down_list.find_all('a')									                #获得每集下载链接和名称
			episode_count = len(episode_names)											#获得总的下载链接数
			episode = []
			for str in episode_names:
				_name = fix_character(str.text)
				episode.append({'name:':_name})
			episode_down_list = []
			i = 0				
			while i <episode_count:				
				down_link = episode_names[i]['href']
				episode_down_list.append(down_link)
				i = i + 1

			phases = {
				'phase': vol,								#美剧编号
				'title': title,								#美剧名称
				'cover': cover,								#美剧封面
				'episodes': episodes,                                                   #全集数
				'formerly': formerly,                                                   #原名
				'director': director,                                                   #导演
				'main_performer': main_performer,                                       #主演
				'release_date': release_date,                                           #上映日期
				'country': country,                                                     #国家
				'episode_count': episode_count,                                         #获得总的下载链接数
				'episode': episode,                                                     #获取下载列表
				'episode_down_list': episode_down_list                                  #获得每集下载链接
			}
	
			self.queue.put(phases)

if __name__ == '__main__':
	spider_queue = queue.Queue()
	test = MainSpider(main_site, vols=['1', '20', '40', '77', '88', '100'], queue=spider_queue)
	test.setDaemon(True)
	test.start()
