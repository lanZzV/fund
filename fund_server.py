import importlib

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
    html = my_fund.marker_html()
    html += "\n" + my_fund.gold_html()
    html += "\n" + my_fund.A_html()
    html += "\n" + my_fund.fund_html()
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8311)
