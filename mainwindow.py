# coding=utf-8
import sys
import os
# import multiprocessing
import timeit
import logging
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
import requests
from gevent import monkey
import gevent.pool
import gevent.queue
import gevent
import signal
import random
import time
import re
import json
import get_product_info
from nike_terminator import NikeTerminator
monkey.patch_all()
# import mail
# import importlib,sys
# importlib.reload(sys)
# sys.setdefaultencoding('gbk')


__version__ = 0.1
__author__ = 'nika15@student.bth.se'


class NikeWidget(QtGui.QWidget):
    def __init__(self):
        super(NikeWidget, self).__init__()
        # 阻塞除了当前窗口以外的窗口

        self.setWindowIcon(QtGui.QIcon('./icon/nike.png'))


class NikeMainWindow(NikeWidget):
    def __init__(self):
        super(NikeMainWindow, self).__init__()
        """
        打印日志设置
        """
        log_file = "./耐克终结者日志.txt"
        log_level = logging.DEBUG
        self.logger_terminator = logging.getLogger("耐克终结者")
        handler = NikeFileHandler(log_file)
        formatter = logging.Formatter("[%(asctime)s]%(message)s")
        handler.setFormatter(formatter)
        self.logger_terminator.addHandler(handler)
        self.logger_terminator.setLevel(log_level)

        """
        成功日志
        """
        log_file = "./成功记录.txt"
        log_level = logging.DEBUG
        self.logger_success = logging.getLogger("成功记录")
        handler = NikeSuccessFileHandler(log_file)
        formatter = logging.Formatter("[%(asctime)s]%(message)s")
        handler.setFormatter(formatter)
        self.logger_success.addHandler(handler)
        self.logger_success.setLevel(log_level)


        self.setWindowTitle('耐克终结者')
        self.setWindowIcon(QtGui.QIcon('./icon/nike.png'))
        self.setGeometry(200, 200, 580, 500)
        self.setFixedSize(580, 500)

        self.button_login = QtGui.QPushButton('自动登录', self)
        self.button_login.setGeometry(30, 30, 60, 30)
        self.button_login.clicked.connect(self.log_in)
        # self.button_login.setStyleSheet("QPushButton {color:white;background-color: rgb(22,94,80);}")

        self.button_logout = QtGui.QPushButton('全部退出', self)
        self.button_logout.setGeometry(100, 30, 60, 30)
        self.button_logout.clicked.connect(self.log_out)
        self.button_logout.setEnabled(False)
        # self.button_logout.setStyleSheet("QPushButton {color:white;background-color: rgb(22,94,80);}")

        self.button_add_account = QtGui.QPushButton('添加账号', self)
        self.button_add_account.setGeometry(170, 30, 60, 30)
        self.button_add_account.clicked.connect(self.open_add_account)
        # button_addUser.setStyleSheet("QPushButton {color:white;background-color: rgb(22,94,80);}")

        self.button_alter_address = QtGui.QPushButton('修改地址', self)
        self.button_alter_address.setGeometry(240, 30, 60, 30)
        self.button_alter_address.clicked.connect(self.open_alter_address)
        # button_alter_address.setStyleSheet("QPushButton {color:white;background-color: rgb(22,94,80);}")

        button_proxy = QtGui.QPushButton('代理池', self)
        button_proxy.setGeometry(310, 30, 60, 30)
        button_proxy.clicked.connect(self.open_proxies_pool)
        # button_proxy.setStyleSheet("QPushButton {color:white;background-color: rgb(22,94,80);}")

        button_time = QtGui.QPushButton('定时', self)
        button_time.setGeometry(380, 30, 60, 30)
        # button_time.setStyleSheet("QPushButton {color:white;background-color: rgb(22,94,80);}")
        button_time.clicked.connect(self.open_timing)

        button_set = QtGui.QPushButton('成功记录', self)
        # button_set = QtGui.QPushButton('可选设置', self)
        button_set.setGeometry(450, 30, 60, 30)
        button_set.clicked.connect(self.logger_success.handlers[0].widget.show)
        # button_set.setStyleSheet("QPushButton {color:white;background-color: rgb(22,94,80);}")
        # button_set.clicked.connect(self.open_setting)

        self.table = NikeAccountTableWidget(0, 5, self)
        self.table.renameAction.triggered.connect(lambda: self.renameSlot(self.table.currentRow()))
        self.table.setSelectionBehavior(QtGui.QTableView.SelectRows)

        # self.table.setStyleSheet(
        # "QTableWidget { background-color: rgb(200, 255,255); border:5px solid rgb(90, 209, 203);}")
        self.table.setGeometry(30, 100, 300, 400)
        # self.table.verticalHeader().setVisible(False)
        self.table.setColumnWidth(0, 180)
        self.table.setColumnWidth(1, 60)
        self.table.setColumnWidth(2, 40)
        self.table.setColumnWidth(3, 100)
        self.table.setColumnWidth(4, 140)
        self.table.setFixedSize(520, 200)
        self.table.setHorizontalHeaderLabels(['账号', '密码', '尺码', '状态', '当前代理'])

        label_monitor_url = QtGui.QLabel("监控链接：", self)
        label_monitor_url.setGeometry(30, 350, 60, 30)

        self.text_url = QtGui.QLineEdit(self)
        self.text_url.setGeometry(92, 355, 360, 20)

        self.button_monitor = QtGui.QPushButton('开启监控', self)
        self.button_monitor.setGeometry(480, 350, 100, 80)
        self.button_monitor.clicked.connect(self.open_monitor)
        self.open_monitor_lock = 1
        # button_monitor.setStyleSheet(" QPushButton {background-color: red;} ")

        label_monitor_interval = QtGui.QLabel('监控间隔(秒)', self)
        # label_monitor_interval.setStyleSheet('QLabel {font-weight: bold;font-size: 12px;}')
        label_monitor_interval.setGeometry(30, 450, 80, 30)

        self.text_monitor_interval = QtGui.QLineEdit('自动', self)
        self.text_monitor_interval.setGeometry(115, 450, 30, 30)

        label_retry_interval = QtGui.QLabel('重试间隔(秒)', self)
        # label_retry_interval.setStyleSheet('QLabel {font-weight: bold;font-size: 12px;}')
        label_retry_interval.setGeometry(210, 450, 80, 30)

        self.text_retry_interval = QtGui.QLineEdit('自动', self)
        self.text_retry_interval.setGeometry(295, 450, 30, 30)

        label_queue_interval = QtGui.QLabel('排队间隔(秒)', self)
        # label_queue_interval.setStyleSheet('QLabel {font-weight: bold;font-size: 12px;}')
        label_queue_interval.setGeometry(390, 450, 80, 30)

        self.text_queue_interval = QtGui.QLineEdit('自动', self)
        self.text_queue_interval.setGeometry(475, 450, 30, 30)

        self.accounts = []
        self.proxies = []
        self.sizes = []
        # 读取 账号,ip,链接,客户自定义功能的配置
        self.initial_config()

        self.nike_thread = NikeTerminator()
        self.add_account_instance = None
        self.setting_instance = None
        self.alter_instance = None
        self.alter_address_instance = None
        self.proxies_pool_instance = None
        self.timing_instance = None
        self.timer = None

    def initial_config(self):
        # 账号初始化部分
        if not os.path.exists('账号.txt'):
            f = open('账号.txt', 'w')
            f.close()
        else:
            with open('账号.txt', 'r') as f:
                row = 0
                while 1:
                    line = f.readline().strip()
                    if not line:
                        break
                    self.table.insertRow(self.table.rowCount())
                    content = re.split(' |,', line.strip())
                    for col, con in enumerate(content):
                        new_item = QtGui.QTableWidgetItem(con)
                        self.table.setItem(row, col, new_item)
                    row += 1
        if not os.path.exists('链接.txt'):
            f = open('链接.txt', 'w')
            f.close()
        # 链接初始化
        with open('链接.txt', 'r') as f:
            self.text_url.setText(f.read())
        if not os.path.exists('ip.txt'):
            f = open('ip.txt', 'w')
            f.close()
        # 代理初始化
        with open('ip.txt', 'r') as f:
            while 1:
                line = f.readline().strip()
                if not line:
                    break
                t = re.split(',| ', line)
                self.proxies.append(t)

    def log_in(self):
        ###
        self.logger_terminator.debug('开始登录')
        ###
        self.button_login.setEnabled(False)
        proxies_num = len(self.proxies)

        if proxies_num >= self.table.rowCount():
            self.nike_thread.proxies = self.proxies[:self.table.rowCount()]
            # 将代理添加至表格中
            for i in range(self.table.rowCount()):
                new_item = QtGui.QTableWidgetItem(self.proxies[i][0])
                self.table.setItem(i, 4, new_item)
        elif proxies_num == self.table.rowCount() - 1:
            t_proxies = self.proxies[:]
            t_proxies.append(None)
            self.nike_thread.proxies = t_proxies
            # 将代理添加至表格中
            for i in range(self.table.rowCount()-1):
                new_item = QtGui.QTableWidgetItem(self.proxies[i][0])
                self.table.setItem(i, 4, new_item)
        else:
            message_box = QtGui.QMessageBox()
            message_box.about(self, '提示', '账号数最多比代理数多一个')
            self.button_login.setEnabled(True)

            return

        self.nike_thread.accounts = [[self.table.item(i, 0).text(), self.table.item(i, 1).text()]
                                     for i in range(self.table.rowCount())]
        for i in range(self.table.rowCount()):
            # 如果用户未填写尺码,就设置需求尺码为None
            if self.table.item(i, 2) is None:
                self.sizes.append(None)
            elif self.table.item(i, 2).text() == '':
                self.sizes.append(None)
            else:
                self.sizes.append(self.table.item(i, 2).text())
        self.nike_thread.sizes = self.sizes
        if not self.text_monitor_interval.text() == '自动':
            self.nike_thread.monitor_interval = int(self.text_monitor_interval.text())

        if not self.text_retry_interval.text() == '自动':
            self.nike_thread.retry_interval = int(self.text_retry_interval.text())

        if not self.text_queue_interval.text() == '自动':
            self.nike_thread.queue_interval = int(self.text_queue_interval.text())


        ###
        self.logger_terminator.debug('\n监控间隔: ' + str(self.nike_thread.monitor_interval) + '\n重试间隔: '
                                     + str(self.nike_thread.retry_interval) + '\n排队间隔: ' + str(self.nike_thread.queue_interval))
        ###
        self.nike_thread.logger_terminator = self.logger_terminator
        self.nike_thread.logger_success = self.logger_success
        self.nike_thread.trigger.connect(self.update_status)

        self.nike_thread.start()

        self.button_logout.setEnabled(True)
        # 表格禁止被编辑
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

    def log_out(self):
        self.button_logout.setEnabled(False)
        self.nike_thread.quit = 1
        self.nike_thread = NikeTerminator()
        self.button_login.setEnabled(True)
        self.button_monitor.setText("开启监控")
        self.open_monitor_lock = 1
        # 表格允许被编辑
        self.table.setEditTriggers(QtGui.QAbstractItemView.AllEditTriggers)
        ###
        self.logger_terminator.debug('全部退出')
        ###

    def open_alter_accounts(self):
        self.alter_instance = NikeAlterAccounts()
        self.alter_instance.show()

    def close_alter_accounts(self):
        self.alter_instance.close()

    def open_alter_address(self):
        self.alter_address_instance = NikeAlterAddress(self.nike_thread.alter_address)
        self.alter_address_instance.show()

    def open_add_account(self):
        self.add_account_instance = NikeAddAccount()
        self.add_account_instance.show()
        self.add_account_instance.button_add.clicked.connect(self.add_account)
        self.add_account_instance.button_clear.clicked.connect(self.clear_account)

    def add_account(self):
        result = self.add_account_instance.line.toPlainText().strip().split("\n")
        print(result)
        for i in result:
            i = i.strip()
            col = 0
            row_num = self.table.rowCount()
            self.table.insertRow(row_num)
            for j in re.split(':|,| ', i):
                new_item = QtGui.QTableWidgetItem(j)
                self.table.setItem(row_num, col, new_item)
                col += 1
        self.add_account_instance.close()

    def clear_account(self):
        self.table.setRowCount(0)

    def open_proxies_pool(self):
        if self.proxies_pool_instance is None:
            self.proxies_pool_instance = NikeProxiesPool(self.proxies)
        self.proxies_pool_instance.show()

    def open_timing(self):
        self.timing_instance = NikeSetTiming()
        self.timing_instance.show()
        self.timing_instance.update.connect(self.run_timing_func)

    def run_timing_func(self):
        self.open_monitor()
        self.log_in()

    def open_setting(self):
        if self.setting_instance is None:
            self.setting_instance = NikeSetting()
            self.setting_instance.button.clicked.connect(self.close_setting)
        self.setting_instance.show()

    def close_setting(self):
        self.default_sizes = self.setting_instance.text_sizes.text()
        self.setting_instance.close()

    def update_status(self, para_list):
        new_item = QtGui.QTableWidgetItem(para_list[1])
        self.table.setItem(para_list[0], 3, new_item)

    def open_monitor(self):
        ###
        self.logger_terminator.info('开启监控')
        ###
        if self.text_url.text() == '':
            message_box = QtGui.QMessageBox()
            message_box.about(self, '提示', '请先填入监控地址')
            return -1

        if not self.text_url.text().startswith('http'):
            message_box = QtGui.QMessageBox()
            message_box.about(self, '提示', '链接不合法')
            return -1

        if self.open_monitor_lock:
            info_dict = get_product_info.get_product_info(self.text_url.text())
            if info_dict == '您查找的商品已不存在':
                message_box = QtGui.QMessageBox()
                message_box.about(self, '提示', '商品不存在')
                return -1
            elif info_dict == -1:
                message_box = QtGui.QMessageBox()
                message_box.about(self, '提示', '未知错误')
                return -1
            else:
                t_str = ''
                for i in info_dict[:-1]:
                    t_str = t_str + '\n' + i[0] + ':' + i[1]
                ###
                self.logger_terminator.info(t_str)
                ###
            # 获得在售尺码
            self.nike_thread.on_sale_sizes = info_dict[3][1].split(',')
            self.nike_thread.payloads = info_dict[-1]
            self.nike_thread.product_url = self.text_url.text()

            try:
                self.nike_thread.monitor = 1
                self.button_monitor.setText("关闭监控")
                self.open_monitor_lock = 0
            except Exception as e:
                print(e)
                self.open_monitor_lock = 1
        else:
            try:
                self.nike_thread.monitor = 0
            except:
                pass
            finally:
                self.button_monitor.setText("开启监控")
                self.open_monitor_lock = 1

    def closeEvent(self, event):
        """
        关闭程序前将数据保存至文件
        :param event:
        :return:
        """

        with open('账号.txt', 'w') as f_a:
            for i in range(self.table.rowCount()):
                if self.table.item(i, 2) is None:
                    f_a.write(self.table.item(i, 0).text() + ' ' + self.table.item(i, 1).text() + '\n')
                else:
                    f_a.write(self.table.item(i, 0).text() + ' ' + self.table.item(i, 1).text() + ' ' +
                              self.table.item(i, 2).text() + '\n')

        with open('链接.txt', 'w') as f_url:
            f_url.write(self.text_url.text())

        with open('ip.txt', 'w') as f_ip:
            for i in self.proxies:
                if len(i) == 1:
                    f_ip.write(i[0] + '\n')
                elif len(i) == 3:
                    f_ip.write(i[0] + ',' + i[1] + ',' + i[2] + '\n')
        # 关闭日志窗口
        self.logger_terminator.handlers[0].widget.close()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            # close函数会发送closeEvent事件
            self.close()

    def renameSlot(self, current_row):
        """
        打开浏览器
        :param current_row:表格当前行数
        :return:
        """
        row = current_row
        try:
            s = self.nike_thread.get_session_by_account_id(row)
            cart_url = 'https://secure-store.nike.com/cn/checkout/html/cart.jsp?country=CN&l=cart&site=nikestore&returnURL=http://www.nike.com/cn/zh_cn/'
            self.cart_browser = NikeBrowser(cart_url, s.cookies)

        except AttributeError:
            message = QtGui.QMessageBox(self)
            message.about(self, '提示', '请先登陆账号')


