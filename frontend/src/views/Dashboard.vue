<template>
  <div class="dashboard">
    <div class="page-container">
      <h1>系统概览</h1>
      
      <!-- 系统状态卡片 -->
      <el-row :gutter="20" class="status-cards">
        <el-col :span="6">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon">
                <el-icon size="40" color="#409EFF"><DataBoard /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-value">{{ systemStatus.dataFiles }}</div>
                <div class="card-label">数据文件</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon">
                <el-icon size="40" color="#67C23A"><Cpu /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-value">{{ systemStatus.modelStatus === 'loaded' ? '已加载' : '未加载' }}</div>
                <div class="card-label">模型状态</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon">
                <el-icon size="40" color="#E6A23C"><Timer /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-value">{{ systemStatus.lastRun }}</div>
                <div class="card-label">最后运行</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="status-card">
            <div class="card-content">
              <div class="card-icon">
                <el-icon size="40" color="#F56C6C"><Warning /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-value">{{ systemStatus.errors }}</div>
                <div class="card-label">错误数量</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 快速操作 -->
      <el-card class="quick-actions" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>快速操作</span>
          </div>
        </template>
        
        <el-row :gutter="20">
          <el-col :span="6">
            <el-button type="primary" size="large" @click="runQuantCore" style="width: 100%;">
              <el-icon><VideoPlay /></el-icon>
              运行量化核心
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="success" size="large" @click="exportReport" style="width: 100%;">
              <el-icon><Document /></el-icon>
              导出分析报告
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="warning" size="large" @click="checkDataQuality" style="width: 100%;">
              <el-icon><Search /></el-icon>
              数据质量检查
            </el-button>
          </el-col>
          <el-col :span="6">
            <el-button type="info" size="large" @click="viewApiDocs" style="width: 100%;">
              <el-icon><DocumentCopy /></el-icon>
              API文档
            </el-button>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 数据概览 -->
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>数据概览</span>
              </div>
            </template>
            
            <el-descriptions :column="2" border>
              <el-descriptions-item label="数据区间">
                {{ dataOverview.dateRange }}
              </el-descriptions-item>
              <el-descriptions-item label="股票数量">
                {{ dataOverview.stockCount }}
              </el-descriptions-item>
              <el-descriptions-item label="行业数量">
                {{ dataOverview.industryCount }}
              </el-descriptions-item>
              <el-descriptions-item label="记录总数">
                {{ dataOverview.totalRecords }}
              </el-descriptions-item>
              <el-descriptions-item label="可用因子">
                {{ dataOverview.availableFactors }}
              </el-descriptions-item>
              <el-descriptions-item label="数据质量">
                <el-tag :type="dataQualityTag.type">{{ dataQualityTag.text }}</el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>最新分析结果</span>
              </div>
            </template>
            
            <div class="analysis-results">
              <div class="result-item">
                <div class="result-label">最佳参数组合</div>
                <div class="result-value">{{ analysisResults.bestParams }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">测试集R²</div>
                <div class="result-value">{{ analysisResults.testR2 }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">年化收益率</div>
                <div class="result-value">{{ analysisResults.annualReturn }}</div>
              </div>
              <div class="result-item">
                <div class="result-label">夏普比率</div>
                <div class="result-value">{{ analysisResults.sharpeRatio }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// 模拟API调用
const api = {
  getSystemStatus: () => Promise.resolve({
    dataFiles: 12,
    modelStatus: 'loaded',
    lastRun: '2小时前',
    errors: 0
  }),
  getDataOverview: () => Promise.resolve({
    dateRange: '2019-01-01 至 2026-02-05',
    stockCount: 300,
    industryCount: 20,
    totalRecords: '85,000',
    availableFactors: 5
  }),
  getAnalysisResults: () => Promise.resolve({
    bestParams: '学习率=0.1, 树数量=100',
    testR2: '0.789',
    annualReturn: '15.67%',
    sharpeRatio: '1.23'
  })
}

export default {
  name: 'Dashboard',
  setup() {
    const systemStatus = ref({
      dataFiles: 0,
      modelStatus: 'not_loaded',
      lastRun: '从未运行',
      errors: 0
    })
    
    const dataOverview = ref({
      dateRange: '',
      stockCount: 0,
      industryCount: 0,
      totalRecords: 0,
      availableFactors: 0
    })
    
    const analysisResults = ref({
      bestParams: '',
      testR2: '',
      annualReturn: '',
      sharpeRatio: ''
    })
    
    const dataQualityTag = ref({
      type: 'success',
      text: '良好'
    })
    
    const loadData = async () => {
      try {
        // 模拟API调用
        const [statusRes, overviewRes, analysisRes] = await Promise.all([
          api.getSystemStatus(),
          api.getDataOverview(),
          api.getAnalysisResults()
        ])
        
        systemStatus.value = statusRes
        dataOverview.value = overviewRes
        analysisResults.value = analysisRes
        
      } catch (error) {
        ElMessage.error('数据加载失败')
      }
    }
    
    const runQuantCore = async () => {
      try {
        ElMessage.info('正在运行量化核心，请稍候...')
        // 实际实现需要调用后端API
        setTimeout(() => {
          ElMessage.success('量化核心运行完成')
          loadData() // 重新加载数据
        }, 3000)
      } catch (error) {
        ElMessage.error('运行量化核心失败')
      }
    }
    
    const exportReport = () => {
      ElMessage.success('分析报告导出成功')
    }
    
    const checkDataQuality = () => {
      ElMessage.info('正在检查数据质量...')
    }
    
    const viewApiDocs = () => {
      window.open('http://localhost:8000/docs', '_blank')
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      systemStatus,
      dataOverview,
      analysisResults,
      dataQualityTag,
      runQuantCore,
      exportReport,
      checkDataQuality,
      viewApiDocs
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.status-cards {
  margin-bottom: 20px;
}

.status-card {
  height: 120px;
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.card-icon {
  flex: 0 0 60px;
  text-align: center;
}

.card-info {
  flex: 1;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.card-label {
  color: #909399;
  font-size: 14px;
}

.card-header {
  font-weight: bold;
}

.analysis-results {
  padding: 10px 0;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.result-item:last-child {
  border-bottom: none;
}

.result-label {
  color: #606266;
}

.result-value {
  font-weight: bold;
  color: #303133;
}
</style>