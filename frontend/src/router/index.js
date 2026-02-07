import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
import Dashboard from '../views/Dashboard.vue'
import FactorIndustryAnalysis from '../views/FactorIndustryAnalysis.vue'
import RiskMetrics from '../views/RiskMetrics.vue'
import ModelTuning from '../views/ModelTuning.vue'
import TrainingLogs from '../views/TrainingLogs.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '系统概览' }
  },
  {
    path: '/factor-industry',
    name: 'FactorIndustryAnalysis',
    component: FactorIndustryAnalysis,
    meta: { title: '因子分行业分析' }
  },
  {
    path: '/risk-metrics',
    name: 'RiskMetrics',
    component: RiskMetrics,
    meta: { title: '风险指标详情' }
  },
  {
    path: '/model-tuning',
    name: 'ModelTuning',
    component: ModelTuning,
    meta: { title: '模型参数调优' }
  },
  {
    path: '/logs',
    name: 'TrainingLogs',
    component: TrainingLogs,
    meta: { title: '运行日志' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = `${to.meta.title} - 沪深300多因子选股系统`
  }
  next()
})

export default router