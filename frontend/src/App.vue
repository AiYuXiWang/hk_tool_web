<template>
  <div id="app">
    <el-config-provider :locale="zhCn">
      <el-container>
        <el-header>
          <h1>环控平台维护工具Web版</h1>
        </el-header>
        <el-main>
        <el-tabs v-model="activeTab">
          <!-- 电耗数据导出标签页 -->
          <el-tab-pane label="电耗数据导出" name="electricity">
            <el-form :model="electricityForm" label-width="120px" style="max-width: 600px;">
              <el-form-item label="选择线路">
                <el-select v-model="electricityForm.line" placeholder="请选择线路" style="width: 100%;">
                  <el-option
                    v-for="line in lines"
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
                  style="width: 100%;"
                  format="YYYY年MM月DD日 HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  :teleported="false"
                />
              </el-form-item>
              
              <el-form-item label="结束时间">
                <el-date-picker
                  v-model="electricityForm.end_time"
                  type="datetime"
                  placeholder="选择结束时间"
                  style="width: 100%;"
                  format="YYYY年MM月DD日 HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  :teleported="false"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="exportElectricityData" 
                  :loading="isExportingElectricity"
                >
                  导出电耗数据
                </el-button>
                <el-button @click="resetElectricityForm">重置</el-button>
                <el-button 
                  v-if="isExportingElectricity" 
                  type="danger" 
                  size="small" 
                  @click="forceResetExportState"
                  style="margin-left: 10px;"
                >
                  紧急停止
                </el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
          
          <!-- 传感器数据导出标签页 -->
          <el-tab-pane label="传感器数据导出" name="sensor">
            <el-form :model="sensorForm" label-width="120px" style="max-width: 600px;">
              <el-form-item label="选择线路">
                <el-select v-model="sensorForm.line" placeholder="请选择线路" style="width: 100%;">
                  <el-option
                    v-for="line in lines"
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
                  style="width: 100%;"
                  format="YYYY年MM月DD日 HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  :teleported="false"
                />
              </el-form-item>
              
              <el-form-item label="结束时间">
                <el-date-picker
                  v-model="sensorForm.end_time"
                  type="datetime"
                  placeholder="选择结束时间"
                  style="width: 100%;"
                  format="YYYY年MM月DD日 HH:mm:ss"
                  value-format="YYYY-MM-DD HH:mm:ss"
                  :teleported="false"
                />
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="exportSensorData" 
                  :loading="isExportingSensor"
                >
                  导出传感器数据
                </el-button>
                <el-button @click="resetSensorForm">重置</el-button>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
        
        <!-- 导出结果展示 -->
        <el-card v-if="exportResult" style="margin-top: 20px;">
          <h3>导出结果</h3>
          <p :class="exportResult.success ? 'success' : 'error'">
            {{ exportResult.message }}
          </p>
          
          <div v-if="exportResult.details">
            <p>总计: {{ exportResult.details.total }} 个站点</p>
            <p>成功: {{ exportResult.details.success_count }} 个</p>
            <p>失败: {{ exportResult.details.fail_count }} 个</p>
            
            <el-table :data="exportResult.details.results" style="width: 100%; margin-top: 20px;">
              <el-table-column prop="station_name" label="站点名称" width="150" />
              <el-table-column prop="station_ip" label="IP地址" width="150" />
              <el-table-column label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.success ? 'success' : 'danger'">
                    {{ scope.row.success ? '成功' : '失败' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="message" label="信息" />
              <el-table-column label="操作" width="100">
                <template #default="scope">
                  <el-button 
                    v-if="scope.row.file_path && scope.row.success"
                    size="small" 
                    type="primary" 
                    @click="downloadFile(scope.row.file_path)"
                  >
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
        
        <!-- 日志输出 -->
        <el-card style="margin-top: 20px;" v-if="logs.length > 0">
          <h3>操作日志</h3>
          <el-scrollbar height="200px">
            <div v-for="(log, index) in logs" :key="index" class="log-item">
              [{{ log.time }}] {{ log.message }}
            </div>
          </el-scrollbar>
        </el-card>
        </el-main>
      </el-container>
    </el-config-provider>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

// 配置axios超时时间，确保有足够时间接收长时间运行的导出操作响应
axios.defaults.timeout = 300000  // 5分钟超时

export default {
  name: 'App',
  setup() {
    // Element Plus 中文本地化
    const locale = zhCn
    
    // 当前激活的标签页
    const activeTab = ref('electricity')
    
    // 线路列表
    const lines = ref([])
    
    // 电耗数据表单
    const electricityForm = ref({
      line: '',
      start_time: '',
      end_time: ''
    })
    
    // 传感器数据表单
    const sensorForm = ref({
      line: '',
      start_time: '',
      end_time: ''
    })
    
    // 导出状态
    const isExportingElectricity = ref(false)
    const isExportingSensor = ref(false)
    
    // 导出结果
    const exportResult = ref(null)
    
    // 日志
    const logs = ref([])
    
    // 添加日志（增强版，确保状态立即同步）
    const addLog = (message) => {
      logs.value.push({
        time: new Date().toLocaleString(),
        message: message
      })
      
      // 强制更新DOM以确保日志立即显示
      nextTick(() => {
        const logContainer = document.querySelector('.el-scrollbar__wrap')
        if (logContainer) {
          logContainer.scrollTop = logContainer.scrollHeight
        }
        // 强制Vue重新渲染（确保状态同步）
        console.log('日志已添加并滚动到底部:', message)
      })
    }
    
    // 获取线路列表
    const fetchLines = async () => {
      try {
        const response = await axios.get('/api/lines')
        lines.value = response.data.lines
        addLog('获取线路列表成功')
      } catch (error) {
        addLog(`获取线路列表失败: ${error.message}`)
      }
    }
    
    // 获取今天0点的时间字符串
    const getTodayStart = () => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day} 00:00:00`
    }
    
    // 获取当前小时00分00秒的时间字符串
    const getCurrentHour = () => {
      const now = new Date()
      now.setMinutes(0, 0, 0)
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      const hour = String(now.getHours()).padStart(2, '0')
      return `${year}-${month}-${day} ${hour}:00:00`
    }
    
    // 重置电耗数据表单
    const resetElectricityForm = () => {
      electricityForm.value = {
        line: lines.value.length > 0 ? lines.value[0] : '',
        start_time: getTodayStart(),
        end_time: getCurrentHour()
      }
      addLog('✅ 电耗数据表单已重置为默认值')
    }
    
    // 重置传感器数据表单
    const resetSensorForm = () => {
      sensorForm.value = {
        line: lines.value.length > 0 ? lines.value[0] : '',
        start_time: getTodayStart(),
        end_time: getCurrentHour()
      }
      addLog('✅ 传感器数据表单已重置为默认值')
    }
    
    // 导出电耗数据（增强状态同步版本）
    const exportElectricityData = async () => {
      if (!electricityForm.value.line) {
        addLog('请选择线路')
        return
      }
      
      if (!electricityForm.value.start_time || !electricityForm.value.end_time) {
        addLog('请选择时间范围')
        return
      }
      
      let requestCompleted = false
      
      try {
        isExportingElectricity.value = true
        exportResult.value = null  // 清空之前的结果
        addLog('开始导出电耗数据...')
        addLog(`选择线路: ${electricityForm.value.line}`)
        addLog(`时间范围: ${electricityForm.value.start_time} 至 ${electricityForm.value.end_time}`)
        addLog('正在向后端发送导出请求...')
        
        console.log('前端开始发送导出请求，按钮状态:', isExportingElectricity.value)
        
        const response = await axios.post('/api/export/electricity', electricityForm.value, {
          timeout: 300000,  // 5分钟超时
          onUploadProgress: () => {
            console.log('请求正在发送中...')
          },
          onDownloadProgress: () => {
            console.log('正在接收响应...')
          }
        })
        
        requestCompleted = true
        addLog('✅ 后端响应接收完成，正在处理结果...')
        console.log('电耗数据导出 - 接收到后端响应:', response.data)
        exportResult.value = response.data
        
        // 强制状态更新
        await nextTick()
        
        // 添加详细的结果日志
        if (response.data.success && response.data.details) {
          const { total, success_count, fail_count, results } = response.data.details
          
          addLog('')  // 空行分隔
          addLog('=== 导出结果统计 ===')
          addLog(`总计站点: ${total} 个`)
          addLog(`成功: ${success_count} 个`)
          addLog(`失败: ${fail_count} 个`)
          
          if (results && results.length > 0) {
            addLog('')
            addLog('=== 详细导出状态 ===')
            results.forEach(result => {
              if (result.success) {
                addLog(`✓ ${result.station_name} (${result.station_ip}) - 导出成功`)
              } else {
                addLog(`✗ ${result.station_name} (${result.station_ip}) - 导出失败: ${result.message}`)
              }
            })
          }
          
          addLog('')
          addLog('=== 电耗数据导出完成 ===')
        } else {
          addLog(response.data.message || '导出操作完成')
        }
        
        // 确保状态同步更新
        addLog('✅ 电耗数据导出任务已全部完成')
        
      } catch (error) {
        console.error('导出电耗数据错误:', error)
        let errorMessage = '未知错误'
        if (error.code === 'ECONNABORTED') {
          errorMessage = '请求超时，请检查网络连接或联系管理员'
          addLog('⚠️ 检测到请求超时，可能是网络问题导致前端无法接收完整响应')
        } else if (error.response) {
          errorMessage = `服务器错误: ${error.response.status} - ${error.response.data?.message || error.message}`
        } else if (error.request) {
          errorMessage = '网络连接失败，请检查网络设置'
          addLog('⚠️ 网络连接问题，请检查前后端服务是否正常运行')
        } else {
          errorMessage = error.message
        }
        addLog(`导出电耗数据失败: ${errorMessage}`)
        exportResult.value = {
          success: false,
          message: `导出失败: ${errorMessage}`
        }
      } finally {
        // 强制重置按钮状态，确保用户能立即看到完成状态
        console.log('开始重置按钮状态，请求是否完成:', requestCompleted)
        isExportingElectricity.value = false
        
        // 强制DOM更新
        await nextTick()
        
        console.log('按钮状态已重置:', isExportingElectricity.value)
        addLog('🔄 电耗数据导出操作已完成，可以进行下次操作')
        
        // 额外的状态检查和修复
        setTimeout(() => {
          if (isExportingElectricity.value) {
            console.warn('检测到按钮状态未正确重置，强制修复')
            isExportingElectricity.value = false
          }
        }, 1000)
      }
    }
    
    // 导出传感器数据
    const exportSensorData = async () => {
      if (!sensorForm.value.line) {
        addLog('请选择线路')
        return
      }
      
      if (!sensorForm.value.start_time || !sensorForm.value.end_time) {
        addLog('请选择时间范围')
        return
      }
      
      try {
        isExportingSensor.value = true
        exportResult.value = null  // 清空之前的结果
        addLog('开始导出传感器数据...')
        addLog(`选择线路: ${sensorForm.value.line}`)
        addLog(`时间范围: ${sensorForm.value.start_time} 至 ${sensorForm.value.end_time}`)
        addLog('正在向后端发送导出请求...')
        
        const response = await axios.post('/api/export/sensor', sensorForm.value, {
          timeout: 300000  // 5分钟超时，确保能接收完整响应
        })
        
        addLog('后端响应接收完成，正在处理结果...')
        console.log('传感器数据导出 - 接收到后端响应:', response.data)
        exportResult.value = response.data
        
        // 立即更新状态，确保前端同步
        await nextTick()  // 强制DOM更新
        
        // 添加详细的结果日志
        if (response.data.success && response.data.details) {
          const { total, success_count, fail_count, results } = response.data.details
          
          addLog('')  // 空行分隔
          addLog('=== 传感器数据导出结果统计 ===')
          addLog(`总计站点: ${total} 个`)
          addLog(`成功: ${success_count} 个`)
          addLog(`失败: ${fail_count} 个`)
          
          if (results && results.length > 0) {
            addLog('')
            addLog('=== 详细导出状态 ===')
            results.forEach(result => {
              if (result.success) {
                addLog(`✓ ${result.station_name} (${result.station_ip}) - 导出成功`)
              } else {
                addLog(`✗ ${result.station_name} (${result.station_ip}) - 导出失败: ${result.message}`)
              }
            })
          }
          
          addLog('')
          addLog('=== 传感器数据导出完成 ===')
        } else {
          addLog(response.data.message || '导出操作完成')
        }
        
        // 确保状态同步更新
        addLog('✅ 传感器数据导出任务已全部完成')
      } catch (error) {
        console.error('导出传感器数据错误:', error)
        let errorMessage = '未知错误'
        if (error.code === 'ECONNABORTED') {
          errorMessage = '请求超时，请检查网络连接或联系管理员'
        } else if (error.response) {
          errorMessage = `服务器错误: ${error.response.status} - ${error.response.data?.message || error.message}`
        } else if (error.request) {
          errorMessage = '网络连接失败，请检查网络设置'
        } else {
          errorMessage = error.message
        }
        addLog(`导出传感器数据失败: ${errorMessage}`)
        exportResult.value = {
          success: false,
          message: `导出失败: ${errorMessage}`
        }
      } finally {
        // 立即更新按钮状态，确保用户能立即看到完成状态
        isExportingSensor.value = false
        await nextTick()  // 确保 DOM 更新
        addLog('传感器数据导出操作已完成，可以进行下次操作')
        console.log('传感器数据导出按钮状态已重置:', isExportingSensor.value)
      }
    }
    
    // 下载文件
    const downloadFile = (filePath) => {
      // 在实际应用中，这里应该调用后端API下载文件
      addLog(`下载文件: ${filePath}`)
      // 使用axios下载文件
      const link = document.createElement('a');
      link.href = `/api/download/${filePath}`;
      link.download = filePath;
      link.click();
    }
    
    // 紧急状态重置功能（防止按钮卡住）
    const forceResetExportState = () => {
      console.log('强制重置导出状态')
      isExportingElectricity.value = false
      isExportingSensor.value = false
      addLog('🛠️ 已强制重置所有导出状态，可以进行操作')
    }
    
    // 状态监控和自动修复
    const startStatusMonitor = () => {
      setInterval(() => {
        // 检查是否有长时间的loading状态（超过10分钟）
        if (isExportingElectricity.value || isExportingSensor.value) {
          const now = Date.now()
          const lastLogTime = logs.value.length > 0 ? new Date(logs.value[logs.value.length - 1].time).getTime() : now
          const timeDiff = now - lastLogTime
          
          if (timeDiff > 10 * 60 * 1000) { // 10分钟没有新日志
            console.warn('检测到可能的状态卡住，自动重置')
            forceResetExportState()
          }
        }
      }, 30000) // 每30秒检查一次
    }
    
    // 组件挂载时获取线路列表
    onMounted(async () => {
      await fetchLines()
      
      // 初始化默认时间 - 确保正确设置为当日0点和当前小时0分0秒
      electricityForm.value.start_time = getTodayStart()
      electricityForm.value.end_time = getCurrentHour()
      sensorForm.value.start_time = getTodayStart()
      sensorForm.value.end_time = getCurrentHour()
      
      // 设置默认线路
      if (lines.value.length > 0) {
        electricityForm.value.line = lines.value[0]
        sensorForm.value.line = lines.value[0]
      }
      
      startStatusMonitor() // 启动状态监控
    })
    
    return {
      zhCn: locale,  // 添加中文本地化
      activeTab,
      lines,
      electricityForm,
      sensorForm,
      isExportingElectricity,
      isExportingSensor,
      exportResult,
      logs,
      resetElectricityForm,
      resetSensorForm,
      exportElectricityData,
      exportSensorData,
      downloadFile,
      forceResetExportState  // 添加紧急重置功能
    }
  }
}
</script>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  min-height: 100vh;
}

.el-header {
  background-color: #409EFF;
  color: #fff;
  text-align: center;
  line-height: 60px;
  position: sticky;
  top: 0;
  z-index: 1000;
}

.el-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: bold;
}

.success {
  color: #67C23A;
}

.error {
  color: #F56C6C;
}

.log-item {
  text-align: left;
  padding: 5px 0;
  border-bottom: 1px solid #eee;
}
</style>