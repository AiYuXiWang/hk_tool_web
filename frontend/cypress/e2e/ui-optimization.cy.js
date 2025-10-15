describe('UI优化端到端测试', () => {
  beforeEach(() => {
    // 访问应用
    cy.visit('/')
  })

  describe('增强按钮组件', () => {
    it('应该正确渲染所有按钮变体', () => {
      cy.visit('/components/buttons')

      // 检查主要按钮
      cy.get('.enhanced-button--primary').should('be.visible')
      cy.get('.enhanced-button--primary').should('have.css', 'background-color').and('match', /rgb\(24,\s*144,\s*255\)/)

      // 检查成功按钮
      cy.get('.enhanced-button--success').should('be.visible')
      cy.get('.enhanced-button--success').should('have.css', 'background-color').and('match', /rgb\(82,\s*196,\s*26\)/)

      // 检查警告按钮
      cy.get('.enhanced-button--warning').should('be.visible')
      cy.get('.enhanced-button--warning').should('have.css', 'background-color').and('match', /rgb\(250,\s*173,\s*20\)/)

      // 检查危险按钮
      cy.get('.enhanced-button--danger').should('be.visible')
      cy.get('.enhanced-button--danger').should('have.css', 'background-color').and('match', /rgb\(255,\s*77,\s*79\)/)
    })

    it('应该正确处理按钮交互', () => {
      cy.visit('/components/buttons')

      // 检查悬停效果
      cy.get('.enhanced-button--primary').realHover()
      cy.get('.enhanced-button--primary').should('have.class', 'enhanced-button--hovered')

      // 检查点击效果
      cy.get('.enhanced-button--primary').realClick()
      cy.get('.enhanced-button--primary').should('have.class', 'enhanced-button--animated')

      // 检查波纹效果
      cy.get('.enhanced-button--primary .button-ripple').should('exist')
    })

    it('应该正确处理加载状态', () => {
      cy.visit('/components/buttons')

      // 点击加载按钮
      cy.get('[data-testid="loading-button"]').realClick()

      // 检查加载状态
      cy.get('.enhanced-button--loading').should('be.visible')
      cy.get('.icon-loading').should('be.visible')
      cy.get('.icon-loading').should('have.class', 'icon-spin')

      // 检查禁用状态
      cy.get('.enhanced-button--loading').should('be.disabled')
    })

    it('应该支持键盘导航', () => {
      cy.visit('/components/buttons')

      // 使用Tab键导航到按钮
      cy.get('body').tab()
      cy.get('.enhanced-button--primary').should('be.focused')

      // 使用Enter键激活
      cy.get('.enhanced-button--primary').type('{enter}')

      // 使用空格键激活
      cy.get('.enhanced-button--primary').focus().type(' ')

      // 检查焦点可见性
      cy.get('.enhanced-button--primary').should('have.css', 'outline-style', 'solid')
    })
  })

  describe('增强KPI卡片组件', () => {
    beforeEach(() => {
      cy.visit('/energy/cockpit')
    })

    it('应该正确渲染KPI卡片', () => {
      // 检查KPI卡片存在
      cy.get('.enhanced-kpi-card').should('have.length', 4)

      // 检查总能耗卡片
      cy.get('.enhanced-kpi-card').eq(0).within(() => {
        cy.get('.kpi-title').should('contain.text', '总能耗')
        cy.get('.kpi-unit').should('contain.text', 'kWh')
        cy.get('.kpi-icon').should('have.class', 'icon-energy')
      })

      // 检查实时功率卡片
      cy.get('.enhanced-kpi-card').eq(1).within(() => {
        cy.get('.kpi-title').should('contain.text', '实时功率')
        cy.get('.kpi-unit').should('contain.text', 'kW')
        cy.get('.kpi-icon').should('have.class', 'icon-activity')
      })

      // 检查峰值功率卡片
      cy.get('.enhanced-kpi-card').eq(2).within(() => {
        cy.get('.kpi-title').should('contain.text', '峰值功率')
        cy.get('.kpi-unit').should('contain.text', 'kW')
        cy.get('.kpi-icon').should('have.class', 'icon-trending-up')
      })

      // 检查监控车站卡片
      cy.get('.enhanced-kpi-card').eq(3).within(() => {
        cy.get('.kpi-title').should('contain.text', '监控车站')
        cy.get('.kpi-unit').should('contain.text', '个')
        cy.get('.kpi-icon').should('have.class', 'icon-map-pin')
      })
    })

    it('应该正确显示趋势指示器', () => {
      cy.get('.kpi-trend').should('be.visible')

      // 检查上升趋势
      cy.get('.enhanced-kpi-card').eq(0).within(() => {
        cy.get('.kpi-trend').should('have.class', 'trend--up')
        cy.get('.kpi-trend').should('contain.text', '5.2%')
        cy.get('.trend-icon').should('have.class', 'icon-arrow-up')
      })

      // 检查下降趋势
      cy.get('.enhanced-kpi-card').eq(1).within(() => {
        cy.get('.kpi-trend').should('have.class', 'trend--down')
        cy.get('.kpi-trend').should('contain.text', '2.1%')
        cy.get('.trend-icon').should('have.class', 'icon-arrow-down')
      })
    })

    it('应该正确处理悬停效果', () => {
      cy.get('.enhanced-kpi-card').eq(0).realHover()

      // 检查悬停状态
      cy.get('.enhanced-kpi-card').eq(0).should('have.class', 'kpi-card--hovered')
      cy.get('.enhanced-kpi-card').eq(0).should('have.css', 'transform', 'translateY(-4px)')

      // 检查阴影效果
      cy.get('.enhanced-kpi-card').eq(0).should('have.css', 'box-shadow').and('not.match', /rgba\(0,\s*0,\s*0,\s*0\)/)
    })

    it('应该支持数值动画', () => {
      // 检查数值动画
      cy.get('.kpi-value').should('be.visible')

      // 等待动画完成
      cy.wait(1000)

      // 检查最终数值
      cy.get('.enhanced-kpi-card').eq(0).within(() => {
        cy.get('.kpi-value').should('not.contain.text', '0')
      })
    })
  })

  describe('加载骨架屏组件', () => {
    it('应该正确渲染不同类型的骨架屏', () => {
      cy.visit('/components/skeletons')

      // 检查卡片骨架屏
      cy.get('.skeleton--card').should('be.visible')
      cy.get('.skeleton-avatar').should('be.visible')
      cy.get('.skeleton-title').should('be.visible')
      cy.get('.skeleton-line').should('have.length.greaterThan', 0)

      // 检查表格骨架屏
      cy.get('.skeleton--table').should('be.visible')
      cy.get('.skeleton-table-header').should('be.visible')
      cy.get('.skeleton-table-row').should('have.length.greaterThan', 0)

      // 检查KPI骨架屏
      cy.get('.skeleton--kpi').should('be.visible')
      cy.get('.skeleton-kpi-icon').should('be.visible')
      cy.get('.skeleton-kpi-value').should('be.visible')

      // 检查图表骨架屏
      cy.get('.skeleton--chart').should('be.visible')
      cy.get('.skeleton-chart-bars').should('be.visible')
      cy.get('.skeleton-bar').should('have.length.greaterThan', 0)
    })

    it('应该正确显示闪烁动画', () => {
      cy.visit('/components/skeletons')

      // 检查闪烁效果
      cy.get('.skeleton--shimmer').should('have.class', 'skeleton--shimmer')

      // 检查脉动动画
      cy.get('.skeleton--animated').should('have.class', 'skeleton--animated')
    })
  })

  describe('响应式设计', () => {
    it('应该在移动端正确显示', () => {
      cy.viewport(375, 667) // iPhone 6/7/8

      cy.visit('/energy/cockpit')

      // 检查移动端布局
      cy.get('.kpi-dashboard').should('be.visible')
      cy.get('.enhanced-kpi-card').should('have.length', 4)

      // 检查移动端按钮大小
      cy.get('.enhanced-button').should('have.css', 'min-height').and('match', /4[0-4]px/)

      // 检查移动端间距
      cy.get('.kpi-card-content').should('have.css', 'padding').and('match', /1[2-6]px/)
    })

    it('应该在平板端正确显示', () => {
      cy.viewport(768, 1024) // iPad

      cy.visit('/energy/cockpit')

      // 检查平板端布局
      cy.get('.chart-section').should('be.visible')
      cy.get('.chart-container').should('have.length', 2)

      // 检查图表布局
      cy.get('.chart-section').should('have.css', 'grid-template-columns').and('match', /1fr/)
    })

    it('应该在桌面端正确显示', () => {
      cy.viewport(1920, 1080) // Full HD

      cy.visit('/energy/cockpit')

      // 检查桌面端布局
      cy.get('.chart-section').should('be.visible')
      cy.get('.chart-section').should('have.css', 'grid-template-columns').and('match', /1fr.*1fr/)

      // 检查底部区域布局
      cy.get('.bottom-section').should('have.css', 'grid-template-columns').and('match', /1fr.*1fr/)
    })
  })

  describe('性能测试', () => {
    it('应该在合理时间内加载页面', () => {
      cy.visit('/energy/cockpit')

      // 检查页面加载时间
      cy.window().then((win) => {
        const loadTime = win.performance.timing.loadEventEnd - win.performance.timing.navigationStart
        expect(loadTime).to.be.lessThan(3000) // 3秒内加载完成
      })
    })

    it('应该正确处理大量数据渲染', () => {
      cy.visit('/device/overview')

      // 检查设备树渲染
      cy.get('.device-tree').should('be.visible')
      cy.get('.tree-node-content').should('have.length.greaterThan', 0)

      // 检查表格渲染性能
      cy.get('.data-table').should('be.visible')
      cy.get('.el-table__row').should('have.length.lteThan', 100) // 限制行数以保证性能
    })
  })

  describe('无障碍访问测试', () => {
    it('应该支持键盘导航', () => {
      cy.visit('/')

      // 使用Tab键导航
      cy.get('body').tab()
      cy.get('.el-tabs__item').should('be.focused')

      // 继续Tab导航
      cy.get('body').tab()
      cy.get('.enhanced-button').should('be.focused')

      // 检查焦点指示器
      cy.get('.enhanced-button').should('have.css', 'outline-style', 'solid')
      cy.get('.enhanced-button').should('have.css', 'outline-width', '2px')
    })

    it('应该正确设置ARIA标签', () => {
      cy.visit('/energy/cockpit')

      // 检查主要区域的ARIA标签
      cy.get('main').should('have.attr', 'role', 'main')
      cy.get('.kpi-dashboard').should('have.attr', 'aria-label', 'KPI仪表板')
      cy.get('.chart-section').should('have.attr', 'aria-label', '图表区域')
    })

    it('应该支持屏幕阅读器', () => {
      cy.visit('/energy/cockpit')

      // 检查语义化标签
      cy.get('h1').should('exist')
      cy.get('h2').should('have.length.greaterThan', 0)
      cy.get('h3').should('have.length.greaterThan', 0)

      // 检查图表的可访问性
      cy.get('.chart-container').should('have.attr', 'role', 'img')
      cy.get('.chart-container').should('have.attr', 'aria-label')
    })
  })

  describe('跨浏览器兼容性', () => {
    it('应该在Chrome中正常工作', () => {
      cy.visit('/energy/cockpit')

      // 检查Chrome特有功能
      cy.get('.enhanced-kpi-card').should('have.css', 'transform', 'matrix(1, 0, 0, 1, 0, 0)')
    })

    it('应该在Firefox中正常工作', () => {
      cy.visit('/energy/cockpit')

      // 检查Firefox滚动条样式
      cy.get('body').should('have.css', 'scrollbar-width', 'thin')
    })

    it('应该在Safari中正常工作', () => {
      cy.visit('/energy/cockpit')

      // 检查Safari特有功能
      cy.get('.enhanced-button').should('have.css', '-webkit-font-smoothing', 'antialiased')
    })
  })

  describe('错误处理', () => {
    it('应该正确处理网络错误', () => {
      // 模拟网络错误
      cy.intercept('GET', '/api/energy/realtime', { forceNetworkError: true })

      cy.visit('/energy/cockpit')

      // 检查错误处理
      cy.get('.el-message--error').should('be.visible')
      cy.get('.el-message--error').should('contain.text', '数据获取失败')
    })

    it('应该正确处理API超时', () => {
      // 模拟API超时
      cy.intercept('GET', '/api/energy/kpi', { delay: 10000 })

      cy.visit('/energy/cockpit')

      // 检查加载状态
      cy.get('.loading-skeleton').should('be.visible')
    })
  })

  describe('国际化测试', () => {
    it('应该支持中文显示', () => {
      cy.visit('/energy/cockpit')

      // 检查中文文本
      cy.get('.kpi-title').should('contain.text', '总能耗')
      cy.get('.kpi-title').should('contain.text', '实时功率')
      cy.get('.control-group label').should('contain.text', '线路选择')
      cy.get('.control-group label').should('contain.text', '车站选择')
    })
  })
})