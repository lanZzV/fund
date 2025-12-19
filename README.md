# 基金市场监控工具

一个功能强大的金融市场实时监控工具，支持命令行和Web两种模式，可追踪基金估值、市场指数、黄金价格、行业板块和市场快讯。

## 功能特性

### 📊 数据监控
- **基金实时估值**：实时更新基金估值、日涨幅、近30天涨跌趋势
- **市场指数**：上证指数、深证指数、创业板指、纳斯达克、道琼斯等
- **黄金价格**：中国黄金基础金价、周大福金价及历史数据
- **行业板块**：各行业板块涨跌幅、主力资金流入情况
- **7×24快讯**：实时金融市场新闻和影响股票分析

### 💡 智能分析
- **连涨/连跌分析**：自动计算基金连续涨跌天数和幅度
- **30天趋势**：展示近30天涨跌分布，一目了然
- **持仓标记**：支持标记持有基金（⭐显示），快速关注重点
- **彩色显示**：终端下红涨绿跌，直观易读
- **🤖 AI深度分析**：集成LangChain提示链，生成1200+字专业分析报告（可选功能）

### 🚀 双模式运行
- **命令行模式**：快速查看，适合终端用户
- **Web界面模式**：可视化展示，支持表格排序，适合浏览器访问

## 安装

### 依赖安装

```bash
pip install -r requirements.txt
```

### 依赖包说明
- `loguru` - 日志输出
- `requests` - HTTP请求
- `tabulate` - 表格格式化
- `flask` - Web服务器（仅Web模式需要）
- `langchain` - AI提示链框架（AI分析功能）
- `langchain-openai` - OpenAI兼容API支持
- `langchain-core` - LangChain核心组件

## 使用方法

### 命令行模式

#### 查看所有信息
```bash
python fund.py
```
或使用编译好的可执行文件：
```bash
./dist/fund.exe  # Windows
```

显示内容包括：
- 7×24快讯
- 行业板块排行
- 实时金价
- 黄金历史价格
- 近7日A股成交量
- 近30分钟上证指数
- 市场指数汇总
- 自选基金估值

#### 管理自选基金

**添加基金**
```bash
python fund.py -a
# 根据提示输入基金代码，多个代码用英文逗号分隔
# 例如：001618,161725,110011
```

**删除基金**
```bash
python fund.py -d
# 根据提示输入要删除的基金代码
```

**标记持有基金**
```bash
python fund.py -c
# 标记后的基金会在名称前显示 ⭐
```

**取消持有标记**
```bash
python fund.py -b
# 移除基金的持有标记
```

### Web服务器模式

#### 启动服务
```bash
python fund_server.py
```

服务默认运行在：`http://0.0.0.0:8311`

#### 访问地址
浏览器访问：`http://localhost:8311/fund`

#### Web API

**添加基金（通过URL）**
```
http://localhost:8311/fund?add=001618,161725
```

**删除基金（通过URL）**
```
http://localhost:8311/fund?delete=001618
```

#### Web功能特性
- 📊 所有数据表格化展示
- 🔄 支持点击表头排序（升序/降序）
- 🎨 现代化UI设计（白底蓝色主题）
- 📱 响应式布局
- ⚡ 多线程并发获取数据，加载快速

## 🤖 AI智能分析（可选）

程序集成了最新版本的**LangChain (0.3.27+)**，使用**提示链（Prompt Chain）模式**生成深度AI分析报告。

### 🆕 AI分析特色

- **🔗 LangChain提示链** - 四个维度的分析使用独立的提示链，每个链都有专业的系统角色
- **📝 深度报告** - 每个维度输出300-400字的专业分析，总计1200-1600字
- **👨‍💼 专业角色** - 资深金融分析师、行业研究专家、基金投资顾问、风险管理专家
- **🎯 分角度分析** - 每个维度4-5个子角度深入剖析，逻辑清晰
- **💼 可操作性强** - 给出具体的配置建议和应对策略
- **⚡ LCEL语法** - 使用LangChain Expression Language，代码简洁优雅

### 四个独立提示链

程序使用4个独立的提示链（Prompt Chain），每个链都有专业的系统角色和详细的分析要求：

