"""
AI分析模块 - 使用LangChain进行基金市场深度分析

该模块提供基于LangChain的AI分析功能，包括：
- 市场趋势分析
- 板块机会分析
- 基金组合建议
- 风险提示分析
"""

import os
import time
import datetime
import re
from loguru import logger


from langchain.tools import tool
from ddgs import DDGS

@tool
def search_news(query: str) -> str:
    """使用DuckDuckGo搜索新闻内容（限制最近一周）

    Args:
        query: 搜索关键词
    """
    try:
        # 解析参数（支持直接传入字符串或JSON字符串）
        import json
        if isinstance(query, str):
            if query.strip().startswith('{'):
                # 如果是JSON格式: {"query": "关键词"}
                try:
                    parsed = json.loads(query)
                    query = parsed.get('query', '')
                except:
                    pass  # 保持原始query

        ddgs = DDGS(verify=False)
        results = ddgs.text(
            query=query,
            region="cn-zh",
            safesearch="off",
            timelimit="w",  # 限制最近一周
            max_results=10,
        )

        if not results:
            return f"未找到关于'{query}'的相关新闻"

        output = f"关于'{query}'的搜索结果（最近一周）：\n\n"
        for i, result in enumerate(results, 1):
            title = result.get("title", "无标题")
            body = result.get("body", "无内容")
            url = result.get("href", "")
            output += f"{i}. {title}\n{body}\n来源: {url}\n\n"

        return output
    except Exception as e:
        return f"搜索失败: {str(e)}"

