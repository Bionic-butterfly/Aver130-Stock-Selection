<template>
  <div class="training-logs">
    <div class="page-container">
      <h1>运行日志</h1>
      
      <!-- 日志筛选 -->
      <el-card class="filter-card" style="margin-bottom: 20px;">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-select v-model="selectedLevel" placeholder="日志级别" clearable style="width: 100%;">
              <el-option label="全部" value=""></el-option>
              <el-option label="INFO" value="INFO"></el-option>
              <el-option label="WARNING" value="WARNING"></el-option>
              <el-option label="ERROR" value="ERROR"></el-option>
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 100%;">
            </el-date-picker>
          </el-col>
          <el-col :span="12">
            <el-button type="primary" @click="loadLogs">查询</el-button>
            <el-button @click="exportLogs">导出日志</el-button>
            <el-button @click="clearLogs">清空日志</el-button>
            <el-button @click="refreshLogs">刷新</el-button>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 日志统计 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-statistic title="总日志数" :value="logStats.total" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="INFO" :value="logStats.info" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="WARNING" :value="logStats.warning" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="ERROR" :value="logStats.error" />
        </el-col>
      </el-row>
      
      <!-- 日志列表 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>运行日志记录</span>
            <el-button type="text" @click="toggleAutoRefresh">
              {{ autoRefresh ? '停止自动刷新' : '开始自动刷新' }}
            </el-button>
          </div>
        </template>
        
        <el-table :data="filteredLogs" border v-loading="loading" style="width: 100%;">
          <el-table-column prop="timestamp" label="时间" width="180">
            <template #default="scope">
              <el-tag size="small">{{ scope.row.timestamp }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="level" label="级别" width="100">
            <template #default="scope">
              <el-tag 
                :type="getLevelType(scope.row.level)"
                size="small">
                {{ scope.row.level }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="消息内容">
            <template #default="scope">
              <span :class="getMessageClass(scope.row.level)">{{ scope.row.message }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="scope">
              <el-button type="text" @click="viewLogDetail(scope.row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 50, 100]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          style="margin-top: 20px;">
        </el-pagination>
      </el-card>
      
      <!-- 日志详情对话框 -->
      <el-dialog v-model="detailVisible" title="日志详情" width="600px">
        <div v-if="selectedLog" class="log-detail">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="时间戳">
              {{ selectedLog.timestamp }}
            </el-descriptions-item>
            <el-descriptions-item label="日志级别">
              <el-tag :type="getLevelType(selectedLog.level)">{{ selectedLog.level }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="消息内容">
              {{ selectedLog.message }}
            </el-descriptions-item>
            <el-descriptions-item label="模块路径" v-if="selectedLog.module">
              {{ selectedLog.module }}
            </el-descriptions-item>
            <el-descriptions-item label="函数名" v-if="selectedLog.function">
              {{ selectedLog.function }}
            </el-descriptions-item>
            <el-descriptions-item label="行号" v-if="selectedLog.lineNo">
              {{ selectedLog.lineNo }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        <template #footer>
          <el-button @click="detailVisible = false">关闭</el-button>
        </template>
      </el-dialog>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 模拟API调用
const api = {
  getLogs: () => Promise.resolve([
    { timestamp: '2024-01-01 10:00:00', level: 'INFO', message: '量化核心启动成功' },
    { timestamp: '2024-01-01 10:01:00', level: 'INFO', message: '开始数据加载与验证' },
    { timestamp: '2024-01-01 10:02:00', level: 'INFO', message: '数据生成完成，共85000条记录' },
    { timestamp: '2024-01-01 10:03:00', level: 'INFO', message: '开始因子有效性分析' },
    { timestamp: '2024-01-01 10:04:00', level: 'WARNING', message: '发现部分异常值，已自动处理' },
    { timestamp: '2024-01-01 10:05:00', level: 'INFO', message: '因子分析完成' },
    { timestamp: '2024-01-01 10:06:00', level: 'INFO', message: '开始模型训练与参数调优' },
    { timestamp: '2024-01-01 10:07:00', level: 'INFO', message: '最佳参数: 学习率=0.1, 树数量=100' },
    { timestamp: '2024-01-01 10:08:00', level: 'INFO', message: '模型训练完成' },
    { timestamp: '2024-01-01 10:09:00', level: 'INFO', message: '开始回测分析与风险评估' },
    { timestamp: '2024-01-01 10:10:00', level: 'INFO', message: '回测分析完成' },
    { timestamp: '2024-01-01 10:11:00', level: 'INFO', message: '分析报告已生成' }
  ])
}

export default {
  name: 'TrainingLogs',
  setup() {
    const logs = ref([])
    const loading = ref(false)
    const selectedLevel = ref('')
    const dateRange = ref([])
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const detailVisible = ref(false)
    const selectedLog = ref(null)
    const autoRefresh = ref(false)
    let refreshTimer = null
    
    const filteredLogs = computed(() => {
      let filtered = logs.value
      
      // 按级别筛选
      if (selectedLevel.value) {
        filtered = filtered.filter(log => log.level === selectedLevel.value)
      }
      
      // 按日期筛选
      if (dateRange.value && dateRange.value.length === 2) {
        const [start, end] = dateRange.value
        filtered = filtered.filter(log => {
          const logDate = new Date(log.timestamp)
          return logDate >= start && logDate <= end
        })
      }
      
      total.value = filtered.length
      
      // 分页
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      return filtered.slice(start, end)
    })
    
    const logStats = computed(() => {
      const stats = {
        total: logs.value.length,
        info: logs.value.filter(log => log.level === 'INFO').length,
        warning: logs.value.filter(log => log.level === 'WARNING').length,
        error: logs.value.filter(log => log.level === 'ERROR').length
      }
      return stats
    })
    
    const loadLogs = async () => {
      loading.value = true
      try {
        const response = await api.getLogs()
        logs.value = response
        ElMessage.success('日志加载成功')
      } catch (error) {
        ElMessage.error('日志加载失败')
        console.error('加载日志失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const getLevelType = (level) => {
      const typeMap = {
        'INFO': 'success',
        'WARNING': 'warning',
        'ERROR': 'danger'
      }
      return typeMap[level] || 'info'
    }
    
    const getMessageClass = (level) => {
      const classMap = {
        'INFO': 'log-info',
        'WARNING': 'log-warning',
        'ERROR': 'log-error'
      }
      return classMap[level] || ''
    }
    
    const viewLogDetail = (log) => {
      selectedLog.value = {
        ...log,
        module: 'quant_core.main_advanced',
        function: 'run_comprehensive_analysis',
        lineNo: 45
      }
      detailVisible.value = true
    }
    
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
    }
    
    const exportLogs = () => {
      if (logs.value.length === 0) return
      
      const logContent = logs.value.map(log => 
        `${log.timestamp} - ${log.level} - ${log.message}`
      ).join('\n')
      
      const blob = new Blob(['\uFEFF' + logContent], { type: 'text/plain;charset=utf-8' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `运行日志_${new Date().toISOString().split('T')[0]}.txt`
      link.click()
      
      ElMessage.success('日志导出成功')
    }
    
    const clearLogs = async () => {
      try {
        await ElMessageBox.confirm('确定要清空所有日志记录吗？', '确认清空', {
          type: 'warning'
        })
        
        logs.value = []
        ElMessage.success('日志已清空')
      } catch {
        // 用户取消操作
      }
    }
    
    const refreshLogs = () => {
      loadLogs()
    }
    
    const toggleAutoRefresh = () => {
      autoRefresh.value = !autoRefresh.value
      
      if (autoRefresh.value) {
        refreshTimer = setInterval(() => {
          loadLogs()
        }, 5000) // 5秒刷新一次
        ElMessage.info('已开启自动刷新')
      } else {
        if (refreshTimer) {
          clearInterval(refreshTimer)
          refreshTimer = null
        }
        ElMessage.info('已停止自动刷新')
      }
    }
    
    onMounted(() => {
      loadLogs()
    })
    
    onUnmounted(() => {
      if (refreshTimer) {
        clearInterval(refreshTimer)
      }
    })
    
    return {
      logs,
      loading,
      selectedLevel,
      dateRange,
      currentPage,
      pageSize,
      total,
      detailVisible,
      selectedLog,
      autoRefresh,
      filteredLogs,
      logStats,
      loadLogs,
      getLevelType,
      getMessageClass,
      viewLogDetail,
      handleSizeChange,
      handleCurrentChange,
      exportLogs,
      clearLogs,
      refreshLogs,
      toggleAutoRefresh
    }
  }
}
</script>

<style scoped>
.training-logs {
  padding: 0;
}

.log-info {
  color: #67c23a;
}

.log-warning {
  color: #e6a23c;
}

.log-error {
  color: #f56c6c;
}

.log-detail {
  padding: 10px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>