import requests
from bs4 import BeautifulSoup
from PyQt4 import QtCore
# from multiprocessing import cpu_count
# from multiprocessing import Pool
from gevent import monkey
import gevent.pool
import gevent
import signal
import random
import time
import logging
import re
import json
import copy
import get_product_info
monkey.patch_all()


class NikeTerminator(QtCore.QThread):
    trigger = QtCore.pyqtSignal(list)

    def __init__(self):
        super(NikeTerminator, self).__init__()

        # 进程数量取决于cpu核的个数
        # self.process_number = cpu_count()
        # self.process_pool = self.init_process()
        self._accounts = None
        self._sizes = None
        self._proxies = None
        self._product_url = None
        self._on_sale_sizes = None
        self._payloads = None

        # quit flag
        self.quit = 0
        # monitor flag
        self.monitor = 0

        self.__sessions = None
        self.__user_ids = None

        self.__buy_status = None

        # 初始化监控、重试、排队间隔
        self.monitor_interval = 1.3
        self.retry_interval = 1.3
        self.queue_interval = 4

        # 加入日志
        self.logger_terminator = None
        # 成功日志
        self.logger_success = None
    @property
    def accounts(self):
        return self._accounts

    @accounts.setter
    def accounts(self, t_accounts):
        if self._accounts is None:
            self._accounts = t_accounts
        else:
            pass
            # raise ValueError('请不要重复添加账号')

    @property
    def proxies(self):
        return self._proxies

    @proxies.setter
    def proxies(self, t_proxies):
        proxies = []
        for proxy in t_proxies:
            if proxy is None:
                proxies.append(None)
            else:
                if len(proxy) == 1:
                    format_proxy = 'http://' + proxy[0]
                    proxies.append({
                        'http': format_proxy,
                        'https': format_proxy
                    })
                elif len(proxy) == 3:
                    format_proxy = 'http://{}:{}@{}'.format(proxy[1], proxy[2], proxy[0])
                    proxies.append({
                        'http': format_proxy,
                        'https': format_proxy
                    })

        self._proxies = proxies

    @property
    def product_url(self):
        return self._product_url

    @product_url.setter
    def product_url(self, t_product_urls):
            self._product_url = t_product_urls

    @property
    def sizes(self):
        return self._sizes

    @sizes.setter
    def sizes(self, t_sizes):
            self._sizes = t_sizes

    @property
    def on_sale_sizes(self):
        return self._on_sale_sizes

    @on_sale_sizes.setter
    def on_sale_sizes(self, t_on_sale_sizes):
            self._on_sale_sizes = t_on_sale_sizes


    @property
    def payloads(self):
        return self._payloads

    @payloads.setter
    def payloads(self, t_payloads):
            self._payloads = t_payloads
            print(self._payloads)


    def get_session_by_account_id(self, account_id):
        return self.__sessions[account_id]

    def init_process(self):
        pass
        # pool = Pool(self.process_number)
        # return pool

    def run_process(self):
        pass

    def run_gevent(self):
        # 程序如果意外退出，协程部分不会被kill掉，需要下面这一行代码来关联信号量
        # gevent.signal(signal.SIGQUIT, gevent.shutdown)
        # 构建一个和账号数量相同的协程池
        coroutine_pool = gevent.pool.Pool(len(self._accounts))
        self.__sessions = [requests.session() for _ in range(len(self.accounts))]
        self.__user_ids = [None for _ in range(len(self.accounts))]
        self.__buy_status = [0 for _ in range(len(self.accounts))]
        
        # 传入账号的序号和账号
        for account_id, account in enumerate(self._accounts):
            coroutine_pool.apply_async(self.do, (account_id, account, self.sizes[account_id], self.proxies[account_id]))
        coroutine_pool.join()

    def do(self, account_id, account, default_size, proxy):
        # 得到账号所对应的session
        s = self.__sessions[account_id]
        status = '初始化中'
        self.trigger.emit([account_id, status])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
        }
        r = s.get('http://www.nike.com/cn/zh_cn/', headers=headers, proxies=proxy)
        # print(r.text)

        s.cookies.update({'CONSUMERCHOICE': 'cn/zh_cn'})
        s.cookies.update({'guidU': '', 'guidS': ''})

        status = '正在登录'
        self.trigger.emit([account_id, status])
        login = self.login(account_id, account, proxy, s)
        while not login:
            if self.quit:
                status = '退出成功'
                self.trigger.emit([account_id, status])
                return
            status = '登陆失败，重试中'
            self.trigger.emit([account_id, status])
            login = self.login(account_id, account, proxy, s)
            # gevent.sleep(0)
        status = '登录成功'
        self.trigger.emit([account_id, status])
        s.cookies.update({'CONSUMERCHOICE': 'cn/zh_cn'})
        s.cookies.update({'guidU': '', 'guidS': ''})

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        url_update = """https://secure-store.nike.com/ap/services/jcartService?callback=jQuery172022823510079993148_1490416228448&action=getCartSummary&rt=json&country=CN&lang_locale=zh_CN&_=1490416246994"""
        r = s.get(url_update, headers=headers, proxies=proxy)
        print(r.headers)
        print(r.text)
        print('初始化完成')
        status = '初始化完成'
        self.trigger.emit([account_id, status])

        # 等待购物车加入状态
        while 1:
            if self.quit:
                status = '退出成功'
                self.trigger.emit([account_id, status])
                return
            if self.__buy_status[account_id]:
                status = '加车成功，任务完成'
                self.trigger.emit([account_id, status])
                break

            if self.monitor:
                try:
                    self.add_to_cart(account_id, default_size, proxy, self.on_sale_sizes, self.payloads, s)
                except Exception as e:
                    ###
                    self.logger_terminator.debug('206行' + str(e))
                    ###
                    status = '还在锁定中'
                    self.trigger.emit([account_id, status])
                    gevent.sleep(self.monitor_interval)

            gevent.sleep(0)

    def add_to_cart(self, account_id, default_size, proxy, on_sale_sizes, payloads, s):
        if default_size is not None:
            # dafault_size是字符串
            default_size_list = default_size.split(',')
            default_size_list = list(set(on_sale_sizes).intersection(set(default_size_list)))
            if default_size_list == []:
                default_size_list = on_sale_sizes[:]
        else:
            default_size_list = on_sale_sizes[:]
        # print(default_size_list)
        # 设置加车需要的payload
        choose_size = random.choice(default_size_list)
        # print('选择尺码', choose_size)
        add_to_cart_payload = payloads[choose_size]
        default_size_list.remove(choose_size)

        # http://hkh:hkh@43.242.159.2:808
        # 58.218.16.149:808:hkh:hkh



        headers = {
            'Referer': 'http://store.nike.com/cn/zh_cn/pd/'
                       'lunarepic-low-flyknit-%E7%94%B7%E5%AD%90%E8%B7%91%E6%AD%A5%E9%9E%8B/pid-11055902/pgid-11493501',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Host': 'secure-store.nike.com',
        }

        s.cookies.update({'guidU': '', 'guidS': ''})
        get_url = 'https://secure-store.nike.com/ap/services/jcartService'
        # 成功 flag
        success = 0
        # 等待 flag
        wait = 0

        # 预编译检查返回状态的正则：
        pattern_status = re.compile(r'success|waitSoldOut|waitOutOfStock|wait')  # 状态正则
        pattern_pilpsh = re.compile(r'"pil" :"(\d+)","psh" :"(.+?)"')  # 排队正则
        pattern_errorcode = re.compile(r'noItemsToAddInStock|ProductLimitExeeded|ServiceException')

        wait_add_to_cart_payload = None
        try:
            status = '准备抢购'
            self.trigger.emit([account_id, status])
            while not success:
                if self.quit:
                    status = '退出成功'
                    self.trigger.emit([account_id, status])
                    return
                if not self.monitor:
                    status = '取消监控'
                    self.trigger.emit([account_id, status])
                    return
                r = s.get(get_url, params=add_to_cart_payload, headers=headers, proxies=proxy)
                if r.status_code != 200:
                    # print(r.headers)
                    status = str(r.status_code) + '错误'
                    self.trigger.emit([account_id, status])
                    ###
                    self.logger_terminator.debug('264行：账号' + str(account_id + 1) + '``' + str(r.status_code) + '``')
                    ###
                else:
                    self.logger_terminator.debug(
                        '264行：账号' + str(account_id + 1) + '``' + str(r.status_code) + '``' + '正常')
                # print(r.headers)
                # print('一开始:', r.text)
                match = pattern_status.search(r.text)
                match_errorcode = pattern_errorcode.search(r.text)
                # print(match)
                if match or match_errorcode:
                    if match:
                        match_status = match.group()
                        # print(match_status)
                        if match_status == 'wait' or match_status == 'waitOutOfStock':
                            status_wait = pattern_pilpsh.search(r.text)
                            status = '开始排队'
                            print('开始排队')
                            # logger_mo.debug(self.account[0] + status)
                            self.trigger.emit([account_id, status])
                            if status_wait:
                                status = '排队号:' + status_wait.group(1)
                                # logger_mo.debug(self.account[0]+status)
                                self.trigger.emit([account_id, status])
                                wait_add_to_cart_payload = copy.deepcopy(add_to_cart_payload)
                                wait_add_to_cart_payload['pil'] = status_wait.group(1)
                                wait_add_to_cart_payload['psh'] = status_wait.group(2)
                                wait = 1
                                # mail.mail('进入排队')
                                ###
                                self.logger_terminator.debug('账号' + str(account_id + 1) + '排队号:' + wait_add_to_cart_payload['pil'])
                                ###
                                break
                        elif match_status == 'success':
                            # mail.mail('加车成功')
                            status = '加入购物车成功'
                            ###
                            self.logger_terminator.debug('账号' + str(account_id+1) + '加入购物车成功')
                            ###
                            ###
                            self.logger_success.info('账号' + self.accounts[account_id][0] + '加入购物车成功')
                            ###
                            self.trigger.emit([account_id, status])
                            self.__buy_status[account_id] = 1
                            print('加入购物车成功')
                            return
                            # print('加车完cookies', s.cookies)

                        elif match_status == 'waitSoldOut':
                            status = '商品暂时售罄,智能换码'
                            # print(match_status, status)
                            self.trigger.emit([account_id, status])
                            if default_size_list != []:
                                choose_size = random.choice(default_size_list)
                                # 智能选码
                                # print('随机选码：', choose_size)
                                add_to_cart_payload = payloads[choose_size]
                                default_size_list.remove(choose_size)
                            else:
                                status = '所有码数已经尝试,开始随机选码'
                                self.trigger.emit([account_id, status])
                                default_size_list = on_sale_sizes[:]
                                choose_size = random.choice(default_size_list)
                                add_to_cart_payload = payloads[choose_size]
                    # print(r.status_code, r.text)

                    if match_errorcode:
                        match_errorcode_status = match_errorcode.group()
                        if match_errorcode_status == 'ProductLimitExeeded':
                            status = '购物车已有，请速去付款'
                            self.trigger.emit([account_id, status])
                            self.monitor = 0
                            return
                        # 归类进400的情况，不做考虑
                        # elif match_errorcode_status == 'ServiceException':
                        #     status = '服务异常'
                        #     self.trigger.emit([account_id, status])
                        #     print(match_errorcode_status, status)
                        elif match_errorcode_status == 'noItemsToAddInStock':
                            status = '商品暂时售罄,智能换码'
                            print(match_errorcode_status, status)
                            self.trigger.emit([account_id, status])
                            if default_size_list != []:
                                choose_size = random.choice(default_size_list)
                                # 智能选码
                                # print('随机选码：', choose_size)
                                add_to_cart_payload = payloads[choose_size]
                                default_size_list.remove(choose_size)
                            else:
                                status = '所有码数已经尝试,开始随机选码'
                                self.trigger.emit([account_id, status])
                                default_size_list = on_sale_sizes[:]
                                choose_size = random.choice(default_size_list)
                                add_to_cart_payload = payloads[choose_size]
                elif r.text.startswith('&lt;html&gt;&lt;body&gt;TIME OUT&lt;br&gt;'):
                    status = '悲剧，ip被禁止'
                    self.trigger.emit([account_id, status])
                    break
                else:
                    self.logger_terminator.debug(
                        '376行：账号' + str(account_id + 1) + '``' + str(r.status_code) + '``' + r.text)
                gevent.sleep(self.retry_interval)

            # 进入排队阶段：
            while wait:
                if self.quit:
                    status = '退出成功'
                    self.trigger.emit([account_id, status])
                    return
                if not self.monitor:
                    status = '取消监控'
                    self.trigger.emit([account_id, status])
                    return
                print(str(account_id+1) + '排队中...')
                gevent.sleep(self.queue_interval)
                r = s.get(get_url, params=wait_add_to_cart_payload, headers=headers, proxies=proxy)
                # print('排队:', r.text)
                match = pattern_status.search(r.text)
                if match:
                    match_status = match.group()
                    if match_status == 'wait':
                        status = '仍在排队中，请等待'
                        # logger_mo.debug(self.account[0] + status)
                        self.trigger.emit([account_id, status])

                    elif match_status == 'success':
                        # mail.mail('成功抢到')
                        status = '恭喜抢购成功'
                        ###
                        self.logger_terminator.debug('账号' + str(account_id + 1) + '加入购物车成功')
                        ###
                        ###
                        self.logger_success.info('账号' + self.accounts[account_id][0] + '加入购物车成功')
                        ###
                        self.trigger.emit([account_id, status])
                        self.__buy_status[account_id] = 1
                        return
                    elif match_status == 'waitSoldOut':
                        status = '商品暂时售罄,智能换码'
                        print(match_status, status)
                        self.trigger.emit([account_id, status])
                        if default_size_list != []:
                            choose_size = random.choice(default_size_list)
                            # 智能选码
                            print('随机选码：', choose_size)
                            add_to_cart_payload = payloads[choose_size]
                            default_size_list.remove(choose_size)
                        else:
                            status = '所有码数已经尝试,开始随机选码'
                            self.trigger.emit([account_id, status])
                            default_size_list = on_sale_sizes[:]
                            choose_size = random.choice(default_size_list)
                            add_to_cart_payload = payloads[choose_size]
                        wait = 0
                        break
                else:
                    # print('排队过程中出错')
                    ###
                    self.logger_terminator.debug('395行：账号' + str(account_id + 1) + '排队过程中出错')
                    ###
                        # gevent.sleep(self.retry_interval)

        except Exception as ex:
            # print('异常退出', ex)
            status = '异常退出'
            ###
            self.logger_terminator.debug('437行：账号' + str(account_id + 1) + '异常情况' + str(ex))
            ###
            self.trigger.emit([account_id, status])


    def check_cart(self, s, proxy):
        '''
        获取能打开购物车的一些必要信息
        :param account_id:
        :param s:
        :return:
        '''
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        url_update = """https://secure-store.nike.com/ap/services/jcartService?callback=jQuery172022823510079993148_1490416228448&action=getCartSummary&rt=json&country=CN&lang_locale=zh_CN&_=1490416246994"""
        s.get(url_update, headers=headers, proxies=proxy)
        print('购物车更新完成')

    def delete_cart(self, account_id, s):
        pass

    def pay_cart(self, account_id):
        confirm_headers = {
            'Referer': 'https://secure-store.nike.com/cn/checkout/html/review.jsp?',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',

        }
        confirm_url = 'https://secure-store.nike.com/cn/checkout/html/confirm.jsp?'
        r = self.__sessions[account_id].get(confirm_url, headers=confirm_headers)

        # qt浏览器打开扫码界面

    def login(self, account_id, account, proxy, s):
        # 登录地址
        url_login = 'https://unite.nike.com/loginWithSetCookie?appVersion=235&experienceVersion=201&uxid=com.nike.commerce.nikedotcom.web&locale=zh_CN&backendEnvironment=default&browser=Google%20Inc.&os=undefined&mobile=false&native=false&visit=1&visitor=cd14a83a-daf5-47ee-a78c-9bfa29ce4264'

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'test.txt/plain',
            'Cookie': '',
            'Host': 'unite.nike.com',
            'Origin': 'http://www.nike.com',
            'Referer': 'http://www.nike.com/cn/zh_cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        print(account)
        payload = {
            "username": account[0],
            "password": account[1],
            "keepMeLoggedIn": True,
            "client_id": "HlHa2Cje3ctlaOqnxvgZXNaAs7T9nAuH",
            "ux_id": "com.nike.commerce.nikedotcom.web",
            "grant_type": "password"
        }

        try:
            r = s.post(url_login, json=payload, headers=headers, proxies=proxy, timeout=5)

            # 获取user_id
            text_json = json.loads(r.text)
            nike_user_id = text_json['user_id']
            self.__user_ids[account_id] = nike_user_id

            if r.status_code == 200:
                status = '登录成功'
                self.trigger.emit([account_id, status])
                # print(s.cookies)
                return 1
            else:
                status = 'IP被封，请换个ip'
                self.trigger.emit([account_id, status])
                # self.monitor = 0
                return 0

        except Exception as e:
            print(e)
            return 0
            # status = '登录超时'
            # self.trigger.emit([account_id, status])

    def alter_address(self, payload):
        coroutine_pool = gevent.pool.Pool()
        for account_id in range(len(self._accounts)):
            coroutine_pool.apply_async(self.alter_address_by_session,
                                       (account_id, self.__sessions[account_id], self.__user_ids[account_id], payload, self.proxies[account_id]))
        coroutine_pool.join()

    def alter_address_by_session(self, account_id, s, user_id, payload, proxies):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        r = s.post('https://www.nike.com/profile/services/users/{}/addresses'.format(user_id), headers=headers,
                   json=payload, proxies=proxies)
        status = '修改成功'
        self.trigger.emit([account_id, status])

    def run(self):
        self.run_gevent()


if __name__ == '__main__':
    # with open('账号.txt', 'r') as f:
    #     accounts = f.read().strip().split('\n')
    #
    # instance = NikeTerminator()
    # instance.accounts = accounts
    # print(accounts)
    # instance.run_gevent()
    account = ['nkzhuanyong187@sina.com', 'Aa123456']
    # nike_one_account_test(account)
    account2 = ['nkzhuanyong199@sina.com', 'Aa123456']
    # nike_one_account_test(account2)
