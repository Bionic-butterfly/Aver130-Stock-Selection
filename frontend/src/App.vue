<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 头部导航 -->
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="title">
            <el-icon><TrendCharts /></el-icon>
            沪深300多因子选股系统
          </h1>
          <div class="nav-tabs">
            <el-tabs v-model="activeTab" @tab-click="handleTabClick">
              <el-tab-pane label="数据概览" name="overview"></el-tab-pane>
              <el-tab-pane label="因子分析" name="factors"></el-tab-pane>
              <el-tab-pane label="模型预测" name="predictions"></el-tab-pane>
              <el-tab-pane label="选股结果" name="results"></el-tab-pane>
              <el-tab-pane label="回测对比" name="backtest"></el-tab-pane>
            </el-tabs>
          </div>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <el-main class="app-main">
        <!-- 数据概览页面 -->
        <div v-if="activeTab === 'overview'" class="page-content">
          <DataOverview />
        </div>

        <!-- 因子分析页面 -->
        <div v-if="activeTab === 'factors'" class="page-content">
          <FactorAnalysis />
        </div>

        <!-- 模型预测页面 -->
        <div v-if="activeTab === 'predictions'" class="page-content">
          <ModelPredictions />
        </div>

        <!-- 选股结果页面 -->
        <div v-if="activeTab === 'results'" class="page-content">
          <StockResults />
        </div>

        <!-- 回测对比页面 -->
        <div v-if="activeTab === 'backtest'" class="page-content">
          <BacktestComparison />
        </div>
      </el-main>

      <!-- 底部信息 -->
      <el-footer class="app-footer">
        <div class="footer-content">
          <span>沪深300多因子选股系统 - 毕业设计项目</span>
          <span>基于行业中性化+XGBoost算法</span>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import DataOverview from './components/DataOverview.vue'
import FactorAnalysis from './components/FactorAnalysis.vue'
import ModelPredictions from './components/ModelPredictions.vue'
import StockResults from './components/StockResults.vue'
import BacktestComparison from './components/BacktestComparison.vue'

// 响应式数据
const activeTab = ref('overview')

// 生命周期
onMounted(() => {
  console.log('应用已加载')
})

// 方法
const handleTabClick = (tab) => {
  console.log('切换到标签:', tab.paneName)
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  background: #f5f7fa;
}

.app-header {
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  padding: 0 20px;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  margin: 0;
  color: #409eff;
  font-size: 24px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-tabs {
  flex: 1;
  margin-left: 40px;
}

:deep(.el-tabs__header) {
  margin: 0;
}

:deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.app-main {
  padding: 20px;
  overflow-y: auto;
}

.page-content {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  min-height: 600px;
}

.app-footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-content {
  display: flex;
  gap: 40px;
  color: #909399;
  font-size: 14px;
}
</style>