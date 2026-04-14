import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建 axios 实例
const request = axios.create({
  baseURL: '/api', // 这里会触发我们在 vite.config.ts 中配置的代理
  timeout: 10000,
})

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    // 如果有登录 Token，可以在这里自动带上
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 直接返回数据部分，简化组件中的调用逻辑
    return response.data
  },
  (error) => {
    ElMessage.error(error.response?.data?.message || '网络或服务器异常，请检查后端是否启动')
    return Promise.reject(error)
  }
)

export default request
