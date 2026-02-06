<template>
  <div class="model-predictions">
    <el-card class="control-card">
      <template #header>
        <div class="card-header">
          <span>模型预测控制</span>
        </div>
      </template>
      
      <el-form :model="controlForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="选股数量">
              <el-input-number 
                v-model="controlForm.topN" 
                :min="10" 
                :max="100" 
                :step="10" 
                controls-position="right" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="行业筛选">
              <el-select v-model="controlForm.industry" placeholder="全部行业" clearable>
                <el-option 
                  v-for="industry in industries" 
                  :key="industry" 
                  :label="industry" 
                  :value="industry" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <el-button type="primary" @click="loadPredictions">执行预测</el-button>
              <el-button @click="resetForm">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <el-card class="results-card">
      <template #header>
        <div class="card-header">
          <span>预测结果</span>
          <div class="result-stats">
            <span>平均预测收益率: <strong>{{ avgReturn }}</strong></span>
            <span>最高预测收益率: <strong>{{ maxReturn }}</strong></span>
          </div>
        </div>
      </template>
      
      <el-table :data="predictions" stripe height="400" v-loading="loading">
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
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="text" @click="viewStockDetail(row)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange" />
      </div>
    </el-card>

    <!-- 股票详情对话框 -->
    <el-dialog v-model="detailVisible" title="股票详情" width="600px">
      <div v-if="selectedStock">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="股票代码">{{ selectedStock.ts_code }}</el-descriptions-item>
          <el-descriptions-item label="行业">{{ selectedStock.industry }}</el-descriptions-item>
          <el-descriptions-item label="预测收益率">
            <span :class="{ 'positive': selectedStock.predicted_return > 0, 'negative': selectedStock.predicted_return < 0 }">
              {{ (selectedStock.predicted_return * 100).toFixed(2) }}%
            </span>
          </el-descriptions-item>
          <el-descriptions-item label="排名">{{ selectedStock.predicted_rank }}</el-descriptions-item>
        </el-descriptions>
        
        <div class="factor-details">
          <h4>因子值（标准化后）</h4>
          <el-table :data="factorData" size="small">
            <el-table-column prop="name" label="因子" />
            <el-table-column prop="value" label="值" />
          </el-table>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import apiService from '../api/index'

// 响应式数据
const controlForm = ref({
  topN: 50,
  industry: ''
})

const predictions = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const detailVisible = ref(false)
const selectedStock = ref(null)

const industries = ref(['金融', '科技', '消费', '制造', '房地产', '医药', '其他'])

// 计算属性
const avgReturn = computed(() => {
  if (predictions.value.length === 0) return '0.00%'
  const avg = predictions.value.reduce((sum, item) => sum + item.predicted_return, 0) / predictions.value.length
  return (avg * 100).toFixed(2) + '%'
})

const maxReturn = computed(() => {
  if (predictions.value.length === 0) return '0.00%'
  const max = Math.max(...predictions.value.map(item => item.predicted_return))
  return (max * 100).toFixed(2) + '%'
})

// 因子数据（模拟）
const factorData = ref([
  { name: 'PE(TTM)', value: '0.85' },
  { name: 'PB(LF)', value: '1.23' },
  { name: 'ROE', value: '0.92' },
  { name: '换手率', value: '-0.45' },
  { name: '总市值', value: '-0.67' }
])

// 生命周期
onMounted(() => {
  loadPredictions()
})

// 方法
const loadPredictions = async () => {
  try {
    loading.value = true
    const data = await apiService.getTopPredictions(controlForm.value.topN)
    
    // 过滤行业
    let filteredData = data
    if (controlForm.value.industry) {
      filteredData = data.filter(item => item.industry === controlForm.value.industry)
    }
    
    predictions.value = filteredData
    total.value = filteredData.length
    
    ElMessage.success(`成功加载 ${filteredData.length} 条预测结果`)
  } catch (error) {
    console.error('加载预测结果失败:', error)
    // 使用模拟数据
    loadSampleData()
    ElMessage.warning('使用示例数据进行演示')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  controlForm.value = {
    topN: 50,
    industry: ''
  }
  loadPredictions()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page) => {
  currentPage.value = page
}

const viewStockDetail = (stock) => {
  selectedStock.value = stock
  detailVisible.value = true
}

const loadSampleData = () => {
  // 模拟数据
  const sampleData = []
  const sampleIndustries = ['金融', '科技', '消费', '制造', '房地产']
  
  for (let i = 1; i <= controlForm.value.topN; i++) {
    sampleData.push({
      ts_code: `600${i.toString().padStart(3, '0')}.SH`,
      industry: sampleIndustries[Math.floor(Math.random() * sampleIndustries.length)],
      predicted_return: Math.random() * 0.3 - 0.1, // -10% 到 20%
      predicted_rank: i
    })
  }
  
  // 按预测收益率排序
  sampleData.sort((a, b) => b.predicted_return - a.predicted_return)
  
  predictions.value = sampleData
  total.value = sampleData.length
}
</script>

<style scoped>
.model-predictions {
  padding: 0;
}

.control-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  font-size: 16px;
}

.result-stats {
  display: flex;
  gap: 20px;
  font-size: 14px;
}

.results-card {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.positive {
  color: #f56c6c;
  font-weight: bold;
}

.negative {
  color: #67c23a;
  font-weight: bold;
}

.factor-details {
  margin-top: 20px;
}

.factor-details h4 {
  margin-bottom: 10px;
  color: #606266;
}
</style>