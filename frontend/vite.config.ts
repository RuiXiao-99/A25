import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    open: true, // 启动时自动打开浏览器
    proxy: {
      // 将所有 /api 开头的请求代理到你的后端 Python 服务
      '/api': {
        target: 'http://localhost:8000', 
        changeOrigin: true,
        // 如果后端接口本身没有 /api 前缀，可以开启下面这行重写路径：
        // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
