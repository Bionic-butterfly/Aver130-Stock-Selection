import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/overview'
    },
    {
      path: '/overview',
      name: 'overview',
      component: () => import('../components/DataOverview.vue')
    },
    {
      path: '/factors',
      name: 'factors',
      component: () => import('../components/FactorAnalysis.vue')
    },
    {
      path: '/predictions',
      name: 'predictions',
      component: () => import('../components/ModelPredictions.vue')
    },
    {
      path: '/results',
      name: 'results',
      component: () => import('../components/StockResults.vue')
    },
    {
      path: '/backtest',
      name: 'backtest',
      component: () => import('../components/BacktestComparison.vue')
    }
  ]
})

export default router