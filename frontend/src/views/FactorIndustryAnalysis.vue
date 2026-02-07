<template>
  <div class="factor-industry-analysis">
    <div class="page-container">
      <h1>因子分行业有效性分析</h1>
      
      <!-- 筛选条件 -->
      <el-card class="filter-card" style="margin-bottom: 20px;">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-select v-model="selectedFactor" placeholder="选择因子" clearable style="width: 100%;">
              <el-option label="市盈率(PE)" value="pe_ttm"></el-option>
              <el-option label="市净率(PB)" value="pb_lf"></el-option>
              <el-option label="净资产收益率(ROE)" value="roe"></el-option>
              <el-option label="换手率" value="turnover_rate"></el-option>
              <el-option label="总市值" value="total_mv"></el-option>
            </el-select>
          </el-col>
          <el-col :span="6">
            <el-select v-model="selectedMetric" placeholder="选择指标" style="width: 100%;">
              <el-option label="IC均值" value="ic_mean"></el-option>
              <el-option label="IR信息比率" value="ir"></el-option>
              <el-option label="单调性" value="monotonicity"></el-option>
            </el-select>
          </el-col>
          <el-col :span="12">
            <el-button type="primary" @click="loadData">查询</el-button>
            <el-button @click="exportChart">导出图表</el-button>
            <el-button @click="exportData">导出数据</el-button>
          </el-col>
        </el-row>
      </el-card>
      
      <!-- 图表展示 -->
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>分行业因子有效性对比</span>
              </div>
            </template>
            
            <div ref="chart" style="width: 100%; height: 400px;"></div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>因子有效性排名</span>
              </div>
            </template>
            
            <div class="factor-ranking">
              <div 
                v-for="(factor, index) in factorRanking" 
                :key="factor.name"
                class="ranking-item"
              >
                <div class="rank">#{{ index + 1 }}</div>
                <div class="factor-name">{{ factor.name }}</div>
                <div class="factor-value">{{ factor.value.toFixed(4) }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <!-- 数据表格 -->
      <el-card style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>详细数据</span>
          </div>
        </template>
        
        <el-table 
          :data="tableData" 
          border 
          v-loading="loading"
          style="width: 100%;">
          <el-table-column prop="industry" label="行业" width="150"></el-table-column>
          <el-table-column prop="factor" label="因子" width="120">
            <template #default="scope">
              {{ getFactorName(scope.row.factor) }}
            </template>
          </el-table-column>
          <el-table-column prop="ic_mean" label="IC均值" width="100">
            <template #default="scope">
              {{ scope.row.ic_mean.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column prop="ic_std" label="IC标准差" width="100">
            <template #default="scope">
              {{ scope.row.ic_std.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column prop="ir" label="IR信息比率" width="100">
            <template #default="scope">
              {{ scope.row.ir.toFixed(4) }}
            </template>
          </el-table-column>
          <el-table-column prop="monotonicity" label="单调性" width="100">
            <template #default="scope">
              {{ scope.row.monotonicity.toFixed(4) }}
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

// 模拟API调用
const api = {
  getFactorIndustryData: () => Promise.resolve([
    { industry: '银行', factor: 'pe_ttm', ic_mean: 0.0456, ic_std: 0.0123, ir: 0.2345, monotonicity: 0.7890 },
    { industry: '银行', factor: 'pb_lf', ic_mean: 0.0321, ic_std: 0.0102, ir: 0.1987, monotonicity: 0.6543 },
    { industry: '证券', factor: 'pe_ttm', ic_mean: 0.0567, ic_std: 0.0154, ir: 0.2876, monotonicity: 0.8123 },
    { industry: '证券', factor: 'roe', ic_mean: 0.0678, ic_std: 0.0189, ir: 0.3456, monotonicity: 0.8765 },
    { industry: '医药生物', factor: 'pe_ttm', ic_mean: 0.0789, ic_std: 0.0201, ir: 0.3987, monotonicity: 0.9123 },
    { industry: '医药生物', factor: 'roe', ic_mean: 0.0890, ic_std: 0.0223, ir: 0.4567, monotonicity: 0.9345 },
    { industry: '电子', factor: 'turnover_rate', ic_mean: 0.0345, ic_std: 0.0112, ir: 0.1765, monotonicity: 0.7123 },
    { industry: '电子', factor: 'total_mv', ic_mean: 0.0234, ic_std: 0.0098, ir: 0.1234, monotonicity: 0.5987 }
  ])
}

export default {
  name: 'FactorIndustryAnalysis',
  setup() {
    const chart = ref(null)
    const tableData = ref([])
    const loading = ref(false)
    const selectedFactor = ref('')
    const selectedMetric = ref('ic_mean')
    const currentPage = ref(1)
    const pageSize = ref(10)
    const total = ref(0)
    const allData = ref([])
    const factorRanking = ref([])
    
    let echartsInstance = null
    
    const initChart = () => {
      if (chart.value) {
        echartsInstance = echarts.init(chart.value)
        window.addEventListener('resize', () => echartsInstance.resize())
      }
    }
    
    const loadData = async () => {
      loading.value = true
      try {
        const response = await api.getFactorIndustryData()
        allData.value = response
        total.value = allData.value.length
        updateTableData()
        updateChart()
        updateFactorRanking()
      } catch (error) {
        ElMessage.error('数据加载失败')
        console.error('加载因子行业分析数据失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const updateTableData = () => {
      const start = (currentPage.value - 1) * pageSize.value
      const end = start + pageSize.value
      
      let filteredData = allData.value
      if (selectedFactor.value) {
        filteredData = filteredData.filter(item => item.factor === selectedFactor.value)
      }
      
      tableData.value = filteredData.slice(start, end)
      total.value = filteredData.length
    }
    
    const updateChart = () => {
      if (!echartsInstance || allData.value.length === 0) return
      
      // 按行业分组数据
      const industryData = {}
      allData.value.forEach(item => {
        if (!industryData[item.industry]) {
          industryData[item.industry] = []
        }
        industryData[item.industry].push(item)
      })
      
      // 准备图表数据
      const industries = Object.keys(industryData)
      const seriesData = []
      const factors = [...new Set(allData.value.map(item => item.factor))]
      
      factors.forEach(factor => {
        const data = industries.map(industry => {
          const item = industryData[industry]?.find(d => d.factor === factor)
          return item ? item[selectedMetric.value] : 0
        })
        
        seriesData.push({
          name: getFactorName(factor),
          type: 'bar',
          data: data
        })
      })
      
      const option = {
        title: {
          text: `因子${getMetricName(selectedMetric.value)}分行业对比`,
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          }
        },
        legend: {
          data: factors.map(f => getFactorName(f)),
          top: 30
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          top: '20%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: industries,
          axisLabel: {
            rotate: 45
          }
        },
        yAxis: {
          type: 'value',
          name: getMetricName(selectedMetric.value)
        },
        series: seriesData
      }
      
      echartsInstance.setOption(option)
    }
    
    const updateFactorRanking = () => {
      // 计算各因子的平均IC值进行排名
      const factorStats = {}
      allData.value.forEach(item => {
        if (!factorStats[item.factor]) {
          factorStats[item.factor] = []
        }
        factorStats[item.factor].push(item.ic_mean)
      })
      
      factorRanking.value = Object.entries(factorStats)
        .map(([factor, values]) => ({
          name: getFactorName(factor),
          value: values.reduce((a, b) => a + b, 0) / values.length
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 5)
    }
    
    const getFactorName = (factor) => {
      const factorMap = {
        'pe_ttm': '市盈率(PE)',
        'pb_lf': '市净率(PB)',
        'roe': '净资产收益率(ROE)',
        'turnover_rate': '换手率',
        'total_mv': '总市值'
      }
      return factorMap[factor] || factor
    }
    
    const getMetricName = (metric) => {
      const metricMap = {
        'ic_mean': 'IC均值',
        'ir': 'IR信息比率',
        'monotonicity': '单调性'
      }
      return metricMap[metric] || metric
    }
    
    const handleSizeChange = (size) => {
      pageSize.value = size
      currentPage.value = 1
      updateTableData()
    }
    
    const handleCurrentChange = (page) => {
      currentPage.value = page
      updateTableData()
    }
    
    const exportChart = () => {
      if (!echartsInstance) return
      
      const chartDataURL = echartsInstance.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      
      const link = document.createElement('a')
      link.download = `因子分行业分析_${new Date().toISOString().split('T')[0]}.png`
      link.href = chartDataURL
      link.click()
      
      ElMessage.success('图表导出成功')
    }
    
    const exportData = () => {
      if (allData.value.length === 0) return
      
      const headers = ['行业', '因子', 'IC均值', 'IC标准差', 'IR信息比率', '单调性']
      const csvData = allData.value.map(item => [
        item.industry,
        getFactorName(item.factor),
        item.ic_mean.toFixed(4),
        item.ic_std.toFixed(4),
        item.ir.toFixed(4),
        item.monotonicity.toFixed(4)
      ])
      
      const csvContent = [headers, ...csvData]
        .map(row => row.join(','))
        .join('\n')
      
      const blob = new Blob(['\uFEFF' + csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = `因子行业分析_${new Date().toISOString().split('T')[0]}.csv`
      link.click()
      
      ElMessage.success('数据导出成功')
    }
    
    onMounted(() => {
      initChart()
      loadData()
    })
    
    watch(selectedMetric, () => {
      updateChart()
    })
    
    watch(selectedFactor, () => {
      updateTableData()
      updateChart()
    })
    
    return {
      chart,
      tableData,
      loading,
      selectedFactor,
      selectedMetric,
      currentPage,
      pageSize,
      total,
      factorRanking,
      loadData,
      handleSizeChange,
      handleCurrentChange,
      exportChart,
      exportData,
      getFactorName
    }
  }
}
</script>

<style scoped>
.factor-industry-analysis {
  padding: 0;
}

.filter-card {
  margin-bottom: 20px;
}

.factor-ranking {
  padding: 10px 0;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #ebeef5;
}

.ranking-item:last-child {
  border-bottom: none;
}

.rank {
  width: 40px;
  font-weight: bold;
  color: #409EFF;
}

.factor-name {
  flex: 1;
  color: #606266;
}

.factor-value {
  width: 80px;
  text-align: right;
  font-weight: bold;
  color: #303133;
}
</style>