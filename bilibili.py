#/usr/bin/env python3
# -*- coding:utf-8 -*-
import requests, random, faker, json, pymysql, threading, time, threadpool
from multiprocessing import pool

fake = faker.Factory.create()
urls = []
for i in range(200, 1000):
    url = 'https://space.bilibili.com/ajax/member/MyInfo?vmid=' + str(i)
    urls.append(url)

def getsource(url):
    time.sleep(random.randint(0, 3))
    head1 = {'Host': 'space.bilibili.com',
             'User-Agent': fake.user_agent(),
             'Accept': '*/*',
             'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
             'Accept-Encoding': 'gzip, deflate, br',
             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
             'X-Requested-With': 'XMLHttpRequest',
             'Referer': 'https://space.bilibili.com/' + str(random.randint(1, 10000)) + '/',
             'Connection': 'keep-alive'
             }

    head2 = {'Host': 'api.bilibili.com',
             'User-Agent': fake.user_agent(),
             'Accept': '*/*',
             'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
             'Accept-Encoding': 'gzip, deflate, br',
             'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
             'X-Requested-With': 'XMLHttpRequest',
             'Referer': 'https://space.bilibili.com/' + str(random.randint(1, 10000)) + '/',
             'Connection': 'keep-alive'
             }

    proxy = []
    with open('proxy.txt', 'r') as f:
        for line in f:
            proxy.append(line[:-1])
    proxie = {'http': random.choice(proxy)}

    try:
        parameter = {'mid': url.replace('https://space.bilibili.com/ajax/member/MyInfo?vmid=', '')}
        resource = requests.session().post('https://space.bilibili.com/ajax/member/GetInfo', \
                                           headers=head1, data=parameter, proxies=proxie, timeout=10)
        print(url, resource.status_code)
        jsDict = json.loads(resource.text)
    except Exception as e:
        print(e)
        return
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
        try:
            res = requests.get('https://api.bilibili.com/x/relation/stat?vmid=' + \
                               str(mid) + '&jsonp=jsonp', headers=head2, proxies=proxie, timeout=10)
            print(res.status_code)
            jsFans = json.loads(res.text)
            #print("jsFans\n\n")
            #print(jsFans)
            following = jsFans['data']['following']
            follower = jsFans['data']['follower']
        except:
            follower = -1
            follower = -1
    else:
            return

    try:
        #print(int(mid), name, int(approve), sex, face, regtime, birthday, sign, place, description, current_level, following, follower)
        conn = pymysql.connect(
            host='10.19.0.49',
            port=3306,
            user='pytest',
            passwd='@abc5500',
            charset='utf8',
            db='pytest'
        )
        print('Mysql connect success!')
        #conn.select_db('pytest')
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

        insert = "insert into bilibili(mid, name, approve, sex, face, regtime, birthday,sign, place, \
                    description, current_level, following, follower) values('%d', '%s', '%d', '%s', \
                    '%s', '%d', '%s', '%s', '%s', '%s', '%d', '%d', '%d')" %\
                 (int(mid), name, int(approve), sex, face, regtime, birthday, sign, place, description, \
                  current_level, following, follower)
        cur.execute(insert)
        conn.commit()
        print("数据写入成功！")
        conn.close()
    except:
        #conn.rollback()
        #conn.close()
        print('database error')
        return
                               
pool = threadpool.ThreadPool(10)
req = threadpool.makeRequests(getsource, urls)
[pool.putRequest(re) for re in req]
pool.wait()
print("Finished!")