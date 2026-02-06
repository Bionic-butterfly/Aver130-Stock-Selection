<template>
  <div class="factor-analysis">
    <el-card class="analysis-card">
      <template #header>
        <div class="card-header">
          <span>因子IC值分析</span>
          <el-button type="primary" @click="refreshIC">刷新数据</el-button>
        </div>
      </template>
      
      <v-chart :option="icChartOption" class="chart" />
    </el-card>

    <el-row :gutter="20" class="detail-row">
      <el-col :span="12">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>因子详细信息</span>
            </div>
          </template>
          
          <el-table :data="factorDetails" stripe height="300">
            <el-table-column prop="factor" label="因子" width="120">
              <template #default="{ row }">
                <el-tag>{{ row.factor }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="ic_value" label="IC值" width="100">
              <template #default="{ row }">
                <span :class="{ 'positive': row.ic_value > 0, 'negative': row.ic_value < 0 }">
                  {{ row.ic_value.toFixed(4) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="有效性" width="100">
              <template #default="{ row }">
                <el-tag 
                  :type="Math.abs(row.ic_value) > 0.05 ? 'success' : 'warning'">
                  {{ Math.abs(row.ic_value) > 0.05 ? '有效' : '一般' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="detail-card">
          <template #header>
            <div class="card-header">
              <span>因子相关性矩阵</span>
            </div>
          </template>
          
          <v-chart :option="correlationOption" class="chart" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, HeatmapChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import apiService from '../api/index'

use([
  CanvasRenderer,
  BarChart,
  HeatmapChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent,
  VisualMapComponent
])

// 响应式数据
const factorDetails = ref([])

// 图表配置
const icChartOption = ref({
  title: { text: '因子IC值', left: 'center' },
  tooltip: {
    trigger: 'axis',
    formatter: (params) => {
      const data = params[0]
      return `${data.name}<br/>IC值: ${data.value.toFixed(4)}`
    }
  },
  xAxis: {
    type: 'category',
    data: []
  },
  yAxis: {
    type: 'value',
    min: -0.2,
    max: 0.2
  },
  series: [{
    data: [],
    type: 'bar',
    itemStyle: {
      color: (params) => {
        return params.value > 0 ? '#f56c6c' : '#67c23a'
      }
    }
  }]
})

const correlationOption = ref({
  title: { text: '因子相关性', left: 'center' },
  tooltip: {
    position: 'top',
    formatter: (params) => {
      return `${params.data[0]}: ${params.data[1].toFixed(3)}`
    }
  },
  grid: { height: '80%', top: '10%' },
  xAxis: {
    type: 'category',
    data: [],
    splitArea: { show: true }
  },
  yAxis: {
    type: 'category',
    data: [],
    splitArea: { show: true }
  },
  visualMap: {
    min: -1,
    max: 1,
    calculable: true,
    orient: 'horizontal',
    left: 'center',
    bottom: '0%'
  },
  series: [{
    name: '相关性',
    type: 'heatmap',
    data: [],
    label: { show: true },
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    }
  }]
})

// 生命周期
onMounted(() => {
  loadFactorData()
})

// 方法
const loadFactorData = async () => {
  try {
    const data = await apiService.getFactorIC()
    factorDetails.value = data
    
    // 更新IC值图表
    icChartOption.value.xAxis.data = data.map(item => item.description)
    icChartOption.value.series[0].data = data.map(item => item.ic_value)
    
    // 更新相关性矩阵（模拟数据）
    updateCorrelationMatrix(data)
    
  } catch (error) {
    console.error('加载因子数据失败:', error)
    ElMessage.error('因子数据加载失败')
    // 使用模拟数据
    loadSampleData()
  }
}

const refreshIC = () => {
  loadFactorData()
  ElMessage.success('因子数据已刷新')
}

const updateCorrelationMatrix = (factors) => {
  const factorNames = factors.map(f => f.factor)
  
  // 模拟相关性矩阵
  const correlations = []
  for (let i = 0; i < factorNames.length; i++) {
    for (let j = 0; j < factorNames.length; j++) {
      if (i === j) {
        correlations.push([i, j, 1.0])
      } else {
        correlations.push([i, j, Math.random() * 0.6 - 0.3]) // -0.3 到 0.3 的随机值
      }
    }
  }
  
  correlationOption.value.xAxis.data = factorNames
  correlationOption.value.yAxis.data = factorNames
  correlationOption.value.series[0].data = correlations
}

const loadSampleData = () => {
  // 示例数据
  factorDetails.value = [
    { factor: 'pe_ttm', description: '市盈率(TTM)', ic_value: 0.0823 },
    { factor: 'pb_lf', description: '市净率(LF)', ic_value: 0.0678 },
    { factor: 'roe', description: '净资产收益率', ic_value: 0.0956 },
    { factor: 'turnover_rate', description: '换手率', ic_value: -0.0432 },
    { factor: 'total_mv', description: '总市值', ic_value: -0.0289 }
  ]
  
  icChartOption.value.xAxis.data = factorDetails.value.map(item => item.description)
  icChartOption.value.series[0].data = factorDetails.value.map(item => item.ic_value)
  
  updateCorrelationMatrix(factorDetails.value)
}
</script>

<style scoped>
.factor-analysis {
  padding: 0;
}

.analysis-card {
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

.detail-row {
  margin-top: 20px;
}

.detail-card {
  margin-bottom: 20px;
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