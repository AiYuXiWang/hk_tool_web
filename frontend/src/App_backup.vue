<template>
  <div class="app-layout">
    <!-- 应用头部 -->
    <header class="app-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="app-title">
            <el-icon class="title-icon"><Setting /></el-icon>
            环控平台维护工具
          </h1>
          <el-tag class="version-tag" type="info">Web版 v1.0</el-tag>
        </div>
        <div class="header-right">
          <el-tag class="operator-tag" type="success">
            <el-icon><User /></el-icon>
            {{ operatorId }}
          </el-tag>
          <el-button 
            size="small" 
            type="primary" 
            @click="loadDeviceTree()" 
            :loading="loadingTree"
            class="refresh-btn"
          >
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </div>
    </header>

    <!-- 标签页导航 -->
    <nav class="nav-tabs">
      <el-tabs v-model="activeTab" class="main-tabs">
        <el-tab-pane name="device">
          <template #label>
            <span class="tab-label">
              <el-icon><Monitor /></el-icon>
              设备控制
            </span>
          </template>
        </el-tab-pane>
        <el-tab-pane name="export">
          <template #label>
            <span class="tab-label">
              <el-icon><Download /></el-icon>
              数据导出
            </span>
          </template>
        </el-tab-pane>
      </el-tabs>
    </nav>

    <!-- 主要内容区域 -->
    <main class="app-main">
      <!-- 设备控制页面 -->
      <div v-show="activeTab === 'device'" class="device-control-page">
        <div class="device-layout">
          <!-- 左侧设备树面板 -->
          <aside class="device-sidebar">
            <div class="sidebar-header">
              <h3 class="sidebar-title">
                <el-icon><List /></el-icon>
                设备树
              </h3>
              <div class="sidebar-actions">
                <el-button 
                  size="small" 
                  @click="loadDeviceTree()" 
                  :loading="loadingTree" 
                  type="primary"
                  class="action-btn"
                >
                  <el-icon><Refresh /></el-icon>
                </el-button>
                <el-button 
                  size="small" 
                  @click="loadDeviceTree(true)" 
                  :loading="loadingTree" 
                  type="warning"
                  class="action-btn"
                >
                  <el-icon><DataAnalysis /></el-icon>
                  测试
                </el-button>
              </div>
            </div>

            <!-- 筛选和选择器 -->
            <div class="filter-section">
              <div class="search-box">
                <el-input 
                  v-model="filter" 
                  placeholder="搜索设备或点位..."
                  size="small"
                  clearable
                  class="filter-input"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </div>
              
              <div class="selector-group">
                <div class="selector-item">
                  <label class="selector-label">线路</label>
                  <el-select 
                    v-model="selectedLine" 
                    placeholder="选择线路" 
                    size="small" 
                    @change="onLineChange"
                    class="selector"
                  >
                    <el-option 
                      v-for="(stations, line) in lineConfigs" 
                      :key="line" 
                      :label="line" 
                      :value="line" 
                    />
                  </el-select>
                </div>
                
                <div class="selector-item">
                  <label class="selector-label">车站</label>
                  <el-select 
                    v-model="selectedStation" 
                    placeholder="选择车站" 
                    size="small" 
                    @change="onStationChange"
                    class="selector"
                  >
                    <el-option 
                      v-for="st in stationsForLine" 
                      :key="st.station_ip" 
                      :label="st.station_name || st.station_ip" 
                      :value="st.station_ip" 
                    />
                  </el-select>
                </div>
              </div>
            </div>

            <!-- 设备树 -->
            <div class="tree-container">
              <el-scrollbar class="tree-scrollbar">
                <el-tree
                  :data="treeDataFiltered"
                  node-key="id"
                  :props="{ label: 'label', children: 'children' }"
                  highlight-current
                  :default-expanded-keys="defaultExpandedKeys"
                  @node-click="onNodeClick"
                  class="device-tree"
                  v-loading="loadingTree"
                  element-loading-text="加载设备数据..."
                >
                  <template #default="{ node, data }">
                    <div class="tree-node-content">
                      <el-icon v-if="isPointNode(data)" class="node-icon point-icon">
                        <Aim />
                      </el-icon>
                      <el-icon v-else-if="data.meta?.object_type === 'device'" class="node-icon device-icon">
                        <Monitor />
                      </el-icon>
                      <el-icon v-else class="node-icon folder-icon">
                        <Folder />
                      </el-icon>
                      
                      <span 
                        class="node-label"
                        :class="{
                          'exceptional-node': isExceptionalNode(data),
                          'point-node': isPointNode(data),
                          'writable-point': isPointNode(data) && data.meta?.is_writable
                        }"
                        :title="getNodeTooltip(data)"
                      >
                        {{ data.label }}
                      </span>
                      
                      <el-tag 
                        v-if="isPointNode(data) && data.meta?.is_writable" 
                        size="small" 
                        type="success" 
                        class="writable-tag"
                      >
                        可写
                      </el-tag>
                    </div>
                  </template>
                </el-tree>
              </el-scrollbar>
            </div>
          </aside>
          <!-- 主内容区域 -->
          <div class="device-main">
            <!-- 查询控制面板 -->
            <div class="query-panel">
              <div class="panel-header">
                <h3 class="panel-title">
                  <el-icon><Search /></el-icon>
                  实时查询
                </h3>
                <div class="query-actions">
                  <div class="input-group">
                    <div class="input-item">
                      <label class="input-label">设备编码</label>
                      <el-input
                        v-model="query.object_code"
                        placeholder="请输入object_code"
                        size="small"
                        class="query-input"
                        clearable
                      />
                    </div>
                    <div class="input-item">
                      <label class="input-label">点位编码</label>
                      <el-input
                        v-model="query.data_code"
                        placeholder="请输入data_code"
                        size="small"
                        class="query-input"
                        clearable
                      />
                    </div>
                    <el-button 
                      type="primary" 
                      @click="fetchRealtime" 
                      :loading="loadingQuery"
                      :disabled="!query.object_code || !query.data_code"
                      class="query-btn"
                    >
                      <el-icon><Search /></el-icon>
                      查询实时值
                    </el-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 数据显示区域 -->
            <div class="data-display">
              <!-- 实时数据表格 -->
              <div class="data-table-section">
                <div class="section-header">
                  <h4 class="section-title">
                    <el-icon><DataBoard /></el-icon>
                    点位实时数据
                  </h4>
                  <el-button 
                    type="success" 
                    size="small" 
                    @click="openBatch = true"
                    class="action-btn"
                  >
                    <el-icon><Edit /></el-icon>
                    批量写值
                  </el-button>
                </div>
                
                <div class="table-container">
                  <el-table 
                    :data="tableRows" 
                    v-loading="loadingQuery"
                    element-loading-text="正在查询数据..."
                    :height="tableHeight"
                    class="data-table"
                    stripe
                    border
                  >
                    <el-table-column prop="object_code" label="设备编码" width="140" fixed="left">
                      <template #default="{ row }">
                        <el-tag type="info" size="small">{{ row.object_code }}</el-tag>
                      </template>
                    </el-table-column>
                    
                    <el-table-column prop="data_code" label="点位编码" width="160">
                      <template #default="{ row }">
                        <code class="code-text">{{ row.data_code }}</code>
                      </template>
                    </el-table-column>
                    
                    <el-table-column prop="value" label="当前值" width="120" align="center">
                      <template #default="{ row }">
                        <div class="value-cell">
                          <span 
                            class="value-text"
                            :class="{
                              'value-error': row.severity === 'error',
                              'value-warning': row.severity === 'warn',
                              'value-normal': row.severity === 'ok'
                            }"
                          >
                            {{ formatValue(row.value) }}
                          </span>
                          <span v-if="row.unit" class="unit-text">{{ row.unit }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    
                    <el-table-column prop="setpoint" label="设定值" width="120" align="center">
                      <template #default="{ row }">
                        <span 
                          class="setpoint-text"
                          :class="{ 'setpoint-diff': row.setpoint !== null && row.value !== row.setpoint }"
                        >
                          {{ formatValue(row.setpoint) }}
                        </span>
                      </template>
                    </el-table-column>
                    
                    <el-table-column prop="ts" label="更新时间" width="180">
                      <template #default="{ row }">
                        <div class="timestamp-cell">
                          <el-icon><Clock /></el-icon>
                          <span class="timestamp-text">{{ formatTimestamp(row.ts) }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    
                    <el-table-column label="阈值状态" width="120" align="center">
                      <template #default="{ row }">
                        <el-tooltip :content="formatThreshold(row)" placement="top">
                          <el-tag 
                            :type="row.severity === 'error' ? 'danger' : (row.severity === 'warn' ? 'warning' : 'success')"
                            size="small"
                          >
                            {{ getSeverityText(row.severity) }}
                          </el-tag>
                        </el-tooltip>
                      </template>
                    </el-table-column>
                    
                    <el-table-column label="状态" width="100" align="center">
                      <template #default="{ row }">
                        <el-tag 
                          :type="row.status === 'ok' ? 'success' : row.status === 'failed' ? 'danger' : 'info'"
                          size="small"
                        >
                          {{ getStatusText(row.status) }}
                        </el-tag>
                      </template>
                    </el-table-column>
                    
                    <el-table-column label="操作" width="120" align="center" fixed="right">
                      <template #default="{ row }">
                        <el-button 
                          size="small" 
                          type="primary" 
                          @click="refreshRow(row)"
                          class="refresh-btn"
                        >
                          <el-icon><Refresh /></el-icon>
                          刷新
                        </el-button>
                      </template>
                    </el-table-column>
                    
                    <template #empty>
                      <div class="empty-state">
                        <el-icon class="empty-icon"><Search /></el-icon>
                        <p class="empty-text">请选择点位并查询实时数据</p>
                      </div>
                    </template>
                  </el-table>
                </div>
              </div>

              <!-- 实时写值面板 -->
              <div class="write-control-section">
                <div class="section-header">
                  <h4 class="section-title">
                    <el-icon><Edit /></el-icon>
                    实时写值控制
                  </h4>
                  <el-tag 
                    v-if="query.object_code && query.data_code" 
                    type="info" 
                    class="target-tag"
                  >
                    {{ query.object_code }} : {{ query.data_code }}
                  </el-tag>
                </div>
                
                <div class="write-form">
                  <el-form label-width="80px" class="control-form">
                    <el-form-item label="写入值">
                      <div class="write-input-group">
                        <el-input 
                          v-model="singleWriteValue" 
                          placeholder="请输入要写入的值" 
                          class="write-input"
                          clearable
                        >
                          <template #append>
                            <span class="input-unit">
                              {{ getCurrentPointUnit() || '值' }}
                            </span>
                          </template>
                        </el-input>
                      </div>
                    </el-form-item>
                    
                    <el-form-item>
                      <div class="write-actions">
                        <el-button 
                          type="primary" 
                          :disabled="!canSingleWrite" 
                          :loading="loadingSingleWrite" 
                          @click="submitSingleWrite"
                          class="write-btn"
                        >
                          <el-icon><Upload /></el-icon>
                          写入
                        </el-button>
                        <el-button 
                          type="warning" 
                          @click="openBatch = true"
                          class="batch-btn"
                        >
                          <el-icon><Edit /></el-icon>
                          批量写值
                        </el-button>
                      </div>
                    </el-form-item>
                    
                    <el-form-item v-if="singleWriteResult">
                      <el-alert 
                        :title="singleWriteResult.message" 
                        :type="singleWriteResult.success ? 'success' : 'error'" 
                        show-icon 
                        :closable="false"
                        class="write-result"
                      />
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

        <!-- 批量写值对话框 -->
        <el-dialog 
          v-model="openBatch" 
          title="批量写值控制" 
          width="800px"
          class="batch-dialog"
          :close-on-click-modal="false"
        >
          <div class="batch-content">
            <div class="batch-form">
              <h4 class="form-title">
                <el-icon><Edit /></el-icon>
                批量命令编辑
              </h4>
              <p class="form-description">
                请在下方输入框中每行输入一个JSON格式的写值命令，系统将会并发执行所有命令。
              </p>
              
              <el-form label-width="100px">
                <el-form-item label="写值命令">
                  <el-input
                    v-model="batchText"
                    type="textarea"
                    :rows="8"
                    placeholder='请输入JSON格式的写值命令，每行一个：&#10;{"point_key":"shuanfa:ChillerOutTempSetMax","data_source":3,"control_value":"12"}&#10;{"point_key":"test:point1","data_source":3,"control_value":"25"}'
                    class="batch-textarea"
                    show-word-limit
                  />
                </el-form-item>
              </el-form>
              
              <div class="batch-example">
                <h5 class="example-title">命令格式示例：</h5>
                <pre class="example-code">{
  "point_key": "shuanfa:ChillerOutTempSetMax",
  "data_source": 3,
  "control_value": "12",
  "object_code": "shuanfa",
  "data_code": "ChillerOutTempSetMax"
}</pre>
              </div>
            </div>
          </div>
          
          <template #footer>
            <div class="dialog-footer">
              <el-button @click="openBatch = false" class="cancel-btn">
                <el-icon><Close /></el-icon>
                取消
              </el-button>
              <el-button 
                type="primary" 
                :loading="loadingBatch" 
                @click="submitBatch"
                class="submit-btn"
              >
                <el-icon><Upload /></el-icon>
                执行批量写值
              </el-button>
            </div>
          </template>
          
          <!-- 执行结果 -->
          <div v-if="batchResult" class="batch-result">
            <div class="result-summary">
              <el-alert 
                :title="`批量操作完成：总数 ${batchResult.total}，成功 ${batchResult.success}，失败 ${batchResult.failed}`" 
                :type="batchResult.failed > 0 ? 'warning' : 'success'" 
                show-icon
                class="result-alert"
              />
              
              <div class="progress-section">
                <el-progress 
                  :percentage="Math.round((batchProgress / Math.max(batchResult.total, 1)) * 100)"
                  :status="batchResult.failed > 0 ? 'warning' : 'success'"
                  class="batch-progress"
                />
              </div>
            </div>
            
            <div class="result-details">
              <h5 class="details-title">执行详情：</h5>
              <el-table 
                :data="batchResult.items" 
                size="small" 
                class="result-table"
                max-height="300"
                stripe
              >
                <el-table-column prop="point_key" label="点位标识" width="200">
                  <template #default="{ row }">
                    <code class="point-key">{{ row.point_key }}</code>
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="80" align="center">
                  <template #default="{ row }">
                    <el-tag 
                      :type="row.status === 'ok' ? 'success' : 'danger'" 
                      size="small"
                    >
                      {{ row.status === 'ok' ? '成功' : '失败' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="after" label="写入值" width="100" align="center">
                  <template #default="{ row }">
                    <span class="write-value">{{ row.after ?? '-' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="message" label="消息" min-width="150">
                  <template #default="{ row }">
                    <span class="message-text" :class="{ 'error-message': row.status !== 'ok' }">
                      {{ row.message || '执行成功' }}
                    </span>
                  </template>
                </el-table-column>
                <el-table-column prop="duration_ms" label="耗时(ms)" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag type="info" size="small">{{ row.duration_ms || '-' }}</el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </div>
        </el-dialog>
      </div>

      <!-- 数据导出页面 -->
      <div v-show="activeTab === 'export'" class="export-page">
        <div class="export-header">
          <h2 class="page-title">
            <el-icon><Download /></el-icon>
            数据导出中心
          </h2>
        </div>

        <div class="export-content">
          <el-row :gutter="24">
            <!-- 电耗数据导出 -->
            <el-col :span="12">
              <div class="export-card electricity-export">
                <div class="card-header">
                  <h3 class="card-title">
                    <el-icon><Lightning /></el-icon>
                    电耗数据导出
                  </h3>
                </div>
                  
                  <el-form :model="electricityForm" label-width="100px" style="max-width: 500px">
                    <el-form-item label="选择线路">
                      <el-select v-model="electricityForm.line" placeholder="请选择线路" aria-label="电耗导出-选择线路" style="width: 100%">
                        <el-option v-for="line in availableLines" :key="line" :label="line" :value="line" />
                      </el-select>
                    </el-form-item>
                    
                    <el-form-item label="开始时间">
                      <el-date-picker
                        v-model="electricityForm.startTime"
                        type="datetime"
                        placeholder="选择开始时间"
                        aria-label="电耗导出-开始时间"
                        style="width: 100%"
                        format="YYYY-MM-DD HH:mm:ss"
                        value-format="YYYY-MM-DD HH:mm:ss"
                      />
                    </el-form-item>
                    
                    <el-form-item label="结束时间">
                      <el-date-picker
                        v-model="electricityForm.endTime"
                        type="datetime"
                        placeholder="选择结束时间"
                        aria-label="电耗导出-结束时间"
                        style="width: 100%"
                        format="YYYY-MM-DD HH:mm:ss"
                        value-format="YYYY-MM-DD HH:mm:ss"
                      />
                    </el-form-item>
                    
                    <el-form-item>
                      <el-button 
                        type="primary" 
                        @click="exportElectricityData" 
                        :loading="electricityExporting"
                        :disabled="!electricityForm.line || !electricityForm.startTime || !electricityForm.endTime"
                      >
                        <el-icon style="margin-right: 4px;"><Download /></el-icon>
                        导出电耗数据
                      </el-button>
                      <el-button 
                        v-if="electricityExporting" 
                        type="danger" 
                        @click="cancelElectricityExport"
                        size="small"
                      >
                        取消导出
                      </el-button>
                    </el-form-item>
                  </el-form>
                  
                  <!-- 电耗导出状态和结果 -->
                  <div v-if="electricityResult" style="margin-top: 20px;">
                    <el-alert 
                      :title="electricityResult.success ? '导出成功' : '导出失败'" 
                      :type="electricityResult.success ? 'success' : 'error'"
                      :description="electricityResult.message"
                      show-icon
                      :closable="false"
                    />
                    
                    <div v-if="electricityResult.success && electricityResult.details" style="margin-top: 10px;">
                      <el-collapse>
                        <el-collapse-item title="查看详细结果" name="details">
                          <el-table :data="electricityResult.details.results" size="small">
                            <el-table-column prop="station_name" label="车站名称" width="150" />
                            <el-table-column prop="station_ip" label="IP地址" width="120" />
                            <el-table-column label="状态" width="100">
                              <template #default="{ row }">
                                <el-tag :type="row.success ? 'success' : 'danger'">
                                  {{ row.success ? '成功' : '失败' }}
                                </el-tag>
                              </template>
                            </el-table-column>
                            <el-table-column prop="message" label="消息" />
                            <el-table-column label="下载" width="80">
                              <template #default="{ row }">
                                <el-button 
                                  v-if="row.success && row.file_path" 
                                  size="small" 
                                  type="primary" 
                                  @click="downloadFile(row.file_path)"
                                >
                                  下载
                                </el-button>
                              </template>
                            </el-table-column>
                          </el-table>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <!-- 传感器数据导出 -->
              <el-col :span="12">
                <el-card shadow="hover">
                  <template #header>
                    <div style="display: flex; align-items: center;">
                      <el-icon style="margin-right: 8px; font-size: 18px; color: #67C23A;"><Monitor /></el-icon>
                      <span style="font-weight: 600;">传感器数据导出</span>
                    </div>
                  </template>
                  
                  <el-form :model="sensorForm" label-width="100px" style="max-width: 500px">
                    <el-form-item label="选择线路">
                      <el-select v-model="sensorForm.line" placeholder="请选择线路" aria-label="传感器导出-选择线路" style="width: 100%">
                        <el-option v-for="line in availableLines" :key="line" :label="line" :value="line" />
                      </el-select>
                    </el-form-item>
                    
                    <el-form-item label="开始时间">
                      <el-date-picker
                        v-model="sensorForm.startTime"
                        type="datetime"
                        placeholder="选择开始时间"
                        aria-label="传感器导出-开始时间"
                        style="width: 100%"
                        format="YYYY-MM-DD HH:mm:ss"
                        value-format="YYYY-MM-DD HH:mm:ss"
                      />
                    </el-form-item>
                    
                    <el-form-item label="结束时间">
                      <el-date-picker
                        v-model="sensorForm.endTime"
                        type="datetime"
                        placeholder="选择结束时间"
                        aria-label="传感器导出-结束时间"
                        style="width: 100%"
                        format="YYYY-MM-DD HH:mm:ss"
                        value-format="YYYY-MM-DD HH:mm:ss"
                      />
                    </el-form-item>
                    
                    <el-form-item>
                      <el-button 
                        type="success" 
                        @click="exportSensorData" 
                        :loading="sensorExporting"
                        :disabled="!sensorForm.line || !sensorForm.startTime || !sensorForm.endTime"
                      >
                        <el-icon style="margin-right: 4px;"><Download /></el-icon>
                        导出传感器数据
                      </el-button>
                      <el-button 
                        v-if="sensorExporting" 
                        type="danger" 
                        @click="cancelSensorExport"
                        size="small"
                      >
                        取消导出
                      </el-button>
                    </el-form-item>
                  </el-form>
                  
                  <!-- 传感器导出状态和结果 -->
                  <div v-if="sensorResult" style="margin-top: 20px;">
                    <el-alert 
                      :title="sensorResult.success ? '导出成功' : '导出失败'" 
                      :type="sensorResult.success ? 'success' : 'error'"
                      :description="sensorResult.message"
                      show-icon
                      :closable="false"
                    />
                    
                    <div v-if="sensorResult.success && sensorResult.details" style="margin-top: 10px;">
                      <el-collapse>
                        <el-collapse-item title="查看详细结果" name="details">
                          <el-table :data="sensorResult.details.results" size="small">
                            <el-table-column prop="station_name" label="车站名称" width="150" />
                            <el-table-column prop="station_ip" label="IP地址" width="120" />
                            <el-table-column label="状态" width="100">
                              <template #default="{ row }">
                                <el-tag :type="row.success ? 'success' : 'danger'">
                                  {{ row.success ? '成功' : '失败' }}
                                </el-tag>
                              </template>
                            </el-table-column>
                            <el-table-column prop="message" label="消息" />
                            <el-table-column label="下载" width="80">
                              <template #default="{ row }">
                                <el-button 
                                  v-if="row.success && row.file_path" 
                                  size="small" 
                                  type="success" 
                                  @click="downloadFile(row.file_path)"
                                >
                                  下载
                                </el-button>
                              </template>
                            </el-table-column>
                          </el-table>
                        </el-collapse-item>
                      </el-collapse>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <!-- 操作日志 -->
            <el-card style="margin-top: 20px;" shadow="never">
              <template #header>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                  <span style="font-weight: 600;">操作日志</span>
                  <el-button size="small" @click="clearExportLogs">清空日志</el-button>
                </div>
              </template>
              <div 
                ref="exportLogContainer" 
                style="height: 300px; overflow-y: auto; background: #f5f5f5; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 12px;"
              >
                <div v-if="exportLogs.length === 0" style="color: #999; text-align: center; padding: 20px;">
                  暂无日志
                </div>
                <div 
                  v-for="(log, index) in exportLogs" 
                  :key="index" 
                  :style="{
                    color: log.type === 'error' ? '#F56C6C' : log.type === 'success' ? '#67C23A' : log.type === 'warning' ? '#E6A23C' : '#606266',
                    marginBottom: '4px'
                  }"
                >
                  [{{ log.time }}] {{ log.message }}
                </div>
              </div>
            </el-card>
          </el-main>
        </el-container>
      </el-tab-pane>
    </el-tabs>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Lightning, 
  Monitor, 
  Download, 
  Aim,
  Setting,
  User,
  Refresh,
  List,
  DataAnalysis,
  Search,
  Folder,
  Edit,
  Upload,
  Clock,
  DataBoard,
  Close,
  Delete,
  Document
} from '@element-plus/icons-vue'
import { fetchRealtimeValue, batchWritePoints, fetchDeviceTree, getSeverityColor } from './api/control'

const activeTab = ref('device')

/* 线路-车站选择状态与计算 */
const lineConfigs = ref({})
const selectedLine = ref('')
const selectedStation = ref('')
const stationsForLine = computed(() => {
  const arr = lineConfigs.value[selectedLine.value] || []
  return Array.isArray(arr) ? arr : []
})
const tableHeight = computed(() => Math.round(window.innerHeight * 0.42))
const defaultExpandedKeys = ref([])

// 设备控制相关状态
const operatorId = ref('web-admin')
const filter = ref('')
const treeData = ref([])
const pointMeta = ref({})
const loadingTree = ref(false)
const treeDataFiltered = computed(() => {
  const q = filter.value.trim()
  if (!q) return treeData.value
  const match = (node) => node.label.toLowerCase().includes(q.toLowerCase())
  const walk = (nodes) => nodes.map(n => {
    if (!n.children) return match(n) ? n : null
    const kids = walk(n.children).filter(Boolean)
    if (kids.length || match(n)) return { ...n, children: kids }
    return null
  }).filter(Boolean)
  return walk(treeData.value)
})
const exceptionalStations = computed(() => {
  const set = new Set()
  for (const r of tableRows.value) {
    if (r && (r.severity === 'error' || r.status === 'failed')) {
      if (r.object_code) set.add(r.object_code)
    }
  }
  return set
})

// 设备控制功能函数
function isExceptionalNode(data) {
  if (data && data.children) {
    return exceptionalStations.value.has(data.id)
  }
  const oc = data?.meta?.object_code
  return oc ? exceptionalStations.value.has(oc) : false
}

function isPointNode(data) {
  // 判断是否为点位节点：没有children且有data_code
  return !data.children && data.meta && data.meta.data_code
}

function getNodeTooltip(data) {
  if (isPointNode(data)) {
    const meta = data.meta
    const writable = meta.is_writable ? '可写' : '只读'
    const unit = meta.unit ? ` (${meta.unit})` : ''
    return `点位: ${meta.object_code}:${meta.data_code}${unit} - ${writable}\n点击填入查询框`
  }
  return data.meta?.object_name || data.label
}

const query = ref({ object_code: '', data_code: '' })
const loadingQuery = ref(false)
const tableRows = ref([])
const openBatch = ref(false)
const batchText = ref('')
const batchResult = ref(null)
const batchProgress = ref(0)
const loadingBatch = ref(false)

/* 实时写值（右侧面板） */
const singleWriteValue = ref('')
const loadingSingleWrite = ref(false)
const singleWriteResult = ref(null)
const canSingleWrite = computed(() => !!query.value.object_code && !!query.value.data_code && singleWriteValue.value !== '')

async function submitSingleWrite() {
  if (!canSingleWrite.value) return
  loadingSingleWrite.value = true
  singleWriteResult.value = null
  try {
    const k = query.value.object_code + '|' + query.value.data_code
    const meta = pointMeta.value[k] || {}
    const payload = {
      point_key: meta.point_key,
      data_source: 3,
      control_value: singleWriteValue.value,
      object_code: query.value.object_code,
      data_code: query.value.data_code
    }
    const result = await batchWritePoints([payload])
    singleWriteResult.value = {
      success: (result?.success ?? 0) >= 1,
      message: (result?.items?.[0]?.message) || ((result?.success ?? 0) >= 1 ? '写入成功' : '写入失败')
    }
    // 写入成功后刷新实时值
    if (singleWriteResult.value.success) {
      await fetchRealtime()
    }
  } catch (e) {
    singleWriteResult.value = { success: false, message: '写入异常' }
  } finally {
    loadingSingleWrite.value = false
  }
}

// 数据导出相关状态
const availableLines = ref(['M1', 'M11', 'M12', 'M13', 'M14'])
const electricityForm = ref({
  line: '',
  startTime: '',
  endTime: ''
})
const sensorForm = ref({
  line: '',
  startTime: '',
  endTime: ''
})
const electricityExporting = ref(false)
const sensorExporting = ref(false)
const electricityResult = ref(null)
const sensorResult = ref(null)
const exportLogs = ref([])
const exportLogContainer = ref(null)

// 初始化时间范围
function initTimeRange() {
  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0)
  const currentHour = new Date(now.getFullYear(), now.getMonth(), now.getDate(), now.getHours(), 0, 0)
  
  const formatTime = (date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hour = String(date.getHours()).padStart(2, '0')
    const minute = String(date.getMinutes()).padStart(2, '0')
    const second = String(date.getSeconds()).padStart(2, '0')
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`
  }
  
  electricityForm.value.startTime = formatTime(startOfToday)
  electricityForm.value.endTime = formatTime(currentHour)
  sensorForm.value.startTime = formatTime(startOfToday)
  sensorForm.value.endTime = formatTime(currentHour)
}

// 添加导出日志
function addExportLog(message, type = 'info') {
  const now = new Date()
  const timeStr = now.toLocaleTimeString()
  exportLogs.value.push({
    time: timeStr,
    message,
    type
  })
  
  // 自动滚动到底部
  nextTick(() => {
    if (exportLogContainer.value) {
      exportLogContainer.value.scrollTop = exportLogContainer.value.scrollHeight
    }
  })
}

// 清空导出日志
function clearExportLogs() {
  exportLogs.value = []
}

// 导出电耗数据
async function exportElectricityData() {
  electricityExporting.value = true
  electricityResult.value = null
  
  addExportLog(`开始导出电耗数据 - 线路: ${electricityForm.value.line}`, 'info')
  addExportLog(`时间范围: ${electricityForm.value.startTime} 至 ${electricityForm.value.endTime}`, 'info')
  
  try {
    const response = await fetch('/api/export/electricity', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        line: electricityForm.value.line,
        start_time: electricityForm.value.startTime,
        end_time: electricityForm.value.endTime
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      electricityResult.value = result
      
      if (result.success) {
        addExportLog('✅ 电耗数据导出成功!', 'success')
        ElMessage.success('电耗数据导出成功!')
        
        if (result.details && result.details.results) {
          addExportLog(`共处理 ${result.details.results.length} 个站点`, 'info')
          const successCount = result.details.results.filter(r => r.success).length
          const failCount = result.details.results.length - successCount
          addExportLog(`成功: ${successCount}, 失败: ${failCount}`, successCount === result.details.results.length ? 'success' : 'warning')
        }
      } else {
        addExportLog(`❌ 导出失败: ${result.message}`, 'error')
        ElMessage.error(`导出失败: ${result.message}`)
      }
    } else {
      const errorText = await response.text()
      addExportLog(`❌ HTTP请求失败: ${response.status} ${errorText}`, 'error')
      ElMessage.error(`请求失败: ${response.status}`)
    }
  } catch (error) {
    addExportLog(`❌ 请求异常: ${error.message}`, 'error')
    ElMessage.error(`请求异常: ${error.message}`)
    console.error('导出请求错误:', error)
  } finally {
    electricityExporting.value = false
  }
}

// 导出传感器数据
async function exportSensorData() {
  sensorExporting.value = true
  sensorResult.value = null
  
  addExportLog(`开始导出传感器数据 - 线路: ${sensorForm.value.line}`, 'info')
  addExportLog(`时间范围: ${sensorForm.value.startTime} 至 ${sensorForm.value.endTime}`, 'info')
  
  try {
    const response = await fetch('/api/export/sensor', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        line: sensorForm.value.line,
        start_time: sensorForm.value.startTime,
        end_time: sensorForm.value.endTime
      })
    })
    
    if (response.ok) {
      const result = await response.json()
      sensorResult.value = result
      
      if (result.success) {
        addExportLog('✅ 传感器数据导出成功!', 'success')
        ElMessage.success('传感器数据导出成功!')
        
        if (result.details && result.details.results) {
          addExportLog(`共处理 ${result.details.results.length} 个站点`, 'info')
          const successCount = result.details.results.filter(r => r.success).length
          const failCount = result.details.results.length - successCount
          addExportLog(`成功: ${successCount}, 失败: ${failCount}`, successCount === result.details.results.length ? 'success' : 'warning')
        }
      } else {
        addExportLog(`❌ 导出失败: ${result.message}`, 'error')
        ElMessage.error(`导出失败: ${result.message}`)
      }
    } else {
      const errorText = await response.text()
      addExportLog(`❌ HTTP请求失败: ${response.status} ${errorText}`, 'error')
      ElMessage.error(`请求失败: ${response.status}`)
    }
  } catch (error) {
    addExportLog(`❌ 请求异常: ${error.message}`, 'error')
    ElMessage.error(`请求异常: ${error.message}`)
    console.error('导出请求错误:', error)
  } finally {
    sensorExporting.value = false
  }
}

// 取消导出操作
function cancelElectricityExport() {
  electricityExporting.value = false
  addExportLog('🚫 用户取消了电耗数据导出操作', 'warning')
  ElMessage.warning('已取消导出操作')
}

function cancelSensorExport() {
  sensorExporting.value = false
  addExportLog('🚫 用户取消了传感器数据导出操作', 'warning')
  ElMessage.warning('已取消导出操作')
}

// 下载文件
function downloadFile(filePath) {
  const filename = filePath.split('/').pop()
  const downloadUrl = `/api/download/${filename}`
  
  addExportLog(`📥 开始下载文件: ${filename}`, 'info')
  
  // 创建下载链接
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  addExportLog(`✅ 文件下载已启动: ${filename}`, 'success')
}

// 挂载时初始化
onMounted(async () => {
  // 拉取线路-车站配置后再加载树
  try {
    const resp = await fetch('/api/config/line_configs')
    if (resp.ok) {
      const conf = await resp.json()
      lineConfigs.value = conf || {}
      const firstLine = Object.keys(lineConfigs.value)[0]
      if (firstLine) {
        selectedLine.value = firstLine
        const stations = lineConfigs.value[firstLine] || []
        const firstStation = stations[0]
        if (firstStation && firstStation.station_ip) {
          selectedStation.value = firstStation.station_ip
        }
      }
    }
  } catch (e) {
    console.debug('line_configs fetch failed', e)
  }

  await loadDeviceTree()
  initTimeRange()

  // 无障碍标签 DOM 补丁（安全选择器与防御性赋值）
  setTimeout(() => {
    try {
      document.querySelectorAll('.el-select input').forEach(inner => {
        if (inner && !inner.getAttribute('aria-label')) {
          inner.setAttribute('aria-label', '选择线路')
        }
      })
      document.querySelectorAll('.el-date-editor input').forEach(inner => {
        if (inner && !inner.getAttribute('aria-label')) {
          inner.setAttribute('aria-label', '选择时间')
        }
      })
    } catch (e) {
      console.debug('ARIA patch failed:', e)
    }
  }, 0)
})

function normalizeTree(rawNodes) {
  const mapNode = (n) => {
    if (!n || typeof n !== 'object') return null
    const label = n.label ?? n.name ?? n.title ?? (n.meta?.object_name ?? n.meta?.data_name) ?? ''
    const childrenRaw = n.children ?? n.nodes ?? n.items ?? null
    const id =
      n.id ??
      n.meta?.point_key ??
      (n.meta?.object_code && n.meta?.data_code ? `${n.meta.object_code}|${n.meta.data_code}` : n.meta?.object_code) ??
      label
    const meta = n.meta ?? {
      object_code: n.object_code ?? n.meta?.object_code ?? '',
      data_code: n.data_code ?? n.meta?.data_code ?? undefined,
      unit: n.unit ?? n.meta?.unit ?? undefined,
      is_writable: n.is_writable ?? n.meta?.is_writable ?? false,
      point_key: n.point_key ?? n.meta?.point_key ?? undefined,
      data_type: n.data_type ?? n.meta?.data_type ?? undefined,
      border_min: n.border_min ?? n.meta?.border_min ?? null,
      border_max: n.border_max ?? n.meta?.border_max ?? null,
      warn_min: n.warn_min ?? n.meta?.warn_min ?? null,
      warn_max: n.warn_max ?? n.meta?.warn_max ?? null,
      error_min: n.error_min ?? n.meta?.error_min ?? null,
      error_max: n.error_max ?? n.meta?.error_max ?? null
    }
    const node = { id: String(id), label: String(label), meta }
    if (Array.isArray(childrenRaw) && childrenRaw.length) {
      node.children = childrenRaw.map(mapNode).filter(Boolean)
    }
    return node
  }
  const input = Array.isArray(rawNodes) ? rawNodes : []
  return input.map(mapNode).filter(Boolean)
}

async function loadDeviceTree(forceTest = false) {
  loadingTree.value = true
  try {
    const res = await fetchDeviceTree(
      forceTest ? { forceTest: true } :
      (selectedStation.value ? { station_ip: selectedStation.value } : undefined)
    )
    const source = Array.isArray(res) ? res : (res.tree || [])
    const nodes = normalizeTree(source)
    console.debug('[tree] source_len=', source.length, 'nodes_len=', nodes.length, 'first_raw=', source[0], 'first_node=', nodes[0])
    if (forceTest) {
      ElMessage.success('已切换为测试树数据')
    }
    
    // 构建点位元数据映射
    const meta = {}
    
    function extractPointMeta(treeNodes) {
      for (const node of treeNodes) {
        if (node.children) {
          extractPointMeta(node.children)
        } else if (node.meta && node.meta.data_code) {
          // 这是一个点位节点
          const k = node.meta.object_code + '|' + node.meta.data_code
          meta[k] = {
            unit: node.meta.unit || '',
            border_min: node.meta.border_min,
            border_max: node.meta.border_max,
            warn_min: node.meta.warn_min,
            warn_max: node.meta.warn_max,
            error_min: node.meta.error_min,
            error_max: node.meta.error_max,
            is_writable: node.meta.is_writable || false,
            point_key: node.meta.point_key,
            data_type: node.meta.data_type
          }
        }
      }
    }
    
    extractPointMeta(nodes)
    pointMeta.value = meta
    treeData.value = nodes

    // 计算默认展开到一级的 keys
    defaultExpandedKeys.value = nodes.map(n => String(n.id))
    
    console.log('设备树加载完成，节点数量:', nodes.length, '点位元数据:', Object.keys(meta).length)
  } catch (error) {
    console.error('加载设备树失败:', error)
    ElMessage.error('加载设备树失败')
  } finally {
    loadingTree.value = false
  }
}

function onLineChange() {
  const stations = lineConfigs.value[selectedLine.value] || []
  const firstStation = stations[0]
  selectedStation.value = firstStation && firstStation.station_ip ? firstStation.station_ip : ''
  // 重新加载对应车站的树数据
  loadDeviceTree(false)
}
function onStationChange() {
  if (selectedStation.value) {
    // 重新加载对应车站的树数据
    loadDeviceTree(false)
  }
}

function onNodeClick(node) {
  // 只有点位节点（有data_code的叶子节点）才可以点击填入
  if (!node.children && node.meta?.data_code) {
    const oc = node.meta.object_code
    const dc = node.meta.data_code
    query.value = { object_code: oc, data_code: dc }
    ElMessage.success(`已填入: ${oc}:${dc}`)
  }
}

async function fetchRealtime() {
  if (!query.value.object_code || !query.value.data_code) return
  loadingQuery.value = true
  const oc = query.value.object_code
  const dc = query.value.data_code
  try {
    const d = await fetchRealtimeValue(query.value.object_code, query.value.data_code)
    const k = oc + '|' + dc
    const meta = pointMeta.value[k] || {}
    const sev = typeof d.value === 'number'
      ? getSeverityColor(d.value, meta.warn_min ?? null, meta.warn_max ?? null, meta.error_min ?? null, meta.error_max ?? null)
      : 'ok'
    tableRows.value = [{
      object_code: d.object_code,
      data_code: d.data_code,
      value: d.value ?? null,
      setpoint: null,
      unit: d.unit ?? meta.unit ?? '',
      ts: d.ts,
      status: 'ok',
      severity: sev
    }]
  } catch (e) {
    tableRows.value = [{
      object_code: query.value.object_code,
      data_code: query.value.data_code,
      value: null,
      setpoint: null,
      unit: '',
      ts: new Date().toISOString(),
      status: 'failed',
      severity: 'error'
    }]
  } finally {
    loadingQuery.value = false
  }
}

async function refreshRow(row) {
  query.value = { object_code: row.object_code, data_code: row.data_code }
  await fetchRealtime()
}

// 格式化工具函数
function formatValue(value) {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return Number.isInteger(value) ? value.toString() : value.toFixed(2)
  }
  return String(value)
}

function formatTimestamp(ts) {
  if (!ts) return '-'
  try {
    const date = new Date(ts)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return ts
  }
}

function getSeverityText(severity) {
  const textMap = {
    'ok': '正常',
    'warn': '警告', 
    'error': '异常'
  }
  return textMap[severity] || '未知'
}

function getStatusText(status) {
  const textMap = {
    'ok': '成功',
    'failed': '失败',
    'pending': '等待'
  }
  return textMap[status] || '未知'
}

function getCurrentPointUnit() {
  const oc = query.value.object_code
  const dc = query.value.data_code
  if (!oc || !dc) return ''
  const k = oc + '|' + dc
  const meta = pointMeta.value[k] || {}
  return meta.unit || ''
}
function formatThreshold(row) {
  const k = row.object_code + '|' + row.data_code
  const m = pointMeta.value[k] || {}
  const wm = m.warn_min ?? '-'
  const wM = m.warn_max ?? '-'
  const em = m.error_min ?? '-'
  const eM = m.error_max ?? '-'
  const bm = m.border_min ?? '-'
  const bM = m.border_max ?? '-'
  return `warn[${wm},${wM}] error[${em},${eM}] border[${bm},${bM}]`
}

async function submitBatch() {
  let cmds = []
  try {
    cmds = batchText.value
      .split('\n')
      .map(l => l.trim())
      .filter(Boolean)
      .map(l => JSON.parse(l))
  } catch (e) {
    return ElMessage.error('JSON 行解析失败，请检查格式')
  }
  if (!cmds.length) return
  loadingBatch.value = true
  batchProgress.value = 0
  try {
    const result = await batchWritePoints(cmds)
    batchResult.value = result
    // 进度细化：以成功条目数作为进度
    batchProgress.value = result?.success ?? 0
  } catch (e) {
    batchResult.value = { total: 0, success: 0, failed: 0, items: [] }
  } finally {
    loadingBatch.value = false
  }
}
</script>

<style>
html, body, #app { height: 100%; margin: 0; }
/* 设备总览两列布局修复 */
.device-split {
  display: flex;
  height: 100%;
}
.device-split .el-aside {
  flex: 0 0 320px;
  max-width: 320px;
  min-width: 320px;
  overflow: auto;
  border-right: 1px solid #eee;
}
.device-split .el-container {
  flex: 1;
  min-width: 0;
  overflow: hidden;
}
.device-split .el-main {
  overflow: hidden; /* 外层隐藏，内部网格自行滚动 */
}
.device-split .tree-scroll {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: auto;
}
/* Tabs 内容区域高度链补齐，确保左侧树容器有约束高度 */
.el-tabs { height: 100%; }
.el-tabs__content { height: 100%; display: flex; }
.el-tab-pane { height: 100%; }

/* 侧栏高度约束，保证 .tree-scroll 的 flex:1 生效 */
.device-split .el-aside {
  height: 100%;
}

</style>