class AIAnalyzer:
    """AI分析器，提供基于LangChain的市场分析功能"""

    def __init__(self):
        """初始化AI分析器"""
        self.llm = None

    def init_langchain_llm(self, fast_mode=False, deep_mode=False):
        """
        初始化LangChain LLM

        Args:
            fast_mode: 是否为快速模式（调整token和超时参数）
            deep_mode: 是否为深度研究模式（大幅提升token限制以支持长报告生成）
        """
        try:
            from langchain_openai import ChatOpenAI

            # 从环境变量读取配置
            api_base = os.getenv("LLM_API_BASE", "https://api.openai.com/v1")
            api_key = os.getenv("LLM_API_KEY", "")
            model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

            if not api_key:
                logger.warning("未配置LLM_API_KEY环境变量，跳过AI分析")
                return None

            # 根据模式调整参数
            if fast_mode:
                max_tokens = 1000
                temperature = 0.2
                timeout = 30
            elif deep_mode:
                # 深度研究模式：支持生成10,000+字的长报告
                max_tokens = 16000
                temperature = 0.2
                timeout = 120
            else:
                max_tokens = 2000
                temperature = 0.2
                timeout = 60

            # 创建ChatOpenAI实例
            llm = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                openai_api_base=api_base,
                temperature=temperature,
                max_tokens=max_tokens,
                request_timeout=timeout
            )

            return llm

        except Exception as e:
            logger.error(f"初始化LangChain LLM失败: {e}")
            return None

    @staticmethod
    def clean_ansi_codes(text):
        """清理所有ANSI颜色代码"""
        if not isinstance(text, str):
            return text
        # 清理完整的ANSI转义序列 \033[XXXm
        text = re.sub(r'\033\[\d+(?:;\d+)?m', '', text)
        # 清理不完整的ANSI代码 [XXXm (可能在某些情况下\033被截断)
        text = re.sub(r'\[\d+(?:;\d+)?m', '', text)
        return text

    @staticmethod
    def strip_markdown(text):
        """移除markdown格式标记，用于控制台显示"""
        # 移除标题符号 (###、##、#)
        text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

        # 移除加粗 (**text** 或 __text__)
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
        text = re.sub(r'__(.+?)__', r'\1', text)

        # 移除斜体 (*text* 或 _text_)
        text = re.sub(r'\*(.+?)\*', r'\1', text)
        text = re.sub(r'_(.+?)_', r'\1', text)

        # 移除删除线 (~~text~~)
        text = re.sub(r'~~(.+?)~~', r'\1', text)

        # 移除代码块标记 (```)
        text = re.sub(r'```[\s\S]*?```', '', text)
        text = re.sub(r'`(.+?)`', r'\1', text)

        # 移除链接 [text](url)
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)

        # 移除列表标记 (-, *, +, 1.)
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

        # 移除表格分隔线 (|---|---|)
        text = re.sub(r'\|[-:\s|]+\|', '', text)

        # 简化表格格式 (| cell |) -> cell
        text = re.sub(r'\s*\|\s*', ' ', text)

        # 移除引用标记 (>)
        text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

        # 移除多余空行
        text = re.sub(r'\n\n+', '\n\n', text)

        return text.strip()

    @staticmethod
    def format_text(text, max_width=60):
        """将markdown文本过滤并智能分行，用于控制台显示"""
        # 先过滤markdown格式
        text = AIAnalyzer.strip_markdown(text)

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

    def analyze(self, data_collector, report_dir="reports"):
        """
        执行AI分析

        Args:
            data_collector: 数据收集器对象，需要提供以下方法：
                - get_market_info(is_return=True)
                - kx(is_return=True)
                - gold(is_return=True)
                - real_time_gold(is_return=True)
                - seven_A(is_return=True)
                - A(is_return=True)
                - bk(is_return=True)
                以及 self.result 和 self.CACHE_MAP 属性
            report_dir: AI分析报告输出目录，默认为"reports"
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser

            logger.debug("正在收集数据进行AI分析...")

            # 初始化LLM
            llm = self.init_langchain_llm()
            if llm is None:
                return

            # 收集市场数据
            market_data = data_collector.get_market_info(is_return=True)
            market_summary = "主要市场指数：\n"
            for item in market_data[:10]:
                market_summary += f"- {item[0]}: {item[1]} ({item[2]})\n"

            # 收集7x24快讯
            kx_data = data_collector.kx(is_return=True)
            kx_summary = "7×24快讯（最新10条）：\n"
            for i, v in enumerate(kx_data[:10], 1):
                evaluate = v.get("evaluate", "")
                evaluate_tag = f"【{evaluate}】" if evaluate else ""
                title = v.get("title", v.get("content", {}).get("items", [{}])[0].get("data", ""))
                publish_time = datetime.datetime.fromtimestamp(int(v["publish_time"])).strftime("%Y-%m-%d %H:%M:%S")
                entity = v.get("entity", [])
                if entity:
                    entity_str = ", ".join([f"{x['code']}-{x['name']}" for x in entity[:3]])  # 最多显示3只股票
                    kx_summary += f"{i}. {publish_time} {evaluate_tag}{title} (影响: {entity_str})\n"
                else:
                    kx_summary += f"{i}. {publish_time} {evaluate_tag}{title}\n"

            # 收集金价数据
            gold_data = data_collector.gold(is_return=True)
            gold_summary = "近期金价（最近5天）：\n"
            for item in gold_data[:5]:
                gold_summary += f"- {item[0]}: 中国黄金{item[1]}, 周大福{item[2]}, 涨跌({item[3]}, {item[4]})\n"

            # 收集实时金价
            realtime_gold_data = data_collector.real_time_gold(is_return=True)
            realtime_gold_summary = "实时金价：\n"
            if realtime_gold_data and len(realtime_gold_data) == 2:
                for row in realtime_gold_data:
                    if row:
                        realtime_gold_summary += f"- {row[0]}: 最新价{row[1]}, 涨跌幅{row[3]}\n"

            # 收集近7日成交量
            seven_a_data = data_collector.seven_A(is_return=True)
            seven_a_summary = "近7日成交量（最近3天）：\n"
            for item in seven_a_data[:3]:
                seven_a_summary += f"- {item[0]}: 总成交{item[1]}, 上交所{item[2]}, 深交所{item[3]}, 北交所{item[4]}\n"

            # 收集近30分钟上证指数
            a_data = data_collector.A(is_return=True)
            a_summary = "近30分钟上证指数（最近5分钟）：\n"
            for item in a_data[-5:]:
                a_summary += f"- {item[0]}: {item[1]}, 涨跌额{item[2]}, 涨跌幅{item[3]}, 成交量{item[4]}, 成交额{item[5]}\n"

            # 收集板块数据
            bk_data = data_collector.bk(is_return=True)
            top_sectors = "涨幅前5板块：\n"
            for i, item in enumerate(bk_data[:5]):
                top_sectors += f"{i+1}. {item[0]}: {item[1]}, 主力净流入{item[2]}, 主力流入占比{item[3]}\n"

            bottom_sectors = "跌幅后5板块：\n"
            for i, item in enumerate(bk_data[-5:]):
                bottom_sectors += f"{i+1}. {item[0]}: {item[1]}, 主力净流入{item[2]}, 主力流入占比{item[3]}\n"

            # 收集基金数据
            fund_data = []
            for fund_code, fund_info in data_collector.CACHE_MAP.items():
                for fund in data_collector.result:
                    if fund[0] == fund_code:
                        fund_data.append({
                            "code": fund[0],
                            "name": AIAnalyzer.clean_ansi_codes(fund[1].replace("⭐ ", "")),
                            "forecast": AIAnalyzer.clean_ansi_codes(fund[3]),
                            "growth": AIAnalyzer.clean_ansi_codes(fund[4]),
                            "consecutive": AIAnalyzer.clean_ansi_codes(fund[5]),
                            "consecutive_growth": AIAnalyzer.clean_ansi_codes(fund[6]),
                            "month_stats": AIAnalyzer.clean_ansi_codes(fund[7]),
                            "month_growth": AIAnalyzer.clean_ansi_codes(fund[8]),
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
                ("user", """请基于以下完整的市场数据，进行深入的市场趋势分析：

【7×24快讯】
{kx_summary}

【市场指数】
{market_summary}

【金价走势】
{gold_summary}

{realtime_gold_summary}

【市场成交量】
{seven_a_summary}

