import importlib
import threading
import json

import urllib3
from dotenv import load_dotenv
from flask import Flask, request, Response, stream_with_context
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from loguru import logger

import fund
from ai_analyzer import AIAnalyzer, search_news, fetch_webpage
from module_html import get_full_page_html

# 加载环境变量
load_dotenv()

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

app = Flask(__name__)
analyzer = AIAnalyzer()


def get_real_time_data_context(user_message):
    """后端智能获取相关数据，根据用户问题判断需要哪些板块"""
    try:
        my_fund = fund.MaYiFund()
        context_parts = []

        # 定义所有数据模块及其关键词
        data_modules = {
            'kx': {
                'name': '7*24快讯',
                'func': my_fund.kx_html,
                'keywords': ['快讯', '新闻', 'news', '消息', '动态']
            },
            'marker': {
                'name': '全球指数',
                'func': my_fund.marker_html,
                'keywords': ['指数', '上证', '深证', '恒生', '道琼斯', 'nasdaq', '纳斯达克', 'market', 'index']
            },
            'real_time_gold': {
                'name': '实时贵金属',
                'func': my_fund.real_time_gold_html,
                'keywords': ['黄金', '白银', '贵金属', 'gold', 'silver', '金价']
            },
            'gold': {
                'name': '历史金价',
                'func': my_fund.gold_html,
                'keywords': ['历史金价', '金价走势', '金价趋势']
            },
            'seven_A': {
                'name': '成交量趋势',
                'func': my_fund.seven_A_html,
                'keywords': ['成交量', '交易量', 'volume']
            },
            'A': {
                'name': '上证分时',
                'func': my_fund.A_html,
                'keywords': ['上证分时', 'A股分时', '分时图']
            },
            'fund': {
                'name': '自选基金',
                'func': my_fund.fund_html,
                'keywords': ['基金', '持仓', '自选', 'fund', '收益', '净值']
            },
            'bk': {
                'name': '行业板块',
                'func': my_fund.bk_html,
                'keywords': ['板块', '行业', 'sector', '涨跌', '主力', '净流入']
            },
        }

        # 智能判断需要获取哪些模块
        modules_to_fetch = []
        user_lower = user_message.lower()

        for module_id, module_info in data_modules.items():
            # 检查用户问题是否包含该模块的关键词
            if any(keyword in user_lower for keyword in module_info['keywords']):
                modules_to_fetch.append((module_id, module_info))

        # 如果没有匹配到任何关键词，获取快讯和基金数据作为默认
        if not modules_to_fetch:
            modules_to_fetch = [
                ('kx', data_modules['kx']),
                ('fund', data_modules['fund']),
            ]
            logger.info(f"未匹配到特定关键词，获取默认模块: 快讯、自选基金")
        else:
            logger.info(f"根据问题匹配到模块: {[m[0] for m in modules_to_fetch]}")

        # 获取匹配的模块数据
        for module_id, module_info in modules_to_fetch:
            try:
                html_content = module_info['func']()

                # 提取HTML中的文本内容
                from html.parser import HTMLParser

                class HTMLTextExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.text = []

                    def handle_data(self, data):
                        if data.strip():
                            self.text.append(data.strip())

                    def get_text(self):
                        return '\n'.join(self.text)

                parser = HTMLTextExtractor()
                parser.feed(html_content)
                text_content = parser.get_text()

                # 添加到context，使用标记格式
                context_parts.append(f"\n=== {module_info['name']} ({module_id}) ===\n{text_content}")

                logger.debug(f"✓ 获取 {module_info['name']} 数据成功 ({len(text_content)} chars)")

            except Exception as e:
                logger.error(f"✗ 获取 {module_info['name']} 数据失败: {e}")
                context_parts.append(f"\n=== {module_info['name']} ({module_id}) ===\n数据获取失败")

        full_context = '\n'.join(context_parts)
        logger.info(f"后端数据获取完成，总长度: {len(full_context)} chars")

        return full_context

    except Exception as e:
        logger.error(f"Failed to get real-time data: {e}")
        return "数据获取失败，请稍后重试"


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    history = data.get('history', [])
    # 不再使用前端传递的context，全部由后端获取

    def generate():
        try:
            llm = analyzer.init_langchain_llm(fast_mode=True)
            if not llm:
                yield f"data: {json.dumps({'error': 'LLM not initialized. Please check your API keys in .env file.'}, ensure_ascii=False)}\n\n"
                return

            # 后端智能获取相关数据
            yield f"data: {json.dumps({'type': 'status', 'message': '正在获取相关数据...'}, ensure_ascii=False)}\n\n"
            backend_context = get_real_time_data_context(user_message)

            # Bind tools to LLM
            tools = [search_news, fetch_webpage]
            llm_with_tools = llm.bind_tools(tools)

            messages = [
                SystemMessage(content="""You are a professional financial analyst assistant in a Bloomberg-like terminal Pro-Chat.

YOUR PRIMARY ROLE: ANALYZE & SUMMARIZE, NOT JUST DISPLAY DATA
- The user can already see all raw data on the page (tables, charts, prices)
- Your value is in ANALYSIS, INSIGHTS, and RECOMMENDATIONS
- DO NOT simply repeat table data unless user explicitly asks for specific data
- Instead, provide: trends, comparisons, opportunities, risks, actionable insights

AVAILABLE DATA IN CONTEXT:
The CONTEXT contains real-time data from relevant market modules:
1. 📰 7*24快讯 (kx) - Financial news (look for market-moving events)
2. 🌍 全球指数 (marker) - Global indices (analyze trends across markets)
3. 💰 实时贵金属 (real_time_gold) - Precious metals (identify price movements)
4. 📊 历史金价 (gold) - Historical gold trends
5. 📈 成交量趋势 (seven_A) - Trading volume trends
6. 🇨🇳 上证分时 (A) - Shanghai Composite intraday
7. 🎯 自选基金 (fund) - User's fund watchlist **← Analyze performance, winners/losers**
8. 🏭 行业板块 (bk) - Sector performance **← Identify hot/cold sectors**

HOW TO RESPOND BASED ON QUESTION TYPE:

1. GENERAL QUESTIONS (e.g., "今天市场怎么样？", "自选基金表现如何？"):
   ✓ DO: Provide high-level summary with key insights
   ✓ DO: Highlight top performers and underperformers
   ✓ DO: Mention noteworthy trends or patterns
   ✗ DON'T: List all funds/sectors in a table

2. SPECIFIC DATA REQUESTS (e.g., "xxx基金今天涨了多少？", "电子板块数据"):
   ✓ DO: Provide the specific data requested
   ✓ DO: Add context (e.g., how it compares to others)
   ✗ DON'T: Ignore the request and give general summary

3. ANALYTICAL QUESTIONS (e.g., "哪些基金值得关注？", "为什么黄金涨了？"):
   ✓ DO: Deep analysis using CONTEXT data
   ✓ DO: Cross-reference news with price movements
   ✓ DO: Provide reasoning and evidence
   ✗ DON'T: Give shallow or generic answers

EXAMPLE RESPONSES:

❌ BAD (just repeating data):
"自选基金数据如下：
易方达消费行业 +1.2%
招商中证白酒 -0.8%
..."

✅ GOOD (analysis & insights):
"<p style='color: #e0e0e0;'>今日 <span style='color: #42a5f5;'>自选基金</span> 整体表现分化：</p>
<ul style='margin: 4px 0; padding-left: 20px; color: #e0e0e0;'>
  <li><span style='color: #4caf50; font-weight: bold;'>消费板块基金领涨</span>（易方达消费行业 +1.2%），受益于消费数据回暖</li>
  <li><span style='color: #f44336;'>白酒板块承压</span>（招商中证白酒 -0.8%），与7*24快讯中提到的调控政策相关</li>
</ul>
<p style='color: #ffa726;'>建议：关注消费复苏趋势，白酒短期谨慎</p>"

RESPONSE STRUCTURE GUIDELINES:
- Start with a clear summary (1-2 sentences)
- Provide 2-4 key insights with evidence from CONTEXT
- Use bullet points for clarity
- End with actionable suggestion (if appropriate)
- Keep total response under 300 words unless deep analysis requested

WHEN TO USE TOOLS:
- User explicitly asks to "search online" or "find latest news from internet"
- Question about events/companies NOT in CONTEXT at all
- CONTEXT data is insufficient to answer

WHEN NOT TO USE TOOLS:
- User asks about "自选基金", "行业板块", "黄金" - data is in CONTEXT!
- General market questions answerable from CONTEXT
- Avoid over-reliance on external searches

RESPONSE FORMATTING (DARK THEME - ULTRA COMPACT):
Use BRIGHT colors on dark background with MINIMAL spacing:
- Default text: <p style="color: #e0e0e0; margin: 1px 0; line-height: 1.2;">
- Headers: <h4 style="color: #ffffff; margin: 2px 0 1px 0; font-size: 0.95em; font-weight: 600; line-height: 1.1;">
- Positive: <span style="color: #4caf50; font-weight: bold;">
- Negative: <span style="color: #f44336; font-weight: bold;">
- Highlights: <span style="color: #ffa726;">
- Module names: <span style="color: #42a5f5;">

Use COMPACT lists/bullets:
- <ul style="margin: 1px 0; padding-left: 14px; color: #e0e0e0; line-height: 1.2;">
- <li style="margin: 0;">

CRITICAL HTML RULES:
- ALWAYS close all HTML tags properly (</p>, </ul>, </span>, etc.)
- Keep HTML structure simple and valid
- Avoid deeply nested tags
- Complete your entire response - don't cut off mid-sentence

CRITICAL SPACING RULES:
- margin: 1px (极致紧凑)
- line-height: 1.2 (极紧行高)
- Minimize empty <p> tags between sections
- Use inline <span> instead of separate <p> when possible
- NO extra spacing between elements

Only use tables if user asks for specific data comparison.

NEVER use white backgrounds (#fff) or dark text (#000) - invisible on dark theme!

Remember: You are an ANALYST, not a data displayer. Keep responses CONCISE and COMPACT. Provide insights, not raw tables.""")
            ]

            # Add history (last 5 messages)
            for msg in history[-5:]:
                content = msg.get('content', '')
                if not content or not content.strip():
                    continue

                if msg.get('role') == 'user':
                    messages.append(HumanMessage(content=content))
                else:
                    messages.append(AIMessage(content=content))

            # Add current context and user message
            combined_input = f"CONTEXT FROM PAGE (后端实时数据):\n{backend_context}\n\nUSER QUESTION: {user_message}"
            messages.append(HumanMessage(content=combined_input))

            # Multi-turn tool calling loop
            max_iterations = 5
            iteration = 0

            while iteration < max_iterations:
                iteration += 1

                # Send status update
                yield f"data: {json.dumps({'type': 'status', 'message': f'Processing (step {iteration})...'}, ensure_ascii=False)}\n\n"

                # On last iteration, force answer without tools
                if iteration == max_iterations:
                    logger.debug(f"\n[Iteration {iteration}] Final iteration - forcing answer without tools")
                    # Add instruction to answer without more tool calls
                    messages.append(HumanMessage(content="Please provide your final answer now based on all the information gathered. Do not call any more tools."))
                    response = llm.invoke(messages)  # Use llm without tools
                else:
                    response = llm_with_tools.invoke(messages)

                # Check if LLM wants to call tools
                if response.tool_calls and iteration < max_iterations:
                    logger.debug(f"\n[Iteration {iteration}] LLM requested {len(response.tool_calls)} tool call(s)")

                    # Send tool call notification
                    tool_names = [tc["name"] for tc in response.tool_calls]
                    yield f"data: {json.dumps({'type': 'tool_call', 'tools': tool_names}, ensure_ascii=False)}\n\n"

                    messages.append(response)

                    # Execute all tool calls
                    for tool_call in response.tool_calls:
                        tool_name = tool_call["name"]
                        logger.debug(f"  → Calling {tool_name} with args: {tool_call['args']}")

                        if tool_name == "search_news":
                            tool_result = search_news.invoke(tool_call["args"])
                        elif tool_name == "fetch_webpage":
                            tool_result = fetch_webpage.invoke(tool_call["args"])
                        else:
                            tool_result = f"Unknown tool: {tool_name}"

                        logger.debug(f"  → Result preview: {str(tool_result)[:100]}...")

                        messages.append(ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_call["id"],
                            name=tool_name
                        ))

                    continue

                else:
                    # No more tool calls, stream the final answer
                    logger.debug(f"\n[Iteration {iteration}] LLM generated final answer")

                    # Stream the content with dynamic chunk size based on length
                    content = response.content
                    content_length = len(content)

                    # Dynamic chunk size: longer content = larger chunks
                    if content_length < 500:
                        chunk_size = 30  # Small content, smaller chunks for effect
                    elif content_length < 2000:
                        chunk_size = 80  # Medium content
                    else:
                        chunk_size = 150  # Large content, bigger chunks for speed

                    logger.debug(f"Streaming {content_length} chars with chunk_size={chunk_size}")

                    for i in range(0, content_length, chunk_size):
                        chunk = content[i:i+chunk_size]
                        yield f"data: {json.dumps({'type': 'content', 'chunk': chunk}, ensure_ascii=False)}\n\n"

                    # Send completion signal
                    yield f"data: {json.dumps({'type': 'done'})}\n\n"
                    return

            # Max iterations reached
            logger.debug(f"\n[Warning] Max iterations ({max_iterations}) reached")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Maximum iterations reached. Please try rephrasing your question.'})}\n\n"

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': f'Error: {str(e)}'})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'X-Accel-Buffering': 'no'
    })


