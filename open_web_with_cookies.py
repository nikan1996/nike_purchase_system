from robobrowser import RoboBrowser
from requests import Session


def open_cart_web(session):
    browser = RoboBrowser(session)
    browser.open('https://secure-store.nike.com/cn/checkout/html/cart.jsp?country=CN&country=CN&l=cart&site=nikestore&returnURL=http://www.nike.com/cn/zh_cn/')

def main():
    # 登录地址
    url_login = 'https://unite.nike.com/loginWithSetCookie?'

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

    payload = {
        "username": 'nkzhuanyong187@sina.com',
        "password": 'Aa123456',
        "keepMeLoggedIn": True,
        "client_id": "HlHa2Cje3ctlaOqnxvgZXNaAs7T9nAuH",
        "ux_id": "com.nike.commerce.nikedotcom.web",
        "grant_type": "password"
    }
    s = Session()
    r = s.post(url_login, json=payload, headers=headers, timeout=5)
    open_cart_web(s)
if __name__ == '__main__':
    main()