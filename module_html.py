# -*- coding: UTF-8 -*-

def get_table_html(title, data, sortable_columns=None):
    """
    生成单个表格的HTML代码。
    :param title: list, 表头标题列表。
    :param data: list of lists, 表格数据。
    :param sortable_columns: list, 可排序的列的索引 (从0开始)。例如 [1, 2, 3]
    """
    if sortable_columns is None:
        sortable_columns = []

    ths = []
    for i, col_name in enumerate(title):
        if i in sortable_columns:
            ths.append(f'<th class="sortable" onclick="sortTable(this.closest(\'table\'), {i})">{col_name}</th>')
        else:
            ths.append(f"<th>{col_name}</th>")

    thead_html = f"""
    <thead>
        <tr>
            {''.join(ths)}
        </tr>
    </thead>
    """

    tbody_rows = []
    for row_data in data:
        tds = [f"<td>{x}</td>" for x in row_data]
        tbody_rows.append(f"<tr>{''.join(tds)}</tr>")

    tbody_html = f"""
    <tbody>
        {''.join(tbody_rows)}
    </tbody>
    """

    return f"""
    <div class="table-container">
        <table class="style-table">
            {thead_html}
            {tbody_html}
        </table>
    </div>
    """


def get_full_page_html(all_tables_html):
    js_script = get_javascript_code()
    css_style = get_css_style()

    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
        <meta http-equiv="Pragma" content="no-cache">
        <meta http-equiv="Expires" content="0">
        <title>MaYi Fund Dashboard</title>
        {css_style}
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">MaYi Fund 蚂蚁基金助手</div>
            <div class="navbar-menu">
                <span class="navbar-item">实时行情</span>
            </div>
        </nav>
        
        <div class="app-container">
            <div class="main-content">
                <div class="dashboard-grid">
                    {''.join(all_tables_html)}
                </div>
            </div>
            
            <div class="pro-chat-sidebar">
                <div id="pro-chat-root" style="height: 100%; width: 100%;"></div>
            </div>
        </div>

        {js_script}
    </body>
    </html>
    """


def get_css_style():
    return r"""
    <style>
        :root {
            --primary-color: #000000;
            --background-color: #ffffff;
            --card-background: #ffffff;
            --text-color: #000000;
            --border-color: #000000;
            --header-bg: #ffffff;
            --hover-bg: #f0f0f0;
            /* Bloomberg 风格：鲜艳的红绿用于金融数据 */
            --up-color: #d10000; /* Red for rise (China) */
            --down-color: #008000; /* Green for fall (China) */
            /* Bloomberg 特有的强调蓝 */
            --bloomberg-blue: #0070e0;
            --font-family: "Haas Grot Text R", "Helvetica Neue", Helvetica, Arial, sans-serif;
            --font-mono: "Menlo", "Consolas", "Roboto Mono", monospace;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: var(--font-family);
            background-color: var(--background-color);
            color: var(--text-color);
            line-height: 1.4;
            -webkit-font-smoothing: antialiased;
        }

        /* Navbar */
        .navbar {
            background-color: #000000;
            color: #ffffff;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
            border-bottom: 4px solid var(--bloomberg-blue);
        }

        .navbar-brand {
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            text-transform: uppercase;
        }

        .navbar-item {
            font-weight: 700;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* Layout */
        .app-container {
            display: flex;
            min-height: calc(100vh - 60px); /* Subtract navbar height */
            overflow: hidden; /* Prevent body scroll */
        }

        .main-content {
            padding: 2rem;
            flex: 1;
            margin: 0;
            overflow-y: auto;
            height: calc(100vh - 60px);
            background-color: #f5f5f5; /* Light grey for content area */
        }

        .dashboard-grid {
            display: flex;
            flex-direction: column;
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
            padding-bottom: 40px;
        }

        /* Pro Chat Sidebar */
        .pro-chat-sidebar {
            width: 400px;
            background-color: #ffffff;
            border-left: 1px solid #e0e0e0;
            height: calc(100vh - 60px);
            position: relative;
            z-index: 10;
        }

        /* Tables */
        .table-container {
            background: var(--card-background);
            /* Bloomberg 风格：无圆角，无阴影，只有实线 */
            border-top: 4px solid #000000;
            border-bottom: 1px solid #000000;
            overflow-x: auto;
            margin-bottom: 1rem;
        }

        .style-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        .style-table th {
            text-align: left;
            padding: 12px 16px;
            background-color: var(--header-bg);
            font-weight: 800;
            color: #000000;
            border-bottom: 2px solid #000000;
            white-space: nowrap;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }

        .style-table td {
            padding: 12px 16px;
            border-bottom: 1px solid #e0e0e0;
            color: #000000;
            font-weight: 400;
        }

        .style-table tbody tr:hover {
            background-color: var(--hover-bg);
        }
        
        /* 最后一行的下划线加粗 */
        .style-table tbody tr:last-child td {
            border-bottom: 1px solid #000000;
        }

        /* Sortable Headers */
        .style-table th.sortable {
            cursor: pointer;
            user-select: none;
            transition: color 0.2s;
        }

        .style-table th.sortable:hover {
            color: var(--bloomberg-blue);
        }

        .style-table th.sortable::after {
            content: '↕';
            display: inline-block;
            margin-left: 8px;
            font-size: 0.8em;
            color: #ccc;
        }

        .style-table th.sorted-asc::after {
            content: '↑';
            color: #000000;
        }

        .style-table th.sorted-desc::after {
            content: '↓';
            color: #000000;
        }

        /* Numeric Columns Alignment & Font */
        .style-table th:nth-child(n+2),
        .style-table td:nth-child(n+2) {
            text-align: right;
            font-family: var(--font-mono); /* 使用等宽字体显示数字 */
            font-variant-numeric: tabular-nums; /* 确保数字对齐 */
        }
        
        /* Colors */
        .positive {
            color: var(--up-color) !important;
            font-weight: 700;
        }

        .negative {
            color: var(--down-color) !important;
            font-weight: 700;
        }
        
        /* Specific tweaks for small screens */
        @media (max-width: 768px) {
            .app-container {
                flex-direction: column;
            }
            .main-content {
                height: auto;
                min-height: 50vh;
            }
            .pro-chat-sidebar {
                width: 100%;
                height: 600px;
                border-left: none;
                border-top: 1px solid #e0e0e0;
            }
            .navbar {
                padding: 1rem;
            }
            .style-table {
                font-size: 0.8rem;
            }
        }
    </style>
    """


def get_javascript_code():
    return r"""
    <!-- Import Map for ESM modules -->
    <script>
    // Polyfill process for React libraries
    window.process = {
        env: {
            NODE_ENV: 'production'
        }
    };
    window.onerror = function(message, source, lineno, colno, error) {
        console.error("Global Error Caught:", error);
        const root = document.getElementById('pro-chat-root');
        if (root && root.innerHTML === '') {
            root.innerHTML = `<div style="padding:20px; color:red;">
                <h3>Failed to load Pro Chat</h3>
                <p>Error: ${message}</p>
                <p>Dependencies might be missing in CDN mode.</p>
                <button onclick="location.reload()" style="padding:5px 10px; margin-top:10px;">Retry</button>
            </div>`;
        }
    };
    </script>
    <link rel="stylesheet" href="https://unpkg.com/quikchat/dist/quikchat.css">
    <script src="https://unpkg.com/quikchat"></script>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize Auto Colorize
        autoColorize();
        
        // Initialize QuikChat
        const chat = new quikchat('#pro-chat-root', async (instance, message) => {
            // Display user message immediately
            instance.messageAddNew(message, 'You', 'right');
            
            // Collect page context
            const context = document.querySelector('.main-content').innerText;
            
            // Extract history from instance
            const rawHistory = instance.historyGetAllCopy();
            console.log("Raw History from QuikChat:", rawHistory);

            const history = rawHistory
                .map(msg => ({
                    role: (msg.name === 'You' || msg.sender === 'You') ? 'user' : 'assistant',
                    content: msg.body || msg.content || msg.text || ""
                }))
                .filter(msg => msg.content && msg.content.trim() !== '');
            
            console.log("Processed History to Send:", history);

            try {
                // Show loading indicator (simulated by a temporary bot message or just waiting)
                // instance.messageAddNew('Thinking...', 'System', 'left'); 
                
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        history: history, // Send empty history for now, or implement history extraction
                        context: context
                    })
                });

                const data = await response.json();
                
                if (data.error) {
                     instance.messageAddNew('Error: ' + data.error, 'System', 'left');
                } else {
                     instance.messageAddNew(data.response, 'AI Analyst', 'left');
                }

            } catch (err) {
                instance.messageAddNew('Network Error: ' + err.message, 'System', 'left');
            }
        }, {
            theme: 'quikchat-theme-dark',
            botName: 'AI Analyst',
            userAvatar: 'https://ui-avatars.com/api/?name=User&background=0D8ABC&color=fff',
            botAvatar: 'https://ui-avatars.com/api/?name=AI&background=ff9900&color=fff',
            placeholder: 'Ask about market data...'
        });

        // Add welcome message
        setTimeout(() => {
            chat.messageAddNew("Welcome to MaYi Fund Pro Terminal. Connected to market data stream.", 'System', 'left');
        }, 500);
    });
    </script>


    <!-- Standard JS for table coloring -->
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        autoColorize();
    });

    function autoColorize() {
        const cells = document.querySelectorAll('.style-table td');
        cells.forEach(cell => {
            const text = cell.textContent.trim();
            const cleanText = text.replace(/[%,亿万手]/g, '');
            const val = parseFloat(cleanText);

            if (!isNaN(val)) {
                if (text.includes('%') || text.includes('涨跌')) {
                    if (text.includes('-')) {
                        cell.classList.add('negative');
                    } else if (val > 0) {
                        cell.classList.add('positive');
                    }
                } else if (text.startsWith('-')) {
                    cell.classList.add('negative');
                } else if (text.startsWith('+')) {
                    cell.classList.add('positive');
                }
            }
        });
    }

    function sortTable(table, columnIndex) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        const currentSortCol = table.dataset.sortCol;
        const currentSortDir = table.dataset.sortDir || 'asc';
        let direction = 'asc';

        if (currentSortCol == columnIndex) {
            direction = currentSortDir === 'asc' ? 'desc' : 'asc';
        }
        table.dataset.sortCol = columnIndex;
        table.dataset.sortDir = direction;

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

        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));

        table.querySelectorAll('th').forEach(th => {
            th.classList.remove('sorted-asc', 'sorted-desc');
        });
        const headerToUpdate = table.querySelectorAll('th')[columnIndex];
        if (headerToUpdate) {
            headerToUpdate.classList.add(direction === 'asc' ? 'sorted-asc' : 'sorted-desc');
        }
    }

    function parseValue(val) {
        if (val === 'N/A' || val === '--' || val === '') {
            return -Infinity;
        }
        const cleanedVal = val.replace(/%|亿|万|元\/克|手/g, '').replace(/,/g, '');
        const num = parseFloat(cleanedVal);
        return isNaN(num) ? val.toLowerCase() : num;
    }
    </script>
    """
