import requests
import time
import gevent.pool
import gevent.monkey
import gevent.queue
gevent.monkey.patch_all()


def ip_delay(index, ip):

    start = time.time()

    if ip is None:
        proxies = None
    else:
        proxies = {
            'http': 'http://' + ip,
        }
    try:
        r = requests.get('http://store.nike.com/cn/zh_cn/', proxies=proxies, timeout=(3, 1))
    except requests.exceptions.ConnectionError:
        return
    except requests.exceptions.ReadTimeout:
        return
    end = time.time()
    delay = '{:.0f}ms'.format((end-start)*1000)
    queue.put([index, delay])

if __name__ == '__main__':
    with open('give.txt', 'r') as f:
        ips = f.read().strip().split('\n')
    pool = gevent.pool.Pool(len(ips))
    queue = gevent.queue.Queue()
    for index, ip in enumerate(ips):
        pool.apply_async(ip_delay, (index, ip))
    pool.join()

    # ip_delay(00, None)
    nums = []
    while True:
        if queue.qsize() > 0:
            task = queue.get()
            print(task)
            nums.append(task[0])
        else:
            break
    nums.sort()
    print(nums)