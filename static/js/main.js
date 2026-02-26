// Polyfill process for React libraries
    window.process = {
        env: {
            NODE_ENV: 'production'
        }
    };

    document.addEventListener('DOMContentLoaded', function() {
        autoColorize();

        const sidebar = document.getElementById('sidebar');
        const sidebarToggle = document.getElementById('sidebarToggle');

        if (sidebar && sidebarToggle && sidebar.id === 'sidebar') {
            sidebarToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                sidebar.classList.toggle('collapsed');
                const isCollapsed = sidebar.classList.contains('collapsed');
                sidebarToggle.textContent = isCollapsed ? '▶' : '◀';
                sidebarToggle.title = isCollapsed ? '展开' : '折叠';
            });
        }

        const hamburger = document.getElementById('hamburgerMenu');
        const mobileSidebar = document.getElementById('sidebar');
        let sidebarOverlay = document.getElementById('sidebarOverlay');

        if (hamburger && mobileSidebar) {
            if (!sidebarOverlay) {
                sidebarOverlay = document.createElement('div');
                sidebarOverlay.id = 'sidebarOverlay';
                sidebarOverlay.className = 'sidebar-overlay';
                document.body.appendChild(sidebarOverlay);
            }

            hamburger.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                const isActive = mobileSidebar.classList.contains('mobile-active');
                if (isActive) {
                    closeMobileSidebar();
                } else {
                    openMobileSidebar();
                }
            });

            sidebarOverlay.addEventListener('click', closeMobileSidebar);

            window.addEventListener('resize', function() {
                if (window.innerWidth > 768) {
                    closeMobileSidebar();
                }
            });

            const sidebarLinks = mobileSidebar.querySelectorAll('.sidebar-item');
            sidebarLinks.forEach(link => {
                link.addEventListener('click', closeMobileSidebar);
            });

            function openMobileSidebar() {
                mobileSidebar.classList.add('mobile-active');
                hamburger.classList.add('active');
                sidebarOverlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            }

            function closeMobileSidebar() {
                mobileSidebar.classList.remove('mobile-active');
                hamburger.classList.remove('active');
                sidebarOverlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        }
    });

    function autoColorize() {
        requestAnimationFrame(() => {
            const cells = document.querySelectorAll('.style-table td');
            cells.forEach(cell => {
                cell.classList.remove('positive', 'negative');

                const text = cell.textContent.trim();

                if (!text || text === '-' || text === 'N/A' || text === '---') {
                    return;
                }

                if (text === '利好') {
                    cell.classList.add('positive');
                    return;
                } else if (text === '利空') {
                    cell.classList.add('negative');
                    return;
                }

                if (text.includes('%')) {
                    let cleanText;
                    if (text.includes('/') && text.includes(' ')) {
                        const parts = text.split(' ');
                        const percentPart = parts[parts.length - 1];
                        cleanText = percentPart.replace(/[%,亿万手]/g, '');
                    } else {
                        cleanText = text.replace(/[%,亿万手]/g, '');
                    }
                    const val = parseFloat(cleanText);

                    if (!isNaN(val)) {
                        if (val < 0 || text.includes('-')) {
                            cell.classList.add('negative');
                        } else if (val > 0 || text.includes('+')) {
                            cell.classList.add('positive');
                        }
                    }
                }
                else if (text.startsWith('+')) {
                    cell.classList.add('positive');
                } else if (text.startsWith('-')) {
                    cell.classList.add('negative');
                }
            });
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
        const percentMatch = val.match(/(-?[\d.]+)%/);
        if (percentMatch) {
            const num = parseFloat(percentMatch[1]);
            if (!isNaN(num)) {
                return num;
            }
        }
        const cleanedVal = val.replace(/[%亿万元\/克手]/g, '').replace(/[¥,]/g, '');
        const num = parseFloat(cleanedVal);
        return isNaN(num) ? val.toLowerCase() : num;
    }

    function openTab(evt, tabId) {
        const allContents = document.querySelectorAll('.tab-content');
        allContents.forEach(content => {
            content.classList.remove('active');
        });

        const allButtons = document.querySelectorAll('.tab-button');
        allButtons.forEach(button => {
            button.classList.remove('active');
        });

        document.getElementById(tabId).classList.add('active');
        evt.currentTarget.classList.add('active');
    }

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

    let currentOperation = null;
    let selectedFundsForOperation = [];
    let allFunds = [];
    let currentFilteredFunds = [];

    async function openFundSelectionModal(operation) {
        currentOperation = operation;
        selectedFundsForOperation = [];

        const titles = {
            'hold': '选择要标记持有的基金',
            'unhold': '选择要取消持有的基金',
            'sector': '选择要标注板块的基金',
            'unsector': '选择要删除板块的基金',
            'delete': '选择要删除的基金'
        };
        document.getElementById('fundSelectionTitle').textContent = titles[operation] || '选择基金';

        try {
            const response = await fetch('/api/fund/data');
            const fundMap = await response.json();
            allFunds = Object.entries(fundMap).map(([code, data]) => ({
                code,
                name: data.fund_name,
                is_hold: data.is_hold,
                sectors: data.sectors || []
            }));

            let filteredFunds = allFunds;
            switch (operation) {
                case 'hold':
                    filteredFunds = allFunds.filter(fund => !fund.is_hold);
                    break;
                case 'unhold':
                    filteredFunds = allFunds.filter(fund => fund.is_hold);
                    break;
                case 'unsector':
                    filteredFunds = allFunds.filter(fund => fund.sectors && fund.sectors.length > 0);
                    break;
                case 'sector':
                case 'delete':
                default:
                    filteredFunds = allFunds;
                    break;
            }

            currentFilteredFunds = filteredFunds;
            renderFundSelectionList(filteredFunds);
            document.getElementById('fundSelectionModal').classList.add('active');
        } catch (e) {
            alert('获取基金列表失败: ' + e.message);
        }
    }

    function renderFundSelectionList(funds) {
        const listContainer = document.getElementById('fundSelectionList');
        listContainer.innerHTML = funds.map(fund => `
            <div class="sector-item" style="text-align: left; padding: 12px; margin-bottom: 8px; cursor: pointer; display: flex; align-items: center; gap: 10px;"
                 onclick="toggleFundSelection('${fund.code}', this)">
                <input type="checkbox" class="fund-selection-checkbox" data-code="${fund.code}"
                       style="width: 18px; height: 18px; cursor: pointer;" onclick="event.stopPropagation(); toggleFundSelectionByCheckbox('${fund.code}', this)">
                <div style="flex: 1;">
                    <div style="font-weight: 600;">${fund.code} - ${fund.name}</div>
                    ${fund.is_hold ? '<span style="color: #667eea; font-size: 12px;">⭐ 持有</span>' : ''}
                    ${fund.sectors && fund.sectors.length > 0 ? `<span style="color: #8b949e; font-size: 12px;"> 🏷️ ${fund.sectors.join(', ')}</span>` : ''}
                </div>
            </div>
        `).join('');
    }

    function toggleFundSelection(code, element) {
        const checkbox = element.querySelector('.fund-selection-checkbox');
        checkbox.checked = !checkbox.checked;
        updateFundSelection(code, checkbox.checked, element);
    }

    function toggleFundSelectionByCheckbox(code, checkbox) {
        const element = checkbox.closest('.sector-item');
        updateFundSelection(code, checkbox.checked, element);
    }

    function updateFundSelection(code, checked, element) {
        if (checked) {
            if (!selectedFundsForOperation.includes(code)) {
                selectedFundsForOperation.push(code);
            }
            element.style.backgroundColor = 'rgba(102, 126, 234, 0.2)';
        } else {
            selectedFundsForOperation = selectedFundsForOperation.filter(c => c !== code);
            element.style.backgroundColor = '';
        }
    }

    function closeFundSelectionModal() {
        document.getElementById('fundSelectionModal').classList.remove('active');
        currentOperation = null;
        selectedFundsForOperation = [];
    }

    async function confirmFundSelection() {
        if (selectedFundsForOperation.length === 0) {
            alert('请至少选择一个基金');
            return;
        }

        switch (currentOperation) {
            case 'hold':
                await markHold(selectedFundsForOperation);
                break;
            case 'unhold':
                await unmarkHold(selectedFundsForOperation);
                break;
            case 'sector':
                const selectedCodes = selectedFundsForOperation;
                closeFundSelectionModal();
                openSectorModal(selectedCodes);
                return;
            case 'unsector':
                await removeSector(selectedFundsForOperation);
                break;
            case 'delete':
                await deleteFunds(selectedFundsForOperation);
                break;
        }

        closeFundSelectionModal();
    }

    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('fundSelectionSearch');
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const keyword = this.value.toLowerCase();
                const filtered = currentFilteredFunds.filter(fund =>
                    fund.code.includes(keyword) || fund.name.toLowerCase().includes(keyword)
                );
                renderFundSelectionList(filtered);
            });
        }
    });

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

    const confirmBtn = document.getElementById('confirmBtn');
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            if (confirmCallback) {
                confirmCallback();
            }
            closeConfirmDialog();
        });
    }

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

    let selectedCodesForSector = [];

    function openSectorModal(codes) {
        selectedCodesForSector = codes;
        document.getElementById('sectorModal').classList.add('active');
        renderSectorCategories();
    }

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

    let selectedSectors = [];

    function renderSectorCategories() {
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
        if (selectedCodesForSector.length === 0) {
            alert('请先选择基金');
            closeSectorModal();
            return;
        }
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
                    calculatePositionSummary();
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

        window.downloadFundMap = function() {
            window.location.href = '/api/fund/download';
        };

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

        function calculatePositionSummary() {
            let totalValue = 0;
            let estimatedGain = 0;
            let actualGain = 0;
            let settledValue = 0;
            const today = new Date().toISOString().split('T')[0];
            const fundDetailsData = [];

            const fundRows = document.querySelectorAll('.style-table tbody tr');
            fundRows.forEach(row => {
                const cells = row.querySelectorAll('td');
                if (cells.length < 6) return;

                const codeCell = cells[0];
                const fundCode = codeCell.textContent.trim();

                const shares = (window.fundSharesData && window.fundSharesData[fundCode]) || 0;
                if (shares <= 0) return;

                try {
                    const fundName = cells[1].innerHTML.trim();

                    const netValueText = cells[3].textContent.trim();
                    const netValueMatch = netValueText.match(/([0-9.]+)\(([0-9-]+)\)/);
                    if (!netValueMatch) return;

                    const netValue = parseFloat(netValueMatch[1]);
                    let netValueDate = netValueMatch[2];

                    if (netValueDate.length === 5) {
                        const currentYear = new Date().getFullYear();
                        netValueDate = `${currentYear}-${netValueDate}`;
                    }

                    const estimatedGrowthText = cells[4].textContent.trim();
                    const estimatedGrowth = estimatedGrowthText !== 'N/A' ?
                        parseFloat(estimatedGrowthText.replace('%', '')) : 0;

                    const dayGrowthText = cells[5].textContent.trim();
                    const dayGrowth = dayGrowthText !== 'N/A' ?
                        parseFloat(dayGrowthText.replace('%', '')) : 0;

                    const positionValue = shares * netValue;
                    totalValue += positionValue;

                    const fundEstimatedGain = positionValue * estimatedGrowth / 100;
                    estimatedGain += fundEstimatedGain;

                    let fundActualGain = 0;
                    if (netValueDate === today) {
                        fundActualGain = positionValue * dayGrowth / 100;
                        actualGain += fundActualGain;
                        settledValue += positionValue;
                    }

                    const sectors = window.fundSectorsData && window.fundSectorsData[fundCode] ? window.fundSectorsData[fundCode] : [];

                    fundDetailsData.push({
                        code: fundCode,
                        name: fundName,
                        shares: shares,
                        positionValue: positionValue,
                        estimatedGain: fundEstimatedGain,
                        estimatedGainPct: estimatedGrowth,
                        actualGain: fundActualGain,
                        actualGainPct: netValueDate === today ? dayGrowth : 0,
                        sectors: sectors
                    });
                } catch (e) {
                    console.warn('解析基金数据失败:', fundCode, e);
                }
            });

            window.fundDetailsData = fundDetailsData;

            const summaryDiv = document.getElementById('positionSummary');
            if (summaryDiv && totalValue > 0) {
                summaryDiv.style.display = 'block';
            } else if (summaryDiv) {
                summaryDiv.style.display = 'none';
            }

            const totalValueEl = document.getElementById('totalValue');
            if (totalValueEl) {
                totalValueEl.className = 'sensitive-value';
                const realValueSpan = totalValueEl.querySelector('.real-value');
                if (realValueSpan) {
                    realValueSpan.textContent = '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                }
            }

            const estimatedGainEl = document.getElementById('estimatedGain');
            const estimatedGainPctEl = document.getElementById('estimatedGainPct');
            if (estimatedGainEl && estimatedGainPctEl) {
                const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
                const sensitiveSpan = estimatedGainEl.querySelector('.sensitive-value');
                if (sensitiveSpan) {
                    sensitiveSpan.className = estimatedGain >= 0 ? 'sensitive-value positive' : 'sensitive-value negative';
                }
                const realValueSpan = estimatedGainEl.querySelector('.real-value');
                if (realValueSpan) {
                    realValueSpan.textContent = `¥${Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                }
                estimatedGainPctEl.textContent = ` (${estGainPct >= 0 ? estGainPct.toFixed(2) : '-' + Math.abs(estGainPct).toFixed(2)}%)`;
                estimatedGainPctEl.style.color = estimatedGain >= 0 ? '#f44336' : '#4caf50';
            }

            const actualGainEl = document.getElementById('actualGain');
            const actualGainPctEl = document.getElementById('actualGainPct');
            if (actualGainEl && actualGainPctEl) {
                if (settledValue > 0) {
                    const actGainPct = (actualGain / settledValue * 100);
                    const sensitiveSpan = actualGainEl.querySelector('.sensitive-value');
                    if (sensitiveSpan) {
                        sensitiveSpan.className = actualGain >= 0 ? 'sensitive-value positive' : 'sensitive-value negative';
                    }
                    const realValueSpan = actualGainEl.querySelector('.real-value');
                    if (realValueSpan) {
                        realValueSpan.textContent = `¥${Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                    }
                    actualGainPctEl.textContent = ` (${actGainPct >= 0 ? actGainPct.toFixed(2) : '-' + Math.abs(actGainPct).toFixed(2)}%)`;
                    actualGainPctEl.style.color = actualGain >= 0 ? '#f44336' : '#4caf50';
                } else {
                    const sensitiveSpan = actualGainEl.querySelector('.sensitive-value');
                    if (sensitiveSpan) {
                        sensitiveSpan.className = 'sensitive-value';
                    }
                    const realValueSpan = actualGainEl.querySelector('.real-value');
                    if (realValueSpan) {
                        realValueSpan.textContent = '净值未更新';
                    }
                    actualGainPctEl.textContent = '';
                }
            }

            const holdCountEl = document.getElementById('holdCount');
            if (holdCountEl) {
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

            const fundDetailsDiv = document.getElementById('fundDetailsSummary');
            if (fundDetailsDiv && fundDetailsData.length > 0) {
                fundDetailsDiv.style.display = 'block';
                const tableBody = document.getElementById('fundDetailsTableBody');
                if (tableBody) {
                    tableBody.innerHTML = fundDetailsData.map(fund => {
                        const estColor = fund.estimatedGain >= 0 ? '#f44336' : '#4caf50';
                        const actColor = fund.actualGain >= 0 ? '#f44336' : '#4caf50';
                        const estGainText = fund.estimatedGain >= 0
                            ? `¥${fund.estimatedGain.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
                            : `-¥${Math.abs(fund.estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                        const actGainText = fund.actualGain >= 0
                            ? `¥${fund.actualGain.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
                            : `-¥${Math.abs(fund.actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                        const sharesBtnText = fund.shares > 0 ? '修改' : '设置';
                        const sharesBtnColor = fund.shares > 0 ? '#10b981' : '#3b82f6';
                        return `
                            <tr style="border-bottom: 1px solid var(--border);">
                                <td style="padding: 10px; text-align: center; vertical-align: middle; color: var(--accent); font-weight: 500;">${fund.code}</td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle; color: var(--text-main); white-space: nowrap; min-width: 120px;">${fund.name}</td>
                                <td class="sensitive-value" style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono);"><span class="real-value">${fund.shares.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span><span class="hidden-value">****</span></td>
                                <td style="padding: 10px; text-align: center; vertical-align: middle;"><button onclick="openSharesModal('${fund.code}')" style="padding: 4px 10px; background: ${sharesBtnColor}; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; transition: all 0.2s;">${sharesBtnText}</button></td>
                                <td class="sensitive-value" style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); font-weight: 600;"><span class="real-value">¥${fund.positionValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span><span class="hidden-value">****</span></td>
                                <td class="sensitive-value ${fund.estimatedGain >= 0 ? 'positive' : 'negative'}" style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); color: ${estColor}; font-weight: 500;"><span class="real-value">${estGainText}</span><span class="hidden-value">****</span></td>
                                <td class="${fund.estimatedGain >= 0 ? 'positive' : 'negative'}" style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); color: ${estColor}; font-weight: 500;">${fund.estimatedGainPct >= 0 ? fund.estimatedGainPct.toFixed(2) : '-' + Math.abs(fund.estimatedGainPct).toFixed(2)}%</td>
                                <td class="sensitive-value ${fund.actualGain >= 0 ? 'positive' : 'negative'}" style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); color: ${actColor}; font-weight: 500;"><span class="real-value">${actGainText}</span><span class="hidden-value">****</span></td>
                                <td class="${fund.actualGain >= 0 ? 'positive' : 'negative'}" style="padding: 10px; text-align: center; vertical-align: middle; font-family: var(--font-mono); color: ${actColor}; font-weight: 500;">${fund.actualGainPct >= 0 ? fund.actualGainPct.toFixed(2) : '-' + Math.abs(fund.actualGainPct).toFixed(2)}%</td>
                            </tr>
                        `;
                    }).join('');
                }
            } else if (fundDetailsDiv) {
                fundDetailsDiv.style.display = 'none';
            }

            const summaryBar = document.getElementById('summaryBar');
            if (summaryBar) {
                let heldCount = 0;
                if (window.fundSharesData) {
                    for (const code in window.fundSharesData) {
                        if (window.fundSharesData[code] > 0) {
                            heldCount++;
                        }
                    }
                }

                const summaryTotalValue = document.getElementById('summaryTotalValue');
                if (summaryTotalValue) {
                    summaryTotalValue.textContent = '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                }

                const summaryTotalChange = document.getElementById('summaryTotalChange');
                if (summaryTotalChange) {
                    const totalPct = totalValue > 0 ? ((estimatedGain + actualGain) / totalValue * 100) : 0;
                    const totalSign = (estimatedGain + actualGain) >= 0 ? '+' : '';
                    summaryTotalChange.textContent = `${totalSign}${totalPct.toFixed(2)}%`;
                    summaryTotalChange.className = 'summary-change ' + ((estimatedGain + actualGain) >= 0 ? 'positive' : 'negative');
                }

                const summaryEstGain = document.getElementById('summaryEstGain');
                if (summaryEstGain) {
                    const estSign = estimatedGain >= 0 ? '+' : '';
                    summaryEstGain.textContent = `${estSign}¥${Math.abs(estimatedGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                }

                const summaryEstChange = document.getElementById('summaryEstChange');
                if (summaryEstChange) {
                    const estGainPct = totalValue > 0 ? (estimatedGain / totalValue * 100) : 0;
                    const estSign = estimatedGain >= 0 ? '+' : '';
                    summaryEstChange.textContent = `${estSign}${estGainPct.toFixed(2)}%`;
                    summaryEstChange.className = 'summary-change ' + (estimatedGain >= 0 ? 'positive' : 'negative');
                }

                const summaryActualGain = document.getElementById('summaryActualGain');
                if (summaryActualGain) {
                    const actSign = actualGain >= 0 ? '+' : '';
                    summaryActualGain.textContent = `${actSign}¥${Math.abs(actualGain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
                }

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

                const summaryHoldCount = document.getElementById('summaryHoldCount');
                if (summaryHoldCount) {
                    summaryHoldCount.textContent = `${heldCount} 只`;
                }
            }
        }

        async function loadSharesData() {
            try {
                const response = await fetch('/api/fund/data');
                if (response.ok) {
                    const fundData = await response.json();

                    window.fundSharesData = {};
                    window.fundSectorsData = {};

                    for (const [code, data] of Object.entries(fundData)) {
                        if (data.shares !== undefined && data.shares !== null) {
                            window.fundSharesData[code] = parseFloat(data.shares) || 0;
                        }
                        if (data.sectors && data.sectors.length > 0) {
                            window.fundSectorsData[code] = data.sectors;
                        }

                        const sharesInput = document.getElementById('shares_' + code);
                        if (sharesInput && data.shares) {
                            sharesInput.value = data.shares;
                        }
                    }

                    console.log('已加载份额数据:', window.fundSharesData);
                    calculatePositionSummary();
                }
            } catch (e) {
                console.error('加载份额数据失败:', e);
                calculatePositionSummary();
            }
        }

        loadSharesData();

        window.toggleFundExpand = function(fundCode) {
            const fundRow = document.querySelector(`.fund-row[data-code="${fundCode}"]`);
            if (fundRow) {
                fundRow.classList.toggle('expanded');
            }
        };

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

        let currentSharesFundCode = null;

        window.getFundShares = function(fundCode) {
            if (window.fundSharesData && window.fundSharesData[fundCode]) {
                return window.fundSharesData[fundCode];
            }
            return 0;
        };

        function updateSharesButton(fundCode, shares) {
            const button = document.getElementById('sharesBtn_' + fundCode);
            if (button) {
                if (shares > 0) {
                    button.textContent = '修改';
                    button.style.background = '#10b981';
                } else {
                    button.textContent = '设置';
                    button.style.background = '#3b82f6';
                }
            }
        }

        window.openSharesModal = function(fundCode) {
            currentSharesFundCode = fundCode;
            const modal = document.getElementById('sharesModal');
            const fundCodeDisplay = document.getElementById('sharesModalFundCode');
            const sharesInput = document.getElementById('sharesModalInput');

            const sharesValue = window.getFundShares(fundCode) || 0;
            sharesInput.value = sharesValue > 0 ? sharesValue : '';
            fundCodeDisplay.textContent = fundCode;

            const header = modal.querySelector('.sector-modal-header');
            if (header) {
                header.textContent = sharesValue > 0 ? '修改持仓份额' : '设置持仓份额';
            }

            modal.classList.add('active');
            setTimeout(() => sharesInput.focus(), 100);
        };

        window.closeSharesModal = function() {
            const modal = document.getElementById('sharesModal');
            if (modal) {
                modal.classList.remove('active');
            }
            currentSharesFundCode = null;
        };

        window.confirmShares = async function() {
            if (!currentSharesFundCode) {
                alert('未选择基金');
                return;
            }

            const sharesInput = document.getElementById('sharesModalInput');
            const shares = parseFloat(sharesInput.value) || 0;

            if (shares < 0) {
                alert('份额不能为负数');
                return;
            }

            try {
                const response = await fetch('/api/fund/shares', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: currentSharesFundCode, shares: shares })
                });
                const result = await response.json();

                if (result.success) {
                    if (!window.fundSharesData) {
                        window.fundSharesData = {};
                    }
                    window.fundSharesData[currentSharesFundCode] = shares;

                    updateSharesButton(currentSharesFundCode, shares);
                    calculatePositionSummary();
                    window.closeSharesModal();

                    alert(result.message);
                } else {
                    alert(result.message);
                }
            } catch (e) {
                alert('设置份额失败: ' + e.message);
            }
        };

        window.openSharesModal = openSharesModal;
        window.closeSharesModal = closeSharesModal;
        window.confirmShares = confirmShares;
        window.getFundShares = getFundShares;

        window.filterHeldFunds = function() {
            const filterCheckbox = document.getElementById('filterHeldOnly');
            const isFiltered = filterCheckbox ? filterCheckbox.checked : false;
            const table = document.querySelector('.fund-content .style-table');
            if (!table) return;

            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const nameCell = row.cells[1];
                if (nameCell) {
                    const nameText = nameCell.textContent.trim();
                    const isHeld = nameText.includes('⭐');
                    row.style.display = (isFiltered && !isHeld) ? 'none' : '';
                }
            });

            if (typeof calculatePositionSummary === 'function') {
                calculatePositionSummary();
            }
        };

        window.getFilterHeldOnly = function() {
            const filterCheckbox = document.getElementById('filterHeldOnly');
            return filterCheckbox ? filterCheckbox.checked : false;
        };

        let refreshInterval;
        const REFRESH_INTERVAL = 60000;

        function startAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
            }
            refreshInterval = setInterval(() => {
                refreshCurrentPage();
            }, REFRESH_INTERVAL);
            console.log('Auto-refresh started (60s interval)');
        }

        function stopAutoRefresh() {
            if (refreshInterval) {
                clearInterval(refreshInterval);
                refreshInterval = null;
                console.log('Auto-refresh stopped');
            }
        }

        async function refreshCurrentPage() {
            const path = window.location.pathname;
            const refreshBtn = document.getElementById('refreshBtn');

            if (refreshBtn) {
                refreshBtn.disabled = true;
                refreshBtn.innerHTML = '⏳ 刷新中...';
            }

            try {
                switch (path) {
                    case '/portfolio':
                        await fetchPortfolioData();
                        break;
                    case '/market-indices':
                        await fetchMarketIndicesData();
                        break;
                    case '/precious-metals':
                        await fetchPreciousMetalsData();
                        break;
                    case '/sectors':
                        await fetchSectorsData();
                        break;
                    case '/market':
                        await fetchNewsData();
                        break;
                    default:
                        console.log('No refresh handler for path:', path);
                }
            } catch (e) {
                console.error('Refresh failed:', e);
            } finally {
                if (refreshBtn) {
                    refreshBtn.disabled = false;
                    refreshBtn.innerHTML = '🔄 刷新';
                }
            }
        }

        async function fetchPortfolioData() {
            try {
                const timingRes = await fetch('/api/timing');
                const timingResult = await timingRes.json();
                if (timingResult.success && timingResult.data) {
                    updateTimingChart(timingResult.data);
                }

                const isFiltered = window.getFilterHeldOnly ? window.getFilterHeldOnly() : false;
                const fundRes = await fetch(`/api/fund/refresh?held_only=${isFiltered}`);
                const fundResult = await fundRes.json();
                if (fundResult.success && fundResult.data) {
                    updateFundTable(fundResult.data);
                }

                autoColorize();
            } catch (e) {
                console.error('Failed to refresh portfolio data:', e);
            }
        }

        function updateFundTable(funds) {
            const table = document.querySelector('.fund-content .style-table');
            if (!table) return;

            const rows = table.querySelectorAll('tbody tr');
            funds.forEach(fund => {
                rows.forEach(row => {
                    const codeCell = row.cells[0];
                    if (codeCell && codeCell.textContent.trim() === fund.code) {
                        if (row.cells[2]) {
                            row.cells[2].textContent = fund.time;
                        }
                        if (row.cells[4]) {
                            const growthValue = fund.estimated_growth.replace(/\x1b\[[0-9;]*m/g, '');
                            row.cells[4].textContent = growthValue;
                            row.cells[4].classList.remove('positive', 'negative');
                            if (growthValue.includes('-')) {
                                row.cells[4].classList.add('negative');
                            } else if (parseFloat(growthValue) > 0) {
                                row.cells[4].classList.add('positive');
                            }
                        }
                        if (row.cells[5]) {
                            const dayValue = fund.day_growth.replace(/\x1b\[[0-9;]*m/g, '');
                            row.cells[5].textContent = dayValue;
                            row.cells[5].classList.remove('positive', 'negative');
                            if (dayValue.includes('-')) {
                                row.cells[5].classList.add('negative');
                            } else if (parseFloat(dayValue) > 0) {
                                row.cells[5].classList.add('positive');
                            }
                        }
                    }
                });
            });

            if (typeof calculatePositionSummary === 'function') {
                calculatePositionSummary();
            }
        }

        async function fetchMarketIndicesData() {
            try {
                const indicesRes = await fetch('/api/indices/global');
                const indicesResult = await indicesRes.json();

                const volumeRes = await fetch('/api/indices/volume');
                const volumeResult = await volumeRes.json();

                if (indicesResult.success) {
                    updateGlobalIndicesTable(indicesResult.data);
                }
                if (volumeResult.success) {
                    updateVolumeChart(volumeResult.data);
                }

                autoColorize();
            } catch (e) {
                console.error('Failed to refresh market indices:', e);
            }
        }

        async function fetchPreciousMetalsData() {
            try {
                const realtimeRes = await fetch('/api/gold/real-time');
                const realtimeResult = await realtimeRes.json();

                const oneDayRes = await fetch('/api/gold/one-day');
                const oneDayResult = await oneDayRes.json();

                const historyRes = await fetch('/api/gold/history');
                const historyResult = await historyRes.json();

                if (realtimeResult.success) {
                    updateRealtimeGoldTable(realtimeResult.data);
                }
                if (oneDayResult.success) {
                    updateGoldOneDayChart(oneDayResult.data);
                }
                if (historyResult.success) {
                    updateGoldHistoryTable(historyResult.data);
                }

                autoColorize();
            } catch (e) {
                console.error('Failed to refresh precious metals:', e);
            }
        }

        async function fetchSectorsData() {
            try {
                const sectorsRes = await fetch('/api/sectors');
                const sectorsResult = await sectorsRes.json();

                if (sectorsResult.success) {
                    updateSectorsTable(sectorsResult.data);
                }

                autoColorize();
            } catch (e) {
                console.error('Failed to refresh sectors:', e);
            }
        }

        async function fetchNewsData() {
            try {
                const newsRes = await fetch('/api/news/7x24');
                const newsResult = await newsRes.json();

                if (newsResult.success) {
                    updateNewsTable(newsResult.data);
                }

                autoColorize();
            } catch (e) {
                console.error('Failed to refresh news:', e);
            }
        }

        function updateTimingChart(data) {
            if (window.timingChartInstance && data.labels && data.labels.length > 0) {
                window.timingChartInstance.data.labels = data.labels;
                window.timingChartInstance.data.datasets[0].data = data.change_pcts || data.prices;
                window.timingChartInstance.update();

                const titleEl = document.getElementById('timingChartTitle');
                if (titleEl && data.current_price !== undefined) {
                    const changePct = data.change_pct || 0;
                    const color = changePct >= 0 ? '#f44336' : '#4caf50';
                    titleEl.style.color = color;
                    titleEl.innerHTML = '📉 上证分时 <span style="font-size:0.9em;">' +
                        (changePct >= 0 ? '+' : '') + changePct.toFixed(2) + '% (' +
                        data.current_price.toFixed(2) + ')</span>';
                }
            }
        }

        function updateGlobalIndicesTable(data) {
            const table = document.querySelector('.style-table');
            if (table && data) {
                const tbody = table.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = data.map(item => `
                        <tr>
                            <td>${item.name}</td>
                            <td>${item.value}</td>
                            <td>${item.change}</td>
                        </tr>
                    `).join('');
                }
            }
        }

        function updateVolumeChart(data) {
            if (window.volumeChartInstance && data.labels && data.labels.length > 0) {
                window.volumeChartInstance.data.labels = data.labels;
                window.volumeChartInstance.data.datasets[0].data = data.total || [];
                window.volumeChartInstance.update();
            }
        }

        function updateRealtimeGoldTable(data) {
            const table = document.querySelector('.style-table');
            if (table && data) {
                const tbody = table.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = data.map(item => `
                        <tr>
                            <td>${item.name}</td>
                            <td>${item.price}</td>
                            <td>${item.change_amount}</td>
                            <td>${item.change_pct}</td>
                            <td>${item.open_price}</td>
                            <td>${item.high_price}</td>
                            <td>${item.low_price}</td>
                            <td>${item.prev_close}</td>
                            <td>${item.update_time}</td>
                            <td>${item.unit}</td>
                        </tr>
                    `).join('');
                }
            }
        }

        function updateGoldOneDayChart(data) {
            if (!data || !Array.isArray(data) || data.length === 0) return;

            const labels = [];
            const prices = [];

            data.forEach(item => {
                if (item.date && item.price !== undefined) {
                    const timePart = item.date.split(' ')[1] || item.date;
                    labels.push(timePart);
                    prices.push(parseFloat(item.price));
                }
            });

            let labelText = '金价 (元/克)';
            if (data.length > 0) {
                const latestData = data[data.length - 1];
                const timePart = latestData.date.split(' ')[1] || latestData.date;
                labelText = `金价 (元/克)  最新: ¥${latestData.price}  ${timePart}`;
            }

            if (window.goldOneDayChartInstance) {
                window.goldOneDayChartInstance.data.labels = labels;
                window.goldOneDayChartInstance.data.datasets[0].data = prices;
                window.goldOneDayChartInstance.data.datasets[0].label = labelText;
                window.goldOneDayChartInstance.update();
            }
        }

        function updateGoldHistoryTable(data) {
            const tables = document.querySelectorAll('.style-table');
            if (tables.length > 1 && data) {
                const tbody = tables[1].querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = data.map(item => `
                        <tr>
                            <td>${item.date}</td>
                            <td>${item.china_gold_price}</td>
                            <td>${item.chow_tai_fook_price}</td>
                            <td>${item.china_gold_change}</td>
                            <td>${item.chow_tai_fook_change}</td>
                        </tr>
                    `).join('');
                }
            }
        }

        function updateSectorsTable(data) {
            const table = document.querySelector('.style-table');
            if (table && data) {
                const tbody = table.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = data.map(item => `
                        <tr>
                            <td>${item.name}</td>
                            <td>${item.change}</td>
                            <td>${item.main_inflow}</td>
                            <td>${item.main_inflow_pct}</td>
                            <td>${item.small_inflow}</td>
                            <td>${item.small_inflow_pct}</td>
                        </tr>
                    `).join('');
                }
            }
        }

        function updateNewsTable(data) {
            const table = document.querySelector('.style-table');
            if (table && data) {
                const tbody = table.querySelector('tbody');
                if (tbody) {
                    tbody.innerHTML = data.map(item => {
                        let sourceClass = '';
                        if (item.source === '利好') {
                            sourceClass = 'positive';
                        } else if (item.source === '利空') {
                            sourceClass = 'negative';
                        }

                        return `
                        <tr>
                            <td>${item.time}</td>
                            <td class="${sourceClass}">${item.source}</td>
                            <td>${item.content}</td>
                        </tr>
                        `;
                    }).join('');
                }
            }
        }

        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                stopAutoRefresh();
            } else {
                refreshCurrentPage();
                startAutoRefresh();
            }
        });

        startAutoRefresh();

        window.refreshCurrentPage = refreshCurrentPage;

        function initSensitiveValuesToggle() {
            const toggleBtn = document.getElementById('toggleSensitiveValues');
            if (!toggleBtn) return;

            const positionSummary = document.getElementById('positionSummary');
            const fundDetailsTable = document.getElementById('fundDetailsTable');

            const isHidden = localStorage.getItem('hideSensitiveValues') === 'true';
            if (isHidden) {
                if (positionSummary) positionSummary.classList.add('hide-values');
                if (fundDetailsTable) fundDetailsTable.classList.add('hide-values');
                toggleBtn.textContent = '😑';
            }

            toggleBtn.addEventListener('click', function() {
                const currentlyHidden = localStorage.getItem('hideSensitiveValues') === 'true';
                if (currentlyHidden) {
                    if (positionSummary) positionSummary.classList.remove('hide-values');
                    if (fundDetailsTable) fundDetailsTable.classList.remove('hide-values');
                    localStorage.setItem('hideSensitiveValues', 'false');
                    toggleBtn.textContent = '😀';
                } else {
                    if (positionSummary) positionSummary.classList.add('hide-values');
                    if (fundDetailsTable) fundDetailsTable.classList.add('hide-values');
                    localStorage.setItem('hideSensitiveValues', 'true');
                    toggleBtn.textContent = '😑';
                }
            });
        }

        initSensitiveValuesToggle();

        window.openShowoffCard = function() {
            const totalValueEl = document.getElementById('totalValue');
            if (!totalValueEl) {
                alert('请先刷新页面加载数据');
                return;
            }

            const realValueText = totalValueEl.querySelector('.real-value')?.textContent || '';
            if (realValueText === '¥0.00' || realValueText === '') {
                alert('暂无持仓数据，无法生成炫耀卡片');
                return;
            }

            const totalValue = parseFloat(realValueText.replace(/[¥,]/g, '')) || 0;

            const estimatedGainEl = document.getElementById('estimatedGain');
            const estimatedGainText = estimatedGainEl?.querySelector('.real-value')?.textContent || '¥0.00';
            const isEstNegative = estimatedGainEl?.querySelector('.sensitive-value')?.classList.contains('negative') ?? false;
            const estimatedGain = parseFloat(estimatedGainText.replace(/[¥,]/g, '')) * (isEstNegative ? -1 : 1) || 0;

            const actualGainEl = document.getElementById('actualGain');
            const actualGainText = actualGainEl?.querySelector('.real-value')?.textContent || '¥0.00';
            const isActNegative = actualGainEl?.querySelector('.sensitive-value')?.classList.contains('negative') ?? false;
            const actualGain = actualGainText.includes('净值') ? 0 :
                parseFloat(actualGainText.replace(/[¥,]/g, '')) * (isActNegative ? -1 : 1) || 0;

            const today = new Date();
            const dateStr = today.getFullYear() + '-' +
                String(today.getMonth() + 1).padStart(2, '0') + '-' +
                String(today.getDate()).padStart(2, '0');

            document.getElementById('showoffDate').textContent = dateStr;
            document.getElementById('showoffTotalValue').textContent =
                '¥' + totalValue.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            const estGainEl = document.getElementById('showoffEstimatedGain');
            estGainEl.textContent = '¥' + Math.abs(estimatedGain).toLocaleString('zh-CN',
                {minimumFractionDigits: 2, maximumFractionDigits: 2});
            estGainEl.className = 'summary-value ' + (estimatedGain >= 0 ? 'positive' : 'negative');

            const actGainEl = document.getElementById('showoffActualGain');
            actGainEl.textContent = actualGainText.includes('净值') ? '净值未更新' :
                ('¥' + Math.abs(actualGain).toLocaleString('zh-CN',
                {minimumFractionDigits: 2, maximumFractionDigits: 2}));
            actGainEl.className = 'summary-value ' + (actualGain > 0 ? 'positive' :
                (actualGain < 0 ? 'negative' : ''));

            const top3Funds = getTop3Funds();
            renderTop3Funds(top3Funds);

            document.getElementById('showoffModal').classList.add('active');
        };

        window.closeShowoffCard = function(event) {
            if (!event || event.target.id === 'showoffModal' || event.target.classList.contains('showoff-close')) {
                document.getElementById('showoffModal').classList.remove('active');
            }
        };

        function getTop3Funds() {
            if (window.fundDetailsData && window.fundDetailsData.length > 0) {
                const sorted = [...window.fundDetailsData].sort((a, b) => {
                    const aGain = a.actualGain !== 0 ? a.actualGain : a.estimatedGain;
                    const bGain = b.actualGain !== 0 ? b.actualGain : b.estimatedGain;
                    return bGain - aGain;
                });
                return sorted.slice(0, 3);
            }
            return [];
        }

        function renderTop3Funds(funds) {
            const container = document.getElementById('showoffFundsList');

            if (!funds || funds.length === 0) {
                container.innerHTML = '<div style="text-align: center; color: rgba(255,255,255,0.4); font-size: 13px;">暂无数据</div>';
                return;
            }

            container.innerHTML = funds.map((fund, index) => {
                const gain = fund.actualGain !== 0 ? fund.actualGain : (fund.estimatedGain || 0);
                const colorClass = gain >= 0 ? 'positive' : 'negative';

                return `
                    <div class="fund-item">
                        <div class="fund-rank">${index + 1}</div>
                        <div class="fund-info">
                            <div class="fund-name">${fund.name}</div>
                        </div>
                        <div class="fund-gain ${colorClass}">¥${Math.abs(gain).toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</div>
                    </div>
                `;
            }).join('');
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                closeShowoffCard();
            }
        });

    });
