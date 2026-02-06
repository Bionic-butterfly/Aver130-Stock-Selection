import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// API接口定义
export const apiService = {
  // 系统状态
  getSystemStatus() {
    return api.get('/')
  },
  
  // 数据概览
  getDataOverview() {
    return api.get('/data/overview')
  },
  
  // 因子分析
  getFactorIC() {
    return api.get('/factors/ic')
  },
  
  // 模型预测
  getTopPredictions(topN = 50) {
    return api.get(`/predictions/top/${topN}`)
  },
  
  // 回测结果
  getBacktestResults() {
    return api.get('/backtest/results')
  },
  
  // 自定义预测
  predictCustomStocks(factorData) {
    return api.post('/predict/custom', factorData)
  }
}

export default apiService