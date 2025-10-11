<template>
  <div class="data-export-view">
    <div class="export-header">
      <h2 class="page-title">
        <el-icon><Download /></el-icon>
        数据导出中心
      </h2>
      <p class="page-description">支持电耗数据和传感器数据的批量导出，可按线路和时间范围筛选</p>
    </div>

    <div class="export-layout">
      <div class="export-main">
        <el-tabs v-model="exportActiveTab" class="export-main-tabs">
          <!-- 电耗数据导出 -->
          <el-tab-pane name="electricity" label="电耗数据导出">
            <div class="export-form-container">
              <el-card class="export-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon><Lightning /></el-icon>
                      电耗数据导出
                    </span>
                  </div>
                </template>

                <el-form :model="electricityForm" label-width="100px" size="default">
                  <el-form-item label="选择线路">
                    <el-select 
                      v-model="electricityForm.line" 
                      placeholder="请选择线路" 
                      style="width: 200px"
                    >
                      <el-option 
                        v-for="line in availableLines" 
                        :key="line" 
                        :label="line" 
                        :value="line" 
                      />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="开始时间">
                    <el-date-picker
                      v-model="electricityForm.start_time"
                      type="datetime"
                      placeholder="选择开始时间"
                      format="YYYY-MM-DD HH:mm:ss"
                      value-format="YYYY-MM-DD HH:mm:ss"
                    />
                  </el-form-item>

                  <el-form-item label="结束时间">
                    <el-date-picker
                      v-model="electricityForm.end_time"
                      type="datetime"
                      placeholder="选择结束时间"
                      format="YYYY-MM-DD HH:mm:ss"
                      value-format="YYYY-MM-DD HH:mm:ss"
                    />
                  </el-form-item>

                  <el-form-item>
                    <el-button 
                      type="primary" 
                      @click="exportElectricityDataAction" 
                      :loading="electricityExporting"
                      :disabled="!electricityForm.line || !electricityForm.start_time || !electricityForm.end_time"
                      size="default"
                    >
                      <el-icon><Download /></el-icon>
                      开始导出
                    </el-button>
                    <el-button 
                      v-if="electricityExporting" 
                      @click="cancelElectricityExport"
                      type="warning"
                    >
                      取消导出
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </div>
          </el-tab-pane>

          <!-- 传感器数据导出 -->
          <el-tab-pane name="sensor" label="传感器数据导出">
            <div class="export-form-container">
              <el-card class="export-card">
                <template #header>
                  <div class="card-header">
                    <span class="card-title">
                      <el-icon><Monitor /></el-icon>
                      传感器数据导出
                    </span>
                  </div>
                </template>

                <el-form :model="sensorForm" label-width="100px" size="default">
                  <el-form-item label="选择线路">
                    <el-select 
                      v-model="sensorForm.line" 
                      placeholder="请选择线路" 
                      style="width: 200px"
                    >
                      <el-option 
                        v-for="line in availableLines" 
                        :key="line" 
                        :label="line" 
                        :value="line" 
                      />
                    </el-select>
                  </el-form-item>

                  <el-form-item label="开始时间">
                    <el-date-picker
                      v-model="sensorForm.start_time"
                      type="datetime"
                      placeholder="选择开始时间"
                      format="YYYY-MM-DD HH:mm:ss"
                      value-format="YYYY-MM-DD HH:mm:ss"
                    />
                  </el-form-item>

                  <el-form-item label="结束时间">
                    <el-date-picker
                      v-model="sensorForm.end_time"
                      type="datetime"
                      placeholder="选择结束时间"
                      format="YYYY-MM-DD HH:mm:ss"
                      value-format="YYYY-MM-DD HH:mm:ss"
                    />
                  </el-form-item>

                  <el-form-item>
                    <el-button 
                      type="primary" 
                      @click="exportSensorDataAction" 
                      :loading="sensorExporting"
                      :disabled="!sensorForm.line || !sensorForm.start_time || !sensorForm.end_time"
                      size="default"
                    >
                      <el-icon><Download /></el-icon>
                      开始导出
                    </el-button>
                    <el-button 
                      v-if="sensorExporting" 
                      @click="cancelSensorExport"
                      type="warning"
                    >
                      取消导出
                    </el-button>
                  </el-form-item>
                </el-form>
              </el-card>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <div class="export-logs">
        <el-card class="logs-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">
                <el-icon><Document /></el-icon>
                操作日志
              </span>
              <el-button 
                size="small" 
                @click="clearExportLogs"
                :disabled="exportLogs.length === 0"
              >
                <el-icon><Delete /></el-icon>
                清空
              </el-button>
            </div>
          </template>
          <div ref="exportLogContainer" class="logs-container">
            <div 
              v-for="(log, index) in exportLogs" 
              :key="index" 
              class="log-item"
              :class="{
                'log-success': log.type === 'success',
                'log-error': log.type === 'error',
                'log-warning': log.type === 'warning',
                'log-info': log.type === 'info'
              }"
            >
              <span class="log-time">{{ log.time }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            <div v-if="exportLogs.length === 0" class="empty-logs">
              <el-icon><Document /></el-icon>
              <p>暂无操作日志</p>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
  
</template>

<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Download, Lightning, Monitor, Delete, Document } from '@element-plus/icons-vue'
import { exportElectricityData, exportSensorData, fetchLineConfigs } from '../api/control'

const exportActiveTab = ref('electricity')

// 线路配置与可选线路
const lineConfigs = ref({})
const availableLines = computed(() => {
  const lineNames = Object.keys(lineConfigs.value || {})
  return lineNames.filter(name => /^M\d+$/.test(name))
})

