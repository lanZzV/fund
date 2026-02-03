# -*- coding: UTF-8 -*-

import argparse
import datetime
import json
import os
import random
import re
import threading
import time

import requests
import urllib3
from curl_cffi import requests as curl_requests
from dotenv import load_dotenv
from loguru import logger
from tabulate import tabulate

from src.ai_analyzer import AIAnalyzer
from src.module_html import get_table_html

# 加载环境变量
load_dotenv()

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

    # 板块分类映射
    MAJOR_CATEGORIES = {
        "科技": ["人工智能", "半导体", "云计算", "5G", "光模块", "CPO", "F5G", "通信设备", "PCB", "消费电子",
                 "计算机", "软件开发", "信创", "网络安全", "IT服务", "国产软件", "计算机设备", "光通信",
                 "算力", "脑机接口", "通信", "电子", "光学光电子", "元件", "存储芯片", "第三代半导体",
                 "光刻胶", "电子化学品", "LED", "毫米波", "智能穿戴", "东数西算", "数据要素", "国资云",
                 "Web3.0", "AIGC", "AI应用", "AI手机", "AI眼镜", "DeepSeek", "TMT", "科技"],
        "医药健康": ["医药生物", "医疗器械", "生物疫苗", "CRO", "创新药", "精准医疗", "医疗服务", "中药",
                     "化学制药", "生物制品", "基因测序", "超级真菌"],
        "消费": ["食品饮料", "白酒", "家用电器", "纺织服饰", "商贸零售", "新零售", "家居用品", "文娱用品",
                 "婴童", "养老产业", "体育", "教育", "在线教育", "社会服务", "轻工制造", "新消费",
                 "可选消费", "消费", "家电零部件", "智能家居"],
        "金融": ["银行", "证券", "保险", "非银金融", "国有大型银行", "股份制银行", "城商行", "金融"],
        "能源": ["新能源", "煤炭", "石油石化", "电力", "绿色电力", "氢能源", "储能", "锂电池", "电池",
                 "光伏设备", "风电设备", "充电桩", "固态电池", "能源", "煤炭开采", "公用事业", "锂矿"],
        "工业制造": ["机械设备", "汽车", "新能源车", "工程机械", "高端装备", "电力设备", "专用设备",
                     "通用设备", "自动化设备", "机器人", "人形机器人", "汽车零部件", "汽车服务",
                     "汽车热管理", "尾气治理", "特斯拉", "无人驾驶", "智能驾驶", "电网设备", "电机",
                     "高端制造", "工业4.0", "工业互联", "低空经济", "通用航空"],
        "材料": ["有色金属", "黄金股", "贵金属", "基础化工", "钢铁", "建筑材料", "稀土永磁", "小金属",
                 "工业金属", "材料", "大宗商品", "资源"],
        "军工": ["国防军工", "航天装备", "航空装备", "航海装备", "军工电子", "军民融合", "商业航天",
                 "卫星互联网", "航母", "航空机场"],
        "基建地产": ["建筑装饰", "房地产", "房地产开发", "房地产服务", "交通运输", "物流"],
        "环保": ["环保", "环保设备", "环境治理", "垃圾分类", "碳中和", "可控核聚变", "液冷"],
        "传媒": ["传媒", "游戏", "影视", "元宇宙", "超清视频", "数字孪生"],
        "主题": ["国企改革", "一带一路", "中特估", "中字头", "并购重组", "华为", "新兴产业",
                 "国家安防", "安全主题", "农牧主题", "农林牧渔", "养殖业", "猪肉", "高端装备"]
    }

    def __init__(self, user_id=None, db=None):
        self.user_id = user_id  # 用户ID，如果为None则使用文件模式
        self.db = db  # 数据库实例，从外部传入

        self.session = requests.Session()
        self.baidu_session = curl_requests.Session(impersonate="chrome")
        self.baidu_session.headers = {
            "accept": "application/vnd.finance-web.v1+json",
            "accept-language": "zh-CN,zh;q=0.9",
            "acs-token": "1769925606098_1770001866425_B6lkFxZg0PzQhmCXjMfTJUxYBn+en+J7W6a8XGyGMqfxPfIv2RgeZG8wimRzlhAxlZlErxq7wN5rVnCfPj6s/UNiA1a1hfyItpnMrru1lzDxUcicsi2ngKjmVCdUfqRZTcHPnfDWrt4phJcS7Ue+Sh6Ru/GVG+1McDUmf/d52zDv5Q6QM7CAJfHDqsCMP65SNjo63Xljm+aAIzDzKErfG+LOR706MJaZGY2o/hGcESyOy3FcWv+pYNFUjpV3M5sMFNEDa50fWh4J9PZpQDxDQLNhr9LSYunQUxe6wtNEGds85p9V6/yU6v+jA9q0h9/OyQJ/ZuD1lP0VPEACEc4qJvfItxhuK9MfKM+j6Spc/N6Qomh6pZYt6iLJjJp652xIqZurCmxem2Z3Vqu+mcZ9FN1l0qU6dx4hkaTZk3850FE/n6YW+HL74Mp8L+YR/Q2VMV3ARkSzPHgOS9iA6rBAaBiJf2Ni/BTHNSyFxJJjazI=",
            "origin": "https://gushitong.baidu.com",
            "priority": "u=1, i",
            "referer": "https://gushitong.baidu.com/",
            "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }
        self._csrf = ""
        self.report_dir = None  # 默认不输出报告文件（需通过 -o 参数指定）
        self.load_cache()
        self.init()
        self.result = []

    def load_cache(self):
        """加载缓存数据，优先从数据库加载（如果有user_id），否则从文件加载"""
        if self.user_id is not None and self.db is not None:
            # 从数据库加载
            self.CACHE_MAP = self.db.get_user_funds(self.user_id)
        else:
            # 从文件加载（CLI模式）
            if not os.path.exists("cache"):
                os.mkdir("cache")
            if os.path.exists("cache/fund_map.json"):
                with open("cache/fund_map.json", "r", encoding="gbk") as f:
                    self.CACHE_MAP = json.load(f)
        # if self.CACHE_MAP:
        #     logger.debug(f"加载 {len(self.CACHE_MAP)} 个基金代码缓存成功")

    def save_cache(self):
        """保存缓存数据，优先保存到数据库（如果有user_id），否则保存到文件"""
        if self.user_id is not None and self.db is not None:
            # 保存到数据库
            self.db.save_user_funds(self.user_id, self.CACHE_MAP)
        else:
            # 保存到文件（CLI模式）
            with open("cache/fund_map.json", "w", encoding="gbk") as f:
                json.dump(self.CACHE_MAP, f, ensure_ascii=False, indent=4)

    def init(self):
        res = self.session.get("https://www.fund123.cn/fund", headers={
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
        }, timeout=10, verify=False)
        self._csrf = re.findall('\"csrf\":\"(.*?)\"', res.text)[0]

        self.baidu_session.get("https://gushitong.baidu.com/index/ab-000001", headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "referer": "https://gushitong.baidu.com/"
        }, timeout=10, verify=False)
        # self.baidu_session.cookies.update({
        #     "BDUSS": "3hJYkhPNEM3Z2xOeH5TLVU4OEhhU1hPUFYxdVV3V0pkd1VEMEhCTEgxRENMWEJsSVFBQUFBJCQAAAAAAAAAAAEAAAAVl0lPamRrZGpiZGIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMKgSGXCoEhlM",
        #     "BDUSS_BFESS": "3hJYkhPNEM3Z2xOeH5TLVU4OEhhU1hPUFYxdVV3V0pkd1VEMEhCTEgxRENMWEJsSVFBQUFBJCQAAAAAAAAAAAEAAAAVl0lPamRrZGpiZGIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMKgSGXCoEhlM",
        # })

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
                        "is_hold": False,
                        "shares": 0
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

    def mark_fund_sector(self):
        """标记基金板块（独立功能）"""
        now_codes = list(self.CACHE_MAP.keys())
        logger.debug(f"当前缓存基金代码: {now_codes}")
        logger.info("请输入基金代码, 多个基金代码以英文逗号分隔:")
        codes = input()
        codes = codes.split(",")
        codes = [code.strip() for code in codes if code.strip()]

        # 构建板块序号到名称的映射
        all_sectors = []
        for category, sectors in self.MAJOR_CATEGORIES.items():
            for sector in sectors:
                all_sectors.append(sector)

        # 表格形式展示板块分类
        logger.info("板块分类列表:")
        results = []
        for i in range(0, len(all_sectors), 5):
            tmp = all_sectors[i:i + 5]
            tmp = [f"{i + 1 + j}. {tmp[j]}" for j in range(len(tmp))]
            results.append(tmp)
        for line_msg in format_table_msg(results).split("\n"):
            logger.info(line_msg)

        for code in codes:
            try:
                if code not in self.CACHE_MAP:
                    logger.warning(f"标记板块【{code}】失败: 不存在该基金代码, 请先添加该基金代码")
                    continue

                # 选择板块
                logger.info(f"为基金 【{code} {self.CACHE_MAP[code]['fund_name']}】 选择板块:")
                logger.info("请输入板块序号或自定义板块名称 (多个用逗号分隔, 如: 1,3,5 或 新能源,医药 或 1,新能源):")
                sector_input = input().strip()

                if sector_input:
                    sector_items = [s.strip() for s in sector_input.split(",")]
                    selected_sectors = []
                    for item in sector_items:
                        # 尝试解析为序号
                        try:
                            idx = int(item)
                            if 1 <= idx <= len(all_sectors):
                                # 是有效序号，从板块列表中获取
                                selected_sectors.append(all_sectors[idx - 1])
                            else:
                                # 序号超出范围，当作自定义板块名称
                                selected_sectors.append(item)
                        except ValueError:
                            # 不是数字，直接作为自定义板块名称
                            selected_sectors.append(item)

                    if selected_sectors:
                        self.CACHE_MAP[code]["sectors"] = selected_sectors
                        logger.info(f"✓ 已绑定板块: {', '.join(selected_sectors)}")
                    else:
                        logger.info("未选择任何板块")
                else:
                    logger.info("未选择任何板块")

                logger.info(f"标记板块【{code}】成功")

            except Exception as e:
                logger.error(f"标记板块【{code}】失败: {e}")
        self.save_cache()

    def mark_fund_sector_web(self, codes, sectors):
        """标记基金板块（Web API使用）

        Args:
            codes: list of str, 基金代码列表
            sectors: list of str, 板块名称列表
        """
        for code in codes:
            if code in self.CACHE_MAP:
                self.CACHE_MAP[code]["sectors"] = sectors
                logger.info(f"✓ 已为基金 {code} 绑定板块: {', '.join(sectors)}")
            else:
                logger.warning(f"基金代码 {code} 不存在")
        self.save_cache()

    def unmark_fund_sector_web(self, codes):
        """删除基金板块标记（Web API使用）

        Args:
            codes: list of str, 基金代码列表
        """
        for code in codes:
            if code in self.CACHE_MAP:
                self.CACHE_MAP[code]["sectors"] = []
                logger.info(f"✓ 已删除基金 {code} 的板块标记")
            else:
                logger.warning(f"基金代码 {code} 不存在")
        self.save_cache()

    def unmark_fund_sector(self):
        """删除基金板块标记（独立功能）"""
        # 找出所有有板块标记的基金
        marked_codes = [code for code, data in self.CACHE_MAP.items() if data.get("sectors", [])]
        if not marked_codes:
            logger.warning("暂无板块标记的基金代码")
            return

        logger.debug(f"当前有板块标记的基金代码: {marked_codes}")
        logger.debug("请输入基金代码, 多个基金代码以英文逗号分隔:")
        codes = input()
        codes = codes.split(",")
        codes = [code.strip() for code in codes if code.strip()]

        for code in codes:
            try:
                if code in self.CACHE_MAP:
                    if self.CACHE_MAP[code].get("sectors", []):
                        self.CACHE_MAP[code]["sectors"] = []
                        logger.info(f"删除板块标记【{code}】成功")
                    else:
                        logger.warning(f"删除板块标记【{code}】失败: 该基金没有板块标记")
                else:
                    logger.warning(f"删除板块标记【{code}】失败: 不存在该基金代码")
            except Exception as e:
                logger.error(f"删除板块标记【{code}】失败: {e}")
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
                dayOfGrowth = re.findall(r'"dayOfGrowth":"(.*?)"', response.text)[0]
                dayOfGrowth = str(round(float(dayOfGrowth), 2)) + "%"

                netValue = re.findall(r'"netValue":"(.*?)"', response.text)[0]
                netValueDate = re.findall(r'"netValueDate":"(.*?)"', response.text)[0]
                netValue = netValue + f"({netValueDate})"
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
                    # 处理持有标记和板块标记（Web 和 CLI 模式都显示）
                    if self.CACHE_MAP[fund].get("is_hold", False):
                        fund_name = "⭐ " + fund_name
                    # 处理板块标记（独立于持有状态）
                    sectors = self.CACHE_MAP[fund].get("sectors", [])
                    if sectors:
                        sector_str = ",".join(sectors)
                        fund_name = f"({sector_str}) {fund_name}"
                    # 合并连涨天数和连涨幅
                    consecutive_info = f"{consecutive_count}天 {consecutive_growth}"
                    # 合并近30天涨跌和总涨幅
                    monthly_info = f"{montly_growth_day}/{montly_growth_day_count} {montly_growth_rate}"
                    self.result.append([
                        fund, fund_name, now_time, netValue, forecastGrowth, dayOfGrowth, consecutive_info, monthly_info
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
                key=lambda x: float(x[4].replace("%", "")) if x[4] != "N/A" else -99,
                reverse=True
            )
            return self.result

        if self.result:
            self.result = sorted(
                self.result,
                key=lambda x: float(x[4].split("m")[1].replace("%", "")) if x[4] != "N/A" else -99,
                reverse=True
            )

            # 计算并显示持仓统计
            position_summary = self.calculate_position_summary()
            if position_summary:
                # 收益统计表格
                logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 收益统计:")

                # 准备表格数据
                total_value = position_summary['total_value']
                est_gain = position_summary['estimated_gain']
                est_gain_pct = position_summary['estimated_gain_pct']
                act_gain = position_summary['actual_gain']
                act_gain_pct = position_summary['actual_gain_pct']
                settled_value = position_summary.get('settled_value', 0)

                est_color = '\033[1;31m' if est_gain >= 0 else '\033[1;32m'
                act_color = '\033[1;31m' if act_gain >= 0 else '\033[1;32m'
                est_sign = '+' if est_gain >= 0 else ''
                act_sign = '+' if act_gain >= 0 else ''

                # 今日实际涨跌：只有当有基金净值更新至今日时才显示数值
                if settled_value > 0:
                    actual_gain_str = f"{act_color}{act_sign}¥{act_gain:,.2f} ({act_sign}{act_gain_pct:.2f}%)\033[0m"
                else:
                    actual_gain_str = "\033[1;90m净值未更新\033[0m"  # 灰色显示

                summary_table = [
                    ["总持仓金额", f"¥{total_value:,.2f}"],
                    ["今日预估涨跌", f"{est_color}{est_sign}¥{est_gain:,.2f} ({est_sign}{est_gain_pct:.2f}%)\033[0m"],
                    ["今日实际涨跌", actual_gain_str],
                ]

                for line_msg in format_table_msg(summary_table).split("\n"):
                    logger.info(line_msg)

                # 显示每个基金的详细涨跌（表格格式）
                if 'fund_details' in position_summary and position_summary['fund_details']:
                    logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 分基金涨跌明细:")

                    # 准备表格数据
                    table_data = []
                    for detail in position_summary['fund_details']:
                        est_color = '\033[1;31m' if detail['estimated_gain'] >= 0 else '\033[1;32m'
                        act_color = '\033[1;31m' if detail['actual_gain'] >= 0 else '\033[1;32m'
                        est_sign = '+' if detail['estimated_gain'] >= 0 else ''
                        act_sign = '+' if detail['actual_gain'] >= 0 else ''

                        table_data.append([
                            detail['code'],
                            detail['name'],
                            f"{detail['shares']:,.2f}",
                            f"¥{detail['position_value']:,.2f}",
                            f"{est_color}{est_sign}¥{detail['estimated_gain']:,.2f}\033[0m",
                            f"{est_color}{est_sign}{detail['estimated_gain_pct']:.2f}%\033[0m",
                            f"{act_color}{act_sign}¥{detail['actual_gain']:,.2f}\033[0m",
                            f"{act_color}{act_sign}{detail['actual_gain_pct']:.2f}%\033[0m",
                        ])

                    for line_msg in format_table_msg([
                        ["基金代码", "基金名称", "持仓份额", "持仓市值", "预估收益", "预估涨跌", "实际收益", "实际涨跌"],
                        *table_data
                    ]).split("\n"):
                        logger.info(line_msg)

            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 基金估值信息:")
            for line_msg in format_table_msg([
                [
                    "基金代码", "基金名称", "当前时间", "净值", "估值", "日涨幅", "连涨/跌", "近30天"
                ],
                *self.result
            ]).split("\n"):
                logger.info(line_msg)

    def calculate_position_summary(self):
        """计算持仓统计信息

        Returns:
            dict: 持仓统计数据，如果没有持仓则返回None
        """
        total_value = 0
        estimated_gain = 0
        actual_gain = 0
        settled_value = 0
        today = datetime.datetime.now().strftime("%Y-%m-%d")

        # 判断是否是9:30之前或今日净值未更新
        now = datetime.datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        before_market_open = current_hour < 9 or (current_hour == 9 and current_minute < 30)

        # 存储每个基金的详细涨跌信息
        fund_details = []

        for fund_data in self.result:
            # fund_data format: [code, name, time, net_value, estimated_growth, day_growth, consecutive_info, monthly_info]
            shares = self.CACHE_MAP.get(fund_data[0], {}).get('shares', 0)
            if shares <= 0:
                continue

            try:
                fund_code = fund_data[0]
                fund_name = fund_data[1]

                # 解析净值 "1.234(2025-02-02)"
                net_value_str = fund_data[3]
                net_value = float(net_value_str.split('(')[0])
                net_value_date = net_value_str.split('(')[1].replace(')', '')

                # 解析估值增长率 "+1.23%" or "N/A"
                estimated_growth_str = fund_data[4]
                if estimated_growth_str != "N/A":
                    # 移除ANSI颜色代码
                    estimated_growth_str = estimated_growth_str.replace('\033[1;31m', '').replace('\033[1;32m',
                                                                                                  '').replace('%', '')
                    estimated_growth = float(estimated_growth_str)
                else:
                    estimated_growth = 0

                # 解析日涨幅 "+1.23%" or "N/A"
                day_growth_str = fund_data[5]
                if day_growth_str != "N/A":
                    # 移除ANSI颜色代码
                    day_growth_str = day_growth_str.replace('\033[1;31m', '').replace('\033[1;32m', '').replace('%', '')
                    day_growth = float(day_growth_str)
                else:
                    day_growth = 0

                # 计算持仓市值
                position_value = shares * net_value
                total_value += position_value

                # 计算预估涨跌（始终计算）
                fund_est_gain = position_value * estimated_growth / 100
                estimated_gain += fund_est_gain

                # 计算实际涨跌
                # 逻辑：只有当净值日期是今天时（今日净值已更新），才计算实际涨跌
                fund_act_gain = 0
                if net_value_date == today:
                    # 今日净值已更新，计算实际收益
                    fund_act_gain = position_value * day_growth / 100
                    actual_gain += fund_act_gain
                    settled_value += position_value

                # 保存每个基金的详细信息
                fund_details.append({
                    'code': fund_code,
                    'name': fund_name,
                    'shares': shares,
                    'position_value': position_value,
                    'estimated_gain': fund_est_gain,
                    'estimated_gain_pct': (fund_est_gain / position_value * 100) if position_value > 0 else 0,
                    'actual_gain': fund_act_gain,
                    'actual_gain_pct': (fund_act_gain / position_value * 100) if position_value > 0 else 0,
                })

            except (ValueError, IndexError, AttributeError) as e:
                logger.warning(f"解析基金数据失败: {fund_data[0]}, {e}")
                continue

        # 如果没有持仓，返回None
        if total_value == 0:
            return None

        return {
            'total_value': total_value,
            'estimated_gain': estimated_gain,
            'estimated_gain_pct': (estimated_gain / total_value * 100) if total_value > 0 else 0,
            'actual_gain': actual_gain,
            'actual_gain_pct': (actual_gain / settled_value * 100) if settled_value > 0 else 0,
            'settled_value': settled_value,
            'fund_details': fund_details  # 新增：每个基金的详细涨跌信息
        }

    def modify_shares(self):
        """CLI交互式修改基金持仓份额"""
        now_codes = list(self.CACHE_MAP.keys())
        if not now_codes:
            logger.warning("暂无基金代码，请先添加基金")
            return

        logger.info("当前基金列表:")
        for code, data in self.CACHE_MAP.items():
            shares = data.get('shares', 0)
            logger.info(f"  {code} - {data['fund_name']} (当前份额: {shares})")

        logger.info("\n请输入基金代码, 多个基金代码以英文逗号分隔:")
        codes = input()
        codes = codes.split(",")
        codes = [code.strip() for code in codes if code.strip()]

        for code in codes:
            try:
                if code not in self.CACHE_MAP:
                    logger.warning(f"修改份额【{code}】失败: 不存在该基金代码, 请先添加该基金代码")
                    continue

                fund_name = self.CACHE_MAP[code]['fund_name']
                current_shares = self.CACHE_MAP[code].get('shares', 0)

                logger.info(f"\n基金 【{code} {fund_name}】")
                logger.info(f"当前份额: {current_shares}")
                logger.info("请输入新的份额数量 (输入0表示清空):")
                shares_input = input().strip()

                if shares_input:
                    try:
                        shares = float(shares_input)
                        if shares < 0:
                            logger.warning("份额不能为负数")
                            continue

                        self.CACHE_MAP[code]['shares'] = shares

                        # 如果份额>0，自动标记为持有
                        if shares > 0:
                            self.CACHE_MAP[code]['is_hold'] = True

                        logger.info(f"✓ 已更新份额: {shares}")
                    except ValueError:
                        logger.warning("份额格式错误，请输入数字")
                        continue
                else:
                    logger.info("未输入份额，跳过")

            except Exception as e:
                logger.error(f"修改份额【{code}】失败: {e}")

        self.save_cache()
        logger.info("\n份额修改完成")

    def fund_html(self):
        result = self.search_code(True)
        return get_table_html(
            [
                "基金代码", "基金名称", "当前时间", "净值", "估值", "日涨幅", "连涨/跌", "近30天"
            ],
            result,
            sortable_columns=[5, 6, 7, 8]
        )

    @staticmethod
    def select_fund(bk_id=None, is_return=False):
        if not is_return:
            logger.critical("板块基金查询功能")
        bk_map = {
            "光模块": "BK000651",
            "F5G": "BK000652",
            "CPO": "BK000641",
            "航天装备": "BK000157",
            "通信设备": "BK000176",
            "PCB": "BK000644",
            "小金属": "BK000051",
            "有色金属": "BK000047",
            "工业金属": "BK000049",
            "卫星互联网": "BK000347",
            "元件": "BK000055",
            "商业航天": "BK000313",
            "黄金股": "BK000292",
            "存储芯片": "BK000642",
            "光通信": "BK000501",
            "算力": "BK000601",
            "脑机接口": "BK000663",
            "军工电子": "BK000161",
            "通信": "BK000174",
            "消费电子": "BK000058",
            "风电设备": "BK000147",
            "家电零部件": "BK000072",
            "稀土永磁": "BK000228",
            "贵金属": "BK000050",
            "可控核聚变": "BK000649",
            "5G": "BK000291",
            "游戏": "BK000387",
            "毫米波": "BK000370",
            "电子": "BK000053",
            "人工智能": "BK000217",
            "通用设备": "BK000151",
            "半导体": "BK000054",
            "电机": "BK000144",
            "光刻胶": "BK000331",
            "液冷": "BK000653",
            "智能穿戴": "BK000248",
            "云计算": "BK000266",
            "专用设备": "BK000152",
            "材料": "BK000195",
            "电子化学品": "BK000059",
            "TMT": "BK000388",
            "锂矿": "BK000645",
            "CRO": "BK000353",
            "工业4.0": "BK000236",
            "科技": "BK000391",
            "第三代半导体": "BK000239",
            "DeepSeek": "BK000561",
            "Web3.0": "BK000326",
            "人形机器人": "BK000581",
            "国防军工": "BK000156",
            "传媒": "BK000166",
            "LED": "BK000393",
            "机械设备": "BK000150",
            "高端装备": "BK000441",
            "AI眼镜": "BK000647",
            "医疗服务": "BK000096",
            "特斯拉": "BK000300",
            "汽车热管理": "BK000251",
            "尾气治理": "BK000346",
            "军民融合": "BK000298",
            "电力设备": "BK000143",
            "智能家居": "BK000247",
            "电池": "BK000148",
            "锂电池": "BK000295",
            "电网设备": "BK000149",
            "IT服务": "BK000164",
            "信创": "BK000299",
            "新能源车": "BK000225",
            "汽车零部件": "BK000061",
            "工程机械": "BK000154",
            "高端制造": "BK000481",
            "低空经济": "BK000521",
            "AI手机": "BK000650",
            "东数西算": "BK000325",
            "工业互联": "BK000392",
            "元宇宙": "BK000305",
            "软件开发": "BK000165",
            "AIGC": "BK000369",
            "影视": "BK000286",
            "计算机": "BK000162",
            "新能源": "BK000226",
            "基础化工": "BK000035",
            "华为": "BK000293",
            "新兴产业": "BK000389",
            "无人驾驶": "BK000279",
            "资源": "BK000386",
            "充电桩": "BK000301",
            "大宗商品": "BK000204",
            "国产软件": "BK000216",
            "自动化设备": "BK000155",
            "化学制药": "BK000091",
            "AI应用": "BK000681",
            "国家安防": "BK000232",
            "一带一路": "BK000254",
            "固态电池": "BK000362",
            "基因测序": "BK000321",
            "国资云": "BK000278",
            "建筑材料": "BK000133",
            "计算机设备": "BK000163",
            "机器人": "BK000234",
            "光伏设备": "BK000146",
            "新消费": "BK000621",
            "精准医疗": "BK000484",
            "在线教育": "BK000220",
            "钢铁": "BK000043",
            "氢能源": "BK000227",
            "创新药": "BK000208",
            "并购重组": "BK000483",
            "农牧主题": "BK000200",
            "碳中和": "BK000482",
            "环保设备": "BK000186",
            "安全主题": "BK000194",
            "轻工制造": "BK000085",
            "超级真菌": "BK000367",
            "储能": "BK000230",
            "保险": "BK000129",
            "社会服务": "BK000114",
            "垃圾分类": "BK000309",
            "教育": "BK000120",
            "航空装备": "BK000158",
            "智能驾驶": "BK000461",
            "超清视频": "BK000307",
            "家居用品": "BK000088",
            "数字孪生": "BK000327",
            "环保": "BK000184",
            "商贸零售": "BK000108",
            "医药生物": "BK000090",
            "数据要素": "BK000602",
            "网络安全": "BK000258",
            "环境治理": "BK000185",
            "汽车": "BK000060",
            "生物疫苗": "BK000280",
            "文娱用品": "BK000089",
            "光学光电子": "BK000056",
            "农林牧渔": "BK000026",
            "纺织服饰": "BK000081",
            "建筑装饰": "BK000137",
            "生物制品": "BK000093",
            "航母": "BK000339",
            "非银金融": "BK000127",
            "养老产业": "BK000256",
            "医疗器械": "BK000095",
            "婴童": "BK000303",
            "国有大型银行": "BK000122",
            "国企改革": "BK000203",
            "通用航空": "BK000264",
            "家用电器": "BK000066",
            "汽车服务": "BK000062",
            "金融": "BK000199",
            "中特估": "BK000421",
            "中字头": "BK000308",
            "养殖业": "BK000032",
            "航海装备": "BK000160",
            "体育": "BK000115",
            "通信服务": "BK000175",
            "银行": "BK000121",
            "可选消费": "BK000198",
            "房地产开发": "BK000106",
            "房地产": "BK000105",
            "绿色电力": "BK000209",
            "石油石化": "BK000180",
            "房地产服务": "BK000107",
            "物流": "BK000101",
            "猪肉": "BK000340",
            "证券": "BK000128",
            "公用事业": "BK000097",
            "煤炭": "BK000177",
            "航空机场": "BK000103",
            "煤炭开采": "BK000178",
            "能源": "BK000197",
            "电力": "BK000098",
            "城商行": "BK000124",
            "交通运输": "BK000100",
            "消费": "BK000390",
            "新零售": "BK000262",
            "股份制银行": "BK000123",
            "中药": "BK000092",
            "食品饮料": "BK000074",
            "白酒": "BK000076"
        }
        bk_list = list(bk_map.keys())

        # 如果是返回模式且没有指定板块ID,返回板块列表
        if is_return and bk_id is None:
            return {"bk_map": bk_map, "bk_list": bk_list}

        results = []
        id_map = {}
        for i in range(0, len(bk_list), 5):
            tmp = bk_list[i:i + 5]
            tmp = [str(i + 1 + j) + ". " + tmp[j] for j in range(len(tmp))]
            for j in range(len(tmp)):
                id_map[str(i + 1 + j)] = bk_map[bk_list[i + j]]
            results.append(tmp)

        if not is_return:
            for line_msg in format_table_msg(results).split("\n"):
                logger.info(line_msg)

            logger.debug("请输入要查询的板块序号(单选):")
            bk_id = input()
            while bk_id not in id_map:
                logger.error("输入有误, 请重新输入要查询的板块序号:")
                bk_id = input()

        # 如果是返回模式,直接使用传入的bk_id
        if is_return and bk_id not in id_map:
            # 如果传入的是板块名称而不是ID,尝试查找
            if bk_id in bk_map:
                bk_code = bk_map[bk_id]
            else:
                return {"error": "无效的板块ID或名称"}
        else:
            bk_code = id_map[bk_id]

        url = "https://fund.eastmoney.com/data/FundGuideapi.aspx"

        params = {
            "dt": "4",
            "sd": "",
            "ed": "",
            "tp": bk_code,
            "sc": "1n",
            "st": "desc",
            "pi": "1",
            "pn": "1000",
            "zf": "diy",
            "sh": "list",
            "rnd": str(random.random())
        }

        headers = {
            "Connection": "keep-alive",
            "Referer": "https://fund.eastmoney.com/daogou/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "accept": "*/*",
            "accept-language": "zh-CN,zh;q=0.9",
            "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\""
        }

        response = requests.get(url, headers=headers, params=params, timeout=30)
        text = json.loads(response.text.replace("var rankData =", "").strip())
        datas = text["datas"]
        fund_results = []
        for data in datas:
            data_list = data.split(",")
            fund_results.append([
                (data_list[0] or "---"),
                (data_list[1] or "---"),
                (data_list[3] or "---"),
                (data_list[15] or "---"),
                (data_list[16] or "---") + "（" + (data_list[17] or "---") + "%）",
                (data_list[5] or "---") + "%",
                (data_list[6] or "---") + "%",
                (data_list[7] or "---") + "%",
                (data_list[8] or "---") + "%",
                (data_list[4] or "---") + "%",
                (data_list[9] or "---") + "%",
                (data_list[10] or "---") + "%",
                (data_list[11] or "---") + "%",
                (data_list[24] or "---") + "%"
            ])

        if is_return:
            return {
                "bk_id": bk_id,
                "bk_name": list(bk_map.keys())[int(bk_id) - 1] if bk_id.isdigit() else bk_id,
                "results": fund_results
            }

        logger.critical(f"板块【{bk_id}. {list(bk_map.keys())[int(bk_id) - 1]}】基金列表:")
        for line_msg in format_table_msg([
            [
                "基金代码", "基金名称", "基金类型", "日期", "净值|日增长率", "近1周", "近1月", "近3月", "近6月",
                "今年来", "近1年", "近2年", "近3年", "成立来"
            ],
            *fund_results
        ]).split("\n"):
            logger.info(line_msg)

    def run(self, is_add=False, is_delete=False, is_hold=False, is_not_hold=False, report_dir=None,
            deep_mode=False, fast_mode=False, with_ai=False, select_mode=False, mark_sector=False, unmark_sector=False,
            modify_shares=False):

        if select_mode:
            self.select_fund()
            return

        # 处理修改份额功能
        if modify_shares:
            self.modify_shares()
            return

        # 处理标记板块功能
        if mark_sector:
            self.mark_fund_sector()
            return

        # 处理删除标记板块功能
        if unmark_sector:
            self.unmark_fund_sector()
            return

        # 存储报告目录到实例属性（None 表示不保存报告文件）
        self.report_dir = report_dir

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
            logger.info("请输入基金代码, 多个基金代码以英文逗号分隔:")
            codes = input()
            codes = codes.split(",")
            codes = [code.strip() for code in codes if code.strip()]

            for code in codes:
                try:
                    if code not in self.CACHE_MAP:
                        logger.warning(f"添加持有标注【{code}】失败: 不存在该基金代码, 请先添加该基金代码")
                        continue

                    self.CACHE_MAP[code]["is_hold"] = True
                    logger.info(f"添加持有标注【{code}】成功")

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
            if with_ai:
                self.ai_analysis(deep_mode=deep_mode, fast_mode=fast_mode)

    def get_market_info(self, is_return=False):
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
            response = self.baidu_session.get(url, params=params, timeout=10, verify=False)
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

    def get_market_chart_data(self):
        """返回全球指数图表数据（用于前端Chart.js）"""
        result = self.get_market_info(True)
        # result 格式: [[名称, 指数, 涨跌幅], ...]
        labels = [item[0] for item in result] if result else []
        prices = []
        changes = []
        for item in result:
            try:
                price = float(item[1]) if item[1] else 0
                # 涨跌幅可能包含%和颜色代码，需要清理
                change_str = item[2] if item[2] else "0%"
                change_str = change_str.replace('%', '').replace('\033[1;31m', '').replace('\033[1;32m', '')
                change = float(change_str)
            except:
                price = 0
                change = 0
            prices.append(price)
            changes.append(change)
        return {
            'labels': labels,
            'prices': prices,
            'changes': changes
        }

    def get_volume_chart_data(self):
        """返回成交量趋势图表数据（用于前端Chart.js）"""
        result = self.seven_A(True)
        # result 格式: [[日期, 总成交额, 上交所, 深交所, 北交所], ...]
        labels = []
        total_data = []
        ss_data = []
        sz_data = []
        bj_data = []
        for item in result:
            try:
                labels.append(item[0])  # 日期
                # 清理数据，移除"亿"等字符
                total = float(item[1].replace('亿', '')) if item[1] else 0
                ss = float(item[2].replace('亿', '')) if item[2] else 0
                sz = float(item[3].replace('亿', '')) if item[3] else 0
                bj = float(item[4].replace('亿', '')) if item[4] else 0
                total_data.append(total)
                ss_data.append(ss)
                sz_data.append(sz)
                bj_data.append(bj)
            except:
                continue
        return {
            'labels': labels[::-1],  # 反转顺序，让日期从早到晚
            'total': total_data[::-1],
            'sh': ss_data[::-1],
            'sz': sz_data[::-1],
            'bj': bj_data[::-1]
        }

    def get_timing_chart_data(self):
        """返回上证分时图表数据（用于前端Chart.js）"""
        result = self.A(True)
        # result 格式: [[时间, 指数, 涨跌额, 涨跌幅, 成交量, 成交额], ...]
        labels = []
        prices = []
        volumes = []
        for item in result:
            try:
                labels.append(item[0])  # 时间
                price = float(item[1]) if item[1] else 0
                # 成交量清理"万手"等字符
                vol_str = item[4].replace('万手', '').replace(',', '') if len(item) > 4 and item[4] else '0'
                volume = float(vol_str)
                prices.append(price)
                volumes.append(volume)
            except:
                continue
        return {
            'labels': labels,
            'prices': prices,
            'volumes': volumes
        }

    def gold_html(self):
        result = self.gold(True)
        if result:
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

    def kx(self, is_return=False, count=10):
        url = f"https://finance.pae.baidu.com/selfselect/expressnews?rn={count}&pn=0&tag=A股&finClientType=pc"
        kx_list = []
        try:
            response = self.baidu_session.get(url, timeout=10, verify=False)
            if response.json()["ResultCode"] == "0":
                kx_list = response.json()["Result"]["content"]["list"]
        except:
            pass

        if is_return:
            return kx_list

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

    def kx_html(self):
        result = self.kx(True)
        # 将 result 转换为表格格式
        # kx 返回的是一个 list of dicts，我们需要将其转换为 list of lists
        table_data = []
        for v in result:
            evaluate = v.get("evaluate", "")
            title = v.get("title", v["content"]["items"][0]["data"])
            publish_time = v["publish_time"]
            publish_time = datetime.datetime.fromtimestamp(int(publish_time)).strftime("%H:%M:%S")

            # 格式化评价，添加颜色
            if evaluate == "利好":
                evaluate = f'<span class="positive">{evaluate}</span>'
            elif evaluate == "利空":
                evaluate = f'<span class="negative">{evaluate}</span>'

            table_data.append([publish_time, evaluate, title])

        return get_table_html(
            ["时间", "多空", "快讯内容"],
            table_data
        )

    @staticmethod
    def gold(is_return=False):
        try:
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
                radio = str(gold.get("q70", "N/A"))
                radio2 = "N/A"
                gold2 = {}
                if len(data2) > i:
                    gold2 = data2[i]
                    radio2 = str(gold.get("q70", "N/A"))
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
        except Exception as e:
            logger.error(f"获取贵金属价格失败: {e}")

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
        try:
            url = "https://api.jijinhao.com/quoteCenter/realTime.htm"
            params = {
                "codes": "JO_71,JO_92233,JO_92232,JO_75",
                "_": str(int(time.time() * 1000))
            }
            response = requests.get(url, headers=headers, params=params, timeout=10, verify=False)
            data = json.loads(response.text.replace("var quote_json = ", ""))
            result = [[], [], []]
            columns = ["名称", "最新价", "涨跌额", "涨跌幅", "开盘价", "最高价", "最低价", "昨收价", "更新时间", "单位"]
            if data:
                data1 = data["JO_71"]
                data2 = data["JO_92233"]
                data3 = data["JO_92232"]
                keys = ["showName", "q63", "q70", "q80", "q1", "q3", "q4", "q2", "time", "unit"]
                for key in keys:
                    if key == "time":
                        for i, t in enumerate([data1[key], data2[key], data3[key]]):
                            date = datetime.datetime.fromtimestamp(t / 1000).strftime("%Y-%m-%d %H:%M:%S")
                            result[i].append(date)

                    else:
                        value1 = data1.get(key, "N/A")
                        value2 = data2.get(key, "N/A")
                        value3 = data3.get(key, "N/A")
                        if not isinstance(value1, str):
                            value1 = round(value1, 2)
                        if not isinstance(value2, str):
                            value2 = round(value2, 2)
                        if not isinstance(value3, str):
                            value3 = round(value3, 2)
                        value1 = str(value1)
                        value2 = str(value2)
                        value3 = str(value3)
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
                                if "-" in value3:
                                    value3 = "\033[1;32m" + value3
                                else:
                                    value3 = "\033[1;31m" + value3
                        if key == "q80":
                            value1 = value1 + "%"
                            value2 = value2 + "%"
                            value3 = value3 + "%"
                        result[0].append(value1)
                        result[1].append(value2)
                        result[2].append(value3)

            if is_return:
                return result
            if result and result[0] and result[1] and result[2]:
                logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 实时贵金属价:")
                for line_msg in format_table_msg([
                    columns,
                    result[0],
                    result[1],
                    result[2]
                ]).split("\n"):
                    logger.info(line_msg)
        except Exception as e:
            logger.error(f"获取实时贵金属价格失败: {e}")

    def real_time_gold_html(self):
        result = self.real_time_gold(True)
        if result:
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
        try:
            if str(response.json()["ResultCode"]) == "0":
                marketData = response.json()["Result"]["newMarketData"]["marketData"][0]["p"]
                if not is_return:
                    marketData = marketData.split(";")[-30:]
                else:
                    marketData = marketData.split(";")
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
        except Exception as e:
            logger.error(f"获取上证指数信息失败: {e}")

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
        try:
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
        except Exception as e:
            logger.error(f"获取近七日成交量信息失败: {e}")

    def seven_A_html(self):
        result = self.seven_A(True)
        if result:
            return get_table_html(
                ["日期", "总成交额", "上交所", "深交所", "北交所"],
                result,
                [1, 2, 3, 4]
            )

    def select_fund_html(self, bk_id=None):
        """生成板块基金查询的HTML"""
        if bk_id is None:
            # 返回板块选择界面
            data = self.select_fund(is_return=True)
            bk_list = data["bk_list"]

            # 使用类属性的大板块分类
            major_categories = self.MAJOR_CATEGORIES

            # 生成分类板块按钮
            buttons_html = '<div style="padding: 20px;">'
            for category, sectors in major_categories.items():
                # 过滤出属于当前大类的板块
                category_sectors = [(idx + 1, name) for idx, name in enumerate(bk_list) if name in sectors]
                if not category_sectors:
                    continue

                buttons_html += f'<div style="margin-bottom: 25px;">'
                buttons_html += f'<h4 style="margin: 0 0 10px 0; color: #666; font-size: 14px; font-weight: 600;">{category}</h4>'
                buttons_html += '<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px;">'

                for idx, bk_name in category_sectors:
                    buttons_html += f'''
                    <button onclick="loadSectorFunds('{idx}')"
                            style="padding: 10px; background: #fff; border: 1px solid #ddd;
                                   cursor: pointer; font-weight: 500; transition: all 0.2s;
                                   text-align: center; font-size: 13px; border-radius: 4px;"
                            onmouseover="this.style.background='#0070e0'; this.style.color='#fff'; this.style.borderColor='#0070e0'"
                            onmouseout="this.style.background='#fff'; this.style.color='#000'; this.style.borderColor='#ddd'">
                        {bk_name}
                    </button>
                    '''
                buttons_html += '</div></div>'
            buttons_html += '</div>'

            return f'''
            <div id="sector-selection">
                <h3 style="padding: 20px 20px 10px 20px; margin: 0; font-size: 1.2rem;">选择板块查看基金列表</h3>
                {buttons_html}
            </div>
            <div id="sector-funds-result"></div>
            <script>
            function loadSectorFunds(bkId) {{
                const resultDiv = document.getElementById('sector-funds-result');
                resultDiv.innerHTML = '<p style="padding: 20px; text-align: center;">加载中...</p>';
                resultDiv.scrollIntoView({{ behavior: 'smooth', block: 'start' }});

                fetch('/fund/sector?bk_id=' + bkId)
                    .then(response => response.text())
                    .then(html => {{
                        resultDiv.innerHTML = html;
                        autoColorize();
                        resultDiv.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    }})
                    .catch(error => {{
                        resultDiv.innerHTML = '<p style="padding: 20px; color: red;">加载失败: ' + error + '</p>';
                    }});
            }}
            </script>
            '''
        else:
            # 返回指定板块的基金列表
            data = self.select_fund(bk_id=bk_id, is_return=True)
            if "error" in data:
                return f'<p style="color: red; padding: 20px;">{data["error"]}</p>'

            return f'''
            <div style="padding: 20px;">
                <h3 style="margin: 0 0 15px 0;">板块: {data["bk_name"]}</h3>
                {get_table_html(
                ["基金代码", "基金名称", "基金类型", "日期", "净值|日增长率", "近1周", "近1月", "近3月", "近6月", "今年来", "近1年", "近2年", "近3年", "成立来"],
                data["results"],
                [4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
            )}
            </div>
            '''

    def ai_analysis(self, deep_mode=False, fast_mode=False):
        """使用AI分析器进行市场分析

        Args:
            deep_mode: 是否启用深度研究模式（默认False）
            fast_mode: 是否启用快速分析模式（默认False）
        """
        analyzer = AIAnalyzer()
        if deep_mode:
            analyzer.analyze_deep(self, report_dir=self.report_dir)
        elif fast_mode:
            analyzer.analyze_fast(self, report_dir=self.report_dir)
        else:
            analyzer.analyze(self, report_dir=self.report_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MaYiFund')
    parser.add_argument('-a', '--add', action='store_true', help='添加基金代码')
    parser.add_argument("-d", "--delete", action="store_true", help="删除基金代码")
    parser.add_argument("-c", "--hold", action="store_true", help="添加持有基金标注")
    parser.add_argument("-b", "--not_hold", action="store_true", help="删除持有基金标注")
    parser.add_argument("-e", "--mark_sector", action="store_true", help="标记板块")
    parser.add_argument("-u", "--unmark_sector", action="store_true", help="删除标记板块")
    parser.add_argument("-s", "--select", action="store_true", help="选择板块查看基金列表")
    parser.add_argument("-m", "--modify-shares", action="store_true", help="修改基金持仓份额")
    parser.add_argument("-o", "--output", type=str, nargs='?', const="reports", default=None,
                        help="输出AI分析报告到指定目录（默认: reports）。只有使用此参数时才会保存报告文件")
    parser.add_argument("-f", "--fast", action="store_true", help="启用快速分析模式")
    parser.add_argument("-D", "--deep", action="store_true", help="启用深度研究模式")
    parser.add_argument("-W", "--with-ai", action="store_true", help="AI分析")
    args = parser.parse_args()

    mayi_fund = MaYiFund()
    # 只有指定了 -o 参数时才传入 report_dir，否则传入 None 表示不保存报告
    report_dir = args.output if args.output is not None else None
    mayi_fund.run(args.add, args.delete, args.hold, args.not_hold, report_dir, args.deep, args.fast, args.with_ai,
                  args.select, args.mark_sector, args.unmark_sector, args.modify_shares)
