// Polyfill process for React libraries
    window.process = {
        env: {
            NODE_ENV: 'production'
        }
    };

    document.addEventListener('DOMContentLoaded', function() {
        // Initialize Auto Colorize
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
        if (val === 'N/A' || val === '--' || val === '---' || val === '') {
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

    // Fund Operations Functions
    // 板块分类数据
    const SECTOR_CATEGORIES = {
        "科技": ["人工智能", "半导体", "云计算", "5G", "光模块", "CPO", "F5G", "通信设备", "PCB", "消费电子",
                "计算机", "软件开发", "信创", "网络安全", "IT服务", "国产软件", "计算机设备", "光通信",
                "算力", "脑机接口", "通信", "电子", "光学光电子", "元件", "存储芯片", "第三代半导体",
                "光刻胶", "电子化学品", "LED", "毫米波", "智能穿戴", "东数西算", "数据要素", "国资云",
                "Web3.0", "AIGC", "AI应用", "AI手机", "AI眼镜", "DeepSeek", "TMT", "科技"],
        "医药健康": ["医药生物", "医疗器械", "生物疫苗", "CRO", "创新药", "精准医疗", "医疗服务", "中药",
                    "化学制药", "生物制品", "基因测序", "超级真菌"],
        "消费": ["食品饮料", "白酒", "家用电器", "纺织服饰", "商贸零售", "新零售", "家居用品", "文娱用品",
                "婴童", "养老产业", "体育", "教育", "在线教育", "社会服务", "轻工制造", "新消费",
                "可选消费", "消费", "家电零部件", "智能家居"],
        "金融": ["银行", "证券", "保险", "非银金融", "国有大型银行", "股份制银行", "城商行", "金融"],
        "能源": ["新能源", "煤炭", "石油石化", "电力", "绿色电力", "氢能源", "储能", "锂电池", "电池",
                "光伏设备", "风电设备", "充电桩", "固态电池", "能源", "煤炭开采", "公用事业", "锂矿"],
        "工业制造": ["机械设备", "汽车", "新能源车", "工程机械", "高端装备", "电力设备", "专用设备",
                    "通用设备", "自动化设备", "机器人", "人形机器人", "汽车零部件", "汽车服务",
                    "汽车热管理", "尾气治理", "特斯拉", "无人驾驶", "智能驾驶", "电网设备", "电机",
                    "高端制造", "工业4.0", "工业互联", "低空经济", "通用航空"],
        "材料": ["有色金属", "黄金股", "贵金属", "基础化工", "钢铁", "建筑材料", "稀土永磁", "小金属",
                "工业金属", "材料", "大宗商品", "资源"],
        "军工": ["国防军工", "航天装备", "航空装备", "航海装备", "军工电子", "军民融合", "商业航天",
                "卫星互联网", "航母", "航空机场"],
        "基建地产": ["建筑装饰", "房地产", "房地产开发", "房地产服务", "交通运输", "物流"],
        "环保": ["环保", "环保设备", "环境治理", "垃圾分类", "碳中和", "可控核聚变", "液冷"],
        "传媒": ["传媒", "游戏", "影视", "元宇宙", "超清视频", "数字孪生"],
        "主题": ["国企改革", "一带一路", "中特估", "中字头", "并购重组", "华为", "新兴产业",
                "国家安防", "安全主题", "农牧主题", "农林牧渔", "养殖业", "猪肉", "高端装备"]
    };

    // 基金选择模态框相关变量
    let currentOperation = null;
    let selectedFundsForOperation = [];
    let allFunds = [];
    let currentFilteredFunds = []; // 当前过滤后的基金列表

    // 打开基金选择模态框
    async function openFundSelectionModal(operation) {
        currentOperation = operation;
        selectedFundsForOperation = [];

        // 设置标题
        const titles = {
            'hold': '选择要标记持有的基金',
            'unhold': '选择要取消持有的基金',
            'sector': '选择要标注板块的基金',
            'unsector': '选择要删除板块的基金',
            'delete': '选择要删除的基金'
        };
        document.getElementById('fundSelectionTitle').textContent = titles[operation] || '选择基金';

        // 获取所有基金列表
        try {
            const response = await fetch('/api/fund/data');
            const fundMap = await response.json();
            allFunds = Object.entries(fundMap).map(([code, data]) => ({
                code,
                name: data.fund_name,
                is_hold: data.is_hold,
                sectors: data.sectors || []
            }));

            // 根据操作类型过滤基金列表
            let filteredFunds = allFunds;
            switch (operation) {
                case 'hold':
                    // 标记持有：只显示未持有的基金
                    filteredFunds = allFunds.filter(fund => !fund.is_hold);
                    break;
                case 'unhold':
                    // 取消持有：只显示已持有的基金
                    filteredFunds = allFunds.filter(fund => fund.is_hold);
                    break;
                case 'unsector':
                    // 删除板块：只显示有板块标记的基金
                    filteredFunds = allFunds.filter(fund => fund.sectors && fund.sectors.length > 0);
                    break;
                case 'sector':
                case 'delete':
                default:
                    // 标注板块、删除基金：显示所有基金
                    filteredFunds = allFunds;
                    break;
            }

            // 保存当前过滤后的列表，供搜索使用
            currentFilteredFunds = filteredFunds;

            // 渲染基金列表
            renderFundSelectionList(filteredFunds);

            // 显示模态框
            document.getElementById('fundSelectionModal').classList.add('active');
        } catch (e) {
            alert('获取基金列表失败: ' + e.message);
        }
    }

    // 渲染基金选择列表
    function renderFundSelectionList(funds) {
        const listContainer = document.getElementById('fundSelectionList');
        listContainer.innerHTML = funds.map(fund => `
            <div class="sector-item" style="text-align: left; padding: 12px; margin-bottom: 8px; cursor: pointer; display: flex; align-items: center; gap: 10px;"
                 onclick="toggleFundSelection('${fund.code}', this)">
                <input type="checkbox" class="fund-selection-checkbox" data-code="${fund.code}"
                       style="width: 18px; height: 18px; cursor: pointer;" onclick="event.stopPropagation();">
                <div style="flex: 1;">
                    <div style="font-weight: 600;">${fund.code} - ${fund.name}</div>
                    ${fund.is_hold ? '<span style="color: #667eea; font-size: 12px;">⭐ 持有</span>' : ''}
                    ${fund.sectors && fund.sectors.length > 0 ? `<span style="color: #8b949e; font-size: 12px;"> 🏷️ ${fund.sectors.join(', ')}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    // 切换基金选择状态
    function toggleFundSelection(code, element) {
        const checkbox = element.querySelector('.fund-selection-checkbox');
        checkbox.checked = !checkbox.checked;

        if (checkbox.checked) {
            if (!selectedFundsForOperation.includes(code)) {
                selectedFundsForOperation.push(code);
            }
            element.style.backgroundColor = 'rgba(102, 126, 234, 0.2)';
        } else {
            selectedFundsForOperation = selectedFundsForOperation.filter(c => c !== code);
            element.style.backgroundColor = '';
        }
    }

    // 关闭基金选择模态框
    function closeFundSelectionModal() {
        document.getElementById('fundSelectionModal').classList.remove('active');
        currentOperation = null;
        selectedFundsForOperation = [];
    }

    // 确认基金选择
    async function confirmFundSelection() {
        if (selectedFundsForOperation.length === 0) {
            alert('请至少选择一个基金');
            return;
        }

        // 根据操作类型执行相应的操作
        switch (currentOperation) {
            case 'hold':
                await markHold(selectedFundsForOperation);
                break;
            case 'unhold':
                await unmarkHold(selectedFundsForOperation);
                break;
            case 'sector':
                closeFundSelectionModal();
                openSectorModal(selectedFundsForOperation);
                return; // 不关闭，等待板块选择
            case 'unsector':
                await removeSector(selectedFundsForOperation);
                break;
            case 'delete':
                await deleteFunds(selectedFundsForOperation);
                break;
        }

        closeFundSelectionModal();
    }

    // 基金选择搜索
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('fundSelectionSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const keyword = this.value.toLowerCase();
                // 在当前过滤后的列表中搜索，而不是在所有基金中搜索
                const filtered = currentFilteredFunds.filter(fund =>
                    fund.code.includes(keyword) || fund.name.toLowerCase().includes(keyword)
                );
                renderFundSelectionList(filtered);
            });
        }
    });

    // 确认对话框相关函数
    let confirmCallback = null;

    function showConfirmDialog(title, message, onConfirm) {
        document.getElementById('confirmTitle').textContent = title;
        document.getElementById('confirmMessage').textContent = message;
        document.getElementById('confirmDialog').classList.add('active');
        confirmCallback = onConfirm;
    }

    function closeConfirmDialog() {
        document.getElementById('confirmDialog').classList.remove('active');
        confirmCallback = null;
    }

    document.getElementById('confirmBtn').addEventListener('click', function() {
        if (confirmCallback) {
            confirmCallback();
        }
        closeConfirmDialog();
    });

    // 添加基金
    async function addFunds() {
        const input = document.getElementById('fundCodesInput');
        const codes = input.value.trim();
        if (!codes) {
            alert('请输入基金代码');
            return;
        }

        try {
            const response = await fetch('/api/fund/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codes })
            });
            const result = await response.json();
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert(result.message);
            }
        } catch (e) {
            alert('操作失败: ' + e.message);
        }
    }

    // 删除基金
    async function deleteFunds(codes) {
        showConfirmDialog(
            '删除基金',
            `确定要删除 ${codes.length} 只基金吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/delete', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(',') })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 标记持有
    async function markHold(codes) {
        showConfirmDialog(
            '标记持有',
            `确定要标记 ${codes.length} 只基金为持有吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/hold', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(','), hold: true })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 取消持有
    async function unmarkHold(codes) {
        showConfirmDialog(
            '取消持有',
            `确定要取消 ${codes.length} 只基金的持有标记吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/hold', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(','), hold: false })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 打开板块选择模态框（用于标注板块）
    let selectedCodesForSector = [];

    function openSectorModal(codes) {
        selectedCodesForSector = codes;
        document.getElementById('sectorModal').classList.add('active');
        renderSectorCategories();
    }

    // 删除板块标记
    async function removeSector(codes) {
        showConfirmDialog(
            '删除板块标记',
            `确定要删除 ${codes.length} 只基金的板块标记吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/sector/remove', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(',') })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 取消持有
    async function unmarkHold() {
        const codes = selectedFundsForOperation;
        if (codes.length === 0) {
            alert('请先选择要取消持有的基金');
            return;
        }

        showConfirmDialog(
            '取消持有',
            `确定要取消 ${codes.length} 只基金的持有标记吗？`,
            async () => {
                try {
                    const response = await fetch('/api/fund/hold', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ codes: codes.join(','), hold: false })
                    });
                    const result = await response.json();
                    if (result.success) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.message);
                    }
                } catch (e) {
                    alert('操作失败: ' + e.message);
                }
            }
        );
    }

    // 板块选择相关
    let selectedSectors = [];

    function renderSectorCategories() {
        // 生成板块分类HTML
        const container = document.getElementById('sectorCategories');
        container.innerHTML = '';

        for (const [category, sectors] of Object.entries(SECTOR_CATEGORIES)) {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'sector-category';

            const header = document.createElement('div');
            header.className = 'sector-category-header';
            header.innerHTML = `<span>${category}</span><span>▼</span>`;
            header.onclick = () => {
                const items = categoryDiv.querySelector('.sector-items');
                items.style.display = items.style.display === 'none' ? 'grid' : 'none';
            };

            const itemsDiv = document.createElement('div');
            itemsDiv.className = 'sector-items';

            sectors.forEach(sector => {
                const item = document.createElement('div');
                item.className = 'sector-item';
                item.textContent = sector;
                item.onclick = () => {
                    item.classList.toggle('selected');
                    if (item.classList.contains('selected')) {
                        if (!selectedSectors.includes(sector)) {
                            selectedSectors.push(sector);
                        }
                    } else {
                        selectedSectors = selectedSectors.filter(s => s !== sector);
                    }
                };
                itemsDiv.appendChild(item);
            });

            categoryDiv.appendChild(header);
            categoryDiv.appendChild(itemsDiv);
            container.appendChild(categoryDiv);
        }

        selectedSectors = [];
        document.getElementById('sectorModal').classList.add('active');
    }

    function closeSectorModal() {
        document.getElementById('sectorModal').classList.remove('active');
        selectedSectors = [];
    }

    async function confirmSector() {
        if (selectedSectors.length === 0) {
            alert('请至少选择一个板块');
            return;
        }

        try {
            const response = await fetch('/api/fund/sector', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ codes: selectedCodesForSector.join(','), sectors: selectedSectors })
            });
            const result = await response.json();
            closeSectorModal();
            if (result.success) {
                alert(result.message);
                location.reload();
            } else {
                alert(result.message);
            }
        } catch (e) {
            closeSectorModal();
            alert('操作失败: ' + e.message);
        }
    }

    // 板块搜索功能
    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('sectorSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const keyword = this.value.toLowerCase();
                const categories = document.querySelectorAll('.sector-category');

                categories.forEach(category => {
                    const items = category.querySelectorAll('.sector-item');
                    let hasVisible = false;

                    items.forEach(item => {
                        const text = item.textContent.toLowerCase();
                        if (text.includes(keyword)) {
                            item.style.display = 'block';
                            hasVisible = true;
                        } else {
                            item.style.display = 'none';
                        }
                    });

                    category.style.display = hasVisible || keyword === '' ? 'block' : 'none';
                });
            });
        }

        // ==================== 新增功能：份额管理和文件操作 ====================

        // 更新基金份额
        window.updateShares = async function(fundCode, shares) {
            if (!fundCode) {
                alert('基金代码无效');
                return;
            }

            try {
                const sharesValue = parseFloat(shares) || 0;
                const response = await fetch('/api/fund/shares', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: fundCode, shares: sharesValue })
                });
                const result = await response.json();
                if (result.success) {
                    // 更新成功后重新计算持仓统计
                    calculatePositionSummary();
                    // 可选：显示成功提示
                    const input = document.getElementById('shares_' + fundCode);
                    if (input) {
                        input.style.borderColor = '#4CAF50';
                        setTimeout(() => {
                            input.style.borderColor = '#ddd';
                        }, 1000);
                    }
                } else {
                    alert(result.message);
                }
            } catch (e) {
                alert('更新份额失败: ' + e.message);
            }
        };

        // 下载fund_map.json
        window.downloadFundMap = function() {
            window.location.href = '/api/fund/download';
        };

        // 上传fund_map.json
        window.uploadFundMap = async function(file) {
            if (!file) {
                alert('请选择文件');
                return;
            }

            if (!file.name.endsWith('.json')) {
                alert('只支持JSON文件');
                return;
            }

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/fund/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                if (result.success) {
                    alert(result.message);
                    location.reload();
                } else {
                    alert(result.message);
                }
            } catch (e) {
                alert('上传失败: ' + e.message);
            }
        };

        // 计算并显示持仓统计
        function calculatePositionSummary() {
            let totalValue = 0;
            let estimatedGain = 0;
            let actualGain = 0;
            let settledValue = 0;
            const today = new Date().toISOString().split('T')[0];

            // 判断是否是9:30之前或今日净值未更新
            const now = new Date();
            const currentHour = now.getHours();
            const currentMinute = now.getMinutes();
            const beforeMarketOpen = currentHour < 9 || (currentHour === 9 && currentMinute < 30);

            // 遍历所有基金行
            const fundRows = document.querySelectorAll('.style-table tbody tr');
            fundRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length < 9) return;

                // 获取基金代码
                const codeCell = cells[1]; // 第二列是基金代码（第一列是复选框）
                const fundCode = codeCell.textContent.trim();

                // 从全局数据获取份额
                const shares = (window.fundSharesData && window.fundSharesData[fundCode]) || 0;
                if (shares <= 0) return;

                try {
                    // 解析净值 "1.234(2025-02-02)"
                    const netValueText = cells[4].textContent.trim();
                    const netValueMatch = netValueText.match(/([0-9.]+)\(([0-9-]+)\)/);
                    if (!netValueMatch) return;

                    const netValue = parseFloat(netValueMatch[1]);
                    const netValueDate = netValueMatch[2];

                    // 解析估值增长率
                    const estimatedGrowthText = cells[5].textContent.trim();
                    const estimatedGrowth = estimatedGrowthText !== 'N/A' ?
                        parseFloat(estimatedGrowthText.replace('%', '')) : 0;

                    // 解析日涨幅
                    const dayGrowthText = cells[6].textContent.trim();
                    const dayGrowth = dayGrowthText !== 'N/A' ?
                        parseFloat(dayGrowthText.replace('%', '')) : 0;

                    // 计算持仓市值
                    const positionValue = shares * netValue;
                    totalValue += positionValue;
                    settledValue += positionValue;

                    // 计算预估涨跌（始终计算）
                    estimatedGain += positionValue * estimatedGrowth / 100;

                    // 计算实际涨跌
                    // 逻辑：9:30之前 或 今日净值未更新 → 用日涨幅（前一日的）计算
                    //      9:30之后且今日净值已更新 → 用今日日涨幅计算
                    if (beforeMarketOpen || netValueDate !== today) {
                        // 使用日涨幅（前一日）计算实际收益
                        actualGain += positionValue * dayGrowth / 100;
                    } else {
                        // 今日9:30后且净值已更新，使用今日日涨幅
                        actualGain += positionValue * dayGrowth / 100;
                    }
                } catch (e) {
                    console.warn('解析基金数据失败:', fundCode, e);
                }
            });

            // 显示或隐藏持仓统计区域 (旧版布局)
            const summaryDiv = document.getElementById('positionSummary');
            if (summaryDiv && totalValue > 0) {
                summaryDiv.style.display = 'block';
            } else if (summaryDiv) {
                summaryDiv.style.display = 'none';
            }

            // 更新持仓基金页面的汇总数据 (始终执行)
            // 更新总持仓金额
            const totalValueEl = document.getElementById('totalValue');
            if (totalValueEl) {
                totalValueEl.textContent = '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            }

            // 更新今日预估
            const estimatedGainEl = document.getElementById('estimatedGain');
            if (estimatedGainEl) {
                const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
                const estSign = estimatedGain >= 0 ? '+' : '';
                const estColor = estimatedGain >= 0 ? '#f44336' : '#4caf50';
                estimatedGainEl.innerHTML = `<span style="color: ${estColor}">${estSign}¥${Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${estSign}${estGainPct.toFixed(2)}%)</span>`;
            }

            // 更新今日实际（始终显示）
            const actualGainEl = document.getElementById('actualGain');
            if (actualGainEl) {
                const actGainPct = totalValue > 0 ? (actualGain / totalValue * 100) : 0;
                const actSign = actualGain >= 0 ? '+' : '';
                const actColor = actualGain >= 0 ? '#f44336' : '#4caf50';
                actualGainEl.innerHTML = `<span style="color: ${actColor}">${actSign}¥${Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${actSign}${actGainPct.toFixed(2)}%)</span>`;
            }

            // 更新持仓数量
            const holdCountEl = document.getElementById('holdCount');
            if (holdCountEl) {
                // 从全局数据计算持仓数量
                let heldCount = 0;
                if (window.fundSharesData) {
                    for (const code in window.fundSharesData) {
                        if (window.fundSharesData[code] > 0) {
                            heldCount++;
                        }
                    }
                }
                holdCountEl.textContent = heldCount + ' 只';
            }

            // Update old positionSummary if exists
            if (summaryDiv && totalValue > 0) {
                // 更新总持仓金额
                summaryDiv.querySelector('#totalValue').textContent =
                    '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});

                // 更新预估涨跌
                const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
                const estSign = estimatedGain >= 0 ? '+' : '';
                const estColor = estimatedGain >= 0 ? '#ef4444' : '#10b981';
                summaryDiv.querySelector('#estimatedGain').innerHTML =
                    `<span style="color: ${estColor}">${estSign}¥${Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${estSign}${estGainPct.toFixed(2)}%)</span>`;

                // 更新实际涨跌（始终显示）
                const actGainPct = totalValue > 0 ? (actualGain / totalValue * 100) : 0;
                const actSign = actualGain >= 0 ? '+' : '';
                const actColor = actualGain >= 0 ? '#ef4444' : '#10b981';
                summaryDiv.querySelector('#actualGain').innerHTML =
                    `<span style="color: ${actColor}">${actSign}¥${Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${actSign}${actGainPct.toFixed(2)}%)</span>`;
            }

            // Update new summary bar if it exists (sidebar layout)
            const summaryBar = document.getElementById('summaryBar');
            if (summaryBar) {
                // Count held funds from global data
                let heldCount = 0;
                if (window.fundSharesData) {
                    for (const code in window.fundSharesData) {
                        if (window.fundSharesData[code] > 0) {
                            heldCount++;
                        }
                    }
                }

                // Update total value
                const summaryTotalValue = document.getElementById('summaryTotalValue');
                if (summaryTotalValue) {
                    summaryTotalValue.textContent = '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                }

                // Update total change
                const summaryTotalChange = document.getElementById('summaryTotalChange');
                if (summaryTotalChange) {
                    const totalPct = totalValue > 0 ? ((estimatedGain + actualGain) / totalValue * 100) : 0;
                    const totalSign = (estimatedGain + actualGain) >= 0 ? '+' : '';
                    summaryTotalChange.textContent = `${totalSign}${totalPct.toFixed(2)}%`;
                    summaryTotalChange.className = 'summary-change ' + ((estimatedGain + actualGain) >= 0 ? 'positive' : 'negative');
                }

                // Update estimated gain
                const summaryEstGain = document.getElementById('summaryEstGain');
                if (summaryEstGain) {
                    const estSign = estimatedGain >= 0 ? '+' : '';
                    summaryEstGain.textContent = `${estSign}¥${Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                }

                // Update estimated change
                const summaryEstChange = document.getElementById('summaryEstChange');
                if (summaryEstChange) {
                    const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
                    const estSign = estimatedGain >= 0 ? '+' : '';
                    summaryEstChange.textContent = `${estSign}${estGainPct.toFixed(2)}%`;
                    summaryEstChange.className = 'summary-change ' + (estimatedGain >= 0 ? 'positive' : 'negative');
                }

                // Update actual gain
                const summaryActualGain = document.getElementById('summaryActualGain');
                if (summaryActualGain) {
                    const actSign = actualGain >= 0 ? '+' : '';
                    summaryActualGain.textContent = `${actSign}¥${Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                }

                // Update actual change
                const summaryActualChange = document.getElementById('summaryActualChange');
                if (summaryActualChange) {
                    if (settledValue > 0) {
                        const actGainPct = (actualGain / settledValue * 100);
                        const actSign = actualGain >= 0 ? '+' : '';
                        summaryActualChange.textContent = `${actSign}${actGainPct.toFixed(2)}%`;
                        summaryActualChange.className = 'summary-change ' + (actualGain >= 0 ? 'positive' : 'negative');
                    } else {
                        summaryActualChange.textContent = '0.00%';
                        summaryActualChange.className = 'summary-change neutral';
                    }
                }

                // Update hold count
                const summaryHoldCount = document.getElementById('summaryHoldCount');
                if (summaryHoldCount) {
                    summaryHoldCount.textContent = `${heldCount} 只`;
                }
            }
        }

        // 页面加载时加载份额数据并计算持仓统计
        async function loadSharesData() {
            try {
                // 从后端API获取用户的基金数据（包含份额）
                const response = await fetch('/api/fund/data');
                if (response.ok) {
                    const fundData = await response.json();

                    // 填充份额输入框
                    for (const [code, data] of Object.entries(fundData)) {
                        const sharesInput = document.getElementById('shares_' + code);
                        if (sharesInput && data.shares) {
                            sharesInput.value = data.shares;
                        }
                    }

                    // 计算持仓统计
                    calculatePositionSummary();
                }
            } catch (e) {
                console.error('加载份额数据失败:', e);
                // 即使加载失败，也尝试计算持仓统计
                calculatePositionSummary();
            }
        }

        // 初始化
        loadSharesData();

        // 展开/收起基金行详情
        window.toggleFundExpand = function(fundCode) {
            const fundRow = document.querySelector(`.fund-row[data-code="${fundCode}"]`);
            if (fundRow) {
                fundRow.classList.toggle('expanded');
            }
        };

        // 全局暴露其他必要的函数
        window.openFundSelectionModal = openFundSelectionModal;
        window.closeFundSelectionModal = closeFundSelectionModal;
        window.confirmFundSelection = confirmFundSelection;
        window.downloadFundMap = downloadFundMap;
        window.uploadFundMap = uploadFundMap;
        window.addFunds = addFunds;
        window.markHold = markHold;
        window.unmarkHold = unmarkHold;
        window.deleteFunds = deleteFunds;
        window.openSectorModal = openSectorModal;
        window.closeSectorModal = closeSectorModal;
        window.confirmSector = confirmSector;
        window.removeSector = removeSector;
    });
