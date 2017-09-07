import requests
import random
import gevent.monkey
from gevent.pool import Pool
gevent.monkey.patch_all()

def reg(i):
    try:
        url = 'https://unite.nike.com/join?appVersion=215&experienceVersion=182&uxid=com.nike.commerce.nikedotcom.web&locale=zh_CN&backendEnvironment=default&browser=Google%20Inc.&os=undefined&mobile=false&native=false'

        headers = {
            'Content-Type' : 'text/plain',
            'Referer' : 'http://www.nike.com/cn/zh_cn/',
            'Origin': 'http://www.nike.com',
            'Host':'unite.nike.com',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        payload = {"locale":"zh_CN",
                   "account":{"email":"{}".format(i),
                              "passwordSettings":{"password":"Aa123456","passwordConfirm":"Aa123456"}},
                   "registrationSiteId":"nikedotcom","username":"908104245@qq.com","lastName":"日","firstName":"勘",
                   "dateOfBirth":"1996-12-13","country":"CN","mobileNumber":"13204822070","gender":"male","receiveEmail":True
                   }
        r = requests.post(url, headers=headers ,json=payload)
        print(r.status_code)
        if r.status_code == 400:
            f = open('fail.txt', 'a')
            f.write(i + '\n')
        else:
            f = open('success.txt', 'a')
            f.write(i + '\n' + 'Aa123456')

    except Exception as e:
        f = open('fail.txt','a')
        f.write(i + '\n')

def register():
    f = open('fail.txt', 'w')
    f.close()
    f = open('success.txt', 'w')
    f.close()
    p = Pool(1000)
    f = open('邮箱.txt', 'r')
    # emails = f.read().strip().split('\n')
    emails = list(map(lambda x: x.split('----')[0], f.read().strip().split('\n')))
    for i in emails:
        p.apply_async(reg, args=(i,))
    p.join()
    print('over!')
if __name__ == '__main__':
    register()