#### 1️⃣ 市场趋势分析链 (`trend_chain`)
- **系统角色**：资深金融分析师
- **输出长度**：300-400字
- **分析角度**：
  - 主要指数走势特征和相互关系
  - 市场所处阶段判断（上涨/震荡/调整）
  - 市场情绪和资金流向特征
  - 国内外市场对比及影响因素

#### 2️⃣ 板块机会分析链 (`sector_chain`)
- **系统角色**：行业研究专家
- **输出长度**：300-400字
- **分析角度**：
  - 领涨板块共同特征和驱动因素
  - 行情可持续性判断
  - 结合资金流入的板块强度评估
  - 重点关注板块和配置建议
  - 弱势板块反转机会分析

#### 3️⃣ 基金组合建议链 (`portfolio_chain`)
- **系统角色**：基金投资顾问
- **输出长度**：300-400字
- **分析角度**：
  - 持仓基金表现和风险特征评估
  - 持仓与市场环境匹配度分析
  - 具体调仓建议（增持/减持/持有）
  - 优异基金背后原因及可持续性
  - 仓位配置和风险敞口优化方向

#### 4️⃣ 风险提示分析链 (`risk_chain`)
- **系统角色**：风险管理专家
- **输出长度**：250-350字
- **分析角度**：
  - 当前市场主要风险点识别
  - 可能引发调整的触发因素
  - 持仓基金风险暴露评估
  - 风险防控建议和应对策略
  - 需要关注的风险信号

### 技术实现

使用LangChain的LCEL（LangChain Expression Language）语法：
```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 创建提示链
chain = prompt_template | llm | output_parser

# 执行分析
result = chain.invoke(input_variables)
```

每个分析维度都是独立执行的，互不干扰，便于调整和优化。

### 三种使用方式

#### 方式1：使用.env文件（推荐）

创建 `.env` 文件：
```bash
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.moonshot.cn/v1
LLM_MODEL=moonshot-v1-8k
```

或者使用DeepSeek：
```bash
LLM_API_KEY=your-api-key
LLM_API_BASE=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
```

运行：
```bash
./run.sh  # 自动加载配置并启动
```

#### 方式2：临时配置

```bash
export LLM_API_KEY="your-api-key"
export LLM_API_BASE="https://api.deepseek.com/v1"
export LLM_MODEL="deepseek-chat"

python3 fund.py
```

#### 方式3：永久配置

在 `~/.bashrc` 或 `~/.zshrc` 添加：
```bash
export LLM_API_KEY="your-api-key"
export LLM_API_BASE="https://api.deepseek.com/v1"
export LLM_MODEL="deepseek-chat"
```

然后 `source ~/.bashrc` 生效。

### 支持的AI服务

| 服务商 | API Base | 推荐模型 | 特点 |
|--------|----------|---------|------|
| Moonshot (Kimi) | `https://api.moonshot.cn/v1` | `moonshot-v1-8k`<br/>`kimi-k2-turbo-preview` | 响应快，质量高 ⭐ |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | 性价比高 |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo` | 阿里云 |
| 智谱AI | `https://open.bigmodel.cn/api/paas/v4` | `glm-4` | 清华出品 |
| OpenAI | `https://api.openai.com/v1` | `gpt-3.5-turbo`<br/>`gpt-4` | 国际版 |

### 成本估算

使用LangChain提示链后，每次完整分析需要调用4次LLM API：

- **Token消耗**：
  - 输入token：约600-1000（市场数据 + 提示词）× 4次 = 2400-4000
  - 输出token：约400-500 × 4次 = 1600-2000
  - 总token：约4000-6000

- **成本参考**（以Moonshot Kimi为例）：
  - 单次完整分析：约 ¥0.01-0.02
  - 每天查看2次：月成本约 ¥0.6-1.2

- **DeepSeek**：单次约 ¥0.002-0.005，每月约 ¥0.1-0.3

> 相比之前的单次调用，token消耗增加约3-4倍，但分析质量提升5-10倍，性价比更高。

### 禁用AI分析

