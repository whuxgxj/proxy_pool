# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import base64
from time import sleep
from lxml import etree
from helper.proxy import Proxy
from util.formater import format_location, format_scheme

from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxy01():
        """
        无忧代理 http://www.data5u.com/
        几乎没有能用的
        不可用
        :return:
        """
        url_list = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml'
        ]
        key = 'ABCDEFGHIZ'
        for url in url_list:
            html_tree = WebRequest().get(url).tree
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    ip = ul.xpath('./span[1]/li/text()')[0]
                    classnames = ul.xpath('./span[2]/li/attribute::class')[0]
                    classname = classnames.split(' ')[1]
                    port_sum = 0
                    for c in classname:
                        port_sum *= 10
                        port_sum += key.index(c)
                    port = port_sum >> 3
                    yield '{}:{}'.format(ip, port)
                except Exception as e:
                    print(e)

    @staticmethod
    def ip66(count=20):
        """
        代理66 http://www.66ip.cn/
        :param count: 提取数量
        :return:
        """
        urls = [
            "http://www.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=",
            "http://www.66ip.cn/nmtq.php?getnum={}&isp=0&anonymoustype=0&s"
            "tart=&ports=&export=&ipaddress=&area=1&proxytype=2&api=66ip"
        ]

        try:
            import execjs
            import requests

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
                       'Accept': '*/*',
                       'Connection': 'keep-alive',
                       'Accept-Language': 'zh-CN,zh;q=0.8'}
            session = requests.session()
            src = session.get("http://www.66ip.cn/", headers=headers).text
            src = src.split("</script>")[0] + '}'
            src = src.replace("<script>", "function test() {")
            src = src.replace("while(z++)try{eval(", ';var num=10;while(z++)try{var tmp=')
            src = src.replace(");break}", ";num--;if(tmp.search('cookie') != -1 | num<0){return tmp}}")
            ctx = execjs.compile(src)
            src = ctx.call("test")
            src = src[src.find("document.cookie="): src.find("};if((")]
            src = src.replace("document.cookie=", "")
            src = "function test() {var window={}; return %s }" % src
            cookie = execjs.compile(src).call('test')
            js_cookie = cookie.split(";")[0].split("=")[-1]
        except Exception as e:
            print(e)
            return

        for url in urls:
            try:
                html = session.get(url.format(count), cookies={"__jsl_clearance": js_cookie}, headers=headers).text
                ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", html)
                for ip in ips:
                    yield Proxy(
                            proxy=ip.strip(),
                            source="66ip.cn",
                            proxy_type="http",
                            region="inside",
                        )
            except Exception as e:
                print(e)
                pass

    @staticmethod
    def freeProxy03(page_count=1):
        """
        西刺代理 http://www.xicidaili.com
        不可用
        :return:
        """
        url_list = [
            'http://www.xicidaili.com/nn/',  # 高匿
            'http://www.xicidaili.com/nt/',  # 透明
        ]
        for each_url in url_list:
            for i in range(1, page_count + 1):
                page_url = each_url + str(i)
                tree = WebRequest().get(page_url).tree
                proxy_list = tree.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                for proxy in proxy_list:
                    try:
                        yield ':'.join(proxy.xpath('./td/text()')[0:2])
                    except Exception as e:
                        pass

    @staticmethod
    def goubanjia():
        """
        guobanjia http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = WebRequest().get(url).tree
        proxy_list = tree.xpath("//table/tbody/tr")
        # proxy_list = tree.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//td[@class="ip"]/*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))

                # HTML中的port是随机数，真正的端口编码在class后面的字母中。
                # 比如这个：
                # <span class="port CFACE">9054</span>
                # CFACE解码后对应的是3128。
                port = 0
                for _ in each_proxy.xpath(".//td[@class='ip']/span[contains(@class, 'port')]"
                                          "/attribute::class")[0]. \
                        replace("port ", ""):
                    port *= 10
                    port += (ord(_) - ord('A'))
                port /= 8
                
                ip_type = each_proxy.xpath(".//td[3]/a/text()")[0].lower()
                region = " ".join(each_proxy.xpath(".//td[4]/a/text()"))
                region, city = format_location(region)
                source = "goubanjia.com"

                yield Proxy(
                        proxy='{}:{}'.format(ip_addr, int(port)),
                        proxy_type=format_scheme(ip_type),
                        region=region,
                        city=city,
                        source=source
                    )

            except Exception as e:
                pass

    @staticmethod
    def kuaidaili(page_count=1):
        """
        快代理 https://www.kuaidaili.com
        """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                region, city = format_location(tr.xpath("./td/text()")[4])
                yield Proxy(
                    proxy=':'.join(tr.xpath('./td/text()')[0:2]),
                    proxy_type=format_scheme(tr.xpath("./td/text()")[3]),
                    region=region,
                    city=city,
                    source="kuaidaili.com"
                )

    @staticmethod
    def freeProxy06():
        """
        disabled
        码农代理 https://proxy.coderbusy.com/
        :return:
        """
        urls = ['https://proxy.coderbusy.com/']
        for url in urls:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def ip3366():
        """
        云代理 http://www.ip3366.net/free/
        :return:
        """
        urls = ['http://www.ip3366.net/free/?stype=1',
                "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            tree = WebRequest().get(url, timeout=10).tree
            proxy_list = tree.xpath("//div[@id='list']/table/tbody/tr")
            # proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for tr in proxy_list:
                region, city = format_location(tr.xpath("./td/text()")[4])
                yield Proxy(
                        proxy=':'.join(tr.xpath('./td/text()')[0:2]),
                        proxy_type=format_scheme(tr.xpath("./td/text()")[3]),
                        region=region,
                        city=city,
                        source="ip3366.net"
                    )

    @staticmethod
    def freeProxy08():
        """
        disabled
        IP海 http://www.iphai.com/free/ng
        :return:
        """
        urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/wp'
        ]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>',
                                 r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def jiangxianli(page_count=1):
        """
        http://ip.jiangxianli.com/?page=
        免费代理库
        :return:
        """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                region, city = format_location(tr.xpath("./td/text()")[4])
                yield Proxy(
                        proxy=":".join(tr.xpath("./td/text()")[0:2]).strip(),
                        proxy_type=format_scheme(tr.xpath("./td/text()")[3]),
                        region=region,
                        city=city,
                        source="jiangxianli.com"
                    )

    # @staticmethod
    # def freeProxy10():
    #     """
    #     墙外网站 cn-proxy
    #     :return:
    #     """
    #     urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)

    # @staticmethod
    # def freeProxy11():
    #     """
    #     https://proxy-list.org/english/index.php
    #     :return:
    #     """
    #     urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
    #     request = WebRequest()
    #     import base64
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
    #         for proxy in proxies:
    #             yield base64.b64decode(proxy).decode()

    # @staticmethod
    # def freeProxy12():
    #     urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)

    @staticmethod
    def qydaili(max_page=2):
        """
        http://www.qydaili.com/free/?action=china&page=1
        齐云代理
        :param max_page:
        :return:
        """
        base_url = 'http://www.qydaili.com/free/?action=china&page='
        for page in range(1, max_page + 1):
            url = base_url + str(page)
            tree = WebRequest().get(url, timeout=10).tree
            proxy_list = tree.xpath("//table/tbody/tr")
            for tr in proxy_list:
                region, city = format_location(tr.xpath("./td/text()")[4])
                yield Proxy(
                        proxy=':'.join(tr.xpath('./td/text()')[0:2]),
                        proxy_type=format_scheme(tr.xpath("./td/text()")[3]),
                        region=region,
                        city=city,
                        source="qydaili.com"
                    )

    @staticmethod
    def ip89(max_page=2):
        """
        http://www.89ip.cn/index.html
        89免费代理
        :param max_page:
        :return:
        """
        base_url = 'http://www.89ip.cn/index_{}.html'
        for page in range(1, max_page + 1):
            url = base_url.format(page)
            html = WebRequest().get(url, timeout=10).text
            parser = etree.HTMLParser(encoding="utf-8")
            tree = etree.HTML(html, parser=parser)
            proxy_list = tree.xpath("//table/tbody/tr")
            for tr in proxy_list:
                region, city = format_location(tr.xpath("./td/text()")[2])
                yield Proxy(
                        proxy=':'.join([i.strip() for i in tr.xpath('./td/text()')[0:2]]),
                        proxy_type="http",
                        region=region,
                        city=city,
                        source="89ip.cn"
                    )

    @staticmethod
    def xiladaili():
        urls = ['http://www.xiladaili.com/putong/',
                "http://www.xiladaili.com/gaoni/",
                "http://www.xiladaili.com/http/",
                "http://www.xiladaili.com/https/"]
        for url in urls:
            tree = WebRequest().get(url, timeout=10).tree
            proxy_list = tree.xpath("//table/tbody/tr")
            for tr in proxy_list:
                region, city = format_location(tr.xpath("./td/text()")[3])
                yield Proxy(
                        proxy=tr.xpath('./td/text()')[0],
                        proxy_type=format_scheme(tr.xpath('./td/text()')[1]),
                        region=region,
                        city=city,
                        source="xiladaili.com"
                    )
                
    @staticmethod
    def nimadaili():
        urls = ['http://www.nimadaili.com/putong/',
                "http://www.nimadaili.com/gaoni/",
                "http://www.nimadaili.com/http/",
                "http://www.nimadaili.com/https/"]
        for url in urls:
            tree = WebRequest().get(url, timeout=10).tree
            proxy_list = tree.xpath("//table/tbody/tr")
            for tr in proxy_list:
                region, city = format_location(tr.xpath("./td/text()")[3])
                yield Proxy(
                        proxy=tr.xpath('./td/text()')[0],
                        proxy_type=format_scheme(tr.xpath('./td/text()')[1]),
                        region=region,
                        city=city,
                        source="nimadaili.com"
                    )
                
    @staticmethod
    def sunjs():
        urls = ["https://www.sunjs.com/proxy/list.html"]
        for url in urls:
            tree = WebRequest().get(url, timeout=10).tree
            proxy_list = tree.xpath("//div[@id='list']/table/tbody/tr")
            for tr in proxy_list:
                try:
                    region, city = format_location(tr.xpath("./td/text()")[3])
                    proxy_code = tr.xpath('./td/script/text()')[0]
                    print(proxy_code, region, city)
                    port = tr.xpath("./td/text()")[1]
                    ip = re.findall(r'document.write\(Base64.decode\(decode\(\"(.*?)\"\)\)\)', proxy_code)[0]
                    proxy = ':'.join([base64.b64decode(ip).decode(), port])
                except Exception as e:
                    print(e)
                else:
                    yield Proxy(
                            proxy=proxy,
                            proxy_type=format_scheme(tr.xpath('./td/text()')[2]),
                            region=region,
                            city=city,
                            source="sunjs.com"
                        )
                
    @staticmethod
    def ihuan():
        page_list = ["b97827cc", "4ce63706", "5crfe930", "f3k1d581", "ce1d45977", "881aaf7b5", "eas7a436", "981o917f5", "2d28bd81a", "a42g5985d"]
        for page in page_list:
            url = "https://ip.ihuan.me/?page={}".format(page)
            html = WebRequest().get(url, timeout=10).text
            parser = etree.HTMLParser(encoding="utf-8")
            tree = etree.HTML(html, parser=parser)
            proxy_list = tree.xpath("//table/tbody/tr")
            for tr in proxy_list:
                region, city = format_location(" ".join(tr.xpath("./td[3]/a/text()")))
                yield Proxy(
                        proxy=tr.xpath('./td[1]/a/text()')[0]+":"+tr.xpath('./td[2]/text()')[0],
                        proxy_type="http",
                        region=region,
                        city=city,
                        source="ihuan.me"
                    )
    
    """
    国外代理
    """
    @staticmethod
    def proxylist():
        """
        代理66 https://www.proxy-list.download/
        :param count: 提取数量
        :return:
        """
        urls = [
            "https://www.proxy-list.download/api/v1/get?type=https",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://www.proxy-list.download/api/v1/get?type=socks4",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
            ]
        
        for url in urls:
            try:
                proxy_type = url.split("=")[-1]
                html = WebRequest().get(url, timeout=10).text
                ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", html)
                for ip in ips:
                    yield Proxy(
                            proxy=ip.strip(),
                            source="proxy-list.download",
                            proxy_type=proxy_type,
                            region="outside",
                        )
            except Exception as e:
                print(e)
                pass
            
    @staticmethod
    def proxy_list(max_page=10):
        base_url = 'https://proxy-list.org/chinese/index.php?p='
        for page in range(1, max_page + 1):
            url = base_url + str(page)
            tree = WebRequest().get(url, timeout=10).tree
            proxy_list = tree.xpath("//div[@id='proxy-table']/div/div/ul")
            for ul in proxy_list:
                proxy_code = ul.xpath('./li/script/text()')[0]
                ip = re.findall(r"Proxy\('(.*?)'\)", proxy_code)[0]
                region = ul.xpath("./li[@class='country-city']//span[@class='country']/@title")[0]
                city = ul.xpath("./li[@class='country-city']//span[@class='city']/span/text()")[0]
                region, city = format_location(region + " " + city)
                yield Proxy(
                        proxy=base64.b64decode(ip).decode(),
                        proxy_type=format_scheme(ul.xpath("./li[@class='https']/text()")[0]),
                        region=region,
                        city=city,
                        source="proxy-list.org"
                        )
    
    @staticmethod
    def proxylistplus(max_page=5):
        base_url = 'https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-'
        for page in range(1, max_page + 1):
            url = base_url + str(page)
            tree = WebRequest().get(url, timeout=10).tree
            proxy_list = tree.xpath("//table[@class='bg']/tbody/tr[@class='cells']")
            for tr in proxy_list:
                region, city = format_location(tr.xpath("./td/text()")[4])
                yield Proxy(
                        proxy=":".join(tr.xpath("./td/text()")[1:3]),
                        proxy_type="http",
                        region=region,
                        city=city,
                        source="proxylistplus.com"
                        )
