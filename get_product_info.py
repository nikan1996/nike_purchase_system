import requests
from bs4 import BeautifulSoup
import re
import time
import timeit

# 参数：链接
def get_product_info(product_url):
    """
    :param product_url:
    :return: info_list:[('product_title', product_title), ('product_category', product_category),
            ('product_price', product_price), ('onsale_size', onsale_size),  ('startdate', startdate), payloads]
    """
    r = requests.get(product_url)

    # 产品标题，分类，价格，配色
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        product_title = soup.select(
            '#content > div > div.exp-pdp-main-pdp-content > div.exp-pdp-content-container > div.exp-product-header > h1'
        )[0].get_text()
        product_category = soup.select(
            '#content > div > div.exp-pdp-main-pdp-content > div.exp-pdp-content-container > div.exp-product-header > h2'
        )[0].get_text()
        product_price = soup.select(
            '#content > div > div.exp-pdp-main-pdp-content > div.exp-pdp-content-container '
            '> div.exp-product-header > div > span > div > span'
        )[0].get_text()

        # 寻找发售时间
        pattern = re.compile(r'"startDate":(.+?),"builderUrl":null')
        match = pattern.search(r.text)
        startdate = match.group(1)
        x = time.localtime(int(startdate)/1000)
        startdate = time.strftime('%Y-%m-%d %H:%M:%S', x)

        # 寻找在售尺码
        pattern_onsale = re.compile(r'"inStock":true,"displaySize":"(.+?)"')
        onsale_size = pattern_onsale.findall(r.text)
        onsale_size = ','.join(onsale_size)

        # 预先生成payloads
        payload = {
            'callback': 'nike_Cart_handleJCartResponse',
            'qty': '1',
            'rt': 'json',
            'view': '3',
            'country': 'CN',
            'sizeType': None,
            # 11154710
            'productId': '11154710',
            'price': '1599.0',
            'siteId': None,
            'passcode': None,
            'lang_locale': 'zh_CN',
            'action': 'addItem',
            'line1': 'AIR JORDAN 11 RETRO',
            'catalogId': 4,
            'line2': '复刻男子运动鞋'
        }
        result = soup.select('#exp-pdp-buying-tools-container > form > input[type="hidden"]')
        skuId = soup.find_all('option', attrs={'name': 'skuId'})
        for i in result:
            try:
                if i['value'] == '':
                    payload[i['name']] = None
                else:
                    payload[i['name']] = i['value']
            except:
                payload[i['name']] = None
        payloads = {}
        for i in skuId:
            t_payload = payload
            t_payload['skuAndSize'] = i['value']
            t_payload['skuId'], payload['displaySize'] = payload['skuAndSize'].split(':')

            payloads[payload['displaySize']] = t_payload.copy()
            # print(payloads[payload['displaySize']])
        return [('产品标题', product_title), ('产品类别', product_category),
                ('产品价格', product_price), ('在售尺码', onsale_size), ('起售日期', startdate), payloads]
    except IndexError:
        product_not_exist_title = soup.select('#content > div > div > h1')
        if product_not_exist_title:
            return '您查找的商品已不存在'
        else:
            print(product_not_exist_title)
            print('未知错误')
            return -1


def main(url):
    # http://store.nike.com/cn/zh_cn/pd/air-zoom-pegasus-33-%E7%94%B7%E5%AD%90%E8%B7%91%E6%AD%A5%E9%9E%8B/pid-10944263/pgid-11137000
    # http://store.nike.com/cn/zh_cn/pd/air-jordan-11-retro-%E5%A4%8D%E5%88%BB%E7%94%B7%E5%AD%90%E8%BF%90%E5%8A%A8%E9%9E%8B/pid-11154710/pgid-10284306
    start = timeit.default_timer()
    info_dict = get_product_info(url)
    if info_dict == '您查找的商品已不存在':
        print('商品不存在')
    else:
        for i in info_dict[:-1]:
            print(i[0] + ':' + i[1])
        print(info_dict[-1])
        # for size in info_dict[3][1].split(','):
        #     print(get_product_payload(url1, size))
    end = timeit.default_timer()
    print('总计用时：', end-start)

if __name__ == "__main__":
    # url1 = 'http://store.nike.com/cn/zh_cn/pd/lunarepic-low-flyknit-2-%E7%94%B7%E5%AD%90%E8%B7%91%E6%AD%A5%E9%9E%8B/pid-11232563/pgid-11493486'
    # main(url1)
    # url2 = 'http://store.nike.com/cn/zh_cn/pd/' \
    #        'air-jordan-1-retro-high-og-as-%E7%94%B7%E5%AD%90%E8%BF%90%E5%8A%A8%E9%9E%8B/pid-11464172/pgid-11592084'
    # main(url2)
    a = get_product_info('http://store.nike.com/cn/zh_cn/pd/lunarepic-low-flyknit-2-%E5%A5%B3%E5%AD%90%E8%B7%91%E6%AD%A5%E9%9E%8B/pid-11232567/pgid-11493487')
    print(a[-1])