不配置 `LLM_API_KEY` 即可禁用，不影响其他功能。

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────┐
│           Presentation Layer             │
│  ┌──────────────┐      ┌──────────────┐ │
│  │  CLI Output  │      │  Web Server  │ │
│  │  (tabulate)  │      │   (Flask)    │ │
│  └──────────────┘      └──────────────┘ │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│            Business Layer                │
│          MaYiFund Class (fund.py)        │
│  ┌────────────────────────────────────┐ │
│  │ • Data Fetching (多线程)            │ │
│  │ • Trend Analysis (30天分析)        │ │
│  │ • Cache Management (基金缓存)      │ │
│  │ • Session Management (会话管理)    │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│             Data Sources                 │
│  ┌────────┐ ┌────────┐ ┌─────────────┐ │
│  │fund123 │ │ Baidu  │ │  Eastmoney  │ │
│  │  .cn   │ │Finance │ │ jijinhao.com│ │
│  └────────┘ └────────┘ └─────────────┘ │
└─────────────────────────────────────────┘
```

### 核心类：MaYiFund

**主要方法：**

| 方法 | 功能 |
|------|------|
| `init()` | 初始化会话，获取CSRF令牌 |
| `add_code(codes)` | 添加基金到自选列表 |
| `delete_code(codes)` | 从自选列表删除基金 |
| `search_code()` | 查询所有自选基金数据（多线程） |
| `search_one_code()` | 查询单个基金（线程执行） |
| `bk()` | 获取行业板块数据 |
| `gold()` | 获取黄金历史价格 |
| `real_time_gold()` | 获取实时金价 |
| `get_market_info()` | 获取市场指数 |
| `A()` | 获取上证指数分时数据 |
| `seven_A()` | 获取近7日成交量 |
| `kx()` | 获取7×24快讯 |
| `init_langchain_llm()` | 初始化LangChain ChatOpenAI实例 |
| `ai_analysis()` | AI智能分析（使用LangChain提示链） |

**HTML输出方法（用于Web模式）：**
- `fund_html()` - 基金数据表格
- `marker_html()` - 市场指数表格
- `gold_html()` - 金价表格
- `bk_html()` - 板块数据表格
- 等等...

### 多线程设计

**并发控制：**
- 使用 `Semaphore(5)` 限制同时最多5个线程查询基金数据
- Web模式下，各数据模块（市场、黄金、基金、板块等）并行获取

**优势：**
- 大幅提升数据获取速度
- 避免API请求过于频繁被限制

### 数据缓存

**缓存文件：** `cache/fund_map.json`

**结构：**
```json
{
  "001618": {
    "fund_key": "JJ_001618",
    "fund_name": "天弘中证电子ETF联接C",
    "is_hold": true
  },
  "161725": {
    "fund_key": "JJ_161725",
    "fund_name": "招商中证白酒指数分级",
    "is_hold": false
  }
}
```

**编码：** 使用 GBK 编码（中文字符支持）

## 数据源

### fund123.cn
- 基金搜索和基本信息
- 基金30天估值曲线
- 实时估值数据

**主要端点：**
- `/api/fund/searchFund` - 搜索基金
- `/matiaria?fundCode=XXX` - 基金日涨幅
- `/api/fund/queryFundQuotationCurves` - 30天趋势
- `/api/fund/queryFundEstimateIntraday` - 实时估值

### 百度股市通 (gushitong.baidu.com)
- 市场指数（上证、深证、创业板、美股等）
- 7×24快讯
- 近7日成交量统计

**主要端点：**
- `/api/getbanner` - 市场指数横幅
- `/vapi/v1/getquotation` - 具体指数数据
- `/selfselect/expressnews` - 快讯新闻
- `/sapi/v1/metrictrend` - 成交量趋势

### 其他数据源
- **api.jijinhao.com** - 中国黄金和周大福金价
- **push2.eastmoney.com** - 东方财富行业板块数据

## 项目结构

```
fund/
├── fund.py              # 核心业务逻辑（MaYiFund类）
├── fund_server.py       # Flask Web服务器
├── module_html.py       # HTML表格生成模块
├── requirements.txt     # Python依赖
├── README.md            # 项目文档（本文件）
├── CLAUDE.md            # 开发者文档
├── .env                 # 环境变量配置（需自行创建）
├── .env.example         # 环境变量配置示例
├── run.sh               # 启动脚本（自动加载.env）
├── test_ai.sh           # AI功能测试脚本
├── cache/              # 缓存目录
│   └── fund_map.json   # 自选基金缓存（GBK编码）
└── dist/               # 编译后的可执行文件
    └── fund.exe        # Windows可执行文件
