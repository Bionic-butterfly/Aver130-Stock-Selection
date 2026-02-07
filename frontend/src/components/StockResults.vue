<template>
  <div class="stock-results">
    <el-card class="summary-card">
      <template #header>
        <div class="card-header">
          <span>选股结果汇总</span>
          <el-button type="primary" @click="exportResults">导出结果</el-button>
        </div>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-value">{{ selectedStocks.length }}</div>
            <div class="summary-label">入选股票数量</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-value positive">{{ positiveRatio }}</div>
            <div class="summary-label">正收益股票比例</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-value">{{ industryCount }}</div>
            <div class="summary-label">覆盖行业数量</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-value">{{ avgRank }}</div>
            <div class="summary-label">平均预测排名</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>行业分布</span>
            </div>
          </template>
          <v-chart :option="industryDistributionOption" class="chart" />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>收益率分布</span>
            </div>
          </template>
          <v-chart :option="returnDistributionOption" class="chart" />
        </el-card>
      </el-col>
    </el-row>

    <el-card class="details-card">
      <template #header>
        <div class="card-header">
          <span>详细选股列表</span>
          <div class="filter-container">
            <el-select v-model="selectedIndustry" placeholder="按行业筛选" size="small" style="margin-right: 10px" clearable>
              <el-option v-for="industry in industries" :key="industry" :label="industry" :value="industry"></el-option>
            </el-select>
            <el-select v-model="sortBy" placeholder="按因子值排序" size="small" style="margin-right: 10px">
              <el-option label="默认排名" value="predicted_rank"></el-option>
              <el-option label="预测收益率↑" value="predicted_return_desc"></el-option>
              <el-option label="预测收益率↓" value="predicted_return_asc"></el-option>
            </el-select>
            <el-input 
              v-model="searchText" 
              placeholder="搜索股票代码" 
              style="width: 150px" 
              clearable />
          </div>
        </div>
      </template>
      
      <el-table :data="filteredStocks" stripe height="400" v-loading="loading">
        <el-table-column type="index" label="排名" width="80" />
        <el-table-column prop="ts_code" label="股票代码" width="120" />
        <el-table-column prop="industry" label="行业" width="120" />
        <el-table-column prop="predicted_return" label="预测收益率" width="120">
          <template #default="{ row }">
            <span :class="{ 'positive': row.predicted_return > 0, 'negative': row.predicted_return < 0 }">
              {{ (row.predicted_return * 100).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="predicted_rank" label="预测排名" width="100" />
        <el-table-column label="投资建议" width="100">
          <template #default="{ row }">
            <el-tag :type="getRecommendationType(row.predicted_return)">
              {{ getRecommendation(row.predicted_return) }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart } from 'echarts/charts'
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
  PieChart,
  BarChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

// 响应式数据
const selectedStocks = ref([])
const loading = ref(false)
const searchText = ref('')
const selectedIndustry = ref('')
const sortBy = ref('predicted_rank')

// 计算属性
const industries = computed(() => {
  const industrySet = new Set(selectedStocks.value.map(stock => stock.industry))
  return Array.from(industrySet).sort()
})

const filteredStocks = computed(() => {
  let result = [...selectedStocks.value]
  
  // 按行业筛选
  if (selectedIndustry.value) {
    result = result.filter(stock => stock.industry === selectedIndustry.value)
  }
  
  // 按搜索词筛选
  if (searchText.value) {
    result = result.filter(stock => 
      stock.ts_code.includes(searchText.value)
    )
  }
  
  // 按因子值排序
  switch (sortBy.value) {
    case 'predicted_return_desc':
      result.sort((a, b) => b.predicted_return - a.predicted_return)
      break
    case 'predicted_return_asc':
      result.sort((a, b) => a.predicted_return - b.predicted_return)
      break
    case 'predicted_rank':
    default:
      result.sort((a, b) => a.predicted_rank - b.predicted_rank)
      break
  }
  
  return result
})

const positiveRatio = computed(() => {
  if (selectedStocks.value.length === 0) return '0%'
  const positiveCount = selectedStocks.value.filter(stock => stock.predicted_return > 0).length
  return ((positiveCount / selectedStocks.value.length) * 100).toFixed(1) + '%'
})

const industryCount = computed(() => {
  const industries = new Set(selectedStocks.value.map(stock => stock.industry))
  return industries.size
})

const avgRank = computed(() => {
  if (selectedStocks.value.length === 0) return 0
  const sum = selectedStocks.value.reduce((total, stock) => total + stock.predicted_rank, 0)
  return Math.round(sum / selectedStocks.value.length)
})

// 图表配置
const industryDistributionOption = ref({
  title: { text: '行业分布', left: 'center' },
  tooltip: { trigger: 'item' },
  series: [{
    type: 'pie',
    radius: '60%',
    data: [],
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    }
  }]
})

const returnDistributionOption = ref({
  title: { text: '收益率分布', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['<-10%', '-10%~0%', '0%~10%', '10%~20%', '>20%']
  },
  yAxis: { type: 'value' },
  series: [{
    data: [0, 0, 0, 0, 0],
    type: 'bar',
    itemStyle: { color: '#409eff' }
  }]
})

// 生命周期
onMounted(() => {
  loadStockResults()
})

// 方法
const loadStockResults = async () => {
  try {
    loading.value = true
    const data = await apiService.getTopPredictions(50)
    selectedStocks.value = data
    
    // 更新图表数据
    updateCharts(data)
    
  } catch (error) {
    console.error('加载选股结果失败:', error)
    // 使用模拟数据
    loadSampleData()
    ElMessage.warning('使用示例数据进行演示')
  } finally {
    loading.value = false
  }
}

const updateCharts = (data) => {
  // 行业分布
  const industryCounts = {}
  data.forEach(stock => {
    industryCounts[stock.industry] = (industryCounts[stock.industry] || 0) + 1
  })
  
  industryDistributionOption.value.series[0].data = Object.entries(industryCounts).map(([name, value]) => ({
    name,
    value
  }))
  
  // 收益率分布
  const returnRanges = [0, 0, 0, 0, 0]
  data.forEach(stock => {
    const returnPercent = stock.predicted_return * 100
    if (returnPercent < -10) returnRanges[0]++
    else if (returnPercent < 0) returnRanges[1]++
    else if (returnPercent < 10) returnRanges[2]++
    else if (returnPercent < 20) returnRanges[3]++
    else returnRanges[4]++
  })
  
  returnDistributionOption.value.series[0].data = returnRanges
}

const exportResults = () => {
  ElMessage.success('导出功能开发中...')
}

const getRecommendation = (returnValue) => {
  if (returnValue > 0.15) return '强烈推荐'
  if (returnValue > 0.05) return '推荐'
  if (returnValue > -0.05) return '观望'
  return '谨慎'
}

const getRecommendationType = (returnValue) => {
  if (returnValue > 0.15) return 'success'
  if (returnValue > 0.05) return 'primary'
  if (returnValue > -0.05) return 'warning'
  return 'danger'
}

const loadSampleData = () => {
  const sampleData = []
  const industries = ['金融', '科技', '消费', '制造', '房地产', '医药']
  
  for (let i = 1; i <= 50; i++) {
    sampleData.push({
      ts_code: `600${i.toString().padStart(3, '0')}.SH`,
      industry: industries[Math.floor(Math.random() * industries.length)],
      predicted_return: Math.random() * 0.3 - 0.1,
      predicted_rank: i
    })
  }
  
  selectedStocks.value = sampleData
  updateCharts(sampleData)
}
</script>

<style scoped>
.stock-results {
  padding: 0;
}

.summary-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.filter-container {
  display: flex;
  align-items: center;
}

.summary-item {
  text-align: center;
  padding: 20px 0;
}

.summary-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.summary-value.positive {
  color: #67c23a;
}

.summary-label {
  font-size: 14px;
  color: #909399;
}

.chart-card {
  margin-bottom: 20px;
}

.chart {
  height: 300px;
  width: 100%;
}

.details-card {
  margin-top: 20px;
}

.positive {
  color: #f56c6c;
  font-weight: bold;
}

.negative {
  color: #67c23a;
  font-weight: bold;
}
</style>