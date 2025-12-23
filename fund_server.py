import importlib
import threading
from dotenv import load_dotenv
from module_html import get_full_page_html

import urllib3
from flask import Flask, request, jsonify
from ai_analyzer import AIAnalyzer, search_news, fetch_webpage
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

import fund

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

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    history = data.get('history', [])
    context = data.get('context', '')

    llm = analyzer.init_langchain_llm(fast_mode=True)
    if not llm:
        return jsonify({"response": "Error: LLM not initialized. Please check your API keys in .env file."})

    # Bind tools to LLM
    tools = [search_news, fetch_webpage]
    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(content="""You are a professional financial assistant in a Bloomberg-like terminal Pro-Chat.

AVAILABLE RESOURCES:
1. Real-time market data from the current page view (provided as CONTEXT)
2. search_news tool - Search for latest financial news and market developments
3. fetch_webpage tool - Get full content from specific news article URLs

IMPORTANT - WHEN TO USE TOOLS:
You MUST actively use these tools in the following situations:

For search_news:
- User asks about "latest news", "recent developments", "what happened"
- User asks about specific companies, sectors, or industries beyond the page context
- User asks predictive questions ("will X rise?", "how will Y perform?") - search for supporting news
- Context data is insufficient to fully answer the user's question
- User mentions events, policies, or market movements not shown in the context

For fetch_webpage:
- search_news returned news titles/summaries but you need more detail
- User asks for in-depth analysis of a specific event or news story
- You need to verify details or get complete background information
- search_news results mention important articles that should be read in full

TOOL USAGE STRATEGY (for deep research):
1. First search with search_news to find relevant news articles
2. If the news summaries are insufficient, use fetch_webpage on important URLs from search results
3. Combine multiple sources for comprehensive analysis

RESPONSE STRATEGY:
1. Check if page CONTEXT can answer the question
2. If context is insufficient or user asks about news/events → CALL search_news
3. If search results need more detail → CALL fetch_webpage on the news URLs
4. Combine context data + search results + webpage content for comprehensive answers
5. Answer concisely and professionally using financial terminology

Remember: Proactive multi-tool use provides the deepest insights. Don't hesitate to call tools multiple times in sequence.""")
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
    combined_input = f"CONTEXT FROM PAGE:\n{context}\n\nUSER QUESTION: {user_message}"
    messages.append(HumanMessage(content=combined_input))

    try:
        # Multi-turn tool calling loop
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call LLM (with tools on first call, without tools on final answer)
            if iteration == 1:
                response = llm_with_tools.invoke(messages)
            else:
                # Continue using llm_with_tools to allow further tool calls
                response = llm_with_tools.invoke(messages)

            # Check if LLM wants to call tools
            if response.tool_calls:
                print(f"\n[Iteration {iteration}] LLM requested {len(response.tool_calls)} tool call(s)")

                # Add the assistant's tool call message
                messages.append(response)

                # Execute all tool calls
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    print(f"  → Calling {tool_name} with args: {tool_call['args']}")

                    # Execute the appropriate tool
                    if tool_name == "search_news":
                        tool_result = search_news.invoke(tool_call["args"])
                    elif tool_name == "fetch_webpage":
                        tool_result = fetch_webpage.invoke(tool_call["args"])
                    else:
                        tool_result = f"Unknown tool: {tool_name}"

                    print(f"  → Result preview: {str(tool_result)[:100]}...")

                    # Add tool result to messages
                    messages.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call["id"],
                        name=tool_name
                    ))

                # Continue loop to let LLM decide next action
                continue

            else:
                # No more tool calls, LLM has generated final answer
                print(f"\n[Iteration {iteration}] LLM generated final answer (no more tool calls)")
                return jsonify({"response": response.content})

        # If max iterations reached, return current response
        print(f"\n[Warning] Max iterations ({max_iterations}) reached")
        if hasattr(response, 'content'):
            return jsonify({"response": response.content})
        else:
            return jsonify({"response": "Maximum tool call iterations reached. Please try rephrasing your question."})

    except Exception as e:
        return jsonify({"response": f"Error generating response: {str(e)}"})

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
    html = get_full_page_html(
        [results[name] for name in ["kx", "marker", "real_time_gold", "gold", "seven_A", "A", "fund", "bk"]]
    )
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8311)