```

## 数据展示说明

### 终端显示（CLI模式）

**颜色说明：**
- 🔴 红色：上涨/涨幅为正
- 🟢 绿色：下跌/跌幅为负

**基金数据列：**
1. **基金代码** - 6位数字代码
2. **基金名称** - 带⭐表示持有
3. **估值时间** - 最新估值的时间
4. **估值** - 当日实时估值涨跌幅
5. **日涨幅** - 前一交易日涨跌幅
6. **连涨天数** - 正数表示连涨，负数表示连跌
7. **连涨幅** - 连涨/连跌的累计幅度
8. **涨/总 (近30天)** - 近30天上涨天数/总天数
9. **总涨幅** - 近30天累计涨跌幅

### Web界面

**交互功能：**
- 点击表头可排序（再次点击切换升序/降序）
- 可排序的列会显示排序箭头指示器
- 表格使用现代化设计，白底蓝色边框

## 技术细节

### 会话管理

**双会话机制：**
```python
self.session          # fund123.cn（需要CSRF保护）
self.baidu_session    # 百度股市通（需要BDUSS cookie）
```

### CSRF保护
fund123.cn 需要从页面提取 CSRF token：
```python
res = self.session.get("https://www.fund123.cn/fund")
self._csrf = re.findall('"csrf":"(.*?)"', res.text)[0]
```

### SSL/TLS配置
为兼容国内金融API，使用了自定义密码套件：
```python
urllib3.util.ssl_.DEFAULT_CIPHERS = ":".join([
    "ECDHE+AESGCM",
    "ECDHE+CHACHA20",
    # ... 更多密码套件
])
```

### 30天趋势算法

1. 获取近一个月的估值数据点
2. 对比相邻数据点的涨跌
3. 从最近一天开始，计算连续涨/跌天数
4. 统计总涨天数和总跌天数
5. 计算累计涨跌幅

## 常见问题

### Q: 基金数据不更新？
A: 确保网络连接正常，部分API可能有访问限制。可以尝试重启程序。

### Q: 添加基金时提示失败？
A: 请确认基金代码正确（6位数字），某些基金可能不在fund123.cn数据库中。

### Q: Web服务访问不了？
A: 检查8311端口是否被占用，可以修改 `fund_server.py` 中的端口号。

### Q: 终端显示乱码？
A: 确保终端支持UTF-8编码和ANSI颜色代码。Windows用户推荐使用Windows Terminal。

### Q: 如何定时刷新数据？
A: 可以配合 cron（Linux）或任务计划程序（Windows）定期执行 `python fund.py`

### Q: 如何禁用AI分析？
A: 不配置 `LLM_API_KEY` 环境变量，或删除/重命名 `.env` 文件即可。程序会自动跳过AI分析。

### Q: AI分析调用失败怎么办？
A: 按顺序检查：
1. 确认 `.env` 文件配置正确或环境变量已设置
2. 验证API密钥是否有效
3. 检查网络连接是否正常
4. 查看程序输出的详细错误信息

### Q: 如何更换其他AI服务？
A: 修改 `.env` 文件中的 `LLM_API_BASE` 和 `LLM_MODEL`，参考上方"支持的AI服务"表格。

### Q: 使用.env文件还是环境变量？
A: 推荐使用 `.env` 文件配合 `./run.sh` 启动，更方便管理。临时测试可以用环境变量。

## 开发说明

### 添加新数据源

1. 在 `MaYiFund` 类中添加新方法
2. 实现数据获取逻辑
3. 添加对应的 `_html()` 方法用于Web展示
4. 在 `run()` 方法中调用（CLI模式）
5. 在 `fund_server.py` 的 tasks 字典中注册（Web模式）

### 修改表格样式

编辑 `module_html.py` 中的：
- `get_css_style()` - 修改CSS样式
- `get_javascript_code()` - 修改排序逻辑

## 许可证

本项目仅供学习交流使用。数据来源于公开API，请遵守相关网站的使用条款。

## 免责声明

本工具仅提供数据展示功能，不构成任何投资建议。投资有风险，入市需谨慎。
