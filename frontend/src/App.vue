<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 侧边栏导航 -->
      <el-aside width="250px" class="sidebar">
        <div class="logo">
          <h2>沪深300多因子选股</h2>
          <p>高级分析系统</p>
        </div>
        
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/">
            <el-icon><House /></el-icon>
            <span>系统概览</span>
          </el-menu-item>
          
          <el-sub-menu index="factor">
            <template #title>
              <el-icon><TrendCharts /></el-icon>
              <span>因子分析</span>
            </template>
            <el-menu-item index="/factor-industry">
              <el-icon><DataAnalysis /></el-icon>
              <span>分行业分析</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="model">
            <template #title>
              <el-icon><Cpu /></el-icon>
              <span>模型训练</span>
            </template>
            <el-menu-item index="/model-tuning">
              <el-icon><Setting /></el-icon>
              <span>参数调优</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="backtest">
            <template #title>
              <el-icon><Histogram /></el-icon>
              <span>回测分析</span>
            </template>
            <el-menu-item index="/risk-metrics">
              <el-icon><Monitor /></el-icon>
              <span>风险指标</span>
            </el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/logs">
            <el-icon><Document /></el-icon>
            <span>运行日志</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区域 -->
      <el-container>
        <el-header class="header">
          <div class="header-content">
            <div class="breadcrumb">
              <el-breadcrumb separator="/">
                <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
                <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="user-info">
              <el-button type="primary" @click="runQuantCore">
                <el-icon><VideoPlay /></el-icon>
                运行量化核心
              </el-button>
            </div>
          </div>
        </el-header>
        
        <el-main class="main-content">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'

export default {
  name: 'App',
  setup() {
    const route = useRoute()
    
    const currentRouteName = computed(() => {
      const routeNames = {
        '/': '系统概览',
        '/factor-industry': '因子分行业分析',
        '/model-tuning': '模型参数调优',
        '/risk-metrics': '风险指标详情',
        '/logs': '运行日志'
      }
      return routeNames[route.path] || '未知页面'
    })
    
    const runQuantCore = async () => {
      try {
        ElMessage.info('正在运行量化核心，请稍候...')
        // 这里可以调用后端API运行量化核心
        // 实际实现需要与后端集成
        setTimeout(() => {
          ElMessage.success('量化核心运行完成')
        }, 2000)
      } catch (error) {
        ElMessage.error('运行量化核心失败')
      }
    }
    
    return {
      currentRouteName,
      runQuantCore
    }
  }
}
</script>

<style>
#app {
  height: 100vh;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.app-container {
  height: 100%;
}

.sidebar {
  background-color: #304156;
  height: 100%;
}

.logo {
  padding: 20px;
  text-align: center;
  color: #fff;
  border-bottom: 1px solid #475669;
}

.logo h2 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.logo p {
  margin: 0;
  font-size: 12px;
  color: #bfcbd9;
}

.sidebar-menu {
  border: none;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
  padding: 0 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.main-content {
  padding: 20px;
  background-color: #f5f7fa;
}

.page-container {
  background: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}
</style>