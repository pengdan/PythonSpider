#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import requests, random, faker
from bs4 import BeautifulSoup

fake = faker.Factory.create()
head = {
    'Host': 'www.xicidaili.com',
    'User-Agent': fake.user_agent(),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}

url = 'http://www.xicidaili.com/nn/1'
testUrl = 'https://www.baidu.com'
req = requests.get(url, headers=head)
soup = BeautifulSoup(req.content, 'html.parser')
table = soup.find_all('tr')
proxy = []
for i in range(1, len(table)):
    ip = table[i].find_all('td')[1].contents[0]
    port = table[i].find_all('td')[2].contents[0]
    protocol = (table[i].find_all('td')[5].contents[0]).lower()
    ip_temp = protocol + "://" + ip + ":" + port
    #print(ip_temp)
    test = requests.get(testUrl, proxies={"http":ip_temp})
    if test.status_code == 200:
        print(ip_temp)
        proxy.append(ip_temp)
    else:
        continue
print(len(proxy))