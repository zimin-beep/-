<template>
  <div class="page page-detection active">
    <!-- 顶部切换Tab：上传/摄像头/批量 -->
    <div class="detect-options">
      <button
        class="detect-tab"
        :class="{ active: detectTab === 'upload' }"
        @click="detectTab = 'upload'"
      >
        📷 图片上传检测
      </button>
      <button
        class="detect-tab"
        :class="{ active: detectTab === 'camera' }"
        @click="detectTab = 'camera'"
      >
        📹 实时拍摄检测
      </button>
      <button
        class="detect-tab"
        :class="{ active: detectTab === 'batch' }"
        @click="detectTab = 'batch'"
      >
        📁 批量检测
      </button>
      <button
        v-if="isAdmin"
        class="detect-tab"
        :class="{ active: detectTab === 'model' }"
        @click="detectTab = 'model'"
      >
        ⚙️ 模型配置
      </button>
    </div>

    <!-- 上传Tab：完整图片上传+预览+检测结果面板 -->
    <div class="upload-section" v-if="detectTab === 'upload'">
      <!-- 隐藏原生文件输入框 -->
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        style="display: none"
        @change="getfile"
      />
      <!-- 虚线上传区域 -->
      <div class="upload-area" @click="triggerUpload">
        <div v-if="!previewUrl" class="upload-placeholder">
          <div class="upload-icon">📁</div>
          <p>点击选择图片</p>
          <span class="upload-hint">支持 JPG、PNG、JPEG 格式</span>
        </div>
        <img v-else :src="previewUrl" class="preview-image" alt="预览图" />
      </div>

      <!-- 选中文件信息 -->
      <div v-if="file" class="file-info">
        <span>📄 {{ file.name }}</span>
        <span class="file-size">{{ formatFileSize(file.size) }}</span>
      </div>

      <!-- 操作按钮 -->
      <div class="action-section">
        <button class="btn-start" :disabled="!file || processing" @click="detect">
          <span v-if="processing">⏳ 检测中...</span>
          <span v-else>🚀 开始检测</span>
        </button>
        <button class="btn-reset" @click="clearCache">重置</button>
      </div>

      <!-- AI检测结果面板（标注图+目标列表） -->
      <div v-if="outputUrl" class="output-section">
        <h2>✅ 检测结果</h2>
        <div class="analysis-layout">
          <!-- 左侧标注结果图 -->
          <div class="result-image-wrapper">
            <img :src="outputUrl" class="result-image" alt="检测结果" />
            <div class="image-legend">🔴 红色数字 = 右侧列表编号</div>
          </div>
          <!-- 右侧识别目标列表 -->
          <div class="objects-panel">
            <div class="panel-header">
              <h3>📊 检测目标列表</h3>
              <span class="panel-count">{{ analysisResult?.summary?.total || 0 }} 个</span>
            </div>
            <div class="objects-list">
              <div
                v-for="obj in displayedObjects"
                :key="obj.id"
                class="obj-card-mini"
                :class="{ active: activeObject === obj.id }"
                @mouseenter="activeObject = obj.id"
                @mouseleave="activeObject = null"
              >
                <div class="obj-num" :style="{ background: getLevelColor(obj.judgment.level) }">
                  {{ obj.id }}
                </div>
                <div class="obj-info">
                  <div class="obj-name">{{ obj.name_cn }}</div>
                  <div class="obj-meta">
                    <span class="conf-text">{{ obj.confidence_percent }}</span>
                    <span class="pos-text">{{ obj.position?.description }}</span>
                  </div>
                  <div class="conf-bar-mini">
                    <div
                      class="conf-fill-mini"
                      :style="{ width: obj.confidence * 100 + '%', background: getLevelColor(obj.judgment.level) }"
                    ></div>
                  </div>
                </div>
                <div class="obj-level-badge" :style="{ color: getLevelColor(obj.judgment.level) }">
                  {{ obj.judgment.level }}
                </div>
              </div>
            </div>
            <!-- 展开/收起按钮 -->
            <div v-if="analysisResult?.detected_objects?.length > 5" class="panel-footer">
              <button class="btn-expand" @click="showAll = !showAll">
                {{ showAll ? '↑ 收起' : '↓ 展开全部' }}
              </button>
            </div>
          </div>
        </div>
        </div>

        <!-- 治理方法展示 -->
        <div v-if="Object.keys(treatments).length > 0" class="treatment-section">
          <h3>💡 治理方法参考</h3>
          <div v-for="(info, name) in treatments" :key="name" class="treatment-card">
            <div class="treatment-name">{{ name }}</div>
            <div v-if="info.symptom" class="treatment-row">
              <span class="treatment-label">症状：</span>{{ info.symptom }}
            </div>
            <div v-if="info.treatment" class="treatment-row">
              <span class="treatment-label">治理：</span>{{ info.treatment }}
            </div>
          </div>
        </div>

    </div>
    

    <!-- 摄像头Tab：后端 RTSP 实时视频流 -->
    <div class="upload-section" v-if="detectTab === 'camera'">

      <div class="upload-area" v-if="!cameraActive" @click="startCamera">
        <div class="upload-icon">📹</div>
        <h3>摄像头实时检测</h3>
        <p>开启后端摄像头视频流，系统将实时分析画面中的病虫害</p>
      </div>
      <div v-if="!cameraActive" class="action-section">
        <button class="btn-start" :disabled="cameraLoading" @click.stop="startCamera">
          <span v-if="cameraLoading">⏳ 连接中...</span>
          <span v-else>📹 开启实时检测</span>
        </button>
        <button class="btn-reset" @click="stopCamera">关闭</button>
      </div>
      
      <div v-if="cameraActive" class="camera-section">
        <!-- 后端 MJPEG 视频流 -->
        <div class="video-stream-wrapper">
          <img :src="videoStreamUrl" class="video-stream" alt="实时视频流" @error="onStreamError" />
          <div class="stream-status">
            <span class="dot" :class="{ live: cameraActive }"></span>
            实时检测中
          </div>
        </div>
        <!-- 云台方向控制 -->
        <div class="ptz-container">
          <h3 class="ptz-title">🔄 云台控制 <span class="ptz-tip">(长按方向键转动，松开停止)</span></h3>

          <!-- 十字方向按键区域 3x3 -->
          <div class="ptz-cross">
            <div></div>
            <button class="ptz-btn dir-btn"
              @mousedown="ptzMove('up')"
              @mouseup="ptzStop"
              @mouseleave="ptzStop"
              @touchstart.prevent="ptzMove('up')"
              @touchend.prevent="ptzStop"
              @touchcancel.prevent="ptzStop"
              @contextmenu.prevent
            >▲</button>
            <div></div>

            <button class="ptz-btn dir-btn"
              @mousedown="ptzMove('left')"
              @mouseup="ptzStop"
              @mouseleave="ptzStop"
              @touchstart.prevent="ptzMove('left')"
              @touchend.prevent="ptzStop"
              @touchcancel.prevent="ptzStop"
              @contextmenu.prevent
            >◀</button>
            <button class="ptz-btn stop-center" @click="ptzStop">■</button>
            <button class="ptz-btn dir-btn"
              @mousedown="ptzMove('right')"
              @mouseup="ptzStop"
              @mouseleave="ptzStop"
              @touchstart.prevent="ptzMove('right')"
              @touchend.prevent="ptzStop"
              @touchcancel.prevent="ptzStop"
              @contextmenu.prevent
            >▶</button>

            <div></div>
            <button class="ptz-btn dir-btn"
              @mousedown="ptzMove('down')"
              @mouseup="ptzStop"
              @mouseleave="ptzStop"
              @touchstart.prevent="ptzMove('down')"
              @touchend.prevent="ptzStop"
              @touchcancel.prevent="ptzStop"
              @contextmenu.prevent
            >▼</button>
            <div></div>
          </div>

          <!-- 变焦 -->
          <div class="ptz-zoom">
            <button class="ptz-btn zoom-btn"
              @mousedown="ptzMove('zoom_out')"
              @mouseup="ptzStop"
              @mouseleave="ptzStop"
              @touchstart.prevent="ptzMove('zoom_out')"
              @touchend.prevent="ptzStop"
              @touchcancel.prevent="ptzStop"
              @contextmenu.prevent
            >−</button>
            <button class="ptz-btn zoom-btn"
              @mousedown="ptzMove('zoom_in')"
              @mouseup="ptzStop"
              @mouseleave="ptzStop"
              @touchstart.prevent="ptzMove('zoom_in')"
              @touchend.prevent="ptzStop"
              @touchcancel.prevent="ptzStop"
              @contextmenu.prevent
            >＋</button>
          </div>

          <!-- 停止检测按钮 -->
          <div class="ptz-detect">
            <button class="ptz-detect-btn" :disabled="cameraLoading" @click="stopCamera">
              <span v-if="cameraLoading">⏳ 停止中...</span>
              <span v-else>停止检测</span>
            </button>
            <div class="ptz-detect-tip">⌛ 等待检测数据...</div>
          </div>
        </div>
        <!-- 实时检测结果 -->
        <div v-if="cameraAnalysis" class="output-section">
          <h2>✅ 实时检测结果</h2>
          <div class="analysis-layout">
            <div class="objects-panel" style="width:100%;">
              <div class="panel-header">
                <h3>📊 检测目标列表</h3>
                <span class="panel-count">{{ cameraAnalysis?.summary?.total || 0 }} 个</span>
              </div>
              <div class="objects-list">
                <div
                  v-for="obj in cameraAnalysis?.detected_objects || []"
                  :key="obj.id"
                  class="obj-card-mini"
                >
                  <div class="obj-num" :style="{ background: getLevelColor(obj.judgment.level) }">
                    {{ obj.id }}
                  </div>
                  <div class="obj-info">
                    <div class="obj-name">{{ obj.name_cn }}</div>
                    <div class="obj-meta">
                      <span class="conf-text">{{ obj.confidence_percent }}</span>
                      <span class="pos-text">{{ obj.position?.description }}</span>
                    </div>
                  </div>
                  <div class="obj-level-badge" :style="{ color: getLevelColor(obj.judgment.level) }">
                    {{ obj.judgment.level }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="cameraActive" class="empty-tip" style="text-align:center;padding:20px;color:#656d76;">
          ⏳ 等待检测数据...
        </div>
      </div>
    </div>

    <!-- 批量检测Tab -->
    <div class="upload-section" v-if="detectTab === 'batch'">
      <input
        ref="batchFileInput"
        type="file"
        accept="image/*"
        multiple
        style="display: none"
        @change="getBatchFiles"
      />
      <div class="upload-area" @click="triggerBatchUpload">
        <div class="upload-icon">📁</div>
        <h3>批量上传图片进行检测</h3>
        <p>可同时选择多张图片，系统将逐一分析并生成报告</p>
        <span class="upload-hint">支持 JPG、PNG、JPEG 格式，可多选</span>
      </div>

      <!-- 操作按钮 -->
      <div v-if="batchTasks.length" class="action-section">
        <button class="btn-start" :disabled="batchProcessing" @click="runBatchDetect">
          <span v-if="batchProcessing">⏳ 批量检测中...</span>
          <span v-else>🚀 开始批量检测</span>
        </button>
        <button class="btn-reset" @click="clearBatch">清空列表</button>
      </div>

      <!-- 批量任务列表 -->
      <div v-if="batchTasks.length" class="batch-list">
        <div v-for="(task, idx) in batchTasks" :key="idx" class="batch-item">
          <div class="batch-thumb">
            <img :src="task.preview" alt="缩略图" />
          </div>
          <div class="batch-info">
            <div class="batch-name">{{ task.file.name }}</div>
            <div class="batch-size">{{ formatFileSize(task.file.size) }}</div>
            <div class="batch-status" :class="'status-' + task.status">
              <span v-if="task.status === 'pending'">⏳ 等待检测</span>
              <span v-else-if="task.status === 'processing'">⏳ 检测中...</span>
              <span v-else-if="task.status === 'done' && task.noDetection">✖️ 未识别出</span>
              <span v-else-if="task.status === 'done'">✅ 检测完成（{{ task.result?.analysis_result?.summary?.total || 0 }} 个目标）</span>
              <span v-else-if="task.status === 'error'">❌ {{ task.error }}</span>
            </div>
          </div>
          <div class="batch-action" v-if="task.status === 'done' && !task.noDetection">
            <button class="btn-view" @click="viewBatchResult(task)">查看结果</button>
          </div>
        </div>
      </div>

      <!-- 批量结果预览弹窗 -->
      <div v-if="viewingTask" class="batch-result-mask" @click.self="viewingTask = null">
        <div class="batch-result-dialog">
          <div class="dialog-header">
            <h3>检测结果 - {{ viewingTask.file.name }}</h3>
            <button class="btn-close" @click="viewingTask = null">×</button>
          </div>
          <div class="dialog-body">
            <img :src="getResultImageUrl(viewingTask.result.imgurl)" class="result-image" alt="检测结果" />
            <div class="objects-list" style="margin-top:16px;">
              <div v-for="obj in viewingTask.result.analysis_result?.detected_objects || []" :key="obj.id" class="obj-card-mini">
                <div class="obj-num" :style="{ background: getLevelColor(obj.judgment.level) }">{{ obj.id }}</div>
                <div class="obj-info">
                  <div class="obj-name">{{ obj.name_cn }}</div>
                  <div class="obj-meta">
                    <span class="conf-text">{{ obj.confidence_percent }}</span>
                    <span class="pos-text">{{ obj.position?.description }}</span>
                  </div>
                </div>
              </div>
            </div>
            <!-- 治理方法展示 -->
            <div v-if="viewingTask.result.treatments && Object.keys(viewingTask.result.treatments).length > 0" class="treatment-section" style="margin-top:16px;">
              <h3>💡 治理方法参考</h3>
              <div v-for="(info, name) in viewingTask.result.treatments" :key="name" class="treatment-card">
                <div class="treatment-name">{{ name }}</div>
                <div v-if="info.symptom" class="treatment-row">
                  <span class="treatment-label">症状：</span>{{ info.symptom }}
                </div>
                <div v-if="info.treatment" class="treatment-row">
                  <span class="treatment-label">治理：</span>{{ info.treatment }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型配置Tab -->
    <div class="upload-section" v-if="detectTab === 'model'">
      <div class="model-config-card">
        <h3>⚙️ 模型配置</h3>
        <p class="config-tip">修改后点击保存，后端会热加载新模型权重，无需重启服务</p>

        <div class="config-form">
          <!-- 模型权重路径 -->
          <div class="config-row">
            <label>模型权重文件 (best.pt)</label>
            <div class="config-file-row">
              <input ref="modelFileInput" type="file" accept=".pt" style="display: none" @change="onModelFileChange" />
              <input v-model="modelPath" readonly placeholder="点击右侧按钮选择 .pt 文件" class="config-input config-input-readonly" />
              <button class="btn-browse" :disabled="modelUploading" @click="triggerModelFileSelect">📂 选择文件</button>
            </div>
            <div v-if="modelUploading" class="config-uploading">⏳ 上传权重文件中...</div>
          </div>

          <!-- 置信度阈值 -->
          <div class="config-row">
            <label>置信度阈值 (低于该阈值的检测框会被直接丢弃)</label>
            <input v-model.number="confThres" type="number" step="0.01" min="0" max="1" class="config-input" />
          </div>

          <!-- IOU 阈值 -->
          <div class="config-row">
            <label>NMS IOU 阈值 (当两个检测框,重叠面积占比,超过该阈值时,去掉置信度低的那个)</label>
            <input v-model.number="iouThres" type="number" step="0.01" min="0" max="1" class="config-input" />
          </div>

          <!-- 保存按钮 -->
          <button class="btn-start" :disabled="modelLoading" @click="saveModelConfig">
            <span v-if="modelLoading">⏳ 保存中...</span>
            <span v-else>💾 保存</span>
          </button>

          <!-- 提示信息 -->
          <p v-if="modelMsg" class="config-msg" :class="{ 'msg-error': modelMsg.includes('失败') }">{{ modelMsg }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>

import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import axios from 'axios';
defineOptions({ name: 'Detect' })
import { formatFileSize, detectImage, batchDetectImages, getResultImageUrl } from '/src/assets/image'

// 权限：user1=1 为系统管理员
const isAdmin = computed(() => localStorage.getItem('user1') === '1')

// Tab切换
const detectTab = ref('upload')
const user_id = ref()

// 文件&检测状态
const fileInput = ref(null)
const file = ref(null)
const previewUrl = ref('')
const processing = ref(false)
const outputUrl = ref('')
const outputPath = ref('')
const resultInfo = ref('')
const showAll = ref(false)
const analysisResult = ref(null)
const activeObject = ref(null)
const treatments = ref({})

// ========== 摄像头相关（后端 RTSP 实时视频流） ==========
const cameraActive = ref(false)
const cameraLoading = ref(false)
const cameraAnalysis = ref(null)
const videoStreamUrl = ref('')
let pollTimer = null

// 切到摄像头 Tab 时查询后端状态（按钮显示"开启"还是"停止"）
async function checkRtspStatus() {
  try {
    const res = await axios.get('/api/rtsp/status')
    const data = res.data
    if (data.success && data.msg?.running) {
      cameraActive.value = true
      cameraAnalysis.value = null
      videoStreamUrl.value = `/api/video_feed?t=${Date.now()}`
      startPolling()
    }
  } catch (err) {
    // 静默忽略
  }
}

// 开启实时检测
async function startCamera() {
  cameraLoading.value = true
  try {
    const res = await axios.post('/api/rtsp/start')
    const data = res.data
    if (data.success) {
      cameraActive.value = true
      cameraAnalysis.value = null
      setTimeout(() => {
        videoStreamUrl.value = `/api/video_feed?t=${Date.now()}`
        startPolling()
      }, 1500)
    } else {
      alert(data.msg || '开启失败')
    }
  } catch (err) {
    alert('请求失败：服务器无响应')
  } finally {
    cameraLoading.value = false
  }
}

// 停止实时检测
async function stopCamera() {
  cameraLoading.value = true
  stopPolling()
  videoStreamUrl.value = ''
  cameraAnalysis.value = null
  try {
    await axios.post('/api/rtsp/stop')
  } catch (err) {
    // 静默忽略
  } finally {
    cameraActive.value = false
    cameraLoading.value = false
  }
}

// ========== 云台 PTZ 控制 ==========
async function ptzMove(direction) {
  try {
    await axios.post('/api/ptz/move', { direction, speed: 0.5 })
  } catch (err) {
    console.error('PTZ 移动失败：', err)
  }
}

async function ptzStop() {
  try {
    await axios.post('/api/ptz/stop')
  } catch (err) {
    // 静默忽略
  }
}

// 轮询获取检测结果
function startPolling() {
  stopPolling()
  pollTimer = setInterval(async () => {
    if (!cameraActive.value) return
    try {
      const res = await axios.get('/api/latest_result')
      const data = res.data
      if (data.success && data.data) {
        cameraAnalysis.value = data.data.analysis_result || data.data
      }
    } catch (err) {
      // 静默忽略
    }
  }, 1500)
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

// 视频流加载失败
function onStreamError() {
  // 不立即停止，只标记一下（可能是首帧还没准备好）
  console.warn('视频流加载失败，可能是首帧尚未就绪')
}

// 切换 Tab：切出摄像头停止检测，切入摄像头查询状态
watch(detectTab, (newTab, oldTab) => {
  if (oldTab === 'camera' && newTab !== 'camera') {
    // 切出摄像头：如果后端在运行，通知停止
    if (cameraActive.value) {
      stopCamera()
    }
  }
  if (newTab === 'camera') {
    // 切入摄像头：查询后端状态，自动恢复
    checkRtspStatus()
  }
  if (newTab === 'model') {
    // 切入模型配置：加载当前配置
    loadModelConfig()
  }
})

// ========== 批量检测相关 ==========
const batchFileInput = ref(null)
const batchTasks = ref([])
const batchProcessing = ref(false)
const viewingTask = ref(null)

// 唤起批量文件选择
const triggerBatchUpload = () => {
  batchFileInput.value?.click()
}

// 处理选中的多个文件
const getBatchFiles = (e) => {
  const files = Array.from(e.target.files)
  if (!files.length) return
  files.forEach(f => {
    if (!f.type.startsWith('image/')) return
    const reader = new FileReader()
    reader.onload = (ev) => {
      batchTasks.value.push({
        file: f,
        preview: ev.target.result,
        status: 'pending',  // pending / processing / done / error
        result: null,
        error: ''
      })
    }
    reader.readAsDataURL(f)
  })
  // 清空 input，方便再次选择相同文件
  e.target.value = ''
}

// 执行批量检测（调用后端批量接口）
const runBatchDetect = async () => {
  if (batchProcessing.value) return

  const pendingTasks = batchTasks.value.filter(t => t.status !== 'done' && t.status !== 'processing')
  if (!pendingTasks.length) {
    alert('没有待检测的图片')
    return
  }

  // 先把所有待检测任务标记为 processing
  pendingTasks.forEach(t => { t.status = 'processing' })
  batchProcessing.value = true

  try {
    const files = pendingTasks.map(t => t.file)
    const result = await batchDetectImages(files)

    if (result.success) {
      // 按顺序把结果回填到任务列表
      for (let i = 0; i < pendingTasks.length; i++) {
        const r = result.results[i]
        const task = pendingTasks[i]
        if (r && r.success) {
          task.result = {
            imgurl: r.imgurl,
            analysis_result: r.analysis_result,
            result_info: r.result_info,
            treatments: r.treatments || {}
          }
          task.status = 'done'
        } else {
          task.error = r?.error || '检测失败'
          task.status = 'error'
        }
      }
      // 非致命错误提示
      if (result.errors && result.errors.length) {
        console.warn('部分文件格式错误：', result.errors)
      }
      alert(`检测完成：成功 ${result.success_count} 张，失败 ${result.fail_count} 张`)
    } else {
      // 全部失败
      pendingTasks.forEach(t => {
        if (t.status === 'processing') {
          t.status = 'error'
          t.error = result.msg || '检测失败'
        }
      })
      alert(result.msg || '批量检测失败')
    }
  } catch (err) {
    pendingTasks.forEach(t => {
      if (t.status === 'processing') {
        t.status = 'error'
        t.error = '请求失败：服务器无响应'
      }
    })
    alert('批量请求失败：服务器无响应')
  } finally {
    batchProcessing.value = false
  }
}

// 查看某一张的检测结果
const viewBatchResult = (task) => {
  viewingTask.value = task
}

// 清空批量列表
const clearBatch = () => {
  if (batchProcessing.value) {
    alert('正在检测中，请稍候')
    return
  }
  batchTasks.value = []
  viewingTask.value = null
}

// ========== 模型配置相关 ==========
const modelPath = ref('')
const modelFileInput = ref(null)
const modelUploading = ref(false)

function triggerModelFileSelect() {
  modelFileInput.value?.click()
}
const confThres = ref(0.25)
const iouThres = ref(0.45)
const modelLoading = ref(false)
const modelMsg = ref('')

// 选择 .pt 文件后自动上传到后端
async function onModelFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  if (!file.name.endsWith('.pt')) {
    modelMsg.value = '❌ 请选择 .pt 格式的权重文件'
    return
  }

  modelUploading.value = true
  modelMsg.value = ''
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await axios.post('/api/upload_model', formData)
    if (res.data.success) {
      modelPath.value = res.data.model_path
      modelMsg.value = '✅ 权重上传成功，请点击"保存并热加载"应用模型'
    } else {
      modelMsg.value = '❌ ' + res.data.msg
    }
  } catch (err) {
    modelMsg.value = '❌ 上传失败：' + (err.response?.data?.msg || err.message)
  } finally {
    modelUploading.value = false
    e.target.value = ''
  }
}

// 切到模型配置Tab时加载当前配置
async function loadModelConfig() {
  try {
    const res = await axios.get('/api/get_model_config')
    const d = res.data.msg
    modelPath.value = d.model_path || ''
    confThres.value = d.conf_thres
    iouThres.value = d.iou_thres
  } catch (err) {
    modelMsg.value = '加载配置失败：' + (err.response?.data?.msg || err.message)
  }
}

// 保存配置 + 热加载模型
async function saveModelConfig() {
  modelLoading.value = true
  modelMsg.value = ''
  try {
    const res = await axios.post('/api/save_model_config', {
      model_path: modelPath.value,
      conf_thres: Number(confThres.value),
      iou_thres: Number(iouThres.value)
    })
    if (res.data.success) {
      modelMsg.value = '✅ 保存成功，模型已热加载'
    } else {
      modelMsg.value = '❌ 保存失败：' + res.data.msg
    }
  } catch (err) {
    modelMsg.value = '❌ 请求失败：' + (err.response?.data?.msg || err.message)
  } finally {
    modelLoading.value = false
  }
}

// 页面加载读取缓存
onMounted(() => {
  const cache = localStorage.getItem('detectCache')
  if (!cache) return
  const data = JSON.parse(cache)
  previewUrl.value = data.previewUrl || ''
  outputUrl.value = data.outputUrl || ''
  outputPath.value = data.outputPath || ''
  resultInfo.value = data.resultInfo || ''
  analysisResult.value = data.analysisResult || null
  showAll.value = data.showAll || false
})

// 页面销毁存入缓存 + 停止视频流和轮询
onUnmounted(() => {
  const saveData = {
    previewUrl: previewUrl.value,
    outputUrl: outputUrl.value,
    outputPath: outputPath.value,
    resultInfo: resultInfo.value,
    analysisResult: analysisResult.value,
    showAll: showAll.value
  }
  localStorage.setItem('detectCache', JSON.stringify(saveData))
  // 组件卸载时停止视频流和轮询
  stopCamera()
})

// 清空缓存（移除llm重置）
const clearCache = () => {
  file.value = null
  previewUrl.value = ''
  outputUrl.value = ''
  outputPath.value = ''
  resultInfo.value = ''
  analysisResult.value = null
  treatments.value = {}
  showAll.value = false
  localStorage.removeItem('detectCache')
}

// 唤起文件选择框
const triggerUpload = () => {
  fileInput.value?.click()
}

// 选中图片处理
const getfile = (e) => {
  const selectedFile = e.target.files[0]
  if (!selectedFile) return
  if (!selectedFile.type.startsWith('image/')) {
    alert('请选择图片文件！')
    return
  }
  file.value = selectedFile
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target.result
  }
  reader.readAsDataURL(selectedFile)
  // 清空旧结果
  outputUrl.value = ''
  outputPath.value = ''
  resultInfo.value = ''
  analysisResult.value = null
  showAll.value = false
}

// 执行AI检测接口
const detect = async () => {
  if (!file.value) return
  processing.value = true
  try {
    const result = await detectImage(file.value)
    if (result.success) {
      user_id.value =localStorage.getItem(user)
      outputUrl.value = getResultImageUrl(result.imgurl)
      outputPath.value = result.record_path
      resultInfo.value = result.result_info
      analysisResult.value = result.analysis_result
      treatments.value = result.treatments || {}
    } else {
      alert('检测失败：' + (result.msg || '未知错误'))
    }
  } catch (err) {
    alert('请求失败：服务器无响应')
  } finally {
    processing.value = false
  }
}

// 最多展示5个目标，超出折叠
const displayedObjects = computed(() => {
  if (!analysisResult.value?.detected_objects) return []
  if (showAll.value) return analysisResult.value.detected_objects
  return analysisResult.value.detected_objects.slice(0, 5)
})

// 风险等级颜色映射
function getLevelColor(level) {
  const colors = {
    '很高': '#82071e',
    '较高': '#cf222e',
    '中等': '#d4a72c',
    '较低': '#54aeff',
    '很低': '#0969da'
  }
  return colors[level] || '#666'
}
</script>

<style scoped src="./Detection.css"></style>
