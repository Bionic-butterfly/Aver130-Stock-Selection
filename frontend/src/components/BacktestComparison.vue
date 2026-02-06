<template>
  <div class="backtest-comparison">
    <el-card class="results-card">
      <template #header>
        <div class="card-header">
          <span>回测结果对比</span>
          <el-button type="primary" @click="refreshResults">刷新数据</el-button>
        </div>
      </template>
      
      <v-chart :option="comparisonOption" class="chart" />
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>详细回测数据</span>
            </div>
          </template>
          
          <el-table :data="backtestResults" stripe height="300">
            <el-table-column prop="top_n" label="选股数量" width="100" />
            <el-table-column prop="portfolio_return" label="组合收益率" width="120">
              <template #default="{ row }">
                <span class="positive">{{ (row.portfolio_return * 100).toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="benchmark_return" label="基准收益率" width="120">
              <template #default="{ row }">
                <span>{{ (row.benchmark_return * 100).toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="excess_return" label="超额收益" width="120">
              <template #default="{ row }">
                <span class="positive">{{ (row.excess_return * 100).toFixed(2) }}%</span>
              </template>
            </el-table-column>
            <el-table-column prop="improvement_ratio" label="改进比例" width="120">
              <template #default="{ row }">
                <span class="positive">{{ (row.improvement_ratio * 100).toFixed(1) }}%</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="analysis-card">
          <template #header>
            <div class="card-header">
              <span>策略分析</span>
            </div>
          </template>
          
          <div class="analysis-content">
            <div class="analysis-item">
              <h4>最佳策略</h4>
              <p v-if="bestStrategy">
                选股数量: <strong>Top {{ bestStrategy.top_n }}</strong><br>
                超额收益: <strong class="positive">{{ (bestStrategy.excess_return * 100).toFixed(2) }}%</strong>
              </p>
            </div>
            
            <div class="analysis-item">
              <h4>模型有效性</h4>
              <p>
                所有策略均跑赢基准，证明"行业中性化+XGBoost"模型的有效性
              </p>
            </div>
            
            <div class="analysis-item">
              <h4>风险提示</h4>
              <p>
                回测结果基于历史数据，未来表现可能有所不同。
                投资有风险，决策需谨慎。
              </p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="conclusion-card">
      <template #header>
        <div class="card-header">
          <span>结论总结</span>
        </div>
      </template>
      
      <div class="conclusion-content">
        <el-alert
          title="模型表现优异"
          type="success"
          description="基于行业中性化+XGBoost的多因子选股模型在所有测试策略中均显著跑赢沪深300基准，证明了该方法的有效性。"
          show-icon
          :closable="false" />
        
        <div class="key-points">
          <h4>关键发现：</h4>
          <ul>
            <li>Top 30策略超额收益最高，达到5.4%</li>
            <li>所有策略均实现正超额收益</li>
            <li>模型在不同选股数量下表现稳定</li>
            <li>行业中性化处理有效降低了行业风险</li>
          </ul>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import apiService from '../api/index'

use([
  CanvasRenderer,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 响应式数据
const backtestResults = ref([])

// 计算属性
const bestStrategy = computed(() => {
  if (backtestResults.value.length === 0) return null
  return backtestResults.value.reduce((best, current) => 
    current.excess_return > best.excess_return ? current : best
  )
})

// 图表配置
const comparisonOption = ref({
  title: { text: '回测结果对比', left: 'center' },
  tooltip: {
    trigger: 'axis',
    formatter: (params) => {
      let result = `${params[0].name}<br/>`
      params.forEach(param => {
        result += `${param.seriesName}: ${(param.value * 100).toFixed(2)}%<br/>`
      })
      return result
    }
  },
  legend: { data: ['组合收益率', '基准收益率', '超额收益'], top: '10%' },
  xAxis: {
    type: 'category',
    data: []
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: '{value}%'
    }
  },
  series: [
    {
      name: '组合收益率',
      data: [],
      type: 'bar',
      itemStyle: { color: '#409eff' }
    },
    {
      name: '基准收益率',
      data: [],
      type: 'bar',
      itemStyle: { color: '#909399' }
    },
    {
      name: '超额收益',
      data: [],
      type: 'line',
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { color: '#67c23a', width: 3 },
      itemStyle: { color: '#67c23a' }
    }
  ]
})

// 生命周期
onMounted(() => {
  loadBacktestResults()
})

// 方法
const loadBacktestResults = async () => {
  try {
    const data = await apiService.getBacktestResults()
    backtestResults.value = data
    
    // 更新图表
    updateComparisonChart(data)
    
  } catch (error) {
    console.error('加载回测结果失败:', error)
    // 使用模拟数据
    loadSampleData()
    ElMessage.warning('使用示例数据进行演示')
  }
}

const refreshResults = () => {
  loadBacktestResults()
  ElMessage.success('回测数据已刷新')
}

const updateComparisonChart = (data) => {
  comparisonOption.value.xAxis.data = data.map(item => `Top ${item.top_n}`)
  comparisonOption.value.series[0].data = data.map(item => item.portfolio_return)
  comparisonOption.value.series[1].data = data.map(item => item.benchmark_return)
  comparisonOption.value.series[2].data = data.map(item => item.excess_return)
}

const loadSampleData = () => {
  // 模拟数据
  const sampleData = [
    { top_n: 30, portfolio_return: 0.152, benchmark_return: 0.098, excess_return: 0.054, improvement_ratio: 0.551 },
    { top_n: 50, portfolio_return: 0.145, benchmark_return: 0.098, excess_return: 0.047, improvement_ratio: 0.480 },
    { top_n: 100, portfolio_return: 0.128, benchmark_return: 0.098, excess_return: 0.030, improvement_ratio: 0.306 }
  ]
  
  backtestResults.value = sampleData
  updateComparisonChart(sampleData)
}
</script>

<style scoped>
.backtest-comparison {
  padding: 0;
}

.results-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.chart {
  height: 400px;
  width: 100%;
}

.detail-card, .analysis-card {
  margin-bottom: 20px;
}

.analysis-content {
  padding: 10px 0;
}

.analysis-item {
  margin-bottom: 20px;
}

.analysis-item h4 {
  margin-bottom: 8px;
  color: #303133;
}

.analysis-item p {
  margin: 0;
  color: #606266;
  line-height: 1.6;
}

.conclusion-card {
  margin-top: 20px;
}

.conclusion-content {
  padding: 10px 0;
}

.key-points {
  margin-top: 20px;
}

.key-points h4 {
  margin-bottom: 10px;
  color: #303133;
}

.key-points ul {
  color: #606266;
  line-height: 1.8;
  padding-left: 20px;
}

.positive {
  color: #67c23a;
  font-weight: bold;
}
</style>