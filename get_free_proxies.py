import requests
import re
import time
import gevent.pool
import gevent.monkey
from gevent.queue import Queue
gevent.monkey.patch_all()


def validate(proxy, queue):
    # print('开始验证')
    url1 = 'http://www.nike.com/cn/zh_cn/'
    url2 = 'http://store.nike.com/cn/zh_cn/'
    t_proxy = {
        "http": proxy
    }
    try:
        r1 = requests.get(url1, proxies=t_proxy, timeout=1)
        r2 = requests.get(url2, proxies=t_proxy, timeout=1)
        if r1.status_code is 200 and r2.status_code is 200:
            queue.put(proxy)
            print('验证成功')
            return 200
        else:
            print('验证失败')
            return 403
    except Exception as e:
        print(e)
        return 403


def main():
    print('请注意，代理数是固定的，原理是从66ip.cn上获取的ip，它是按时间排序的，所以建议一段时间获取一次，可以同步该网站的更新。')
    num = input('请输入你获取的代理数(建议500-2000)：')
    r = requests.get(
        'http://www.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=http%3A%2F%2Fwww.66ip.cn%2F%3Fsxb%3D%26tqsl%3D10%26ports%255B%255D2%3D%26ktip%3D%26sxa%3D%26radio%3Dradio%26submit%3D%25CC%25E1%2B%2B%25C8%25A1'.format(num))
    r.encoding = 'gb2312'

    result = re.findall(r'\d+[.]\d+[.]\d+[.]\d+[:]\d+', r.text)

    gevent_pool = gevent.pool.Pool(len(result))
    print(len(result))
    queue = Queue()
    for proxy in result:
        gevent_pool.apply_async(validate, (proxy, queue))
    gevent_pool.join()

    useful_proxies = []
    queue.put(StopIteration)
    with open('免费可用.txt', 'w') as f:
        for item in queue:
            useful_proxies.append(item)
            f.write(item + '\n')
    print('通过数量:', len(useful_proxies))
    print('通过率:', str(len(useful_proxies)/len(result)*100) + '%')
    return useful_proxies

if __name__ == '__main__':
    print(main())
