// Sidebar Navigation Controller
class SidebarNavigation {
  constructor() {
    this.currentSection = 'funds';
    this.sidebar = document.getElementById('sidebarNav');
    this.sidebarToggle = document.getElementById('sidebarToggle');
    this.sidebarIcons = document.querySelectorAll('.sidebar-icon');
    this.sectionTitle = document.getElementById('sectionTitle');
    this.summaryBar = document.getElementById('summaryBar');

    // Mapping from section ID to actual DOM element ID
    this.sectionIdMap = {
      'news': 'kx',
      'indices': 'marker',
      'gold-realtime': 'real_time_gold',
      'gold-history': 'gold',
      'volume': 'seven_A',
      'timing': 'A',
      'funds': 'fund',  // Special case - uses holdingsSection and watchlistSection
      'sectors': 'bk',
      'query': 'select_fund'
    };

    this.init();
  }

  init() {
    // Sidebar icon click handlers
    this.sidebarIcons.forEach(icon => {
      icon.addEventListener('click', (e) => {
        const section = icon.dataset.section;
        const tabId = icon.dataset.tabId;
        this.navigateToSection(section, tabId);
      });
    });

    // Sidebar toggle
    if (this.sidebarToggle) {
      this.sidebarToggle.addEventListener('click', () => {
        this.toggleSidebar();
      });
    }

    // Mobile overlay
    this.createMobileOverlay();

    // Wait a bit for DOM to fully settle before initializing first section
    setTimeout(() => {
      this.navigateToSection(this.currentSection, 'fund');
    }, 100);
  }

  navigateToSection(sectionId, tabId) {
    // Update active icon
    this.sidebarIcons.forEach(icon => {
      if (icon.dataset.section === sectionId) {
        icon.classList.add('active');
      } else {
        icon.classList.remove('active');
      }
    });

    // Update section title
    const titles = {
      'news': '7*24快讯',
      'indices': '全球指数',
      'gold-realtime': '实时贵金属',
      'gold-history': '历史金价',
      'volume': '成交量趋势',
      'timing': '上证分时',
      'funds': '自选基金',
      'sectors': '行业板块',
      'query': '板块基金查询'
    };
    if (this.sectionTitle) {
      this.sectionTitle.textContent = titles[sectionId] || sectionId;
    }

    // Show/hide summary bar (only for funds section)
    if (this.summaryBar) {
      if (sectionId === 'funds') {
        this.summaryBar.style.display = 'grid';
      } else {
        this.summaryBar.style.display = 'none';
      }
    }

    // Load section content if needed
    this.loadSectionContent(sectionId, tabId);

    this.currentSection = sectionId;
  }

  async loadSectionContent(sectionId, tabId) {
    // For funds section, show holdings and watchlist
    if (sectionId === 'funds') {
      this.contentSections.forEach(section => {
        section.classList.add('hidden');
      });
      const holdingsSection = document.getElementById('holdingsSection');
      const watchlistSection = document.getElementById('watchlistSection');
      if (holdingsSection) {
        holdingsSection.classList.remove('hidden');
      } else {
        console.warn('holdingsSection not found in DOM');
      }
      if (watchlistSection) {
        watchlistSection.classList.remove('hidden');
      } else {
        console.warn('watchlistSection not found in DOM');
      }
      return;
    }

    // For other sections, get the actual DOM element ID
    const actualTabId = this.sectionIdMap[sectionId] || tabId;
    const sectionElement = document.getElementById(actualTabId + 'Section');

    if (!sectionElement) {
      console.warn('Section not found:', sectionId, '(looking for:', actualTabId + 'Section)');
      return;
    }

    // Show section
    this.contentSections.forEach(section => {
      section.classList.add('hidden');
    });
    sectionElement.classList.remove('hidden');

    // Lazy load content if not already loaded
    const contentDiv = sectionElement.querySelector('.section-content');
    if (contentDiv && contentDiv.innerHTML.trim() === '') {
      await this.fetchTabContent(actualTabId, contentDiv);
    }
  }

  async fetchTabContent(tabId, targetElement) {
    try {
      targetElement.innerHTML = '<div class="loading">加载中...</div>';

      const response = await fetch(`/api/tab/${tabId}`);
      const data = await response.json();

      if (data.success) {
        targetElement.innerHTML = data.content;
        // Re-apply auto-colorization if function exists
        if (typeof autoColorize === 'function') {
          autoColorize();
        }
      } else {
        targetElement.innerHTML = '<div class="error">加载失败</div>';
      }
    } catch (error) {
      console.error('Failed to load tab content:', error);
      targetElement.innerHTML = '<div class="error">加载失败</div>';
    }
  }

  toggleSidebar() {
    if (this.sidebar) {
      this.sidebar.classList.toggle('expanded');
    }
  }

  createMobileOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'sidebar-overlay';
    overlay.id = 'sidebarOverlay';
    overlay.addEventListener('click', () => {
      this.closeMobileSidebar();
    });
    document.body.appendChild(overlay);
  }

  closeMobileSidebar() {
    if (this.sidebar) {
      this.sidebar.classList.remove('mobile-open');
    }
    const overlay = document.getElementById('sidebarOverlay');
    if (overlay) {
      overlay.classList.remove('active');
    }
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  window.sidebarNav = new SidebarNavigation();
});
