<template>
  <div class="risk-metrics">
    <div class="page-container">
      <h1>风险指标详情</h1>
      
      <!-- 风险指标卡片 -->
      <el-card class="risk-summary-card" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>风险收益特征概览</span>
            <el-button type="primary" size="small" @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </template>
        
        <div class="risk-cards-grid">
          <el-card class="metric-card success">
            <div class="metric-content">
              <div class="metric-value">{{ formatPercentage(riskMetrics.annual_return) }}</div>
              <div class="metric-label">年化收益率</div>
            </div>
          </el-card>
          
          <el-card class="metric-card info">
            <div class="metric-content">
              <div class="metric-value">{{ formatPercentage(riskMetrics.benchmark_annual_return) }}</div>
              <div class="metric-label">基准年化收益率</div>
            </div>
          </el-card>
          
          <el-card class="metric-card warning">
            <div class="metric-content">
              <div class="metric-value">{{ formatPercentage(riskMetrics.annual_volatility) }}</div>
              <div class="metric-label">年化波动率</div>
            </div>
          </el-card>
          
          <el-card class="metric-card danger">
            <div class="metric-content">
              <div class="metric-value">{{ formatPercentage(riskMetrics.max_drawdown) }}</div>
              <div class="metric-label">最大回撤</div>
            </div>
          </el-card>
          
          <el-card class="metric-card success">
            <div class="metric-content">
              <div class="metric-value">{{ riskMetrics.sharpe_ratio.toFixed(4) }}</div>
              <div class="metric-label">夏普比率</div>
            </div>
          </el-card>
          
          <el-card class="metric-card info">
            <div class="metric-content">
              <div class="metric-value">{{ riskMetrics.calmar_ratio.toFixed(4) }}</div>
              <div class="metric-label">卡玛比率</div>
            </div>
          </el-card>
          
          <el-card class="metric-card warning">
            <div class="metric-content">
              <div class="metric-value">{{ formatPercentage(riskMetrics.win_rate) }}</div>
              <div class="metric-label">策略胜率</div>
            </div>
          </el-card>
          
          <el-card class="metric-card danger">
            <div class="metric-content">
              <div class="metric-value">{{ riskMetrics.profit_loss_ratio.toFixed(4) }}</div>
              <div class="metric-label">累计盈亏比</div>
            </div>
          </el-card>
        </div>
      </el-card>
      
      <!-- 风险收益对比图表 -->
      <el-card style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>风险收益特征对比</span>
            <el-button type="primary" size="small" @click="exportChart">
              <el-icon><Download /></el-icon>
              导出图表
            </el-button>
          </div>
        </template>
        
        <div ref="radarChart" style="width: 100%; height: 400px;"></div>
      </el-card>
      
      <!-- 回测场景对比 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>多场景回测对比</span>
            <el-select v-model="selectedFrequency" placeholder="选择调仓频率" size="small" @change="loadScenarios">
              <el-option label="月度调仓" value="monthly"></el-option>
              <el-option label="季度调仓" value="quarterly"></el-option>
            </el-select>
          </div>
        </template>
        
        <el-table 
          :data="scenarioResults" 
          border 
          style="width: 100%;">
          <el-table-column prop="scenario" label="市场阶段" width="120">
            <template #default="scope">
              <el-tag :type="getScenarioTagType(scope.row.scenario)">
                {{ getScenarioName(scope.row.scenario) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="frequency" label="调仓频率" width="120">
            <template #default="scope">
              {{ scope.row.frequency === 'monthly' ? '月度' : '季度' }}
            </template>
          </el-table-column>
          <el-table-column prop="top_n" label="选股数量" width="100"></el-table-column>
          <el-table-column prop="risk_metrics.annual_return" label="年化收益率">
            <template #default="scope">
              {{ formatPercentage(scope.row.risk_metrics.annual_return) }}
            </template>
          </el-table-column>
          <el-table-column prop="risk_metrics.sharpe_ratio" label="夏普比率">
            <template #default="scope">
              {{ scope.row.risk_metrics.sharpe_ratio.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column prop="risk_metrics.max_drawdown" label="最大回撤">
            <template #default="scope">
              {{ formatPercentage(scope.row.risk_metrics.max_drawdown) }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Refresh, Download } from '@element-plus/icons-vue'
import { apiService } from '../api'

export default {
  name: 'RiskMetrics',
  setup() {
    const riskMetrics = ref({
      annual_return: 0,
      benchmark_annual_return: 0,
      annual_volatility: 0,
      sharpe_ratio: 0,
      max_drawdown: 0,
      calmar_ratio: 0,
      win_rate: 0,
      profit_loss_ratio: 0
    })
    
    const scenarioResults = ref([])
    const loading = ref(false)
    const radarChart = ref(null)
    const selectedFrequency = ref('monthly')
    let echartsInstance = null
    
    const loadRiskMetrics = async () => {
      loading.value = true
      try {
        const data = await apiService.getRiskMetrics()
        riskMetrics.value = data
        ElMessage.success('风险指标数据加载成功')
      } catch (error) {
        ElMessage.error('风险指标数据加载失败')
        console.error('加载风险指标失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const loadScenarios = async () => {
      try {
        const data = await apiService.getBacktestScenarios({
          frequency: selectedFrequency.value
        })
        scenarioResults.value = data
      } catch (error) {
        ElMessage.error('回测场景数据加载失败')
        console.error('加载回测场景失败:', error)
      }
    }
    
    const refreshData = async () => {
      await loadRiskMetrics()
      await loadScenarios()
      initChart()
    }
    
    const initChart = () => {
      if (radarChart.value) {
        echartsInstance = echarts.init(radarChart.value)
        window.addEventListener('resize', () => echartsInstance.resize())
        updateChart()
      }
    }
    
    const updateChart = () => {
      if (!echartsInstance) return
      
      const metrics = [
        { key: 'annual_return', label: '年化收益率', value: riskMetrics.value.annual_return },
        { key: 'sharpe_ratio', label: '夏普比率', value: riskMetrics.value.sharpe_ratio },
        { key: 'calmar_ratio', label: '卡玛比率', value: riskMetrics.value.calmar_ratio },
        { key: 'win_rate', label: '胜率', value: riskMetrics.value.win_rate },
        { key: 'profit_loss_ratio', label: '盈亏比', value: riskMetrics.value.profit_loss_ratio }
      ]
      
      // 标准化数据
      const maxValues = metrics.map(m => m.value).map(v => Math.abs(v))
      const maxValue = Math.max(...maxValues, 1)
      
      const normalizedValues = metrics.map(m => (m.value / maxValue) * 100)
      const labels = metrics.map(m => m.label)
      
      const option = {
        title: {
          text: '策略风险收益特征雷达图',
          left: 'center'
        },
        tooltip: {
          trigger: 'item'
        },
        legend: {
          data: ['策略表现'],
          bottom: 10
        },
        radar: {
          indicator: labels.map((label, index) => ({
            name: label,
            max: 100
          }))
        },
        series: [{
          name: '策略表现',
          type: 'radar',
          data: [{
            value: normalizedValues,
            name: '策略表现',
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.2)'
            },
            lineStyle: {
              color: '#409EFF'
            },
            itemStyle: {
              color: '#409EFF'
            }
          }]
        }]
      }
      
      echartsInstance.setOption(option)
    }
    
    const exportChart = () => {
      if (echartsInstance) {
        const chartDataURL = echartsInstance.getDataURL({
          type: 'png',
          pixelRatio: 2,
          backgroundColor: '#fff'
        })
        
        const link = document.createElement('a')
        link.download = `风险指标雷达图_${new Date().toISOString().split('T')[0]}.png`
        link.href = chartDataURL
        link.click()
        
        ElMessage.success('图表导出成功')
      }
    }
    
    const formatPercentage = (value) => {
      return (value * 100).toFixed(2) + '%'
    }
    
    const getScenarioTagType = (scenario) => {
      const typeMap = {
        bull: 'success',
        bear: 'danger',
        neutral: 'warning'
      }
      return typeMap[scenario] || 'info'
    }
    
    const getScenarioName = (scenario) => {
      const nameMap = {
        bull: '牛市',
        bear: '熊市',
        neutral: '震荡市'
      }
      return nameMap[scenario] || scenario
    }
    
    onMounted(() => {
      loadRiskMetrics()
      loadScenarios()
      initChart()
    })
    
    watch(riskMetrics, () => {
      updateChart()
    }, { deep: true })
    
    return {
      riskMetrics,
      scenarioResults,
      loading,
      radarChart,
      selectedFrequency,
      refreshData,
      exportChart,
      formatPercentage,
      getScenarioTagType,
      getScenarioName
    }
  }
}
</script>

<style scoped>
.risk-metrics {
  padding: 0;
}

.risk-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.metric-card {
  transition: all 0.3s ease;
}

.metric-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.metric-card.success {
  border-top: 4px solid #67C23A;
}

.metric-card.info {
  border-top: 4px solid #409EFF;
}

.metric-card.warning {
  border-top: 4px solid #E6A23C;
}

.metric-card.danger {
  border-top: 4px solid #F56C6C;
}

.metric-content {
  text-align: center;
}

.metric-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 14px;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .risk-cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .risk-cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
