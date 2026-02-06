<template>
  <div class="data-overview">
    <el-row :gutter="20">
      <!-- 数据统计卡片 -->
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: stat.color }">
              <el-icon><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-title">{{ stat.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 数据图表 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>数据时间分布</span>
            </div>
          </template>
          <v-chart :option="timeDistributionOption" class="chart" />
        </el-card>
      </el-col>
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
    </el-row>

    <!-- 系统状态 -->
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <span>系统状态</span>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="后端服务">
          <el-tag :type="systemStatus.status === 'running' ? 'success' : 'danger'">
            {{ systemStatus.status === 'running' ? '运行中' : '未连接' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="模型状态">
          <el-tag :type="systemStatus.model_status === 'loaded' ? 'success' : 'warning'">
            {{ systemStatus.model_status === 'loaded' ? '已加载' : '未加载' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="数据文件">
          {{ systemStatus.data_files?.length || 0 }} 个
        </el-descriptions-item>
        <el-descriptions-item label="最后更新">
          {{ lastUpdateTime }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  TrendCharts,
  DataBoard,
  Coin,
  Histogram
} from '@element-plus/icons-vue'
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
const stats = ref([
  { title: '总记录数', value: '0', icon: DataBoard, color: '#409eff' },
  { title: '股票数量', value: '0', icon: Coin, color: '#67c23a' },
  { title: '行业数量', value: '0', icon: Histogram, color: '#e6a23c' },
  { title: '因子数量', value: '5', icon: TrendCharts, color: '#f56c6c' }
])

const systemStatus = ref({
  status: 'unknown',
  message: '',
  data_files: [],
  model_status: 'unknown'
})

const lastUpdateTime = ref('-')

// 图表配置
const timeDistributionOption = ref({
  title: { text: '数据时间分布', left: 'center' },
  tooltip: { trigger: 'axis' },
  xAxis: {
    type: 'category',
    data: ['2018', '2019', '2020', '2021', '2022', '2023']
  },
  yAxis: { type: 'value' },
  series: [{
    data: [120, 200, 150, 80, 70, 110],
    type: 'bar',
    itemStyle: { color: '#409eff' }
  }]
})

const industryDistributionOption = ref({
  title: { text: '行业分布', left: 'center' },
  tooltip: { trigger: 'item' },
  legend: { orient: 'vertical', right: 10, top: 'center' },
  series: [{
    type: 'pie',
    radius: ['40%', '70%'],
    data: [
      { value: 35, name: '金融' },
      { value: 25, name: '科技' },
      { value: 20, name: '消费' },
      { value: 15, name: '制造' },
      { value: 5, name: '其他' }
    ],
    emphasis: {
      itemStyle: {
        shadowBlur: 10,
        shadowOffsetX: 0,
        shadowColor: 'rgba(0, 0, 0, 0.5)'
      }
    }
  }]
})

// 生命周期
onMounted(() => {
  loadDataOverview()
  loadSystemStatus()
})

// 方法
const loadDataOverview = async () => {
  try {
    const data = await apiService.getDataOverview()
    if (data.total_records) {
      stats.value[0].value = data.total_records.toLocaleString()
      stats.value[1].value = data.unique_stocks?.toLocaleString() || '300'
      stats.value[2].value = data.industries?.toLocaleString() || '10'
    }
  } catch (error) {
    console.error('加载数据概览失败:', error)
    ElMessage.error('数据概览加载失败')
  }
}

const loadSystemStatus = async () => {
  try {
    const status = await apiService.getSystemStatus()
    systemStatus.value = status
    lastUpdateTime.value = new Date().toLocaleString()
  } catch (error) {
    console.error('加载系统状态失败:', error)
    systemStatus.value.status = 'error'
    ElMessage.error('后端服务连接失败')
  }
}
</script>

<style scoped>
.data-overview {
  padding: 0;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.chart-row {
  margin-top: 20px;
}

.chart-card {
  margin-bottom: 20px;
}

.card-header {
  font-weight: bold;
  font-size: 16px;
}

.chart {
  height: 300px;
  width: 100%;
}

.status-card {
  margin-top: 20px;
}
</style>