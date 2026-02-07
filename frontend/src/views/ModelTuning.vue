<template>
  <div class="model-tuning">
    <div class="page-container">
      <h1>模型参数调优</h1>
      
      <!-- 参数调优结果卡片 -->
      <el-card class="tuning-summary-card" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>XGBoost参数调优结果</span>
            <el-button type="primary" size="small" @click="refreshData" :loading="loading">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </div>
        </template>
        
        <div class="tuning-stats">
          <el-statistic title="最佳学习率" :value="bestParams.learning_rate" suffix="">
            <template #suffix>
              <span class="stat-suffix">/ 最佳树数量: {{ bestParams.n_estimators }}</span>
            </template>
          </el-statistic>
          
          <el-statistic title="最佳测试集R²" :value="bestScore" suffix="">
            <template #suffix>
              <span class="stat-suffix">/ 最佳排名: {{ bestRank }}</span>
            </template>
          </el-statistic>
        </div>
      </el-card>
      
      <!-- 参数调优图表 -->
      <el-card class="chart-card" style="margin-bottom: 20px;">
        <template #header>
          <div class="card-header">
            <span>参数组合性能对比</span>
            <el-button type="primary" size="small" @click="exportChart">
              <el-icon><Download /></el-icon>
              导出图表
            </el-button>
          </div>
        </template>
        
        <div ref="tuningChart" style="width: 100%; height: 400px;"></div>
      </el-card>
      
      <!-- 参数调优表格 -->
      <el-card>
        <template #header>
          <div class="card-header">
            <span>参数组合详细结果</span>
            <el-button type="success" size="small" @click="exportData">
              <el-icon><Download /></el-icon>
              导出数据
            </el-button>
          </div>
        </template>
        
        <el-table 
          :data="tuningResults" 
          border 
          style="width: 100%;"
          v-loading="loading">
          <el-table-column prop="rank" label="排名" width="80">
            <template #default="scope">
              <el-tag :type="scope.row.rank === 1 ? 'success' : 'info'">
                {{ scope.row.rank }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="learning_rate" label="学习率" width="120"></el-table-column>
          <el-table-column prop="n_estimators" label="树数量" width="100"></el-table-column>
          <el-table-column prop="train_score" label="训练集R²">
            <template #default="scope">
              {{ scope.row.train_score.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column prop="test_score" label="测试集R²">
            <template #default="scope">
              <span :class="{ 'best-score': scope.row.rank === 1 }">
                {{ scope.row.test_score.toFixed(4) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="性能差异">
            <template #default="scope">
              <span :class="{ 'overfitting': scope.row.train_score - scope.row.test_score > 0.1 }">
                {{ (scope.row.train_score - scope.row.test_score).toFixed(4) }}
              </span>
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
  name: 'ModelTuning',
  setup() {
    const tuningResults = ref([])
    const loading = ref(false)
    const tuningChart = ref(null)
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const bestParams = ref({ learning_rate: 0, n_estimators: 0 })
    const bestScore = ref(0)
    const bestRank = ref(0)
    let echartsInstance = null
    
    const loadTuningResults = async () => {
      loading.value = true
      try {
        const data = await apiService.getModelTuningResults(20)
        tuningResults.value = data
        total.value = data.length
        
        if (data.length > 0) {
          const bestResult = data[0]
          bestParams.value = {
            learning_rate: bestResult.learning_rate,
            n_estimators: bestResult.n_estimators
          }
          bestScore.value = bestResult.test_score
          bestRank.value = bestResult.rank
        }
        
        ElMessage.success('模型参数调优结果加载成功')
      } catch (error) {
        ElMessage.error('模型参数调优结果加载失败')
        console.error('加载调优结果失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const refreshData = async () => {
      await loadTuningResults()
      initChart()
    }
    
    const initChart = () => {
      if (tuningChart.value) {
        echartsInstance = echarts.init(tuningChart.value)
        window.addEventListener('resize', () => echartsInstance.resize())
        updateChart()
      }
    }
    
    const updateChart = () => {
      if (!echartsInstance || tuningResults.value.length === 0) return
      
      // 准备图表数据
      const learningRates = [...new Set(tuningResults.value.map(item => item.learning_rate))].sort()
      const nEstimators = [...new Set(tuningResults.value.map(item => item.n_estimators))].sort()
      
      // 构建热力图数据
      const heatmapData = []
      const seriesData = []
      
      tuningResults.value.forEach(item => {
        const lrIndex = learningRates.indexOf(item.learning_rate)
        const neIndex = nEstimators.indexOf(item.n_estimators)
        heatmapData.push([lrIndex, neIndex, item.test_score])
        seriesData.push({
          name: `学习率: ${item.learning_rate}, 树数量: ${item.n_estimators}`,
          type: 'scatter',
          xAxisIndex: 0,
          yAxisIndex: 0,
          data: [[item.learning_rate, item.n_estimators]],
          symbolSize: item.test_score * 100,
          itemStyle: {
            color: `rgba(64, 158, 255, ${item.test_score})`
          },
          label: {
            show: true,
            formatter: `{c}`,
            position: 'top'
          }
        })
      })
      
      const option = {
        title: {
          text: 'XGBoost参数组合性能热力图',
          left: 'center'
        },
        tooltip: {
          position: 'top'
        },
        legend: {
          data: ['测试集R²'],
          bottom: 10
        },
        grid: {
          height: '60%',
          top: '10%'
        },
        xAxis: {
          type: 'category',
          data: learningRates,
          splitArea: {
            show: true
          },
          name: '学习率'
        },
        yAxis: {
          type: 'category',
          data: nEstimators,
          splitArea: {
            show: true
          },
          name: '树数量'
        },
        visualMap: {
          min: Math.min(...tuningResults.value.map(item => item.test_score)),
          max: Math.max(...tuningResults.value.map(item => item.test_score)),
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: '15%',
          inRange: {
            color: ['#e0f2ff', '#409EFF', '#0066cc']
          }
        },
        series: [{
          name: '测试集R²',
          type: 'heatmap',
          data: heatmapData,
          label: {
            show: true,
            formatter: function(params) {
              return params.value[2].toFixed(4)
            }
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
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
        link.download = `参数调优热力图_${new Date().toISOString().split('T')[0]}.png`
        link.href = chartDataURL
        link.click()
        
        ElMessage.success('图表导出成功')
      }
    }
    
    const exportData = () => {
      if (tuningResults.value.length === 0) return
      
      const headers = ['排名', '学习率', '树数量', '训练集R²', '测试集R²', '性能差异']
      const csvData = tuningResults.value.map(item => [
        item.rank,
        item.learning_rate,
        item.n_estimators,
        item.train_score.toFixed(4),
        item.test_score.toFixed(4),
        (item.train_score - item.test_score).toFixed(4)
      ])
      
      const csvContent = [headers, ...csvData]
        .map(row => row.join(','))
        .join('\n')
      
      const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `参数调优结果_${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      
      ElMessage.success('数据导出成功')
    }
    
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
    }
    
    onMounted(() => {
      loadTuningResults()
      initChart()
    })
    
    watch(tuningResults, () => {
      updateChart()
    }, { deep: true })
    
    return {
      tuningResults,
      loading,
      tuningChart,
      currentPage,
      pageSize,
      total,
      bestParams,
      bestScore,
      bestRank,
      refreshData,
      exportChart,
      exportData,
      handleSizeChange,
      handleCurrentChange
    }
  }
}
</script>

<style scoped>
.model-tuning {
  padding: 0;
}

.tuning-stats {
  display: flex;
  gap: 40px;
  margin: 20px 0;
}

.stat-suffix {
  font-size: 14px;
  color: #606266;
  margin-left: 10px;
}

.best-score {
  font-weight: bold;
  color: #67C23A;
}

.overfitting {
  color: #F56C6C;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .tuning-stats {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
