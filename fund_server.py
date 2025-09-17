import importlib
import threading
from module_html import get_full_page_html

import urllib3
from flask import Flask, request

import fund

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
    }
    for name, func in tasks.items():
        func = tasks[name]
        thread = threading.Thread(target=fetch_html, args=(name, func))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()
    html = get_full_page_html(
        [results[name] for name in ["marker", "real_time_gold", "gold", "seven_A", "A", "fund", "bk"]]
    )
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8311)
