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


def get_full_page_html(tabs_data):
    js_script = get_javascript_code()
    css_style = get_css_style()

    # Generate Tab Headers
    tab_headers = []
    tab_contents = []

    # Check if tabs_data is a list of dicts (new format) or list of strings (old format fallback)
    if isinstance(tabs_data, list) and len(tabs_data) > 0 and isinstance(tabs_data[0], str):
        # Fallback for old format
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MaYi Fund Dashboard</title>
            {css_style}
        </head>
        <body>
            <div class="app-container">
                <div class="main-content">
                    <div class="dashboard-grid">
                        {''.join(tabs_data)}
                    </div>
                </div>
            </div>
            {js_script}
        </body>
        </html>
        """

    for index, tab in enumerate(tabs_data):
        is_active = 'active' if index == 0 else ''
        tab_id = tab['id']
        tab_title = tab['title']
        content = tab['content']

        tab_headers.append(f"""
            <button class="tab-button {is_active}" onclick="openTab(event, '{tab_id}')">
                {tab_title}
            </button>
        """)

        tab_contents.append(f"""
            <div id="{tab_id}" class="tab-content {is_active}">
                {content}
            </div>
        """)

    # Check if we have actual data or if this is initial SSE setup
    has_data = tabs_data and len(tabs_data) > 0 and tabs_data[0].get('content', '').strip()

    if not has_data:
        # Return SSE-enabled loading page
        return get_sse_loading_page(css_style, js_script)

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
                <div class="tabs-header">
                    {''.join(tab_headers)}
                </div>
                <div class="dashboard-grid">
                    {''.join(tab_contents)}
                </div>
            </div>
            
            <div class="pro-chat-sidebar" id="chat-sidebar">
                <div class="resize-handle" id="resize-handle"></div>
                <div id="pro-chat-root" style="height: 100%; width: 100%;"></div>
            </div>
        </div>

        {js_script}
    </body>
    </html>
    """


