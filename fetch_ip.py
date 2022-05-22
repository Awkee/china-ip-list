#!/usr/bin/env python3
# -*- utf-8 -*-
######################################################
# 功能: 采集国内IP段信息工具
# 采集源: 
######################################################

import requests
from lxml import etree
import math
import time

ua = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'

def get_resp(url, proxies=None, headers=None, timeout=10, verify=True, allow_redirects=True):
    '''
    发送requests请求模块，最多尝试3次
    '''
    headers = headers
    if headers is None:
        headers = {'user-agent': ua}
    if isinstance(proxies, str):
        proxies = {
            'http': proxies,
            'https': proxies,
        }
    resp = None
    for _ in range(3):
        try:
            print("开始访问:", url)
            resp = requests.get(url, proxies=proxies, headers=headers, timeout=timeout, verify=verify, allow_redirects=allow_redirects)
            return resp
        except Exception as e:
            print("requests异常信息:", str(e))
    return None


def get_city_ip(city_ip_url):
    """
    功能: 采集指定城市IP段数据
    返回:
        类型: list
        数据: [{ "ip": "1.2.2.0/24" , "isp": "联通"},...]
    """
    # 限制常用的国内ISP运营商#
    isp_mask = ["联通", "电信", "移动", "铁通", "科技网", "广电", "教育网", "方正宽带"]

    resp1 = get_resp(city_ip_url)
    doc = etree.HTML(resp1.content)
    # 提取IP段信息及ISP运营商信息
    ip_list = doc.xpath('//table/tbody/tr/td[1]/a/text()')
    mask_list = doc.xpath('//table/tbody/tr/td[3]/text()')
    isp_list = doc.xpath('//table/tbody/tr/td[4]/text()')
    # result = []
    result = ""
    for i in range(len(isp_list)):
        if isp_list[i] not in isp_mask:
            continue
        mask = int(mask_list[i])
        prefix = 32 - math.ceil(math.log2(mask))
        # result.append({
        #     "ip": ip_list[i] + "/" + str(prefix),
        #     "isp": isp_list[i]
        # })
        line = ip_list[i] + "/" + str(prefix) + " " + isp_list[i] + "\n"
        if result == "":
            result = line
        else:
            result += line
    print("获取城市IP段信息:", len(result.split('\n')))
    return result

def get_city_info():
    """
    功能: 采集城市编码、名称及IP段URL信息
    返回: 
        类型: list
        数据: [{"name":"北京市", "url": "http://ip.bczs.net/city/110000", "file": "ip_bczs_net北京市_110000" },...]
    """
    url_city = "http://ip.bczs.net/city"
    url_home = "http://ip.bczs.net"

    resp = get_resp(url_city)
    # XPath提取信息
    doc = etree.HTML(resp.content)

    code_list = doc.xpath('//table/tbody/tr/td[3]/a/@href')
    name_list = doc.xpath('//table/tbody/tr/td[3]/a/text()')

    city_info = []
    for i in range(len(code_list)):
        file_name = "ip_bczs_net_" + name_list[i] + "_" + code_list[i][6:] + ".txt"
        city_info.append({
            "name": name_list[i],
            "url": url_home + code_list[i],
            "file": file_name
        })
    print("获取城市信息数量:", len(city_info))
    return city_info


def start_get_ip():
    out_dir = "./ip/"
    # 1.获取全国各地区IP段URL地址
    city_info = get_city_info()

    # 2.按城市采集IP段数据
    clen = len(city_info)
    cur = 0
    for city in city_info:
        try:
            print(f"[{cur}/{clen}]正在采集 {city['name']} 地区数据...")
            result = get_city_ip(city['url'])
            cur += 1
            # 保存到文件
            with open( out_dir + city['file'], "w") as f:
                f.write(result)
            time.sleep(1)
        except Exception as e:
            print("采集IP段时发生异常:", str(e))
    print(f"共采集 {cur}/{clen} 个地区 IP段数据!")


if __name__ == "__main__":
    start_get_ip()