【上证分时数据】
{a_summary}

【领涨板块】
{top_sectors}

请从以下角度进行分析（输出300-400字）：
1. 结合7×24快讯，分析当前市场热点和重要事件
2. 分析主要指数的走势特征和相互关系
3. 判断当前市场所处的阶段（上涨/震荡/调整）
4. 分析市场情绪和资金流向特征（结合成交量和分时数据）
5. 对比国内外市场表现，指出关键影响因素
6. 分析金价走势对市场的影响

请用专业、客观的语言输出，使用markdown格式（可使用##、###标题，**加粗**，列表，表格等），输出结构化、易读的专业分析报告。""")
            ])

            # 创建提示链 - 板块机会分析
            sector_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位行业研究专家，精通各个行业板块的投资逻辑和周期规律。"),
                ("user", """请基于以下板块数据和市场环境，深入分析行业投资机会：

【涨幅领先板块】
{top_sectors}

【跌幅板块】
{bottom_sectors}

【市场成交量】
{seven_a_summary}

【上证分时】
{a_summary}

请从以下角度进行分析（输出300-400字）：
1. 分析领涨板块的共同特征和驱动因素
2. 判断这些板块的行情可持续性（结合成交量和资金流向）
3. 结合资金流入情况，评估板块强度
4. 提示哪些板块值得重点关注，给出配置建议
5. 分析弱势板块是否存在反转机会

请用专业、深入的语言输出，使用markdown格式（可使用##、###标题，**加粗**，列表，表格等），输出结构化、易读的专业分析报告。""")
            ])

            # 创建提示链 - 基金组合建议
            portfolio_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位专业的基金投资顾问，擅长基金组合配置和风险管理。"),
                ("user", """请基于以下基金持仓和完整市场环境，给出投资建议：

【基金持仓】
{fund_summary}

【市场环境】
{market_summary}

【市场成交量】
{seven_a_summary}

【板块表现】
{top_sectors}

请从以下角度给出建议（输出300-400字）：
1. 评估当前持仓基金的表现和风险特征
2. 分析持仓基金与市场环境的匹配度（结合成交量和板块轮动）
3. 给出具体的调仓建议（增持/减持/持有）
4. 对表现优异的基金，分析背后原因和可持续性
5. 提示仓位配置和风险敞口的优化方向

请给出具体、可操作的建议，使用markdown格式（可使用##、###标题，**加粗**，列表，表格等），输出结构化、易读的专业分析报告。""")
            ])

            # 创建提示链 - 风险提示
            risk_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位风险管理专家，擅长识别市场风险和制定风控策略。"),
                ("user", """请基于当前完整的市场数据，进行全面的风险分析：

【市场指数】
{market_summary}

【金价走势】
{gold_summary}

【市场成交量】
{seven_a_summary}

【上证分时】
{a_summary}

【板块表现】
{top_sectors}
{bottom_sectors}

【基金持仓】
{fund_summary}

请从以下角度进行风险分析（输出250-350字）：
1. 识别当前市场的主要风险点（结合成交量萎缩/放大、分时走势等）
2. 分析可能引发调整的触发因素
3. 评估持仓基金的风险暴露
4. 给出风险防控建议和应对策略
5. 提示需要关注的风险信号（包括技术面和资金面）

请客观、谨慎地提示风险，使用markdown格式（可使用##、###标题，**加粗**，列表，表格等），输出结构化、易读的专业分析报告。""")
            ])

            # 创建输出解析器
            output_parser = StrOutputParser()

            # 执行四个维度的分析
            logger.info("正在进行市场趋势分析...")
            trend_chain = trend_prompt | llm | output_parser
            trend_analysis = trend_chain.invoke({
                "kx_summary": kx_summary,
                "market_summary": market_summary,
                "gold_summary": gold_summary,
                "realtime_gold_summary": realtime_gold_summary,
                "seven_a_summary": seven_a_summary,
                "a_summary": a_summary,
                "top_sectors": top_sectors
            })

            logger.info("正在进行板块机会分析...")
            sector_chain = sector_prompt | llm | output_parser
            sector_analysis = sector_chain.invoke({
                "top_sectors": top_sectors,
                "bottom_sectors": bottom_sectors,
                "seven_a_summary": seven_a_summary,
                "a_summary": a_summary
            })

            logger.info("正在进行基金组合分析...")
            portfolio_chain = portfolio_prompt | llm | output_parser
            portfolio_analysis = portfolio_chain.invoke({
                "fund_summary": fund_summary,
                "market_summary": market_summary,
                "seven_a_summary": seven_a_summary,
                "top_sectors": top_sectors
            })

            logger.info("正在进行风险分析...")
            risk_chain = risk_prompt | llm | output_parser
            risk_analysis = risk_chain.invoke({
                "market_summary": market_summary,
                "gold_summary": gold_summary,
                "seven_a_summary": seven_a_summary,
                "a_summary": a_summary,
                "top_sectors": top_sectors,
                "bottom_sectors": bottom_sectors,
                "fund_summary": fund_summary
            })

            # 生成markdown文件内容
            markdown_content = f"""# AI市场深度分析报告

**生成时间**：{time.strftime('%Y-%m-%d %H:%M')}

---

## 📊 原始数据概览

### 7×24快讯

{kx_summary}

### 市场指数

{market_summary}

### 金价走势

{gold_summary}

{realtime_gold_summary}

### 市场成交量

{seven_a_summary}

### 上证指数分时（最近5分钟）

{a_summary}

### 涨幅领先板块（Top 5）

{top_sectors}

### 跌幅板块（Bottom 5）

{bottom_sectors}

### 基金持仓情况

{fund_summary}

---

## 1️⃣ 市场整体趋势分析

{trend_analysis}

---

## 2️⃣ 行业板块机会分析

{sector_analysis}

---

## 3️⃣ 基金组合投资建议

{portfolio_analysis}

---

## 4️⃣ 风险提示与应对

{risk_analysis}

---

💡 **提示**：以上分析由AI生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。
"""

            # 保存markdown文件
            if not os.path.exists(report_dir):
                os.makedirs(report_dir, exist_ok=True)

            report_filename = f"{report_dir}/AI市场分析报告{time.strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"✅ AI分析报告已保存至：{report_filename}")

            # 输出完整的AI分析报告
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 📊 AI市场深度分析报告")
            logger.info("=" * 80)

            logger.info("1️⃣ 市场整体趋势分析")
            logger.info("-" * 80)
            for line in self.format_text(trend_analysis):
                logger.info(line)

            logger.info("=" * 80)
            logger.info("2️⃣ 行业板块机会分析")
            logger.info("-" * 80)
            for line in self.format_text(sector_analysis):
                logger.info(line)

            logger.info("=" * 80)
            logger.info("3️⃣ 基金组合投资建议")
            logger.info("-" * 80)
            for line in self.format_text(portfolio_analysis):
                logger.info(line)

            logger.info("=" * 80)
            logger.info("4️⃣ 风险提示与应对")
            logger.info("-" * 80)
            for line in self.format_text(risk_analysis):
                logger.info(line)

            logger.info("=" * 80)
            logger.info("💡 提示：以上分析由AI生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"AI分析过程出错: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def analyze_fast(self, data_collector, report_dir="reports"):
        """
        快速分析模式 - 一次性生成简明分析报告

        Args:
            data_collector: 数据收集器对象
            report_dir: AI分析报告输出目录，默认为"reports"
        """
        try:
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser

            logger.info("🚀 启动快速分析模式...")

            # 初始化LLM（快速模式）
            llm = self.init_langchain_llm(fast_mode=True)
            if llm is None:
                return

            # 收集市场数据
            market_data = data_collector.get_market_info(is_return=True)
            market_summary = "主要市场指数：\n"
            for item in market_data[:8]:
                market_summary += f"- {item[0]}: {item[1]} ({item[2]})\n"

            # 收集7x24快讯（只取前5条）
            kx_data = data_collector.kx(is_return=True)
            kx_summary = "最新快讯（前5条）：\n"
            for i, v in enumerate(kx_data[:5], 1):
                evaluate = v.get("evaluate", "")
                evaluate_tag = f"【{evaluate}】" if evaluate else ""
                title = v.get("title", v.get("content", {}).get("items", [{}])[0].get("data", ""))
                kx_summary += f"{i}. {evaluate_tag}{title}\n"

            # 收集板块数据
            bk_data = data_collector.bk(is_return=True)
            top_sectors = "涨幅前5板块：\n"
            for i, item in enumerate(bk_data[:5]):
                top_sectors += f"{i+1}. {item[0]}: {item[1]}, 主力净流入{item[2]}\n"

            # 收集基金数据
            fund_data = []
            for fund_code, fund_info in data_collector.CACHE_MAP.items():
                for fund in data_collector.result:
                    if fund[0] == fund_code:
                        fund_data.append({
                            "code": fund[0],
                            "name": AIAnalyzer.clean_ansi_codes(fund[1].replace("⭐ ", "")),
                            "forecast": AIAnalyzer.clean_ansi_codes(fund[3]),
                            "growth": AIAnalyzer.clean_ansi_codes(fund[4]),
                            "is_hold": fund_info.get("is_hold", False)
                        })
                        break

            # 构建基金摘要
            fund_summary = f"自选基金总数: {len(fund_data)}只\n"
            hold_funds = [f for f in fund_data if f["is_hold"]]
            if hold_funds:
                fund_summary += f"持有基金数: {len(hold_funds)}只\n"

            # 表现最好的基金
            top_funds = sorted(fund_data, key=lambda x: float(x["forecast"].replace("%", "")) if x["forecast"] != "N/A" else -999, reverse=True)[:3]
            fund_summary += "今日涨幅前3的基金：\n"
            for i, f in enumerate(top_funds, 1):
                hold_mark = "【持有】" if f["is_hold"] else ""
                fund_summary += f"{i}. {hold_mark}{f['name']}: 估值{f['forecast']}\n"

            # 创建一次性分析提示
            fast_prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一位资深金融分析师，擅长快速抓住市场要点。"),
                ("user", """请基于以下市场数据，生成简明扼要的市场分析报告：

【7×24快讯】
{kx_summary}

【市场指数】
{market_summary}

【领涨板块】
{top_sectors}

【基金持仓】
{fund_summary}

请生成一份简明的市场分析报告，包含以下4个部分（总共400-500字）：

## 1. 市场趋势（100字）
简要分析当前市场热点、整体走势和市场情绪。

## 2. 板块机会（80字）
指出领涨板块的特征和值得关注的投资机会。

## 3. 基金建议（80字）
评估持仓基金表现，给出简要的配置建议。

## 4. 风险提示（80字）
提示当前主要风险点和应对策略。

输出要求：使用markdown格式，简洁明了，要点突出。""")
            ])

            # 执行快速分析
            logger.info("正在生成快速分析报告...")
            output_parser = StrOutputParser()
            fast_chain = fast_prompt | llm | output_parser

            analysis_result = fast_chain.invoke({
                "kx_summary": kx_summary,
                "market_summary": market_summary,
                "top_sectors": top_sectors,
                "fund_summary": fund_summary
            })

            # 生成markdown报告
            markdown_content = f"""# 📊 AI快速市场分析报告

**生成时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

{analysis_result}

---

💡 **提示**：快速分析模式，仅供参考，不构成投资建议。投资有风险，入市需谨慎。
"""

            # 保存markdown文件
            if not os.path.exists(report_dir):
                os.makedirs(report_dir, exist_ok=True)

            report_filename = f"{report_dir}/AI快速分析报告{time.strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"✅ 快速分析报告已保存至：{report_filename}")

            # 输出分析报告
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 📊 AI快速市场分析报告")
            logger.info("=" * 80)
            for line in self.format_text(analysis_result):
                logger.info(line)
            logger.info("=" * 80)
            logger.info("💡 提示：快速分析模式，仅供参考，不构成投资建议。")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"快速分析过程出错: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def analyze_deep(self, data_collector, report_dir="reports"):
        """
        深度研究模式 - 使用 ReAct Agent 自主收集数据并生成报告

        Args:
            data_collector: 数据收集器对象
            report_dir: AI分析报告输出目录，默认为"reports"
        """
        try:
            from langchain.agents import create_react_agent, AgentExecutor
            from langchain.tools import tool
            from langchain_core.prompts import PromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            from ddgs import DDGS
            from bs4 import BeautifulSoup
            import requests
            import urllib3
            urllib3.disable_warnings()

            logger.info("🚀 启动深度研究模式...")

            # 初始化LLM（深度模式使用更高的token限制，支持生成10,000+字长报告）
            llm = self.init_langchain_llm(fast_mode=False, deep_mode=True)
            if llm is None:
                return

            # 定义工具函数 - 包装数据收集器的方法为 LangChain tools

            @tool
            def get_market_indices() -> str:
                """获取市场指数数据（上证、深证、纳指、道指等）"""
                try:
                    market_data = data_collector.get_market_info(is_return=True)
                    result = "主要市场指数：\n"
                    for item in market_data[:12]:
                        result += f"- {item[0]}: {item[1]} ({item[2]})\n"
                    return result
                except Exception as e:
                    return f"获取市场指数失败: {str(e)}"

            @tool
            def get_news_flash(count: str = "30") -> str:
                """获取7×24快讯（市场新闻）

                Args:
                    count: 要获取的快讯数量，默认30条，最多50条
                """
                try:
                    # 解析参数（支持直接传入数字或JSON字符串）
                    import json
                    if isinstance(count, str):
                        if count.strip().startswith('{'):
                            # 如果是JSON格式: {"count": 30}
                            try:
                                parsed = json.loads(count)
                                count = parsed.get('count', 30)
                            except:
                                count = 30
                        else:
                            # 如果是纯数字字符串: "30"
                            try:
                                count = int(count)
                            except:
                                count = 30

                    # 限制最大数量
                    count = min(int(count), 50)
                    kx_data = data_collector.kx(is_return=True, count=count)
                    result = f"7×24快讯（最新{len(kx_data)}条）：\n\n"
                    for i, v in enumerate(kx_data[:count], 1):
                        evaluate = v.get("evaluate", "")
                        evaluate_tag = f"【{evaluate}】" if evaluate else ""
                        title = v.get("title", v.get("content", {}).get("items", [{}])[0].get("data", ""))
                        publish_time = datetime.datetime.fromtimestamp(int(v["publish_time"])).strftime("%Y-%m-%d %H:%M:%S")
                        entity = v.get("entity", [])
                        if entity:
                            entity_str = ", ".join([f"{x['code']}-{x['name']}" for x in entity[:3]])
                            result += f"{i}. {publish_time} {evaluate_tag}{title}\n   影响: {entity_str}\n\n"
                        else:
                            result += f"{i}. {publish_time} {evaluate_tag}{title}\n\n"
                    return result
                except Exception as e:
                    return f"获取7×24快讯失败: {str(e)}"

            @tool
            def get_sector_performance() -> str:
                """获取行业板块表现（涨跌幅、资金流向等）"""
                try:
                    bk_data = data_collector.bk(is_return=True)
                    result = "涨幅前10板块：\n"
                    for i, item in enumerate(bk_data[:10], 1):
                        result += f"{i}. {item[0]}: {item[1]}, 主力净流入{item[2]}, 流入占比{item[3]}\n"

                    result += "\n跌幅后10板块：\n"
                    for i, item in enumerate(bk_data[-10:], 1):
                        result += f"{i}. {item[0]}: {item[1]}, 主力净流入{item[2]}, 流入占比{item[3]}\n"
                    return result
                except Exception as e:
                    return f"获取板块数据失败: {str(e)}"

            @tool
            def get_gold_prices() -> str:
                """获取黄金价格数据（近期金价和实时金价）"""
                try:
                    # 近期金价
                    gold_data = data_collector.gold(is_return=True)
                    result = "近期金价（最近7天）：\n"
                    for item in gold_data[:7]:
                        result += f"- {item[0]}: 中国黄金{item[1]}, 周大福{item[2]}, 涨跌({item[3]}, {item[4]})\n"

                    # 实时金价
                    realtime_gold_data = data_collector.real_time_gold(is_return=True)
                    result += "\n实时金价：\n"
                    if realtime_gold_data and len(realtime_gold_data) == 2:
                        for row in realtime_gold_data:
                            if row:
                                result += f"- {row[0]}: 最新价{row[1]}, 涨跌幅{row[3]}\n"
                    return result
                except Exception as e:
                    return f"获取金价数据失败: {str(e)}"

            @tool
            def get_trading_volume() -> str:
                """获取近7日市场成交量数据"""
                try:
                    seven_a_data = data_collector.seven_A(is_return=True)
                    result = "近7日成交量：\n"
                    for item in seven_a_data[:7]:
                        result += f"- {item[0]}: 总成交{item[1]}, 上交所{item[2]}, 深交所{item[3]}, 北交所{item[4]}\n"
                    return result
                except Exception as e:
                    return f"获取成交量数据失败: {str(e)}"

            @tool
            def get_shanghai_intraday() -> str:
                """获取上证指数近30分钟分时数据"""
                try:
                    a_data = data_collector.A(is_return=True)
                    result = "上证指数近30分钟分时（最新10分钟）：\n"
                    for item in a_data[-10:]:
                        result += f"- {item[0]}: {item[1]}, 涨跌额{item[2]}, 涨跌幅{item[3]}, 成交量{item[4]}, 成交额{item[5]}\n"
                    return result
                except Exception as e:
                    return f"获取上证分时数据失败: {str(e)}"

            @tool
            def get_fund_portfolio() -> str:
                """获取自选基金组合的详细数据"""
                try:
                    fund_data = []
                    for fund_code, fund_info in data_collector.CACHE_MAP.items():
                        for fund in data_collector.result:
                            if fund[0] == fund_code:
                                fund_data.append({
                                    "code": fund[0],
                                    "name": AIAnalyzer.clean_ansi_codes(fund[1].replace("⭐ ", "")),
                                    "forecast": AIAnalyzer.clean_ansi_codes(fund[3]),
                                    "growth": AIAnalyzer.clean_ansi_codes(fund[4]),
                                    "consecutive": AIAnalyzer.clean_ansi_codes(fund[5]),
                                    "consecutive_growth": AIAnalyzer.clean_ansi_codes(fund[6]),
                                    "month_stats": AIAnalyzer.clean_ansi_codes(fund[7]),
                                    "month_growth": AIAnalyzer.clean_ansi_codes(fund[8]),
                                    "is_hold": fund_info.get("is_hold", False)
                                })
                                break

                    result = f"自选基金总数: {len(fund_data)}只\n\n"

                    # 持有基金
                    hold_funds = [f for f in fund_data if f["is_hold"]]
                    if hold_funds:
                        result += f"持有基金（{len(hold_funds)}只）：\n"
                        for i, f in enumerate(hold_funds, 1):
                            result += f"{i}. {f['name']}({f['code']}): 估值{f['forecast']}, 日涨幅{f['growth']}, 连续{f['consecutive']}天, 近30天{f['month_stats']}\n"
                        result += "\n"

                    # 表现最好的基金
                    top_funds = sorted(fund_data, key=lambda x: float(x["forecast"].replace("%", "")) if x["forecast"] != "N/A" else -999, reverse=True)[:8]
                    result += "今日涨幅前8的基金：\n"
                    for i, f in enumerate(top_funds, 1):
                        hold_mark = "【持有】" if f["is_hold"] else ""
                        result += f"{i}. {hold_mark}{f['name']}({f['code']}): 估值{f['forecast']}, 日涨幅{f['growth']}, 近30天{f['month_stats']}\n"

                    return result
                except Exception as e:
                    return f"获取基金组合数据失败: {str(e)}"

            @tool
            def fetch_webpage(url: str) -> str:
                """获取网页内容并提取文本

                Args:
                    url: 网页URL
                """
                try:
                    # 解析参数（支持直接传入字符串或JSON字符串）
                    import json
                    if isinstance(url, str):
                        if url.strip().startswith('{'):
                            # 如果是JSON格式: {"url": "https://..."}
                            try:
                                parsed = json.loads(url)
                                url = parsed.get('url', '')
                            except:
                                pass  # 保持原始url

                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    }
                    response = requests.get(url, headers=headers, timeout=10, verify=False)
                    response.encoding = response.apparent_encoding

                    soup = BeautifulSoup(response.text, 'lxml')

                    # 移除script和style标签
                    for script in soup(["script", "style"]):
                        script.decompose()

                    # 提取文本
                    text = soup.get_text()

                    # 清理文本
                    lines = (line.strip() for line in text.splitlines())
                    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                    text = '\n'.join(chunk for chunk in chunks if chunk)

                    # 限制长度
                    if len(text) > 3000:
                        text = text[:3000] + "...(内容过长已截断)"

                    return f"网页内容：\n{text}"
                except Exception as e:
                    return f"获取网页失败: {str(e)}"

            @tool
            def get_current_time() -> str:
                """获取当前日期和时间"""
                return f"当前时间: {datetime.datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}"

            # 组装工具列表
            tools = [
                get_market_indices,
                get_news_flash,
                get_sector_performance,
                get_gold_prices,
                get_trading_volume,
                get_shanghai_intraday,
                get_fund_portfolio,
                search_news,
                fetch_webpage,
                get_current_time
            ]

            # 创建ReAct Agent的prompt
            current_date = datetime.datetime.now().strftime('%Y年%m月%d日')

            react_prompt = PromptTemplate.from_template("""你是一位资深金融研究分析师，擅长深度市场研究和数据可视化。今天是{current_date}。

你的任务是：通过自主调用工具收集数据，生成一份**格式丰富、结构清晰、数据详实**的市场分析报告。

**工具使用说明**：
- 📰 **get_news_flash**：获取7×24快讯列表（包含标题和摘要）
- 🔍 **search_news**：根据关键词搜索快讯的详细内容和相关报道
- 📄 **fetch_webpage**：获取完整新闻文章的详细内容
- 💡 **建议流程**：先用get_news_flash获取快讯列表，再针对重要事件用search_news和fetch_webpage获取详情

**研究流程建议**：
1. 首先调用 get_current_time 确认当前时间
2. 收集基础数据（指数、板块、基金、黄金等）
3. 调用 get_news_flash 获取7×24快讯列表
4. **【可选步骤 - 深度解读】** 针对快讯中的重要事件：
   - 使用 search_news 搜索相关的详细报道（如："政策名称 详情"、"事件名 市场影响"）
   - 使用 fetch_webpage 获取完整文章内容，深入了解事件背景
5. 综合所有数据，生成**数据详实、分析深入、风险充分提示**的报告

**可用工具**：
{tools}

工具名称: {tool_names}

**报告生成要求**：

你是一位资深金融分析师，需要生成一份**详尽的专业行业研究报告**。

**核心要求**：
1. ⭐ **报告总字数必须达到10000字以上** - 这是最重要的要求
2. 📊 **内容必须详实深入** - 每个分析点都要展开详细论述，不能浅尝辄止
3. 🔍 **数据支撑充分** - 所有判断必须有具体数据和案例支持
4. 📈 **格式丰富清晰** - 使用表格、列表、加粗等Markdown格式增强可读性

**深度解读建议**：
- 针对7×24快讯中的重要事件，可使用 search_news 搜索相关详细报道
- 对搜索到的重要文章，可使用 fetch_webpage 获取原文完整内容
- 结合快讯信息和详细报道，提供更深入的分析和解读

**报告内容建议**（你可以自由发挥，不必严格遵循）：
- 宏观市场环境（全球市场联动、A股技术面、成交量分析、市场情绪）
- 重大事件深度解读（每个重要快讯都要详细分析500-1000字：事件背景+市场影响+投资启示）
- 行业板块机会挖掘（强势板块的驱动因素、持续性判断、龙头标的分析，每个板块300-500字）
- 弱势板块风险提示（下跌原因、底部判断、反弹时机）
- 基金组合诊断（每只持仓基金的详细分析：业绩、持仓、风险、操作建议，每只500-800字）
- 调仓建议（推荐基金+理由+风险提示，每个推荐300-500字）
- 多维度风险分析（系统性风险、政策风险、市场情绪、行业风险，每类风险300-500字）
- 投资策略（短期/中期/长期策略，具体可执行的操作计划）
- 信息来源说明（列出所有使用的工具和数据来源）

**格式建议**（Markdown）：
- 使用表格展示结构化数据（指数、板块、基金等）
- 使用列表组织要点
- 使用加粗突出关键信息
- 使用引用块突出核心结论
- 使用分隔线分隔章节
- 适当使用Emoji增强可读性

**写作风格**：
- 专业严谨，数据详实
- 逻辑清晰，层次分明
- 语言流畅，易于理解
- 分析深入，见解独到
- **重点：内容要充实，不要惜字如金，要像写一本小册子一样详细**

**重要提示**：
- 每次只调用一个工具，观察结果后再决定下一步
- 可以使用 search_news 和 fetch_webpage 获取7×24快讯的详细内容
- 确保报告**字数达到10000字以上**，内容详实、数据充分、建议具体
- 充分提示风险，避免过度乐观或悲观

使用以下格式：

Question: 要解决的问题
Thought: 你应该思考要做什么
Action: 要采取的行动，必须是 [{tool_names}] 中的一个
Action Input: 行动的输入
Observation: 行动的结果
... (这个 Thought/Action/Action Input/Observation 可以重复N次)
Thought: 我现在知道最终答案了
Final Answer: 最终答案（完整的markdown格式报告，内容详实，字数10000字以上）

开始！

Question: {input}
Thought: {agent_scratchpad}""")

            # 创建agent
            agent = create_react_agent(
                llm=llm,
                tools=tools,
                prompt=react_prompt
            )

            # 创建executor
            agent_executor = AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=True,
                handle_parsing_errors=True,
                max_iterations=50,  # 增加迭代次数支持更复杂的研究流程
                max_execution_time=900,  # 增加到15分钟，支持深度网页抓取
                return_intermediate_steps=True  # 返回中间步骤，防止超时时丢失内容
            )

            # 执行深度研究
            logger.info("🔍 Agent开始自主研究和数据收集...")

            result = agent_executor.invoke({
                "input": f"""请生成一份关于当前市场（{current_date}）的深度分析报告。

【报告要求】必须包含以下章节，并使用丰富的Markdown格式（表格、列表、加粗、引用块、Emoji等）：
1. 市场整体趋势分析（包含指数表格、热点列表）
2. 行业板块机会分析（包含领涨/跌板块表格）
3. 基金组合投资建议（包含持仓表格、调仓建议列表）
4. 风险提示与应对（包含风险表格，含信息来源说明）

【深度解读建议】针对7×24快讯中的重要事件：
- 可使用 search_news 搜索相关详细报道（如："政策名称 详情"、"事件名 分析"）
- 可使用 fetch_webpage 获取完整新闻文章内容，深入了解事件背景

务必使用Markdown表格展示所有数据，确保报告字数达到10000字以上！""",
                "current_date": current_date
            })

            # 提取最终报告（增强容错处理）
            final_report = result.get("output", "")

            # 如果output为空（可能由于超时），尝试从intermediate_steps提取内容
            if not final_report or final_report == "Agent stopped due to iteration limit or time limit.":
                logger.warning("⚠️ Agent未返回完整输出，尝试从中间步骤提取内容...")
                intermediate_steps = result.get("intermediate_steps", [])

                # 提取所有Observation中的内容
                collected_info = []
                for step in intermediate_steps:
                    if len(step) >= 2:
                        action, observation = step[0], step[1]
                        if observation and isinstance(observation, str) and len(observation) > 50:
                            collected_info.append(f"### {action.tool if hasattr(action, 'tool') else '数据收集'}\n\n{observation}\n")

                if collected_info:
                    final_report = "\n\n".join(collected_info)
                    final_report += "\n\n---\n\n⚠️ **注意**：由于Agent执行时间限制，本报告由中间数据自动组合生成。建议增加迭代次数或执行时间限制。"
                else:
                    final_report = "Agent stopped due to iteration limit or time limit."

            # 生成完整的markdown文件
            markdown_content = f"""# 🔬 AI深度研究报告

**生成时间**：{time.strftime('%Y-%m-%d %H:%M:%S')}
**研究模式**：ReAct Agent 自主研究

---

{final_report}

---

💡 **提示**：本报告由AI深度研究生成，Agent自主决定数据收集策略。仅供参考，不构成投资建议。投资有风险，入市需谨慎。
"""

            # 保存markdown文件
            if not os.path.exists(report_dir):
                os.makedirs(report_dir, exist_ok=True)

            report_filename = f"{report_dir}/AI市场深度研究报告{time.strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_filename, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            logger.info(f"✅ 深度研究报告已保存至：{report_filename}")

            # 输出报告到控制台
            logger.critical(f"{time.strftime('%Y-%m-%d %H:%M')} 🔬 AI深度研究报告")
            logger.info("=" * 80)
            for line in self.format_text(final_report, max_width=70):
                logger.info(line)
            logger.info("=" * 80)
            logger.info("💡 提示：本报告由AI深度研究生成，仅供参考，不构成投资建议。")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"深度研究模式出错: {e}")
            import traceback
            logger.error(traceback.format_exc())