def get_sse_loading_page(css_style, js_script):
    """Return a loading page that will be updated via SSE"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MaYi Fund Dashboard - Loading</title>
        {css_style}
        <style>
            .loading-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100%;
                padding: 2rem;
            }}
            .loading-spinner {{
                border: 4px solid #f3f3f3;
                border-top: 4px solid var(--bloomberg-blue);
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
            }}
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
            .loading-status {{
                margin-top: 1rem;
                font-size: 0.9rem;
                color: #666;
            }}
            .task-list {{
                margin-top: 1rem;
                max-width: 400px;
            }}
            .task-item {{
                padding: 0.5rem;
                margin: 0.3rem 0;
                border-radius: 4px;
                background: #f5f5f5;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .task-item.completed {{
                background: #d4edda;
                color: #155724;
            }}
            .task-item.error {{
                background: #f8d7da;
                color: #721c24;
            }}
        </style>
    </head>
    <body>
        <nav class="navbar">
            <div class="navbar-brand">MaYi Fund 蚂蚁基金助手</div>
            <div class="navbar-menu">
                <span class="navbar-item">加载中...</span>
            </div>
        </nav>
        
        <div class="app-container">
            <div class="main-content">
                <div class="loading-container">
                    <div class="loading-spinner"></div>
                    <div class="loading-status" id="status">正在连接数据源...</div>
                    <div class="task-list" id="task-list"></div>
                </div>
            </div>
        </div>

        <script>
        const eventSource = new EventSource('/fund' + window.location.search);
        const taskList = document.getElementById('task-list');
        const statusEl = document.getElementById('status');
        const taskElements = {{}};

        eventSource.addEventListener('message', function(e) {{
            try {{
                const data = JSON.parse(e.data);
                
                if (data.type === 'init') {{
                    statusEl.textContent = '正在加载数据模块...';
                    data.tasks.forEach(taskName => {{
                        const taskEl = document.createElement('div');
                        taskEl.className = 'task-item';
                        taskEl.innerHTML = `<span>${{getTaskTitle(taskName)}}</span><span>⏳</span>`;
                        taskList.appendChild(taskEl);
                        taskElements[taskName] = taskEl;
                    }});
                }}
                else if (data.type === 'task_complete') {{
                    if (taskElements[data.name]) {{
                        taskElements[data.name].className = 'task-item completed';
                        taskElements[data.name].querySelector('span:last-child').textContent = '✓';
                    }}
                }}
                else if (data.type === 'error') {{
                    if (taskElements[data.name]) {{
                        taskElements[data.name].className = 'task-item error';
                        taskElements[data.name].querySelector('span:last-child').textContent = '✗';
                    }}
                }}
                else if (data.type === 'complete') {{
                    statusEl.textContent = '加载完成！正在渲染页面...';
                    eventSource.close();
                    // Replace entire page with the complete HTML
                    document.open();
                    document.write(data.html);
                    document.close();
                }}
            }} catch (err) {{
                console.error('SSE parse error:', err);
            }}
        }});

        eventSource.addEventListener('error', function(e) {{
            statusEl.textContent = '连接错误，正在重试...';
            console.error('SSE error:', e);
        }});

        function getTaskTitle(taskName) {{
            const titles = {{
                'kx': '7*24快讯',
                'marker': '全球指数',
                'real_time_gold': '实时贵金属',
                'gold': '历史金价',
                'seven_A': '成交量趋势',
                'A': '上证分时',
                'fund': '自选基金',
                'bk': '行业板块'
            }};
            return titles[taskName] || taskName;
        }}
        </script>
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

        .tabs-header {
            display: flex;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 1rem;
            background: #fff;
            padding: 0 1rem;
        }

        .tab-button {
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 700;
            text-align: center;
            position: relative;
            transition: all 0.3s;
            color: #666;
            font-size: 0.95rem;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }

        .tab-button:hover {
            color: var(--bloomberg-blue);
            background-color: rgba(0, 112, 224, 0.05);
        }

        .tab-button.active {
            color: var(--bloomberg-blue);
            border-bottom: 3px solid var(--bloomberg-blue);
        }

        .tab-content {
            display: none;
            padding: 1rem 0;
            animation: fadeIn 0.3s ease-in-out;
        }

        .tab-content.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .dashboard-grid {
            display: flex;
            border-bottom: 2px solid #e0e0e0;
            margin-bottom: 1rem;
        }

        .tab-button {
            flex: 1;
            padding: 12px 16px;
            background: none;
            border: none;
            cursor: pointer;
            font-weight: 700;
            text-align: center;
            position: relative;
            transition: color 0.3s;
        }

        .tab-button.active {
            color: var(--bloomberg-blue);
            border-bottom: 2px solid var(--bloomberg-blue);
        }

        .tab-content {
            display: none;
            padding: 1rem 0;
        }

        .tab-content.active {
            display: block;
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
            min-width: 300px;
            max-width: 800px;
        }

        /* Resize Handle */
        .resize-handle {
            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 5px;
            cursor: ew-resize;
            background: transparent;
            z-index: 100;
            transition: background 0.2s;
        }

        .resize-handle:hover,
        .resize-handle.resizing {
            background: #0D8ABC;
        }

        /* Typing Indicator Animation */
        .typing-indicator {
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .typing-indicator span {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #999;
            animation: typing-bounce 1.4s infinite;
        }

        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing-bounce {
            0%, 60%, 100% {
                transform: translateY(0);
            }
            30% {
                transform: translateY(-10px);
            }
        }

        /* Streaming content animation */
        #streaming-response {
            animation: fadeIn 0.3s ease-in;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
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

        /* Chat Content Styles - Dark Theme Optimized & Compact */
        #pro-chat-root {
            line-height: 1.4;
        }
        
        #pro-chat-root p { 
            margin: 4px 0; 
            color: #e0e0e0;
        }
        
        #pro-chat-root h1, #pro-chat-root h2, #pro-chat-root h3, #pro-chat-root h4, #pro-chat-root h5 {
            color: #ffffff;
            margin: 8px 0 4px 0;
            font-weight: 600;
            line-height: 1.3;
        }
        
        #pro-chat-root h4 {
            font-size: 1em;
        }
        
        #pro-chat-root ul, #pro-chat-root ol { 
            margin: 4px 0; 
            padding-left: 20px; 
            color: #e0e0e0;
        }
        
        #pro-chat-root li { 
            margin: 2px 0; 
        }
        
        #pro-chat-root code { 
            font-family: var(--font-mono); 
            background: rgba(255,255,255,0.1); 
            padding: 2px 4px; 
            border-radius: 3px;
            color: #ffa726;
        }
        
        #pro-chat-root pre { 
            background: rgba(0,0,0,0.3); 
            padding: 8px; 
            border-radius: 4px; 
            overflow-x: auto; 
            margin: 6px 0;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        #pro-chat-root pre code { 
            background: none; 
            padding: 0; 
            color: #e0e0e0;
        }
        
        #pro-chat-root blockquote { 
            border-left: 3px solid #0D8ABC; 
            padding: 4px 0 4px 10px; 
            margin: 6px 0; 
            color: #b0b0b0;
            background: rgba(255,255,255,0.03);
        }
        
        /* Ensure all tables in chat are dark-theme compatible */
        #pro-chat-root table {
            color: #e0e0e0;
            background: transparent;
            border-collapse: collapse;
            font-size: 0.85em;
            margin: 6px 0;
        }
        
        #pro-chat-root th {
            color: #ffffff;
            background: rgba(255,255,255,0.08);
            padding: 4px 8px;
            border-bottom: 1px solid #555;
            text-align: left;
        }
        
        #pro-chat-root td {
            color: #e0e0e0;
            padding: 3px 8px;
            border-bottom: 1px solid #333;
        }
        
        #pro-chat-root tr:hover {
            background: rgba(255,255,255,0.05);
        }
        
        /* Override any white backgrounds that might come from AI output */
        #pro-chat-root div[style*="background-color: #fff"],
        #pro-chat-root div[style*="background-color: #ffffff"],
        #pro-chat-root div[style*="background-color: #f5f5f5"],
        #pro-chat-root div[style*="background: #fff"],
        #pro-chat-root div[style*="background: #ffffff"] {
            background: rgba(255,255,255,0.05) !important;
        }
        
        /* Ensure dark text becomes light */
        #pro-chat-root span[style*="color: #000"],
        #pro-chat-root span[style*="color: #333"],
        #pro-chat-root p[style*="color: #000"],
        #pro-chat-root p[style*="color: #333"] {
            color: #e0e0e0 !important;
        }
        
        /* Typewriter content container */
        #typewriter-content {
            color: #e0e0e0;
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
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Initialize Auto Colorize
        autoColorize();
        
        // Initialize QuikChat
        const chat = new quikchat('#pro-chat-root', async (instance, message) => {
            // Display user message immediately
            instance.messageAddNew(message, 'You', 'right');
            
            // 不再收集前端context，所有数据由后端获取
            console.log("Sending message to backend (context will be fetched by backend)");
            
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

            // Create loading indicator
            const loadingHtml = '<div class="ai-loading-indicator" style="display: flex; align-items: center; gap: 10px;"><div class="typing-indicator"><span></span><span></span><span></span></div><span style="color: #999;">AI Analyst is thinking...</span></div>';
            instance.messageAddNew(loadingHtml, 'System', 'left');

            try {
                let streamingContent = '';
                let hasReceivedContent = false;
                let contentDisplayed = false;
                let loadingRemoved = false;
                let currentStepElement = null; // Track current step status element
                
                // Helper to remove loading indicator
                function removeLoadingIndicator() {
                    if (!loadingRemoved) {
                        try {
                            // Find and remove by class name
                            const loadingElements = document.querySelectorAll('.ai-loading-indicator');
                            loadingElements.forEach(el => {
                                const messageDiv = el.closest('.quikchat-message');
                                if (messageDiv) {
                                    messageDiv.remove();
                                }
                            });
                            loadingRemoved = true;
                            console.log('Loading indicator removed');
                        } catch (e) {
                            console.warn('Failed to remove loading indicator:', e);
                        }
                    }
                }
                
                // Helper to show step status
                function showStepStatus(message, icon = '⏳') {
                    // Remove previous step if exists
                    if (currentStepElement) {
                        try {
                            currentStepElement.remove();
                            console.log('Previous step removed');
                        } catch (e) {
                            console.warn('Failed to remove previous step:', e);
                        }
                    }
                    
                    // Create new step status
                    const stepHtml = `<div style="display: flex; align-items: center; gap: 8px; padding: 4px 8px; background: rgba(13,138,188,0.1); border-radius: 4px;">
                        <span style="font-size: 1.2em;">${icon}</span>
                        <span style="color: #42a5f5; font-size: 0.9em;">${message}</span>
                    </div>`;
                    
                    instance.messageAddNew(stepHtml, 'System', 'left');
                    
                    // Get the newly added element
                    setTimeout(() => {
                        const allMessages = document.querySelectorAll('.quikchat-message');
                        currentStepElement = allMessages[allMessages.length - 1];
                    }, 10);
                }
                
                // Use fetch with SSE
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: message,
                        history: history
                    })
                });

                if (!response.ok) {
                    instance.messageAddNew('Network Error: ' + response.statusText, 'System', 'left');
                    return;
                }

                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                let buffer = '';
                let lastChunkTime = Date.now();
                
                // Timeout checker
                const timeoutChecker = setInterval(() => {
                    const timeSinceLastChunk = Date.now() - lastChunkTime;
                    if (timeSinceLastChunk > 30000) { // 30 seconds timeout
                        console.warn('Stream timeout detected');
                        clearInterval(timeoutChecker);
                        reader.cancel();
                    }
                }, 5000);
                
                // Helper function to detect and render content
                function renderContent(content) {
                    const looksLikeHTML = content.trim().startsWith('<') && /<[^>]+>/.test(content);
                    if (looksLikeHTML) {
                        return content;
                    } else {
                        try {
                            if (typeof marked !== 'undefined') {
                                return marked.parse(content);
                            }
                        } catch (e) {
                            console.warn('Marked.js not available or parsing failed:', e);
                        }
                        return content;
                    }
                }
                
                // Helper function to display content with typewriter effect
                function displayWithTypewriter(content) {
                    if (contentDisplayed) return; // Prevent duplicate display
                    contentDisplayed = true;
                    
                    const uniqueId = 'typewriter-' + Date.now();
                    instance.messageAddNew(`<div id="${uniqueId}"></div>`, 'AI Analyst', 'left');
                    
                    setTimeout(() => {
                        const typewriterDiv = document.getElementById(uniqueId);
                        if (typewriterDiv) {
                            const contentLength = content.length;
                            let currentIndex = 0;
                            
                            let speed, interval;
                            if (contentLength < 500) {
                                speed = 15;
                                interval = 20;
                            } else if (contentLength < 2000) {
                                speed = 30;
                                interval = 15;
                            } else {
                                speed = 50;
                                interval = 10;
                            }
                            
                            console.log(`Typewriter: ${contentLength} chars, speed=${speed}, interval=${interval}ms`);
                            
                            const typewriterInterval = setInterval(() => {
                                if (currentIndex < contentLength) {
                                    currentIndex += speed;
                                    typewriterDiv.textContent = content.substring(0, Math.min(currentIndex, contentLength));
                                    
                                    // Auto-scroll to keep the message visible
                                    typewriterDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
                                } else {
                                    const renderedContent = renderContent(content);
                                    typewriterDiv.innerHTML = renderedContent;
                                    typewriterDiv.removeAttribute('id');
                                    clearInterval(typewriterInterval);
                                    
                                    // Final scroll to ensure full content is visible
                                    typewriterDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
                                    console.log('Content rendered');
                                }
                            }, interval);
                        }
                    }, 50);
                }
                
                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) {
                        clearInterval(timeoutChecker);
                        break;
                    }
                    
                    lastChunkTime = Date.now();
                    buffer += decoder.decode(value, { stream: true });
                    
                    // Process SSE messages
                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep incomplete line in buffer
                    
                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            try {
                                const data = JSON.parse(line.substring(6));
                                
                                if (data.type === 'status') {
                                    // Remove initial loading indicator on first status
                                    removeLoadingIndicator();
                                    
                                    // Show step status with animated icon
                                    showStepStatus(data.message, '⏳');
                                    console.log('Status:', data.message);
                                } else if (data.type === 'tool_call') {
                                    // Show tool call step
                                    const toolNames = data.tools.join(', ');
                                    showStepStatus(`正在调用: ${toolNames}`, '🔍');
                                    console.log('Calling tools:', data.tools);
                                } else if (data.type === 'content') {
                                    // Remove all status indicators when content starts
                                    removeLoadingIndicator();
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    console.log('All indicators removed, starting content');
                                    
                                    streamingContent += data.chunk;
                                    hasReceivedContent = true;
                                } else if (data.type === 'done') {
                                    console.log('Streaming complete, total length:', streamingContent.length);
                                    // Remove any remaining step indicators
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    if (streamingContent) {
                                        displayWithTypewriter(streamingContent);
                                    }
                                } else if (data.type === 'error' || data.error) {
                                    // Remove step indicators on error
                                    if (currentStepElement) {
                                        currentStepElement.remove();
                                        currentStepElement = null;
                                    }
                                    instance.messageAddNew('Error: ' + (data.message || data.error), 'System', 'left');
                                }
                            } catch (e) {
                                console.error('Failed to parse SSE data:', e, 'Line:', line);
                            }
                        }
                    }
                }

                // Fallback: if we received content but no 'done' signal, display it anyway
                if (hasReceivedContent && streamingContent && !contentDisplayed) {
                    console.warn('Stream ended without done signal, displaying partial content');
                    displayWithTypewriter(streamingContent);
                } else if (!streamingContent && !contentDisplayed) {
                    instance.messageAddNew('No response received.', 'System', 'left');
                }

            } catch (err) {
                console.error('Chat error:', err);
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

        // Initialize resize functionality
        const resizeHandle = document.getElementById('resize-handle');
        const chatSidebar = document.getElementById('chat-sidebar');
        let isResizing = false;
        let startX = 0;
        let startWidth = 0;

        resizeHandle.addEventListener('mousedown', function(e) {
            isResizing = true;
            startX = e.clientX;
            startWidth = chatSidebar.offsetWidth;
            resizeHandle.classList.add('resizing');
            document.body.style.cursor = 'ew-resize';
            document.body.style.userSelect = 'none';
            e.preventDefault();
        });

        document.addEventListener('mousemove', function(e) {
            if (!isResizing) return;
            
            const dx = startX - e.clientX; // Reversed because we're dragging from the left
            const newWidth = startWidth + dx;
            
            // Constrain width between min and max
            const minWidth = 300;
            const maxWidth = 800;
            const constrainedWidth = Math.min(Math.max(newWidth, minWidth), maxWidth);
            
            chatSidebar.style.width = constrainedWidth + 'px';
        });

        document.addEventListener('mouseup', function() {
            if (isResizing) {
                isResizing = false;
                resizeHandle.classList.remove('resizing');
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        });
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

    function openTab(evt, tabId) {
        // Hide all tab contents
        const allContents = document.querySelectorAll('.tab-content');
        allContents.forEach(content => {
            content.classList.remove('active');
        });

        // Remove active class from all tab buttons
        const allButtons = document.querySelectorAll('.tab-button');
        allButtons.forEach(button => {
            button.classList.remove('active');
        });

        // Show the clicked tab's content and add active class to the button
        document.getElementById(tabId).classList.add('active');
        evt.currentTarget.classList.add('active');
    }
    </script>
    """
