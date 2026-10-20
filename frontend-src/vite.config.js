import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    host: '127.0.0.1',
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        ws: true,
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes, req, res) => {
            const ct = proxyRes.headers['content-type'] || ''
            if (ct.includes('x-mixed-replace') || ct.includes('multipart/')) {
              proxyRes.headers['cache-control'] = 'no-cache'
              proxyRes.headers['x-accel-buffering'] = 'no'
              res.setHeader('Cache-Control', 'no-cache')
              res.setHeader('X-Accel-Buffering', 'no')
            }
          })
        }
      },
      '/pases': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true
      }
    }
  }
})