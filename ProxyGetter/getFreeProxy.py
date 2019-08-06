# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25:
-------------------------------------------------
"""
import re
import sys
import base64
import requests

sys.path.append('..')

from Util.WebRequest import WebRequest
from Util.utilFunction import getHtmlTree

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()


class GetFreeProxy(object):
    """
    proxy getter
    """
    
    @staticmethod
    def freeProxyFirst(page=10):
        """
        无忧代理 http://www.data5u.com/
        几乎没有能用的
        :param page: 页数
        :return:
        """
        url_list = [
            'http://www.data5u.com/'
        ]
        for url in url_list:
            html_tree = getHtmlTree(url)
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    yield ':'.join(ul.xpath('.//li/text()')[0:2])
                except Exception as e:
                    print(e)
    
    @staticmethod
    def freeProxySecond(count=20):
        """
        代理66 http://www.66ip.cn/   失效
        :param count: 提取数量
        :return:
        """
        urls = [
            "http://www.66ip.cn/mo.php?sxb=&tqsl={count}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=",
            "http://www.66ip.cn/nmtq.php?getnum={count}"
            "&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=0&proxytype=2&api=66ip",
        ]
        request = WebRequest()
        for _ in urls:
            url = _.format(count=count)
            html = request.get(url).text
            # print(html)
            ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", html)
            for ip in ips:
                yield ip.strip()
    
    @staticmethod
    def freeProxyThird():
        """
        sunjs https://www.sunjs.com/proxy/list.html   墙外可访问
        :return:
        """
        url = "https://www.sunjs.com/proxy/list.html"
        tree = getHtmlTree(url)
        ip_list = tree.xpath('//td[@data-title="IP"]/script/text()')
        port_list = tree.xpath('//td[@data-title="PORT"]/text()')
        try:
            for ip, port in zip(ip_list, port_list):
                ip = re.findall('document.write\(Base64.decode\(decode\(\"(.*?)\"\)\)\)', ip)[0]
                print(base64.b64decode(ip).decode())
                yield ':'.join([base64.b64decode(ip).decode(), port])
        except Exception as e:
            pass
    
    @staticmethod
    def freeProxyFourth(page_count=1):
        """
        西刺代理 http://www.xicidaili.com
        :return:
        """
        url_list = [
            'https://www.xicidaili.com/nn/',  # 国内高匿
            'https://www.xicidaili.com/nt/',  # 国内透明
            'https://www.xicidaili.com/wn/',  # 国内https
            'https://www.xicidaili.com/wt/',  # 国内http
        ]
        for each_url in url_list:
            for i in range(1, page_count + 1):
                page_url = each_url + str(i)
                tree = getHtmlTree(page_url)
                proxy_list = tree.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                for proxy in proxy_list:
                    try:
                        yield ':'.join(proxy.xpath('./td/text()')[0:2])
                    except Exception as e:
                        pass
    
    @staticmethod
    def freeProxyFifth():
        """
        guobanjia http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = getHtmlTree(url)
        proxy_list = tree.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))
                port = each_proxy.xpath(".//span[contains(@class, 'port')]/text()")[0]
                yield '{}:{}'.format(ip_addr, port)
            except Exception as e:
                pass
    
    @staticmethod
    def freeProxySixth():
        """
        齐云代理 http://www.qydaili.com/free/
        :return:
        """
        url = 'http://www.qydaili.com/free/'
        tree = getHtmlTree(url)
        ip_list = tree.xpath('//td[@data-title="IP"]/text()')
        port_list = tree.xpath('//td[@data-title="PORT"]/text()')
        try:
            for ip, port in zip(ip_list, port_list):
                yield ':'.join([ip, port])
        except Exception as e:
            pass
    
    @staticmethod
    def freeProxySeventh():
        """
        快代理 https://www.kuaidaili.com 国外可访问
        """
        url_list = [
            'https://www.kuaidaili.com/free/inha/',
            'https://www.kuaidaili.com/free/intr/'
        ]
        for url in url_list:
            tree = getHtmlTree(url)
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
    
    @staticmethod
    def freeProxyEight():
        """
        89ip http://www.89ip.cn/index.html
        """
        url_list = ["http://www.89ip.cn/tqdl.html?api=1&num=30&port=&address=&isp="]
        request = WebRequest()
        for url in url_list:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)<br>', r.text)
            for proxy in proxies:
                yield proxy
    
    @staticmethod
    def freeProxyNinth():
        """
        码农代理 http://www.xiladaili.com/
        :return:
        """
        urls = ['http://www.xiladaili.com/putong/', 'http://www.xiladaili.com/gaoni/', 'http://www.xiladaili.com/http/',
                'http://www.xiladaili.com/https/']
        request = WebRequest()
        for url in urls:
            tree = getHtmlTree(url)
            proxy_list = tree.xpath('.//table//tbody//tr')
            for proxy in proxy_list:
                yield proxy.xpath("./td/text()")[0]
    
    @staticmethod
    def freeProxyTen():
        """
        云代理 http://www.ip3366.net/free/
        :return:
        """
        urls = ['http://www.ip3366.net/free/?stype=1', 'http://www.ip3366.net/free/?stype=2']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)
    
    @staticmethod
    def freeProxyEleven():
        """
        IP海 http://www.iphai.com/free/ng
        :return:
        """
        urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/wp'
        ]
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>',
                                 r.text)
            for proxy in proxies:
                yield ":".join(proxy)
    
    @staticmethod
    def freeProxyTwelve(page_count=2):
        """
        http://ip.jiangxianli.com/?page=
        免费代理库
        超多量
        :return:
        """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?page={}'.format(i)
            html_tree = getHtmlTree(url)
            tr_list = html_tree.xpath("/html/body/div[1]/div/div[1]/div[2]/table/tbody/tr")
            if len(tr_list) == 0:
                continue
            for tr in tr_list:
                yield tr.xpath("./td[2]/text()")[0] + ":" + tr.xpath("./td[3]/text()")[0]
    
    @staticmethod
    def freeProxyThirteen():
        """
        https://ip.ihuan.me/address/5Lit5Zu9.html   反爬严厉
        免费代理库
        超多量
        :return:
        """
        url_list = ['https://ip.ihuan.me/']
        for url in url_list:
            tree = getHtmlTree(url)
            proxy_list = tree.xpath('.//table/tbody/tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
    
    @staticmethod
    def freeProxyWallFirst():
        """
        https://www.proxy-list.download/api/v0/get?l=en&t=https
        :return:
        """
        urls = ['https://www.proxy-list.download/api/v0/get?l=en&t=https',
                'https://www.proxy-list.download/api/v0/get?l=en&t=http']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = r.json()[0]["LISTA"]
            for proxy in proxies:
                if proxy["COUNTRY"] == "China":
                    yield ':'.join([proxy["IP"], proxy["PORT"]])
    
    @staticmethod
    def freeProxyWallSecond():
        """
        https://proxy-list.org/english/index.php
        :return:
        """
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                yield base64.b64decode(proxy).decode()
    
    @staticmethod
    def freeProxyWallThird():
        """
        https://list.proxylistplus.com
        :return:
        """
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)
    
    @staticmethod
    def freeProxyNima():
        """
        泥马代理：http://www.nimadaili.com/
        :return:
        """
        urls = ['http://www.nimadaili.com/putong/', "http://www.nimadaili.com/gaoni/", "http://www.nimadaili.com/http/",
                "http://www.nimadaili.com/https/"]
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)</td>', r.text)
            for proxy in proxies:
                yield proxy


if __name__ == '__main__':
    from CheckProxy import CheckProxy
    
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFirst)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySecond)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyThird)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFourth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFifth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySixth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySeventh)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyEight)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyNinth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyTen)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyEleven)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyTwelve)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyThirteen)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyWallFirst)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyWallSecond)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyWallThird)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyNima)
    # CheckProxy.checkAllGetProxyFunc()