class NikeAccountTableWidget(QtGui.QTableWidget):
    def __init__(self, a, b, c):
        super(NikeAccountTableWidget, self).__init__(a, b, c)
        self.menu = None
        self.renameAction = QtGui.QAction('查看浏览器', self)
        self.delete_action = QtGui.QAction('删除该行', self)
        self.delete_action.triggered.connect(self.delete_by_current_row)

    def contextMenuEvent(self, event):
        self.menu = QtGui.QMenu(self)
        self.menu.addAction(self.renameAction)
        self.menu.addAction(self.delete_action)
        self.menu.popup(QtGui.QCursor.pos())

    def delete_by_current_row(self):
        self.removeRow(self.currentRow())


class NikeSetting(NikeWidget):
    def __init__(self):
        super(NikeSetting, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle("可选设置")
        self.setGeometry(250, 250, 250, 200)
        self.setFixedSize(250, 200)

        self.label_mail = QtGui.QLabel("加入购物车后发送邮件", self)
        self.label_mail.setGeometry(20, 20, 50, 20)

        self.rb_mail = QtGui.QRadioButton(self)
        self.rb_mail.setGeometry(75, 20, 15, 20)

        self.text_mail = QtGui.QLineEdit(self)
        self.text_mail.setText('859905874@qq.com')

        self.label_size = QtGui.QLabel("默认尺码", self)
        self.label_size.setGeometry(20, 45, 50, 20)
        self.text_sizes = QtGui.QLineEdit(self)
        self.text_sizes.setGeometry(75, 45, 100, 20)

        self.label_pay_in_qrcode = QtGui.QLabel('二维码付款', self)
        self.rb_pay_in_qrcode = QtGui.QRadioButton(self)

        self.button = QtGui.QPushButton('确定', self)
        self.button.setGeometry(160, 150, 80, 40)


class NikeAlterAccounts(NikeWidget):
    def __init__(self):
        super(NikeAlterAccounts, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle("账号批量修改")


class NikeAddAccount(NikeWidget):
    def __init__(self):
        super(NikeAddAccount, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle("账号添加")
        self.setFixedSize(500, 400)

        self.label = QtGui.QLabel(' 以空格/逗号/冒号为分界线，一个账号一行，例：\nabc@qq.com 123456 42或abc@qq.com,123456或abc@qq.com:123456:42 ', self)

        self.line = QtGui.QTextEdit(self)

        self.button_add = QtGui.QPushButton('添加账号', self)

        self.button_clear = QtGui.QPushButton('清空账号', self)

        hbox = QtGui.QHBoxLayout()
        hbox.addStretch(3)
        hbox.addWidget(self.button_add)
        hbox.addWidget(self.button_clear)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.line)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

class NikeProxiesPoolTableWidget(QtGui.QTableWidget):
    def __init__(self, a, b, c):
        super(NikeProxiesPoolTableWidget, self).__init__(a, b, c)
        self.menu = None
        self.delete_action = QtGui.QAction('删除该行', self)

    def contextMenuEvent(self, event):
        self.menu = QtGui.QMenu(self)
        self.menu.addAction(self.delete_action)
        # 将菜单显示在鼠标点击的位置上
        self.menu.popup(QtGui.QCursor.pos())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            pass
        else:
            super(NikeProxiesPoolTableWidget, self).mousePressEvent(event)


class NikeProxiesPool(NikeWidget):
    trigger = QtCore.pyqtSignal(list)

    def __init__(self, t_proxies):
        self.proxies = t_proxies
        super(NikeProxiesPool, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle("代理池")
        # self.setFixedSize(500, 400)

        self.table = NikeProxiesPoolTableWidget(0, 5, self)
        # 让表格中各column跟随table尺寸变化而进行对应的拉伸
        self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.table.setHorizontalHeaderLabels(['代理', '账号', '密码', '延时', '状态'])
        # 先把action内的信号和槽连接起来，再添加进菜单中，若顺序相反，则出错
        self.table.delete_action.triggered.connect(self.delete_proxy_by_current_row)
        # 取消编辑触发槽
        # self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QTableView.SelectRows)
        # 初始化表格内容
        self.refresh_table()
        self.label = QtGui.QLabel('检测2次不可用就删除代理\n'
                                  '格式：ip地址：端口 用户名 密码，一行一个代理 例：\n43.222.119.2:808 aa aa\n43.222.119.2:808 aa aa', self)
        # 'http://hkh:hkh@43.242.159.2:808'
        self.line = QtGui.QTextEdit(self)
        # self.line.setPlaText('请在此处输入要添加的HTTP代理')
        self.button_add = QtGui.QPushButton('添加', self)
        self.button_add.clicked.connect(self.add_proxies_from_text)
        self.button_validate = QtGui.QPushButton('检测状态', self)
        self.button_validate.clicked.connect(self.check)
        self.button_save = QtGui.QPushButton('清空代理', self)
        self.button_save.clicked.connect(self.clean_all_proxies)
        grid = QtGui.QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.addWidget(self.table, 0, 0, 1, 10)
        grid.addWidget(self.label, 1, 0, 1, 10)
        grid.addWidget(self.line, 2, 0, 1, 10)
        grid.addWidget(self.button_add, 3, 3, 1, 1)
        grid.addWidget(self.button_validate, 3, 5, 1, 1)
        grid.addWidget(self.button_save, 3, 7, 1, 1)

        self.setLayout(grid)

        self.useful_proxies = []

        self.queue = gevent.queue.Queue()
        self.has_delay_indices = set()
        self.invalid_indices = set()
        self.delete_indices = set()
        self.trigger.connect(self.update_table_status)

    def refresh_table(self):
        # 删除所有行
        self.table.setRowCount(0)
        for index, proxy in enumerate(self.proxies):
            self.table.insertRow(self.table.rowCount())
            if len(proxy) == 1:
                new_item = QtGui.QTableWidgetItem(proxy[0])
                self.table.setItem(index, 0, new_item)
            elif len(proxy) == 3:
                new_item = QtGui.QTableWidgetItem(proxy[0])
                self.table.setItem(index, 0, new_item)
                new_item = QtGui.QTableWidgetItem(proxy[1])
                self.table.setItem(index, 1, new_item)
                new_item = QtGui.QTableWidgetItem(proxy[2])
                self.table.setItem(index, 2, new_item)

    def check(self):
        pool = gevent.pool.Pool(len(self.proxies))
        for index, ip in enumerate(self.proxies):
            pool.apply_async(self.ip_delay, (index, ip))
        pool.join()
        self.trigger.emit([0])

    def ip_delay(self, index, ip):
        start = time.time()

        if ip is None:
            proxies = None
        else:
            if len(ip) == 1:
                proxies = {
                    'http': 'http://' + ip[0],
                }
            elif len(ip) == 3:
                proxies = {
                    'http': 'http://{}:{}@{}'.format(ip[1], ip[2], ip[0])
                }
        try:
            r = requests.get('http://store.nike.com/cn/zh_cn/', proxies=proxies, timeout=(3, 1))
        except requests.exceptions.ConnectionError:
            return
        except requests.exceptions.ReadTimeout:
            return
        end = time.time()
        delay = '{:.0f}ms'.format((end - start) * 1000)
        self.trigger.emit([index, delay])

    def update_table_status(self, emitted_list):
        if len(emitted_list) == 1:
            print(1)
            for i in range(len(self.proxies)):
                if i not in self.has_delay_indices:
                    print(str(i) + ' not in', self.has_delay_indices)
                    if i in self.invalid_indices:
                        print(str(i) + ' in', self.invalid_indices)
                        # 如果2次超时，则删除该代理
                        self.delete_indices.add(i)
                    else:
                        # 进入无效索引集合
                        self.invalid_indices.add(i)
                        t_item = QtGui.QTableWidgetItem('不可用')
                        self.table.setItem(i, 4, t_item)
                        t_item = QtGui.QTableWidgetItem('超时')
                        self.table.setItem(i, 3, t_item)

            if len(self.delete_indices) >= 1:
                self.proxies[:] = [i for j, i in enumerate(self.proxies) if j not in self.delete_indices]
                # self.proxies = [i for j, i in enumerate(self.proxies) if j not in self.delete_indices]
                self.refresh_table()
                self.invalid_indices = set()
                self.delete_indices = set()
                self.has_delay_indices = set()
            return
        elif len(emitted_list) == 2:
            item = QtGui.QTableWidgetItem('')
            self.table.setItem(emitted_list[0], 3, item)
            item = QtGui.QTableWidgetItem('')
            self.table.setItem(emitted_list[0], 4, item)
            item_delay = self.table.item(emitted_list[0], 3)
            item_status = self.table.item(emitted_list[0], 4)
            item_delay.setText(emitted_list[1])
            if int(emitted_list[1][:-2]) < 2000:
                self.has_delay_indices.add(emitted_list[0])
                item_status.setText('可用')
            else:
                if emitted_list[0] in self.invalid_indices:
                    # 如果2次超时，则删除该代理
                    self.delete_indices.add(emitted_list[0])
                self.has_delay_indices.add(emitted_list[0])
                self.invalid_indices.add(emitted_list[0])
                item_status.setText('不可用')

    def add_proxies_from_text(self):
        t_proxies = self.line.toPlainText().split('\n')
        for index, proxy in enumerate(t_proxies):
            t_proxy = re.split(',| ', proxy)
            print(t_proxy)
            if not (len(t_proxy) == 1 or len(t_proxy) == 3):
                message = QtGui.QMessageBox()
                message.about(self, '提示', '第{}行代理不合法'.format(index))
                return
            self.proxies.append(t_proxy)
        self.refresh_table()

    def delete_proxy_by_current_row(self):
        # 在python中 event.pos().x()永远为0 原因不明
        # print(event.pos().x())
        print(self.table.currentRow())
        row = self.table.currentRow()
        self.table.removeRow(row)
        self.proxies.pop(row)

    def clean_all_proxies(self):
        # del self.proxies[:]效果相同
        self.proxies[:] = []
        self.refresh_table()

    def save(self):
        self.proxies[:] = []
        for row in range(self.table.rowCount()):
            if self.table.item(row, 1) is None:
                self.proxies.append([self.table.item(row, 0).text()])
            else:
                self.proxies.append([self.table.item(row, 0).text(), self.table.item(row, 1).text()
                                    , self.table.item(row, 2).text()])

    def closeEvent(self, event):
        self.save()
        event.accept()


class NikeSetTiming(NikeWidget):
    update = QtCore.pyqtSignal(str)

    def __init__(self):
        super(NikeSetTiming, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setWindowTitle('定时设置')
        # self.setFixedSize(500, 400)
        self.timer = None
        label_start_time = QtGui.QLabel('开始时间')
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        self.line = QtGui.QLineEdit(current_time)
        self.time_label = QtGui.QLabel('剩余时间')
        self.time_label.setFixedSize(200, 20)
        self.button_confirm = QtGui.QPushButton('确定')
        self.button_confirm.clicked.connect(self.add_timing)
        grid = QtGui.QGridLayout()
        # 组件间的间距为10
        grid.setSpacing(10)
        grid.addWidget(label_start_time, 1, 0)
        grid.addWidget(self.line, 1, 1)
        grid.addWidget(self.time_label, 2, 0)
        grid.addWidget(self.button_confirm, 2, 1)
        self.setLayout(grid)

    # 创建计时器
    def add_timing(self):
        self.timer = Timer()
        expect_time = time.mktime(time.strptime(self.line.text(), '%Y-%m-%d %H:%M:%S'))
        try:
            self.timer.time = expect_time
            self.timer.update.connect(self.update_time_label)
            self.timer.start()
            self.button_confirm.setEnabled(False)
        except ValueError:
            message_box = QtGui.QMessageBox()
            message_box.about(self, '提示', '请正确设置时间')

    def update_time_label(self, string):
        self.time_label.setText(string)
        if string == '开始':
            print('计时器是否还在运行', self.timer.isRunning())
            self.update.emit('开始')
            self.close()

    def closeEvent(self, event):
        if self.time_label.text() == '开始':
            event.accept()
        else:
            reply = QtGui.QMessageBox(QtGui.QMessageBox.NoIcon, ' ', '取消定时？', QtGui.QMessageBox.Yes)
            reply.addButton(QtGui.QMessageBox.No)
            reply.setWindowFlags(QtCore.Qt.FramelessWindowHint |
                                 QtCore.Qt.WindowTitleHint)
            result = reply.exec_()
            if result == QtGui.QMessageBox.Yes:
                if not self.button_confirm.isEnabled():
                    self.timer.quit = 1
                    # self.timer.wait()
                    print('计时器退出成功')
                event.accept()
            else:
                event.ignore()


class Timer(QtCore.QThread):
    update = QtCore.pyqtSignal(str)

    def __init__(self):
        super(Timer, self).__init__()
        self._time = None
        self.quit = 0

    @property
    def time(self):
        return self._time

    # 检查传入时间是否小于当前时间
    @time.setter
    def time(self, time_value):
        if time_value < time.time():
            raise ValueError('请正确设置时间')
        else:
            self._time = time_value

    def run(self):
        now = time.time()
        while self._time > now and not self.quit:

            # 未解决时间差转化成日/小时/秒
            remain_time = float(self._time) - now
            m, s = divmod(remain_time, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            message = "还剩{:.0f}天{:02.0f}时{:02.0f}分{:02.0f}秒".format(d, h, m, s)
            self.update.emit(message)
            time.sleep(1)
            now = time.time()
        self.update.emit('开始')
        self.exit()


class NikeBrowser(QtWebKit.QWebView):
    def __init__(self, url, request_cookiejar):
        super(NikeBrowser, self).__init__()

        self.setWindowTitle('终结者浏览器')

        # 将字典转化成QNetworkCookieJar的格式
        self.cookie_jar = QtNetwork.QNetworkCookieJar()
        cookies = []
        # 直接通过cookie.name和cookie.value的方式迭代
        for cookie in request_cookiejar:
            my_cookie = QtNetwork.QNetworkCookie(QtCore.QByteArray(cookie.name), QtCore.QByteArray(cookie.value))
            my_cookie.setDomain('.nike.com')
            cookies.append(my_cookie)
        self.cookie_jar.setAllCookies(cookies)
        self.page().networkAccessManager().setCookieJar(self.cookie_jar)
        # self.cookie_jar.setCookiesFromUrl(cookies, QUrl
        # ('https://secure-store.nike.com/cn/checkout/html/cart.jsp?country=CN&l=cart&site=nikestore&returnURL=http://www.nike.com/cn/zh_cn/'))
        self.load(QtCore.QUrl(url))
        self.show()


class NikeAlterAddress(NikeWidget):
    def __init__(self, callback):
        super(NikeAlterAddress, self).__init__()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.callback = callback
        self.setWindowTitle('填写地址')
        self.setFixedSize(300, 400)
        self.setStyleSheet("background-color: white")

        label_first_name = QtGui.QLabel("姓氏*")
        label_first_name.setStyleSheet("QLabel {color : red; }")
        self.text_first_name = QtGui.QLineEdit()

        label_last_name = QtGui.QLabel("名字*")
        self.text_last_name = QtGui.QLineEdit()
        label_last_name.setStyleSheet("QLabel {color : red; }")

        label_country = QtGui.QLabel("国家/地区*")
        self.text_country = QtGui.QLineEdit('中国')
        self.text_country.setDisabled(True)
        label_country.setStyleSheet("QLabel {color : red; }")

        label_state = QtGui.QLabel("省*")
        self.text_state = QtGui.QLineEdit()
        label_state.setStyleSheet("QLabel {color : red; }")

        label_city = QtGui.QLabel("城市*")
        self.text_city = QtGui.QLineEdit()
        label_city.setStyleSheet("QLabel {color : red; }")

        label_county_district = QtGui.QLabel("区/县*")
        self.text_countyDistrict = QtGui.QLineEdit()
        label_county_district.setStyleSheet("QLabel {color : red; }")

        label_address1 = QtGui.QLabel("地址1*")
        self.text_address1 = QtGui.QLineEdit()
        label_address1.setStyleSheet("QLabel {color : red; }")

        label_address2 = QtGui.QLabel("地址2")
        self.text_address2 = QtGui.QLineEdit()

        label_phone_number = QtGui.QLabel("电话号码*")
        self.text_phone_number = QtGui.QLineEdit()
        label_phone_number.setStyleSheet("QLabel {color : red; }")

        label_additional_phone_number = QtGui.QLabel("其他电话号码")
        self.text_additionalPhoneNumber = QtGui.QLineEdit()

        label_postal_code = QtGui.QLabel("邮编")
        self.text_postalCode = QtGui.QLineEdit()

        ok_button = QtGui.QPushButton("保存")
        ok_button.setStyleSheet("color : red")
        ok_button.clicked.connect(self.save_address)
        # ok_button.setFixedWidth(55)
        label_info = QtGui.QLabel('带*为必填项')
        label_info.setStyleSheet("QLabel {color : red; }")
        fbox = QtGui.QFormLayout()
        fbox.addRow(label_first_name, self.text_first_name)
        fbox.addRow(label_last_name, self.text_last_name)
        fbox.addRow(label_country, self.text_country)
        fbox.addRow(label_state, self.text_state)
        fbox.addRow(label_city, self.text_city)
        fbox.addRow(label_county_district, self.text_countyDistrict)
        fbox.addRow(label_address1, self.text_address1)
        fbox.addRow(label_address2, self.text_address2)
        fbox.addRow(label_phone_number, self.text_phone_number)
        fbox.addRow(label_additional_phone_number, self.text_additionalPhoneNumber)
        fbox.addRow(label_postal_code, self.text_postalCode)
        fbox.addRow(label_info)
        fbox.addWidget(ok_button)
        self.setLayout(fbox)

    def save_address(self):
        a = [{"id": "CN-23", "name": "黑龙江省"}, {"id": "CN-50", "name": "重庆市"}, {"id": "CN-22", "name": "吉林省"},
             {"id": "CN-21", "name": "辽宁省"}, {"id": "CN-52", "name": "贵州省"}, {"id": "CN-51", "name": "四川省"},
             {"id": "CN-42", "name": "湖北省"}, {"id": "CN-43", "name": "湖南省"}, {"id": "CN-44", "name": "广东省"},
             {"id": "CN-45", "name": "广西壮族自治区"}, {"id": "CN-64", "name": "宁夏回族自治区"}, {"id": "CN-46", "name": "海南省"},
             {"id": "CN-65", "name": "新疆维吾尔自治区"}, {"id": "CN-63", "name": "青海省"}, {"id": "CN-14", "name": "山西省"},
             {"id": "CN-13", "name": "河北省"}, {"id": "CN-62", "name": "甘肃省"}, {"id": "CN-61", "name": "陕西省"},
             {"id": "CN-15", "name": "内蒙古自治区"}, {"id": "CN-41", "name": "河南省"}, {"id": "CN-12", "name": "天津市"},
             {"id": "CN-11", "name": "北京市"}, {"id": "CN-33", "name": "浙江省"}, {"id": "CN-34", "name": "安徽省"},
             {"id": "CN-31", "name": "上海市"}, {"id": "CN-32", "name": "江苏省"}, {"id": "CN-37", "name": "山东省"},
             {"id": "CN-53", "name": "云南省"}, {"id": "CN-35", "name": "福建省"}, {"id": "CN-36", "name": "江西省"},
             {"id": "CN-54", "name": "西藏自治区"}]
        name = self.text_state.text()
        stateid = 0
        for i in a:
            if i["name"] == name:
                stateid = i["id"]
                break
        payload = {"additionalPhoneNumber": self.text_additionalPhoneNumber.text(),
                   "address1": self.text_address1.text(),
                   "address2": self.text_address2.text(),
                   "address3": "", "city": self.text_city.text(),
                   "country": "CN", "firstName": self.text_last_name.text(), "id": None,
                   "lastName":self.text_first_name.text(), "otherName": None,
                   "phoneNumber": self.text_phone_number.text(),
                   "postalCode": self.text_postalCode.text(),
                   "preferred": True,  # 代表默认地址
                   "state": stateid,
                   "type": "SHIPPING",
                   "countyDistrict": self.text_countyDistrict.text()}
        try:
            # ------
            # 这里填入调用函数
            self.callback(payload)
            # ------
        except Exception as e:
            QtGui.QMessageBox.about(self, "My message box", e)
        self.close()


class NikeCart(NikeWidget):
    def __init__(self, s):
        super(NikeCart, self).__init__()
        self.cookies = s.cookies
        self.setWindowTitle('账号购物车')

    def cart_load_in_browser(self):
        cart_browser = NikeBrowser(self.cookies)


class NikeFileHandler(logging.FileHandler):
    def __init__(self, name):
        super(NikeFileHandler, self).__init__(name, encoding='utf-8')
        self.widget = QtGui.QPlainTextEdit()
        self.widget.setWindowIcon(QtGui.QIcon('./icon/nike.png'))
        self.widget.setReadOnly(True)
        self.widget.setWindowTitle('耐克终结者日志')
        self.widget.setStyleSheet("background-color:black;color:white;");
        self.widget.setFixedSize(400, 200)
        self.widget.move(100, 100)
        self.widget.show()

    def emit(self, record):
        super(NikeFileHandler, self).emit(record)
        msg = self.format(record)

        self.widget.appendPlainText(msg)

class NikeSuccessFileHandler(logging.FileHandler):
    def __init__(self, name):
        super(NikeSuccessFileHandler, self).__init__(name, encoding='utf-8')
        self.widget = QtGui.QPlainTextEdit()
        self.widget.setWindowIcon(QtGui.QIcon('./icon/nike.png'))
        self.widget.setReadOnly(True)
        self.widget.setWindowTitle('成功记录')
        # self.widget.setStyleSheet("background-color:black;color:white;");
        self.widget.setFixedSize(400, 200)

    def emit(self, record):
        super(NikeSuccessFileHandler, self).emit(record)
        msg = self.format(record)

        self.widget.appendPlainText(msg)
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)

    window = NikeMainWindow()
    window.show()

    sys.exit(app.exec_())
