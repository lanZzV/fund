# -*- coding: UTF-8 -*-


def get_result_html(title):
    ths = [f"<th>{x}</th>" for x in title]
    ths = "\n".join(ths)
    result = r"""
    <table class="style-table">
        <thread>
            <tr>
    """ + ths + r"""</tr>
        </thread>
        <tbody>
        {tbody}
        </tbody>
    </table>
    """
    return result


def get_tbody(data):
    tds = [f"<td>{x}</td>" for x in data]
    tds = "\n".join(tds)
    tbody = r"""
        <tr>
    """ + tds + r"""
        </tr>
    """
    return tbody


style = r"""
<style>
    .style-table {
        border-collapse: collapse;
        margin: 50px auto;
        font-size: 0.9em;
        /*min-width: 800px;*/
        width: 100%;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
    }

    .style-table thead tr {
        background-color: #0398dd;
        color: #ffffff;
        text-align: center;
    }

    .style-table th,
    .style-table td {
        padding: 12px 15px;
    }

    .style-table tbody tr {
        border-bottom: 1px solid #dddddd;
        text-align: center;

    }

    .style-table tbody tr:nth-of-type(even) {
        background-color: #f3f3f3;
    }

    .style-table tbody tr:last-of-type {
        border-bottom: 2px solid #0398dd;
    }

</style>
"""
