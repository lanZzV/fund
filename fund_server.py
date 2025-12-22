import importlib
import threading
from dotenv import load_dotenv
from module_html import get_full_page_html

import urllib3
from flask import Flask, request, jsonify
from ai_analyzer import AIAnalyzer, search_news
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
    tools = [search_news]
    llm_with_tools = llm.bind_tools(tools)

    messages = [
        SystemMessage(content="You are a professional financial assistant in a Bloomberg-like terminal Pro-Chat. "
                              "You have access to the real-time market data provided by the user from the current page view. "
                              "You also have a 'search_news' tool to find latest market news. "
                              "Answer concisely, professionally, and use financial terminology where appropriate. "
                              "If the user asks about specific data, refer to the provided context.")
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
        # First call: LLM decides whether to use tools or answer directly
        response = llm_with_tools.invoke(messages)
        
        # If tool calls are generated
        if response.tool_calls:
            messages.append(response) # Add the assistant's tool call message
            
            for tool_call in response.tool_calls:
                # Execute tool
                if tool_call["name"] == "search_news":
                    print(f"Tool 'search_news' called with args: {tool_call['args']}")
                    tool_result = search_news.invoke(tool_call["args"])
                    print(f"Tool 'search_news' result: {tool_result[:100]}...") # Print first 100 chars
                    
                    # Add tool result to messages
                    messages.append(ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_call["id"],
                        name=tool_call["name"]
                    ))
            
            # Second call: Generate final answer based on tool results
            final_response = llm.invoke(messages)
            return jsonify({"response": final_response.content})
            
        else:
            # No tool call needed, return direct answer
            return jsonify({"response": response.content})

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