// 表单与状态
const electricityForm = ref({
  line: '',
  start_time: null,
  end_time: null
})
const sensorForm = ref({
  line: '',
  start_time: null,
  end_time: null
})
const electricityExporting = ref(false)
const sensorExporting = ref(false)
const exportLogs = ref([])
const exportLogContainer = ref(null)

function addExportLog(message, type = 'info') {
  const now = new Date()
  const timeStr = now.toLocaleTimeString()
  exportLogs.value.push({ time: timeStr, message, type })
  if (exportLogs.value.length > 100) {
    exportLogs.value = exportLogs.value.slice(-100)
  }
  nextTick(() => {
    if (exportLogContainer.value) {
      exportLogContainer.value.scrollTop = exportLogContainer.value.scrollHeight
    }
  })
}

function clearExportLogs() {
  exportLogs.value = []
  ElMessage.success('日志已清空')
}

function downloadFile(filePath) {
  if (!filePath) return
  const filename = filePath.split('/').pop()
  const downloadUrl = `/api/download/${filename}`
  const link = document.createElement('a')
  link.href = downloadUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function exportElectricityDataAction() {
  if (!electricityForm.value.line || !electricityForm.value.start_time || !electricityForm.value.end_time) {
    ElMessage.warning('请填写完整的导出参数')
    return
  }
  electricityExporting.value = true
  const request = { ...electricityForm.value }
  addExportLog(`🚀 开始导出电耗数据: 线路=${request.line}, 时间=${request.start_time} 至 ${request.end_time}`, 'info')
  try {
    const result = await exportElectricityData(request)
    if (result.success) {
      addExportLog(`✅ 电耗数据导出成功: ${result.message}`, 'success')
      if (result.details && result.details.results) {
        result.details.results.forEach(station => {
          if (station.success) {
            addExportLog(`✓ ${station.station_name} (${station.station_ip}): 导出成功`, 'success')
            if (station.file_path) {
              addExportLog(`└─ 文件: ${station.file_path}，已开始下载到本地`, 'info')
              downloadFile(station.file_path)
            }
          } else {
            addExportLog(`❌ ${station.station_name} (${station.station_ip}): ${station.message}`, 'error')
          }
        })
      }
    } else {
      addExportLog(`❌ 电耗数据导出失败: ${result.message}`, 'error')
      ElMessage.error(`导出失败: ${result.message}`)
    }
  } catch (error) {
    addExportLog(`❌ 导出请求失败: ${error.message}`, 'error')
    ElMessage.error(`导出请求失败: ${error.message}`)
    console.error('导出电耗数据错误:', error)
  } finally {
    electricityExporting.value = false
  }
}

async function exportSensorDataAction() {
  if (!sensorForm.value.line || !sensorForm.value.start_time || !sensorForm.value.end_time) {
    ElMessage.warning('请填写完整的导出参数')
    return
  }
  sensorExporting.value = true
  const request = { ...sensorForm.value }
  addExportLog(`🚀 开始导出传感器数据: 线路=${request.line}, 时间=${request.start_time} 至 ${request.end_time}`, 'info')
  try {
    const result = await exportSensorData(request)
    if (result.success) {
      addExportLog(`✅ 传感器数据导出成功: ${result.message}`, 'success')
      if (result.details && result.details.results) {
        result.details.results.forEach(station => {
          if (station.success) {
            addExportLog(`✓ ${station.station_name} (${station.station_ip}): 导出成功`, 'success')
            if (station.file_path) {
              addExportLog(`└─ 文件: ${station.file_path}，已开始下载到本地`, 'info')
              downloadFile(station.file_path)
            }
          } else {
            addExportLog(`❌ ${station.station_name} (${station.station_ip}): ${station.message}`, 'error')
          }
        })
      }
    } else {
      addExportLog(`❌ 传感器数据导出失败: ${result.message}`, 'error')
      ElMessage.error(`导出失败: ${result.message}`)
    }
  } catch (error) {
    addExportLog(`❌ 导出请求失败: ${error.message}`, 'error')
    ElMessage.error(`导出请求失败: ${error.message}`)
    console.error('导出传感器数据错误:', error)
  } finally {
    sensorExporting.value = false
  }
}

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

onMounted(async () => {
  try {
    const conf = await fetchLineConfigs()
    lineConfigs.value = conf || {}
  } catch (e) {
    console.debug('fetchLineConfigs failed', e)
  }
})
</script>

<style scoped>
.data-export-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.export-header {
  padding: 8px 0;
}

.page-title {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-description {
  margin: 4px 0 0 0;
  color: #606266;
  font-size: 13px;
}

.export-layout {
  display: flex;
  gap: 16px;
}

.export-main {
  flex: 1;
}

.export-card .el-form {
  padding: 16px 0;
}

.export-card .el-form-item {
  margin-bottom: 24px;
}

.export-card .el-form-item__label {
  font-weight: 500;
  color: #333;
}

.export-card .el-select,
.export-card .el-date-editor {
  width: 100%;
  max-width: 300px;
}

.export-card .el-button {
  margin-right: 12px;
  padding: 10px 20px;
}

.export-logs {
  flex-shrink: 0;
  width: 340px;
  flex: 0 0 340px;
}

.logs-container {
  max-height: 420px;
  overflow-y: auto;
}

.log-item {
  display: flex;
  gap: 8px;
  font-size: 12px;
  padding: 4px 0;
}

.log-success { color: #67C23A; }
.log-error { color: #F56C6C; }
.log-warning { color: #E6A23C; }
.log-info { color: #606266; }

.empty-logs {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: #909399;
}
</style>