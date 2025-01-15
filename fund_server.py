import urllib3
from flask import Flask, request

from fund import MaYiFund

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

    fund = MaYiFund()
    if add:
        fund.add_code(add)
    if delete:
        fund.delete_code(delete)
    html = fund.marker_html()
    html += "\n" + fund.gold_html()
    html += "\n" + fund.A_html()
    html += "\n" + fund.fund_html()
    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8311)