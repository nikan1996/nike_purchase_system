import sys
from PyQt4 import QtGui, QtCore
import requests
import random
import gevent.monkey
from gevent.pool import Pool
gevent.monkey.patch_all()


class nike_register_gui(QtGui.QWidget):

    def __init__(self):
        super(nike_register_gui, self).__init__()
        self.setFixedSize(300, 80)
        self.center()
        self.setWindowTitle('nike账号注册工具')
        self.setWindowIcon(QtGui.QIcon('./nike.ico'))
        self.btn_start = QtGui.QPushButton('开始',self)
        self.btn_start.resize(200, 80)
        self.btn_start.move(100, 0)


        self.success_num = 0
        self.label_success = QtGui.QLabel('成功数：' + str(self.success_num), self)
        self.label_success.resize(200, 20)
        self.fail_num = 0
        self.label_fail = QtGui.QLabel('失败数：' + str(self.fail_num), self)
        self.label_fail.resize(200, 20)
        self.label_fail.move(0, 50)
        # 设置工作线程
        self.getInstance = nike_register()
        # self.work_thread = QtCore.QThread()
        # self.getInstance.moveToThread(self.work_thread)
        # self.work_thread.start()
        self.getInstance.signalStatus.connect(self.updateStatus)

        self.btn_start.clicked.connect(self.onClicked)

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def onClicked(self):
        self.btn_start.setEnabled(False)
        # 运行
        self.getInstance.start()

    def updateStatus(self, status):
        if status == 'fail':
            self.fail_num += 1
            self.label_fail.setText('失败数：' + str(self.fail_num))
        if status == 'success':
            self.success_num += 1
            self.label_success.setText(str(self.success_num))
            self.label_success.setText('成功数' + str(self.fail_num))

        if status == '完成':
            self.btn_start.setText('完成')

class nike_register(QtCore.QThread):
    signalStatus = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super(nike_register, self).__init__(parent)

    def reg(self, i, passw):
        try:
            url = 'https://unite.nike.com/join?appVersion=215&experienceVersion=182&uxid=com.nike.commerce.nikedotcom.web&locale=zh_CN&backendEnvironment=default&browser=Google%20Inc.&os=undefined&mobile=false&native=false'

            headers = {
                'Content-Type' : 'text/plain',
                'Referer': 'http://www.nike.com/cn/zh_cn/',
                'Origin': 'http://www.nike.com',
                'Host':'unite.nike.com',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
            }
            payload = {"locale":"zh_CN",
                       "account":{"email":"{}".format(i),
                                  "passwordSettings":{"password":passw,"passwordConfirm":passw}},
                       "registrationSiteId":"nikedotcom","username":"908104245@qq.com","lastName":"日","firstName":"勘",
                       "dateOfBirth":"1996-12-13","country":"CN","mobileNumber":"13204822070","gender":"male","receiveEmail":True
                       }
            post = 0
            while not post:
                try:
                    r = requests.post(url, headers=headers,json=payload, timeout=2)
                    post = 1
                except requests.exceptions.RequestException:
                    post = 0
            print(r.status_code)
            if r.status_code == 400:
                f = open('fail.txt', 'a')
                f.write(i + '\n')
                f.close()
                self.signalStatus.emit('fail')
            else:
                f = open('success.txt', 'a')
                f.write(i + ' ' + passw + '\n')
                f.close()
                self.signalStatus.emit('success')
        except Exception as e:
                f = open('fail.txt', 'a')
                f.write(i + '\n')
                f.close()
                self.signalStatus.emit('fail')

    def register(self):
        f = open('fail.txt', 'w')
        f.close()
        f = open('success.txt', 'w')
        f.close()
        p = Pool(200)
        f = open('邮箱.txt', 'w+')
        # emails = f.read().strip().split('\n')
        emails = list(map(lambda x: x.split('----')[0], f.read().strip().split('\n')))
        if emails and emails[0] == "":
            return
        # emails = ['nkzhuanyong' + str(i) + '@sina.com' for i in range(200)]
        passw = 'Aa123456'
        for i in emails:
            p.apply_async(self.reg, args=(i, passw))
        p.join()
        self.signalStatus.emit('完成')

    def run(self):
        self.register()


def main():
    app = QtGui.QApplication(sys.argv)

    gui = nike_register_gui()
    gui.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()