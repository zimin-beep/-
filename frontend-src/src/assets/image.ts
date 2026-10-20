import axios from "axios";
const API_BASE = '/api'

// 格式化文件大小
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'
  var k = 1024
  var sizes = ['B', 'KB', 'MB', 'GB']
  var i = 0
  while (bytes >= k && i < sizes.length - 1) {
    bytes = bytes / k
    i = i + 1
  }
  return bytes.toFixed(2) + ' ' + sizes[i]
}

// 上传图片检测
export async function detectImage(file) {
  const fd = new FormData()
  fd.append('file', file) // 前后端字段名统一为 file

  const res = await axios.post(API_BASE + '/upload', fd)
  // axios 直接返回data，删除错误的 .json()
  return res.data
  
}

// 获取结果图URL（加时间戳防缓存）
export function getResultImageUrl(path) {
  if (!path) return ''
  // 已经是完整URL（如检测结果图），直接返回
  if (path.startsWith("http")) {
    return path + '?t=' + Date.now()
  }
  // 相对路径（如知识库图片），走Vite代理
  return path + '?t=' + Date.now()
}

// 批量检测（一次性传多个文件）
export async function batchDetectImages(files: File[]) {
  const fd = new FormData()
  files.forEach(f => fd.append('files', f))  // 注意字段名是 files（复数）

  const res = await axios.post(API_BASE + '/batch_upload', fd)
  return res.data
}