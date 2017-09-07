import requests
import requests
from requests.adapters import HTTPAdapter
import sys
from bs4 import BeautifulSoup
from PyQt4.QtWebKit import QWebView
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl, QByteArray
from PyQt4.QtNetwork import QNetworkCookieJar, QNetworkCookie


class NikeBrowser(QWebView):
    def __init__(self, url, request_cookiejar):
        super(NikeBrowser, self).__init__()
        self.setWindowTitle('终结者浏览器')

        # 将字典转化成QNetworkCookieJar的格式
        self.cookie_jar = QNetworkCookieJar()
        cookies = []
        # 直接通过cookie.name和cookie.value的方式迭代
        for cookie in request_cookiejar:
            my_cookie = QNetworkCookie(QByteArray(cookie.name), QByteArray(cookie.value))
            my_cookie.setDomain('.nike.com')
            cookies.append(my_cookie)
        self.cookie_jar.setAllCookies(cookies)
        self.page().networkAccessManager().setCookieJar(self.cookie_jar)
        # self.cookie_jar.setCookiesFromUrl(cookies, QUrl('https://secure-store.nike.com/cn/checkout/html/cart.jsp?country=CN&l=cart&site=nikestore&returnURL=http://www.nike.com/cn/zh_cn/'))
        self.load(QUrl(url))
        self.show()
def main():
    s = requests.session()
    headers = {
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


    # s.proxies = proxies
    r = s.get('http://www.nike.com/cn/zh_cn/', headers=headers)
    print(r.headers)


    # 登录
    headers_login = {
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
    url_login = 'https://unite.nike.com/loginWithSetCookie?'
    payload = {
                    "username": 'nyongg7376@sina.com',
                    "password": 'Aa123456',
                    "keepMeLoggedIn": True,
                    "client_id": "HlHa2Cje3ctlaOqnxvgZXNaAs7T9nAuH",
                    "ux_id": "com.nike.commerce.nikedotcom.web",
                    "grant_type": "password"
                }
    r = s.post(url_login, json=payload, headers=headers_login)

    print(r.text)
    print('登录cookies', s.cookies)


    s.cookies.update({'CONSUMERCHOICE': 'cn/zh_cn'})
    s.cookies.update({'guidU': '', 'guidS': ''})
    url = 'https://secure-store.nike.com/ap/services/jcartService?action=getCartSummary&rt=json&country=CN&lang_locale=zh_CN'
    headers = {
        # 'Cookie': 'AnalysisUserId=115.231.9.38.153081490417644545; NIKE_COMMERCE_COUNTRY=CN; NIKE_COMMERCE_LANG_LOCALE=zh_CN; nike_locale=cn/zh_cn; guidU=c0ae4ecb-afb2-4fd0-c939-c186c9175ac1; neo.swimlane=19;guidS=dd99af9f-8f49-4b81-bcf9-dbe5b3db783d;slCheck=w9UplD/cRA9UgF7hs2YrYg79zjdY9IXDkaFPbl2FfCPWfvVgwriN2X+NDqvAPFBpIeCq375itxIRypSCLeXqLA==;',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    r = s.get(url, headers=headers)
    print(r.headers)
    print(r.text)
    return s.cookies

if __name__ == '__main__':
    # fun_test()
    app = QApplication(sys.argv)
    cart_url = 'https://secure-store.nike.com/cn/checkout/html/cart.jsp?country=CN&l=cart&site=nikestore&returnURL=http://www.nike.com/cn/zh_cn/'
    cookies = main()
    browser = NikeBrowser(cart_url, cookies)
    # confirm_url = 'https://secure-store.nike.com/cn/checkout/html/confirm.jsp?'

    # browser2 = NikeBrowser(confirm_url, cookies)
    app.exec_()