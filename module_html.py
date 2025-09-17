# -*- coding: UTF-8 -*-

def get_table_html(title, data, sortable_columns=None):
    """
    生成单个表格的HTML代码。
    :param title: list, 表头标题列表。
    :param data: list of lists, 表格数据。
    :param sortable_columns: list, 可排序的列的索引 (从0开始)。例如 [1, 2, 3]
    """
    # 1. 生成表头 (thead)
    if sortable_columns is None:
        sortable_columns = []

    ths = []
    # enumerate(title) 可以同时获得索引和值
    for i, col_name in enumerate(title):
        if i in sortable_columns:
            # 如果当前列是可排序的，添加 sortable 类和 onclick 事件
            # onclick="sortTable(this.closest('table'), i)"
            # this.closest('table') 会找到当前点击的 th 所在的 table 元素
            # i 是当前列的索引
            ths.append(f'<th class="sortable" onclick="sortTable(this.closest(\'table\'), {i})">{col_name}</th>')
        else:
            # 不可排序的列，生成普通的 th
            ths.append(f"<th>{col_name}</th>")

    thead_html = f"""
    <thead>
        <tr>
            {''.join(ths)}
        </tr>
    </thead>
    """

    # 2. 生成表体 (tbody)
    tbody_rows = []
    for row_data in data:
        tds = [f"<td>{x}</td>" for x in row_data]
        tbody_rows.append(f"<tr>{''.join(tds)}</tr>")

    tbody_html = f"""
    <tbody>
        {''.join(tbody_rows)}
    </tbody>
    """

    # 3. 组合成完整的 table
    return f"""
    <table class="style-table">
        {thead_html}
        {tbody_html}
    </table>
    """


def get_full_page_html(all_tables_html):
    # 将所有JS和CSS代码放在页面底部，只加载一次
    js_script = get_javascript_code()
    css_style = get_css_style()

    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>基金助手</title>
    </head>
    <body>
        {''.join(all_tables_html)}
        {css_style}
        {js_script}
    </body>
    </html>
    """


def get_css_style():
    # 这是根据你的最新要求设计的最终样式。
    # 白色背景，蓝色底线，蓝色箭头。
    return r"""
    <style>
        .style-table {
            border-collapse: collapse;
            margin: 50px auto;
            font-size: 0.9em;
            width: 100%;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            font-family: sans-serif;
        }

        /* --- 核心修改区域 --- */
        .style-table thead tr {
            background-color: #ffffff; /* 1. 改为白色背景 */
            color: #333333; /* 2. 字体颜色改为深灰色，更清晰 */
            text-align: center;
            border-bottom: 2px solid #0398dd; /* 3. 核心改动：添加底部的蓝色实线 */
        }
        /* --- 核心修改区域结束 --- */

        .style-table th,
        .style-table td {
            padding: 12px 15px;
            text-align: center;
        }

        .style-table tbody tr {
            border-bottom: 1px solid #dddddd;
        }

        .style-table tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }

        .style-table tbody tr:last-of-type {
            border-bottom: 2px solid #0398dd;
        }

        /* --- 同样需要调整排序箭头的样式以适应新背景 --- */
        .style-table th.sortable {
            cursor: pointer;
            position: relative;
            padding-right: 30px; 
        }

        /* 5. 修改鼠标悬浮效果，以适应新的白色背景 */
        .style-table th.sortable:hover {
            background-color: #f5f5f5; 
        }

        .style-table th.sortable::before,
        .style-table th.sortable::after {
            content: "";
            position: absolute;
            right: 12px;
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            opacity: 0.4;
            transition: opacity 0.2s ease-in-out;
        }

        .style-table th.sortable::before {
            top: 50%;
            margin-top: -10px;
            /* 4. 将箭头颜色从白色改为蓝色，以适应白色背景 */
            border-bottom: 6px solid #0398dd; 
        }

        .style-table th.sortable::after {
            top: 50%;
            margin-top: 2px;
            /* 4. 将箭头颜色从白色改为蓝色，以适应白色背景 */
            border-top: 6px solid #0398dd;
        }

        .style-table th.sorted-asc::before {
            opacity: 1;
        }
        .style-table th.sorted-asc::after {
            opacity: 0.4;
        }

        .style-table th.sorted-desc::after {
            opacity: 1;
        }
         .style-table th.sorted-desc::before {
            opacity: 0.4;
        }
    </style>
    """


def get_javascript_code():
    # 这是实现排序的核心JS代码
    return r"""
    <script>
    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));

        // --- 排序方向逻辑 ---
        // 获取当前排序列和方向 (存储在 table 的 data-* 属性中)
        const currentSortCol = table.dataset.sortCol;
        const currentSortDir = table.dataset.sortDir || 'asc';
        let direction = 'asc';

        // 如果点击的是同一列，则切换排序方向
        if (currentSortCol == columnIndex) {
            direction = currentSortDir === 'asc' ? 'desc' : 'asc';
        }
        // 更新 table 的 data-* 属性
        table.dataset.sortCol = columnIndex;
        table.dataset.sortDir = direction;

        // --- 数据解析和排序 ---
        rows.sort((a, b) => {
            const aText = a.cells[columnIndex].textContent.trim();
            const bText = b.cells[columnIndex].textContent.trim();

            const valA = parseValue(aText);
            const valB = parseValue(bText);

            let comparison = 0;
            if (valA > valB) {
                comparison = 1;
            } else if (valA < valB) {
                comparison = -1;
            }

            return direction === 'asc' ? comparison : -comparison;
        });

        // --- 更新DOM ---
        // 1. 清空 tbody
        tbody.innerHTML = '';
        // 2. 将排序后的 rows 重新插入
        rows.forEach(row => tbody.appendChild(row));

        // 3. 更新表头的CSS类，以显示正确的箭头
        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
        });
        const headerToUpdate = table.querySelectorAll('th')[columnIndex];
        if (headerToUpdate) {
            headerToUpdate.classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }
    }

    function parseValue(val) {
        // 如果值是 'N/A' 或 '--' 等，当作最小值处理以便排序
        if (val === 'N/A' || val === '--' || val === '') {
            return -Infinity;
        }

        // 尝试将值转换为数字，处理百分比、逗号、单位等
        // 这个正则表达式会移除大部分非数字字符，但保留负号和小数点
        const cleanedVal = val.replace(/%|亿|万|元\/克|手/g, '').replace(/,/g, '');
        const num = parseFloat(cleanedVal);

        // 如果转换后是有效的数字，则返回数字；否则返回原始字符串（进行文本排序）
        return isNaN(num) ? val.toLowerCase() : num;
    }
    </script>
    """
