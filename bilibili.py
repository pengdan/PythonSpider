#/usr/bin/env python3
# -*- coding:utf-8 -*-
import requests, random, faker, json, pymysql, threading, time, threadpool
from multiprocessing import pool

fake = faker.Factory.create()
head1 = {'Host': 'space.bilibili.com',
        'User_Agent': fake.user_agent(),
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://space.bilibili.com/' + str(random.randint(1, 10000)) + '/',
        'Connection': 'keep-alive'
        }

head2 = {'Host': 'api.bilibili.com',
        'User_Agent': fake.user_agent(),
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://space.bilibili.com/' + str(random.randint(1, 10000)) + '/',
        'Connection': 'keep-alive'
        }
proxy = {'http': 'http://10.19.0.49:8118/'}
urls = []
for i in range(1, 100):
    url = 'https://space.bilibili.com/ajax/member/MyInfo?vmid=' + str(i)
    urls.append(url)


def getsource(url):
    
   
        parameter = {'mid': url.replace('https://space.bilibili.com/ajax/member/MyInfo?vmid=', '')}
        resource = requests.session().post('https://space.bilibili.com/ajax/member/GetInfo', headers=head1, data=parameter)
            
        jsDict = json.loads(resource.text)
        #print(jsDict)
        if jsDict['status']:
            jsData = jsDict['data']
            #print("jsData\n\n" )
            #print(jsData)
            mid = jsData['mid']
            name = jsData['name']
            approve = jsData['approve']
            sex = jsData['sex']
            face = jsData['face']
            regtime = jsData['regtime'] if 'regtime' in jsData.keys() else 0
            birthday = jsData['birthday'] if 'birthday' in jsData.keys() else None
            sign = jsData['sign'] if 'sign' in jsData.keys() else None
            place = jsData['place'] if 'place' in jsData.keys() else None
            description = jsData['description'] if 'description' in jsData.keys() else None
            current_level = jsData['level_info']['current_level']                
            res = requests.get('https://api.bilibili.com/x/relation/stat?vmid='+ str(mid) + '&jsonp=jsonp', headers=head2)
            jsFans = json.loads(res.text)
            #print("jsFans\n\n")
            #print(jsFans)
            following = jsFans['data']['following']
            follower = jsFans['data']['follower']
                
        else:
                exit                
        try:
            #print(int(mid), name, int(approve), sex, face, regtime, birthday, sign, place, description, current_level, following, follower)
            conn = pymysql.connect(
                host='192.168.123.44',
                user='pytest',
                passwd='@abc5500',
                charset='utf8'
            )
            print('Mysql connect success!')
            conn.select_db('pytest')
            cur = conn.cursor()
            cur.execute('create database IF NOT EXISTS pytest default charset utf8 collate utf8_general_ci')                
            cur.execute("CREATE TABLE IF NOT EXISTS `bilibili` ( \
                                                    `id` int(10) unsigned NOT NULL AUTO_INCREMENT,\
                                                    `mid` int(10) unsigned NOT NULL,\
                                                    `name` varchar(255) DEFAULT NULL,\
                                                    `approve` tinyint(1) DEFAULT NULL,\
                                                    `sex` varchar(10) DEFAULT NULL,\
                                                    `face` varchar(255) DEFAULT NULL,\
                                                    `regtime` int(11) unsigned DEFAULT NULL,\
                                                    `birthday` varchar(255) DEFAULT NULL,\
                                                    `sign` varchar(255) DEFAULT NULL,\
                                                    `place` varchar(255) DEFAULT NULL,\
                                                    `description` varchar(255) DEFAULT NULL,\
                                                    `current_level` int(4) unsigned DEFAULT NULL,\
                                                    `following` int(10) DEFAULT NULL,\
                                                    `follower` int(10) DEFAULT NULL,\
                                                    PRIMARY KEY (`id`),\
                                                    UNIQUE KEY `mid` (`mid`) USING BTREE\
                                                ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 \
                        ")
            insert = "insert into bilibili(mid, name, approve, sex, face, regtime, birthday, sign, place, description, current_level, following, follower)\
                                            values('%d', '%s', '%d', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%d', '%d', '%d')" % \
                                            (int(mid), name, int(approve), sex, face, regtime, birthday, sign, place, description, current_level, following, follower)
            print(insert)
            cur.execute(insert)
            conn.commit()
            print("数据写入成功！")
            conn.close()
        except:
            conn.rollback()
            conn.close()
            print('database error')
                               
pool = threadpool.ThreadPool(10)
req = threadpool.makeRequests(getsource, urls)
[pool.putRequest(re) for re in req]
pool.wait()
print("Finished!")