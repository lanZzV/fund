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


class AIAnalyzer:
    """AI分析器，提供基于LangChain的市场分析功能"""

    def __init__(self):
        """初始化AI分析器"""
        self.llm = None

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

    def analyze(self, data_collector):
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
            if not os.path.exists("reports"):
                os.mkdir("reports")

            report_filename = f"reports/ai_analysis_{time.strftime('%Y%m%d_%H%M%S')}.md"
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
