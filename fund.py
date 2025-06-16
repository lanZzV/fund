# -*- coding: UTF-8 -*-

import argparse
import datetime
import json
import os
import re
import time

import requests
import urllib3
from loguru import logger
from tabulate import tabulate

from module_html import get_result_html, get_tbody, style

urllib3.disable_warnings()
urllib3.util.ssl_.DEFAULT_CIPHERS = ":".join(
    [
        "ECDHE+AESGCM",
        "ECDHE+CHACHA20",
        'ECDHE-RSA-AES128-SHA',
        'ECDHE-RSA-AES256-SHA',
        "RSA+AESGCM",
        'AES128-SHA',
        'AES256-SHA',
    ]
)
tabulate.PRESERVE_WHITESPACE = True


def format_table_msg(table, tablefmt="pretty"):
    return tabulate(table, tablefmt=tablefmt, missingval="N/A")


class MaYiFund:
    CACHE_MAP = {}

    def __init__(self):
        self.session = requests.Session()
        self.baidu_session = requests.Session()
        self._csrf = ""
        self.load_cache()
        self.init()

    def load_cache(self):
        if not os.path.exists("cache"):
            os.mkdir("cache")
        if os.path.exists("cache/fund_map.json"):
            with open("cache/fund_map.json", "r", encoding="gbk") as f:
                self.CACHE_MAP = json.load(f)
        # if self.CACHE_MAP:
        #     logger.debug(f"加载 {len(self.CACHE_MAP)} 个基金代码缓存成功")

    def save_cache(self):
        with open("cache/fund_map.json", "w", encoding="gbk") as f:
            json.dump(self.CACHE_MAP, f, ensure_ascii=False, indent=4)

    def init(self):
        res = self.session.get("http://www.fund123.cn/fund", headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }, timeout=10, verify=False)
        self._csrf = re.findall('\"csrf\":\"(.*?)\"', res.text)[0]

        self.baidu_session.get("https://gushitong.baidu.com/index/ab-000001", headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "referer": "https://gushitong.baidu.com/"
        }, timeout=10, verify=False)
        self.baidu_session.cookies.update({
            "BDUSS": "3hJYkhPNEM3Z2xOeH5TLVU4OEhhU1hPUFYxdVV3V0pkd1VEMEhCTEgxRENMWEJsSVFBQUFBJCQAAAAAAAAAAAEAAAAVl0lPamRrZGpiZGIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMKgSGXCoEhlM",
            "BDUSS_BFESS": "3hJYkhPNEM3Z2xOeH5TLVU4OEhhU1hPUFYxdVV3V0pkd1VEMEhCTEgxRENMWEJsSVFBQUFBJCQAAAAAAAAAAAEAAAAVl0lPamRrZGpiZGIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMKgSGXCoEhlM",
        })

    def add_code(self, codes):
        codes = codes.split(",")
        codes = [code.strip() for code in codes if code.strip()]
        for code in codes:
            try:
                headers = {
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "Origin": "http://www.fund123.cn",
                    "Referer": "http://www.fund123.cn/fund",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    "X-API-Key": "foobar",
                    "accept": "json"
                }
                url = "http://www.fund123.cn/api/fund/searchFund"
                params = {
                    "_csrf": self._csrf
                }
                data = {
                    "fundCode": code
                }
                response = self.session.post(url, headers=headers, params=params, json=data, timeout=10, verify=False)
                if response.json()["success"]:
                    fund_key = response.json()["fundInfo"]["key"]
                    fund_name = response.json()["fundInfo"]["fundName"]
                    self.CACHE_MAP[code] = {
                        "fund_key": fund_key,
                        "fund_name": fund_name
                    }
                    logger.info(f"添加基金代码【{code}】成功")
                else:
                    logger.error(f"添加基金代码【{code}】失败: {response.text.strip()}")
            except Exception as e:
                logger.error(f"添加基金代码【{code}】失败: {e}")
        self.save_cache()

    def delete_code(self, codes):
        codes = codes.split(",")
        codes = [code.strip() for code in codes if code.strip()]
        for code in codes:
            try:
                if code in self.CACHE_MAP:
                    del self.CACHE_MAP[code]
                    logger.info(f"删除基金代码【{code}】成功")
                else:
                    logger.warning(f"删除基金代码【{code}】失败: 不存在该基金代码")
            except Exception as e:
                logger.error(f"删除基金代码【{code}】失败: {e}")
        self.save_cache()

    def search_code(self, is_return=False):
        result = []
        for fund, fund_data in self.CACHE_MAP.items():
            try:
                headers = {
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "Origin": "http://www.fund123.cn",
                    "Referer": "http://www.fund123.cn/fund",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    "X-API-Key": "foobar",
                    "accept": "json"
                }
                url = f"https://www.fund123.cn/matiaria?fundCode={fund}"
                response = self.session.get(url, headers=headers, timeout=10, verify=False)
                dayOfGrowth = re.findall('\"dayOfGrowth\"\:\"(.*?)\"', response.text)[0]
                dayOfGrowth = str(round(float(dayOfGrowth), 2)) + "%"

                url = "https://www.fund123.cn/api/fund/queryFundEstimateIntraday"
                params = {
                    "_csrf": self._csrf
                }
                fund_key = fund_data["fund_key"]
                fund_name = fund_data["fund_name"]
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                data = {
                    "startTime": today,
                    "endTime": tomorrow,
                    "limit": 200,
                    "productId": fund_key,
                    "format": True,
                    "source": "WEALTHBFFWEB"
                }
                response = self.session.post(url, headers=headers, params=params, json=data, timeout=10, verify=False)
                if response.json()["success"]:
                    if not response.json()["list"]:
                        now_time = "N/A"
                        forecastGrowth = "N/A"
                    else:
                        fund_info = response.json()["list"][-1]
                        now_time = datetime.datetime.fromtimestamp(fund_info["time"] / 1000).strftime(
                            "%Y-%m-%d %H:%M:%S")
                        forecastGrowth = str(round(float(fund_info["forecastGrowth"]) * 100, 2)) + "%"
                        if not is_return:
                            if "-" in forecastGrowth:
                                forecastGrowth = "\033[1;32m" + forecastGrowth
                            else:
                                forecastGrowth = "\033[1;31m" + forecastGrowth
                    if not is_return:
                        if "-" in dayOfGrowth:
                            dayOfGrowth = "\033[1;32m" + dayOfGrowth
                        else:
                            dayOfGrowth = "\033[1;31m" + dayOfGrowth
                    result.append([fund, fund_name, now_time, forecastGrowth, dayOfGrowth])
                else:
                    logger.error(f"查询基金代码【{fund}】失败: {response.text.strip()}")
            except Exception as e:
                logger.error(f"查询基金代码【{fund}】失败: {e}")
        if is_return:
            result = sorted(
                result,
                key=lambda x: float(x[3].replace("%", "")) if x[3] != "N/A" else -99,
                reverse=True
            )
            return result
        if result:
            result = sorted(
                result,
                key=lambda x: float(x[3].split("m")[1].replace("%", "")) if x[3] != "N/A" else -99,
                reverse=True
            )
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 基金估值信息:")
            for line_msg in format_table_msg([
                [
                    "基金代码", "基金名称", "估值时间", "估值", "日涨幅"
                ],
                *result
            ]).split("\n"):
                logger.info(line_msg)

    def fund_html(self):
        result = self.search_code(True)
        info = ""
        for i in result:
            info += get_tbody(i)

        return get_result_html(["基金代码", "基金名称", "估值时间", "估值", "日涨幅"]).format(tbody=info) + style

    def run(self, is_add=False, is_delete=False):
        if not self.CACHE_MAP:
            logger.warning("暂无缓存代码信息, 请先添加基金代码")
            is_add = True
        if is_delete:
            now_codes = list(self.CACHE_MAP.keys())
            logger.debug(f"当前缓存基金代码: {now_codes}")
            logger.debug("请输入基金代码, 多个基金代码以英文逗号分隔:")
            codes = input()
            self.delete_code(codes)
            logger.success("删除基金代码成功")
            if not is_add:
                return
        if is_add:
            logger.debug("请输入基金代码, 多个基金代码以英文逗号分隔:")
            codes = input()
            self.add_code(codes)
            logger.success("添加基金代码成功")
        else:
            self.kx()
            self.bk()
            self.gold()
            self.A()
            self.get_market_info()
            self.search_code()

    def get_market_info(self, is_return=False):
        target_matket = ["上证指数", "深证指数", "纳斯达克", "道琼斯"]
        result = []
        try:
            markets = ["asia", "america"]
            for market in markets:
                url = f"https://finance.pae.baidu.com/api/getbanner?market={market}&finClientType=pc"
                response = self.baidu_session.get(url, timeout=10, verify=False)
                if response.json()["ResultCode"] == "0":
                    market_list = response.json()["Result"]["list"]
                    for market_info in market_list:
                        if market_info["name"] in target_matket:
                            ratio = market_info["ratio"]
                            if not is_return:
                                if "-" in ratio:
                                    ratio = "\033[1;32m" + ratio
                                else:
                                    ratio = "\033[1;31m" + ratio
                            result.append([
                                market_info["name"],
                                market_info["lastPrice"],
                                ratio
                            ])

            # 增加创业板指
            url = "https://finance.pae.baidu.com/vapi/v1/getquotation"
            params = {
                "srcid": "5353",
                "all": "1",
                "pointType": "string",
                "group": "quotation_index_minute",
                "query": "399006",
                "code": "399006",
                "market_type": "ab",
                "newFormat": "1",
                "name": "创业板指",
                "finClientType": "pc"
            }
            response = requests.get(url, params=params, timeout=10, headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }, verify=False)
            if str(response.json()["ResultCode"]) == "0":
                cur = response.json()["Result"]["cur"]
                ratio = cur["ratio"]
                if not is_return:
                    if "-" in ratio:
                        ratio = "\033[1;32m" + ratio
                    else:
                        ratio = "\033[1;31m" + ratio
                result.insert(2, [
                    "创业板指",
                    cur["price"],
                    ratio
                ])
        except Exception as e:
            logger.error(f"获取市场信息失败: {e}")
        if is_return:
            return result
        if result:
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 市场信息:")
            for line_msg in format_table_msg([
                [
                    "指数名称", "指数", "涨跌幅"
                ],
                *result
            ]).split("\n"):
                logger.info(line_msg)

    def marker_html(self):
        result = self.get_market_info(True)
        info = ""
        for i in result:
            info += get_tbody(i)

        return get_result_html(["指数名称", "指数", "涨跌幅"]).format(tbody=info) + style

    def gold_html(self):
        result = self.gold(True)
        info = ""
        for i in result:
            info += get_tbody(i)
        return get_result_html(
            ["日期", "中国黄金基础金价", "周大福金价", "中国黄金基础金价涨跌", "周大福金价涨跌"]
        ).format(tbody=info) + style

    @staticmethod
    def bk():
        bk_result = []
        TRADE_DATE = "2023-08-31"
        try:
            url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
            params = {
                "callback": "",
                "sortColumns": "ADD_MARKET_CAP",
                "sortTypes": "-1",
                "pageSize": "100",
                "pageNumber": "1",
                "reportName": "RPT_MUTUAL_BOARD_HOLDRANK_WEB",
                "columns": "ALL",
                "quoteColumns": "f3~05~SECURITY_CODE~INDEX_CHANGE_RATIO",
                "quoteType": "0",
                "source": "WEB",
                "client": "WEB",
                "filter": "(BOARD_TYPE=\"5\")(INTERVAL_TYPE=\"1\")(TRADE_DATE='%s')" % TRADE_DATE,
            }
            response = requests.get(url, params=params, timeout=10, verify=False)
            if str(response.json()["code"]) == "0":
                data = response.json()["result"]["data"]
                for bk in data:
                    ratio = str(bk["INDEX_CHANGE_RATIO"]) + "%"
                    if "-" in ratio:
                        ratio = "\033[1;32m" + ratio
                    else:
                        ratio = "\033[1;31m" + ratio
                    bk_result.append([
                        bk["BOARD_NAME"],
                        ratio,
                        str(round(bk["HK_VALUE"] / 100000000, 2)) + "亿",
                        str(round(bk["ADD_MARKET_CAP"] / 100000000, 2)) + "亿",
                        str(round(bk["ADD_RATIO"], 2)) + "%"
                    ])
        except:
            pass
        if bk_result:
            bk_result = sorted(
                bk_result,
                key=lambda x: float(x[1].split("m")[1].replace("%", "")) if x[3] != "N/A" else -99,
                reverse=True
            )
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 行业板块:")
            for line_msg in format_table_msg([
                [
                    "板块名称", "最新涨跌幅", "北向资金今日持股市值", "北向资金今日增持估计市值",
                    "北向资金今日增持估计市值增幅",
                ],
                *bk_result
            ]).split("\n"):
                logger.info(line_msg)

    @staticmethod
    def kx():
        url = "https://finance.pae.baidu.com/selfselect/expressnews?rn=10&pn=0&tag=A股&finClientType=pc"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        kx_list = []
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            if response.json()["ResultCode"] == "0":
                kx_list = response.json()["Result"]["content"]["list"]
        except:
            pass

        if kx_list:
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 7*24 快讯:")
            for i, v in enumerate(kx_list):
                evaluate = v.get("evaluate", "")
                if evaluate == "利好":
                    pre = "\033[1;31m"
                elif evaluate == "利空":
                    pre = "\033[1;32m"
                else:
                    pre = ""
                title = v.get("title", v["content"]["items"][0]["data"])
                publish_time = v["publish_time"]
                publish_time = datetime.datetime.fromtimestamp(int(publish_time)).strftime("%Y-%m-%d %H:%M:%S")
                entity = v.get("entity", [])
                entity = ", ".join([f"{x['code'].strip()}-{x['name'].strip()} {x['ratio'].strip()}" for x in entity])
                logger.info(f"{pre}{i + 1}. {publish_time} {title}.")
                if entity:
                    logger.debug(f"影响股票: {entity}.")

    @staticmethod
    def gold(is_return=False):
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "referer": "https://quote.cngold.org/gjs/swhj_zghj.html",
            "sec-ch-ua": "\"Chromium\";v=\"128\", \"Not;A=Brand\";v=\"24\", \"Google Chrome\";v=\"128\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "script",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        }
        url = "https://api.jijinhao.com/quoteCenter/history.htm"
        params = {
            "code": "JO_52683",
            "style": "3",
            "pageSize": "10",
            "needField": "128,129,70",
            "currentPage": "1",
            "_": int(time.time() * 1000)
        }
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        data = json.loads(response.text.replace("var quote_json = ", ""))["data"]

        url = "https://api.jijinhao.com/quoteCenter/history.htm"
        params = {
            "code": "JO_42660",
            "style": "3",
            "pageSize": "10",
            "needField": "128,129,70",
            "currentPage": "1",
            "_": int(time.time() * 1000)
        }
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        data2 = json.loads(response.text.replace("var quote_json = ", ""))["data"]

        gold_list = []

        for i in range(len(data)):
            gold = data[i]
            t = gold["time"]
            date = datetime.datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d")
            radio = str(gold["q70"])
            radio2 = "N/A"
            gold2 = {}
            if len(data2) > i:
                gold2 = data2[i]
                radio2 = str(gold2["q70"])
            if not is_return:
                if "-" in radio:
                    radio = "\033[1;32m" + radio
                else:
                    radio = "\033[1;31m" + radio
                if "-" in radio2:
                    radio2 = "\033[1;32m" + radio2
                else:
                    radio2 = "\033[1;31m" + radio2
            gold_list.append([
                date,
                gold["q1"],
                gold2.get("q1", "N/A"),
                radio,
                radio2
            ])
        if is_return:
            return gold_list[::-1]
        if gold_list:
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 金价:")
            for line_msg in format_table_msg([
                [
                    "日期", "中国黄金基础金价", "周大福金价", "中国黄金基础金价涨跌", "周大福金价涨跌"
                ],
                *gold_list[::-1]
            ]).split("\n"):
                logger.info(line_msg)

    def A(self, is_return=False):
        url = "https://finance.pae.baidu.com/vapi/v1/getquotation"
        params = {
            "srcid": "5353",
            "all": "1",
            "pointType": "string",
            "group": "quotation_index_minute",
            "query": "000001",
            "code": "000001",
            "market_type": "ab",
            "newFormat": "1",
            "name": "上证指数",
            "finClientType": "pc"
        }
        response = self.baidu_session.get(url, params=params, timeout=10, verify=False)
        if str(response.json()["ResultCode"]) == "0":
            marketData = response.json()["Result"]["newMarketData"]["marketData"][0]["p"]
            if not is_return:
                marketData = marketData.split(";")[-30:]
            else:
                marketData = marketData.split(";")[-15:]
            marketData = [x.split(",")[1:] for x in marketData]
            if marketData:
                result = []
                for i in marketData:
                    if not is_return:
                        if "+" in i[2]:
                            i[1] = "\033[1;31m" + i[1]
                        else:
                            i[1] = "\033[1;32m" + i[1]
                    i[3] = i[3] + "%"
                    try:
                        i[4] = str(round(float(float(i[4]) / 10000), 2)) + "万手"
                        i[5] = str(round(float(float(i[5]) / 10000 / 10000), 2)) + "亿"
                    except:
                        pass
                    result.append(i)
                if is_return:
                    return result
                logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 近 30 分钟上证指数:")
                for line_msg in format_table_msg([
                    [
                        "时间", "价格", "涨跌额", "涨跌幅", "成交量", "成交额"
                    ],
                    *result
                ]).split("\n"):
                    logger.info(line_msg)

    def A_html(self):
        result = self.A(True)
        info = ""
        for i in result:
            info += get_tbody(i)
        return get_result_html(
            ["时间", "价格", "涨跌额", "涨跌幅", "成交量", "成交额"]
        ).format(tbody=info) + style

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MaYiFund')
    parser.add_argument('-a', '--add', action='store_true', help='添加基金代码')
    parser.add_argument("-d", "--delete", action="store_true", help="删除基金代码")
    args = parser.parse_args()

    mayi_fund = MaYiFund()
    mayi_fund.run(args.add, args.delete)