@app.route('/fund', methods=['GET'])
def get_fund():
    add = request.args.get("add")
    delete = request.args.get("delete")
    importlib.reload(fund)
    my_fund = fund.MaYiFund()
    if add:
        my_fund.add_code(add)
    if delete:
        my_fund.delete_code(delete)
    results = {}

    def fetch_html(_name, _func):
        results[_name] = _func()

    threads = []
    tasks = {
        'marker': my_fund.marker_html,
        'gold': my_fund.gold_html,
        "real_time_gold": my_fund.real_time_gold_html,
        'A': my_fund.A_html,
        'fund': my_fund.fund_html,
        "seven_A": my_fund.seven_A_html,
        "bk": my_fund.bk_html,
        "kx": my_fund.kx_html,
    }
    for name, func in tasks.items():
        func = tasks[name]
        thread = threading.Thread(target=fetch_html, args=(name, func))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    tabs_data = [
        {"id": "kx", "title": "7*24快讯", "content": results["kx"]},
        {"id": "marker", "title": "全球指数", "content": results["marker"]},
        {"id": "real_time_gold", "title": "实时贵金属", "content": results["real_time_gold"]},
        {"id": "gold", "title": "历史金价", "content": results["gold"]},
        {"id": "seven_A", "title": "成交量趋势", "content": results["seven_A"]},
        {"id": "A", "title": "上证分时", "content": results["A"]},
        {"id": "fund", "title": "自选基金", "content": results["fund"]},
        {"id": "bk", "title": "行业板块", "content": results["bk"]},
    ]
    html = get_full_page_html(tabs_data)
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8311)
