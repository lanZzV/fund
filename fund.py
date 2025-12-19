# -*- coding: UTF-8 -*-

import argparse
import datetime
import json
import os
import re
import threading
import time

import requests
import urllib3
from loguru import logger
from tabulate import tabulate

from module_html import get_table_html

sem = threading.Semaphore(5)

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
        self.result = []

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
        res = self.session.get("https://www.fund123.cn/fund", headers={
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
                    "Origin": "https://www.fund123.cn",
                    "Referer": "https://www.fund123.cn/fund",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    "X-API-Key": "foobar",
                    "accept": "json"
                }
                url = "https://www.fund123.cn/api/fund/searchFund"
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
                        "fund_name": fund_name,
                        "is_hold": False
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

    def search_one_code(self, fund, fund_data, is_return):
        with sem:
            try:
                fund_key = fund_data["fund_key"]
                fund_name = fund_data["fund_name"]

                headers = {
                    "Accept-Language": "zh-CN,zh;q=0.9",
                    "Connection": "keep-alive",
                    "Content-Type": "application/json",
                    "Origin": "https://www.fund123.cn",
                    "Referer": "https://www.fund123.cn/fund",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                    "X-API-Key": "foobar",
                    "accept": "json"
                }
                url = f"https://www.fund123.cn/matiaria?fundCode={fund}"
                response = self.session.get(url, headers=headers, timeout=10, verify=False)
                dayOfGrowth = re.findall('\"dayOfGrowth\"\:\"(.*?)\"', response.text)[0]
                dayOfGrowth = str(round(float(dayOfGrowth), 2)) + "%"

                netValueDate = re.findall('\"netValueDate\"\:\"(.*?)\"', response.text)[0]
                if is_return:
                    dayOfGrowth = f"{dayOfGrowth}({netValueDate})"

                url = "https://www.fund123.cn/api/fund/queryFundQuotationCurves"
                params = {
                    "_csrf": self._csrf
                }
                data = {
                    "productId": fund_key,
                    "dateInterval": "ONE_MONTH"
                }
                response = self.session.post(url, headers=headers, params=params, json=data, timeout=10, verify=False)
                if not response.json()["success"]:
                    logger.error(f"查询基金代码【{fund}】失败: {response.text.strip()}")
                    return
                points = response.json()["points"]
                points = [x for x in points if x["type"] == "fund"]

                montly_growth = []
                last_rate = None
                for point in points:
                    if last_rate is None:
                        last_rate = point["rate"]
                        continue
                    now_rate = point["rate"]
                    if now_rate >= last_rate:
                        montly_growth.append(f"涨,{now_rate}")
                    else:
                        montly_growth.append(f"跌,{now_rate}")
                    last_rate = now_rate

                montly_growth = montly_growth[::-1]
                montly_growth_day = sum(1 for x in montly_growth if x[0] == "涨")
                montly_growth_day_count = len(montly_growth)
                consecutive_count = 1
                start_rate = montly_growth[0].split(",")[1]
                montly_growth_rate = str(round(round(float(start_rate), 4) * 100, 2)) + "%"
                end_rate = 0
                for i in montly_growth[1:]:
                    if i[0] == montly_growth[0][0]:
                        consecutive_count += 1
                    else:
                        end_rate = i.split(",")[1]
                        break

                montly_growth_day = str(montly_growth_day)
                if "-" in montly_growth_rate:
                    if not is_return:
                        montly_growth_day = "\033[1;32m" + montly_growth_day
                else:
                    if not is_return:
                        montly_growth_day = "\033[1;31m" + montly_growth_day

                consecutive_growth = str(round(round(float(start_rate) - float(end_rate), 4) * 100, 2)) + "%"
                if montly_growth[0][0] == "跌":
                    if not is_return:
                        consecutive_count = "\033[1;32m" + str(-consecutive_count)
                        consecutive_growth = "\033[1;32m" + str(consecutive_growth)
                    else:
                        consecutive_count = str(-consecutive_count)
                        consecutive_growth = str(consecutive_growth)
                else:
                    if not is_return:
                        consecutive_count = "\033[1;31m" + str(consecutive_count)
                        consecutive_growth = "\033[1;31m" + str(consecutive_growth)
                    else:
                        consecutive_count = str(consecutive_count)
                        consecutive_growth = str(consecutive_growth)

                url = "https://www.fund123.cn/api/fund/queryFundEstimateIntraday"
                params = {
                    "_csrf": self._csrf
                }
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
                            "%H:%M:%S"
                        )
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
                    if not is_return:
                        if self.CACHE_MAP[fund].get("is_hold", False):
                            fund_name = "⭐ " + fund_name
                    self.result.append([
                        fund, fund_name, now_time, forecastGrowth, dayOfGrowth, consecutive_count, consecutive_growth,
                        f"{montly_growth_day} / {montly_growth_day_count}", montly_growth_rate
                    ])
                else:
                    logger.error(f"查询基金代码【{fund}】失败: {response.text.strip()}")
            except Exception as e:
                logger.error(f"查询基金代码【{fund}】失败: {e}")

    def search_code(self, is_return=False):
        self.result = []
        threads = []
        for fund, fund_data in self.CACHE_MAP.items():
            t = threading.Thread(target=self.search_one_code, args=(fund, fund_data, is_return))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        if is_return:
            self.result = sorted(
                self.result,
                key=lambda x: float(x[3].replace("%", "")) if x[3] != "N/A" else -99,
                reverse=True
            )
            return self.result
        if self.result:
            self.result = sorted(
                self.result,
                key=lambda x: float(x[3].split("m")[1].replace("%", "")) if x[3] != "N/A" else -99,
                reverse=True
            )
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 基金估值信息:")
            for line_msg in format_table_msg([
                [
                    "基金代码", "基金名称", "估值时间", "估值", "日涨幅", "连涨天数", "连涨幅", "涨/总 (近30天)", "总涨幅"
                ],
                *self.result
            ]).split("\n"):
                logger.info(line_msg)

    def fund_html(self):
        result = self.search_code(True)
        return get_table_html(
            [
                "基金代码", "基金名称", "估值时间", "估值", "日涨幅", "连涨天数", "连涨幅", "涨/总 (近30天)", "总涨幅"
            ],
            result,
            sortable_columns=[3, 4, 5, 6, 7, 8]
        )

    def run(self, is_add=False, is_delete=False, is_hold=False, is_not_hold=False):
        if not self.CACHE_MAP:
            logger.warning("暂无缓存代码信息, 请先添加基金代码")
            is_add = True
            is_delete = False
            is_hold = False
            is_not_hold = False
        if is_not_hold:
            hold_codes = [code for code, data in self.CACHE_MAP.items() if data.get("is_hold", False)]
            if not hold_codes:
                logger.warning("暂无持有标注基金代码")
                return
            logger.debug(f"当前持有标注基金代码: {hold_codes}")
            logger.debug("请输入基金代码, 多个基金代码以英文逗号分隔:")
            codes = input()
            codes = codes.split(",")
            codes = [code.strip() for code in codes if code.strip()]
            for code in codes:
                try:
                    if code in self.CACHE_MAP:
                        self.CACHE_MAP[code]["is_hold"] = False
                        logger.info(f"删除持有标注【{code}】成功")
                    else:
                        logger.warning(f"删除持有标注【{code}】失败: 不存在该基金代码")
                except Exception as e:
                    logger.error(f"删除持有标注【{code}】失败: {e}")
            self.save_cache()
            return
        if is_hold:
            now_codes = list(self.CACHE_MAP.keys())
            logger.debug(f"当前缓存基金代码: {now_codes}")
            logger.debug("请输入基金代码, 多个基金代码以英文逗号分隔:")
            codes = input()
            codes = codes.split(",")
            codes = [code.strip() for code in codes if code.strip()]
            for code in codes:
                try:
                    if code in self.CACHE_MAP:
                        self.CACHE_MAP[code]["is_hold"] = True
                        logger.info(f"添加持有标注【{code}】成功")
                    else:
                        logger.warning(f"添加持有标注【{code}】失败: 不存在该基金代码, 请先添加该基金代码")
                except Exception as e:
                    logger.error(f"添加持有标注【{code}】失败: {e}")
            self.save_cache()
            return

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
            self.real_time_gold()
            self.gold()
            self.seven_A()
            self.A()
            self.get_market_info()
            self.search_code()
            # 添加AI分析
            self.ai_analysis()

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
        return get_table_html(
            ["指数名称", "指数", "涨跌幅"],
            result,
        )

    def gold_html(self):
        result = self.gold(True)
        return get_table_html(
            ["日期", "中国黄金基础金价", "周大福金价", "中国黄金基础金价涨跌", "周大福金价涨跌"],
            result
        )

    @staticmethod
    def bk(is_return=False):
        bk_result = []
        try:
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "cb": "",
                "fid": "f62",
                "po": "1",
                "pz": "100",
                "pn": "1",
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "ut": "8dec03ba335b81bf4ebdf7b29ec27d15",
                "fs": "m:90 t:2",
                "fields": "f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124,f1,f13"
            }
            response = requests.get(url, params=params, timeout=10, verify=False)
            if str(response.json()["data"]):
                data = response.json()["data"]
                for bk in data["diff"]:
                    ratio = str(bk["f3"]) + "%"
                    if not is_return:
                        if "-" in ratio:
                            ratio = "\033[1;32m" + ratio
                        else:
                            ratio = "\033[1;31m" + ratio
                    add_market_cap = bk["f62"]
                    add_market_cap = str(round(add_market_cap / 100000000, 2)) + "亿"
                    if not is_return:
                        if "-" in add_market_cap:
                            add_market_cap = "\033[1;32m" + add_market_cap
                        else:
                            add_market_cap = "\033[1;31m" + add_market_cap
                    add_market_cap2 = bk["f84"]
                    add_market_cap2 = str(round(add_market_cap2 / 100000000, 2)) + "亿"
                    if not is_return:
                        if "-" in add_market_cap2:
                            add_market_cap2 = "\033[1;32m" + add_market_cap2
                        else:
                            add_market_cap2 = "\033[1;31m" + add_market_cap2
                    bk_result.append([
                        bk["f14"],
                        ratio,
                        add_market_cap,
                        str(round(bk["f184"], 2)) + "%",
                        add_market_cap2,
                        str(round(bk["f87"], 2)) + "%",
                    ])
        except:
            pass

        bk_result = sorted(
            bk_result,
            key=lambda x: float(x[1].split("m")[-1].replace("%", "")) if x[3] != "N/A" else -99,
            reverse=True
        )
        if is_return:
            return bk_result
        if bk_result:
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 行业板块:")
            for line_msg in format_table_msg([
                [
                    "板块名称", "今日涨跌幅", "今日主力净流入", "今日主力净流入占比", "今日小单净流入", "今日小单流入占比"
                ],
                *bk_result
            ]).split("\n"):
                logger.info(line_msg)

    def bk_html(self):
        result = self.bk(True)
        return get_table_html(
            ["板块名称", "今日涨跌幅", "今日主力净流入", "今日主力净流入占比", "今日小单净流入", "今日小单流入占比"],
            result,
            sortable_columns=[1, 2, 3, 4, 5]
        )

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

    @staticmethod
    def real_time_gold(is_return=False):
        headers = {
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "referer": "https://quote.cngold.org/gjs/gjhj.html",
            "sec-ch-ua": "\"Not;A=Brand\";v=\"99\", \"Google Chrome\";v=\"139\", \"Chromium\";v=\"139\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "script",
            "sec-fetch-mode": "no-cors",
            "sec-fetch-site": "cross-site",
            "sec-fetch-storage-access": "active",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }
        url = "https://api.jijinhao.com/quoteCenter/realTime.htm"
        params = {
            "codes": "JO_71,JO_92233",
            "_": str(int(time.time() * 1000))
        }
        response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
        data = json.loads(response.text.replace("var quote_json = ", ""))
        result = [[], []]
        columns = ["名称", "最新价", "涨跌额", "涨跌幅", "开盘价", "最高价", "最低价", "昨收价", "更新时间", "单位"]
        if data:
            data1 = data["JO_71"]
            data2 = data["JO_92233"]
            keys = ["showName", "q63", "q70", "q80", "q1", "q3", "q4", "q2", "time", "unit"]
            for key in keys:
                if key == "time":
                    t = data1[key]
                    date = datetime.datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    result[0].append(date)
                    t = data2[key]
                    date = datetime.datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    result[1].append(date)
                else:
                    value1 = data1.get(key, "N/A")
                    value2 = data2.get(key, "N/A")
                    if not isinstance(value1, str):
                        value1 = round(value1, 2)
                    if not isinstance(value2, str):
                        value2 = round(value2, 2)
                    value1 = str(value1)
                    value2 = str(value2)
                    if key == "q70":
                        if not is_return:
                            if "-" in value1:
                                value1 = "\033[1;32m" + value1
                            else:
                                value1 = "\033[1;31m" + value1
                            if "-" in value2:
                                value2 = "\033[1;32m" + value2
                            else:
                                value2 = "\033[1;31m" + value2
                    if key == "q80":
                        value1 = value1 + "%"
                        value2 = value2 + "%"
                    result[0].append(value1)
                    result[1].append(value2)

        if is_return:
            return result
        if result and result[0] and result[1]:
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 实时金价:")
            for line_msg in format_table_msg([
                columns,
                result[0],
                result[1]
            ]).split("\n"):
                logger.info(line_msg)

    def real_time_gold_html(self):
        result = self.real_time_gold(True)
        return get_table_html(
            ["名称", "最新价", "涨跌额", "涨跌幅", "开盘价", "最高价", "最低价", "昨收价", "更新时间", "单位"],
            result
        )

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
                    result.append(i[:-2])
                if is_return:
                    return result
                logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 近 30 分钟上证指数:")
                for line_msg in format_table_msg([
                    [
                        "时间", "指数", "涨跌额", "涨跌幅", "成交量", "成交额"
                    ],
                    *result
                ]).split("\n"):
                    logger.info(line_msg)

    def A_html(self):
        result = self.A(True)
        return get_table_html(
            ["时间", "指数", "涨跌额", "涨跌幅", "成交量", "成交额"],
            result
        )

    def seven_A(self, is_return=False):
        url = "https://finance.pae.baidu.com/sapi/v1/metrictrend"
        params = {
            "financeType": "index",
            "market": "ab",
            "code": "000001",
            "targetType": "market",
            "metric": "amount",
            "finClientType": "pc"
        }
        response = self.baidu_session.get(url, params=params, timeout=10, verify=False)
        if str(response.json()["ResultCode"]) == "0":
            trend = response.json()["Result"]["trend"]
            result = []
            # 近七天的日期
            today = datetime.datetime.now()
            dates = [(today - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(8)]
            for i in dates:
                total = trend[0]
                ss = trend[1]
                sz = trend[2]
                bj = trend[3]
                total_data = [x for x in total["content"] if x["marketDate"] == i]
                ss_data = [x for x in ss["content"] if x["marketDate"] == i]
                sz_data = [x for x in sz["content"] if x["marketDate"] == i]
                bj_data = [x for x in bj["content"] if x["marketDate"] == i]
                if total_data and ss_data and sz_data and bj_data:
                    total_amount = total_data[0]["data"]["amount"] + "亿"
                    ss_amount = ss_data[0]["data"]["amount"] + "亿"
                    sz_amount = sz_data[0]["data"]["amount"] + "亿"
                    bj_amount = bj_data[0]["data"]["amount"] + "亿"
                    result.append([
                        i, total_amount, ss_amount, sz_amount, bj_amount
                    ])

            if is_return:
                return result
            if result:
                logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 近 7 日成交量:")
                for line_msg in format_table_msg([
                    [
                        "日期", "总成交额", "上交所", "深交所", "北交所"
                    ],
                    *result
                ]).split("\n"):
                    logger.info(line_msg)

    def seven_A_html(self):
        result = self.seven_A(True)
        return get_table_html(
            ["日期", "总成交额", "上交所", "深交所", "北交所"],
            result,
            [1, 2, 3, 4]
        )

    def init_langchain_llm(self):
        """初始化LangChain LLM"""
        try:
            from langchain_openai import ChatOpenAI

            # 从环境变量读取配置
            api_base = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
            api_key = os.getenv("LLM_API_KEY", "")
            model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

            if not api_key:
                logger.warning("未配置LLM_API_KEY环境变量，跳过AI分析")
                return None

            # 创建ChatOpenAI实例
            llm = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                openai_api_base=api_base,
                temperature=0.7,
                max_tokens=2000,
                request_timeout=60
            )

            return llm

        except Exception as e:
            logger.error(f"初始化LangChain LLM失败: {e}")
            return None

    def ai_analysis(self):
        """使用LangChain提示链进行AI分析"""
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser

            logger.debug("正在收集数据进行AI分析...")

            # 初始化LLM
            llm = self.init_langchain_llm()
            if llm is None:
                return

            # 收集市场数据
            market_data = self.get_market_info(is_return=True)
            market_summary = "主要市场指数：\n"
            for item in market_data[:10]:
                market_summary += f"- {item[0]}: {item[1]} ({item[2]})\n"

            # 收集板块数据
            bk_data = self.bk(is_return=True)
            top_sectors = "涨幅前5板块：\n"
            for i, item in enumerate(bk_data[:5]):
                top_sectors += f"{i+1}. {item[0]}: {item[1]}, 主力净流入{item[2]}, 主力流入占比{item[3]}\n"

            bottom_sectors = "跌幅后5板块：\n"
            for i, item in enumerate(bk_data[-5:]):
                bottom_sectors += f"{i+1}. {item[0]}: {item[1]}, 主力净流入{item[2]}, 主力流入占比{item[3]}\n"

            # 收集基金数据
            fund_data = []
            for fund_code, fund_info in self.CACHE_MAP.items():
                for fund in self.result:
                    if fund[0] == fund_code:
                        fund_data.append({
                            "code": fund[0],
                            "name": fund[1].replace("⭐ ", "").replace("\033[1;31m", "").replace("\033[1;32m", ""),
                            "forecast": fund[3].replace("\033[1;31m", "").replace("\033[1;32m", ""),
                            "growth": fund[4].replace("\033[1;31m", "").replace("\033[1;32m", ""),
                            "consecutive": fund[5].replace("\033[1;31m", "").replace("\033[1;32m", ""),
                            "consecutive_growth": fund[6].replace("\033[1;31m", "").replace("\033[1;32m", ""),
                            "month_stats": fund[7],
                            "month_growth": fund[8].replace("\033[1;31m", "").replace("\033[1;32m", ""),
                            "is_hold": fund_info.get("is_hold", False)
                        })
                        break

            # 构建基金摘要
            fund_summary = f"自选基金总数: {len(fund_data)}只\n\n"

            # 持有基金
            hold_funds = [f for f in fund_data if f["is_hold"]]
            if hold_funds:
                fund_summary += "持有基金：\n"
                for i, f in enumerate(hold_funds, 1):
                    fund_summary += f"{i}. {f['name']}: 估值{f['forecast']}, 日涨幅{f['growth']}, 连续{f['consecutive']}天, 近30天{f['month_stats']}\n"
                fund_summary += "\n"

            # 表现最好的基金
            top_funds = sorted(fund_data, key=lambda x: float(x["forecast"].replace("%", "")) if x["forecast"] != "N/A" else -999, reverse=True)[:5]
            fund_summary += "今日涨幅前5的基金：\n"
            for i, f in enumerate(top_funds, 1):
                hold_mark = "【持有】" if f["is_hold"] else ""
                fund_summary += f"{i}. {hold_mark}{f['name']}: 估值{f['forecast']}, 日涨幅{f['growth']}\n"

            # 创建提示链 - 市场趋势分析
            trend_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位资深金融分析师，擅长宏观市场分析和趋势判断。请从专业角度深入分析市场走势。"),
                ("user", """请基于以下市场数据，进行深入的市场趋势分析：

{market_summary}

{top_sectors}

请从以下角度进行分析（输出300-400字）：
1. 分析主要指数的走势特征和相互关系
2. 判断当前市场所处的阶段（上涨/震荡/调整）
3. 分析市场情绪和资金流向特征
4. 对比国内外市场表现，指出关键影响因素

请用专业、客观的语言输出，使用纯文本格式（不要使用markdown语法如#、*、**、表格等），适合命令行展示。""")
            ])

            # 创建提示链 - 板块机会分析
            sector_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位行业研究专家，精通各个行业板块的投资逻辑和周期规律。"),
                ("user", """请基于以下板块数据，深入分析行业投资机会：

涨幅领先板块：
{top_sectors}

跌幅板块：
{bottom_sectors}

请从以下角度进行分析（输出300-400字）：
1. 分析领涨板块的共同特征和驱动因素
2. 判断这些板块的行情可持续性
3. 结合资金流入情况，评估板块强度
4. 提示哪些板块值得重点关注，给出配置建议
5. 分析弱势板块是否存在反转机会

请用专业、深入的语言输出，使用纯文本格式（不要使用markdown语法如#、*、**、表格等），适合命令行展示。""")
            ])

            # 创建提示链 - 基金组合建议
            portfolio_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位专业的基金投资顾问，擅长基金组合配置和风险管理。"),
                ("user", """请基于以下基金持仓和表现数据，给出投资建议：

{fund_summary}

当前市场环境：
{market_summary}

请从以下角度给出建议（输出300-400字）：
1. 评估当前持仓基金的表现和风险特征
2. 分析持仓基金与市场环境的匹配度
3. 给出具体的调仓建议（增持/减持/持有）
4. 对表现优异的基金，分析背后原因和可持续性
5. 提示仓位配置和风险敞口的优化方向

请给出具体、可操作的建议，使用纯文本格式（不要使用markdown语法如#、*、**、表格等），适合命令行展示。""")
            ])

            # 创建提示链 - 风险提示
            risk_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位风险管理专家，擅长识别市场风险和制定风控策略。"),
                ("user", """请基于当前市场数据，进行全面的风险分析：

市场概况：
{market_summary}

板块表现：
{top_sectors}
{bottom_sectors}

基金持仓：
{fund_summary}

请从以下角度进行风险分析（输出250-350字）：
1. 识别当前市场的主要风险点
2. 分析可能引发调整的触发因素
3. 评估持仓基金的风险暴露
4. 给出风险防控建议和应对策略
5. 提示需要关注的风险信号

请客观、谨慎地提示风险，使用纯文本格式（不要使用markdown语法如#、*、**、表格等），适合命令行展示。""")
            ])

            # 创建输出解析器
            output_parser = StrOutputParser()

            # 执行四个维度的分析
            logger.info("正在进行市场趋势分析...")
            trend_chain = trend_prompt | llm | output_parser
            trend_analysis = trend_chain.invoke({
                "market_summary": market_summary,
                "top_sectors": top_sectors
            })

            logger.info("正在进行板块机会分析...")
            sector_chain = sector_prompt | llm | output_parser
            sector_analysis = sector_chain.invoke({
                "top_sectors": top_sectors,
                "bottom_sectors": bottom_sectors
            })

            logger.info("正在进行基金组合分析...")
            portfolio_chain = portfolio_prompt | llm | output_parser
            portfolio_analysis = portfolio_chain.invoke({
                "fund_summary": fund_summary,
                "market_summary": market_summary
            })

            logger.info("正在进行风险分析...")
            risk_chain = risk_prompt | llm | output_parser
            risk_analysis = risk_chain.invoke({
                "market_summary": market_summary,
                "top_sectors": top_sectors,
                "bottom_sectors": bottom_sectors,
                "fund_summary": fund_summary
            })

            # 定义文本格式化函数
            def format_text(text, max_width=60):
                """将长文本按照标点符号智能分行，保持可读性"""
                lines = []
                # 先去掉多余的空行，合并成一段
                text = " ".join(line.strip() for line in text.split("\n") if line.strip())

                # 按句子分割（句号、问号、感叹号、分号）
                current_line = ""
                for char in text:
                    current_line += char
                    # 遇到句子结束符号且长度超过30字符，或长度超过max_width
                    if (char in "。！？；" and len(current_line) > 30) or len(current_line) >= max_width:
                        lines.append(current_line.strip())
                        current_line = ""

                # 添加剩余内容
                if current_line.strip():
                    lines.append(current_line.strip())

                return lines

            # 输出完整的AI分析报告
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 📊 AI市场深度分析报告")
            logger.info("=" * 80)

            logger.info("1️⃣ 市场整体趋势分析")
            logger.info("-" * 80)
            for line in format_text(trend_analysis):
                logger.info(line)

            logger.info("=" * 80)
            logger.info("2️⃣ 行业板块机会分析")
            logger.info("-" * 80)
            for line in format_text(sector_analysis):
                logger.info(line)

            logger.info("=" * 80)
            logger.info("3️⃣ 基金组合投资建议")
            logger.info("-" * 80)
            for line in format_text(portfolio_analysis):
                logger.info(line)

            logger.info("=" * 80)
            logger.info("4️⃣ 风险提示与应对")
            logger.info("-" * 80)
            for line in format_text(risk_analysis):
                logger.info(line)

            logger.info("=" * 80)
            logger.info("💡 提示：以上分析由AI生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"AI分析过程出错: {e}")
            import traceback
            logger.error(traceback.format_exc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MaYiFund')
    parser.add_argument('-a', '--add', action='store_true', help='添加基金代码')
    parser.add_argument("-d", "--delete", action="store_true", help="删除基金代码")
    parser.add_argument("-c", "--hold", action="store_true", help="添加持有基金标注")
    parser.add_argument("-b", "--not_hold", action="store_true", help="删除持有基金标注")
    args = parser.parse_args()

    mayi_fund = MaYiFund()
    mayi_fund.run(args.add, args.delete, args.hold, args.not_hold)
