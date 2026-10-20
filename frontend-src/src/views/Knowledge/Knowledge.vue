<template>
<div class="knowledge-container">
    <h2 class="page-title">荔枝病害知识库管理</h2>

    <!-- 顶部工具栏 -->
    <div class="tool-bar">
      <button class="btn btn-primary" @click="openAddDialog">新增病害</button>
      <button class="btn btn-danger" @click="batchDelete">批量删除</button>
      <input
        v-model="searchForm.name"
        type="text"
        placeholder="输入病害名称搜索"
      />
      <select v-model="searchForm.type">
        <option value="">全部类型</option>
        <option value="0">病害</option>
        <option value="1">虫害</option>
      </select>
      <button class="btn btn-primary" @click="searchList">查询</button>
      <button class="btn btn-default" @click="resetSearch">重置</button>
    </div>

    <!-- 数据表格 -->
    <table>
      <thead>
        <tr>
          <th width="50">
            <input
              type="checkbox"
              v-model="isCheckAll"
              @change="checkAllChange"
            />
          </th>
          <th width="70">ID</th>
          <th width="160">病害名称</th>
          <th width="100">类型</th>
          <th width="90">样例图</th>
          <th>病症描述</th>
          <th>治理方案</th>
          <th width="180">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in tableList" :key="item.id">
          <td>
            <input
              class="row-check"
              type="checkbox"
              v-model="checkedIdList"
              :value="item.id"
            />
          </td>
          <td>{{ item.id }}</td>
          <td>{{ item.name }}</td>
          <td :class="item.type === 0 ? 'type-tag-disease' : 'type-tag-pest'">
            {{ item.type === 0 ? '病害' : '虫害' }}
          </td>
          <td>
            <span v-if="item.imgUrl">
              <img class="small-img" :src="getImageUrl(item.imgUrl)" alt="图例" />
            </span>
            <span v-else>无图</span>
          </td>
          <td class="text-ellipsis">{{ item.symptom }}</td>
          <td class="text-ellipsis">{{ item.treat }}</td>
          <td>
            <button class="btn btn-primary" @click="openDetail(item)">查看</button>
            <button class="btn btn-primary" @click="openEdit(item)">编辑</button>
            <button class="btn btn-danger" @click="singleDelete(item.id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- 分页区域 -->
    <div class="page-box">
      <span>当前第 {{ page.current }} 页 </span>
      <button class="btn btn-default" @click="prevPage">上一页</button>
      <button class="btn btn-default" @click="nextPage">下一页</button>
    </div>

    <!-- 新增/编辑弹窗遮罩 -->
    <div class="mask" v-if="dialog.showEdit" @click.self="closeEditDialog">
      <div class="dialog">
        <h3 class="dialog-title">{{ dialog.title }}</h3>
        <div class="form-item">
          <label>ID：</label>
          <div class="form-right">
            <input v-model="form.id" disabled placeholder="自动生成" />
          </div>
        </div>
        <div class="form-item">
          <label>病害名称：</label>
          <div class="form-right">
            <input v-model="form.name" placeholder="请输入病害名称" />
          </div>
        </div>
        <div class="form-item">
          <label>类型：</label>
          <div class="form-right">
            <select v-model.number="form.type">
              <option value="0">病害</option>
              <option value="1">虫害</option>
            </select>
          </div>
        </div>
        <div class="form-item">
          <label>样例图片：</label>
          <div class="form-right">
            <input
              type="file"
              accept="image/png,image/jpg,image/jpeg,image/gif,image/webp"
              @change="uploadImgChange"
              ref="fileRef"
            />
            <div class="img-preview">
              <span v-if="!tempImgSrc">暂无图片</span>
              <img v-else :src="tempImgSrc" alt="预览图" />
            </div>
          </div>
        </div>
        <div class="form-item">
          <label>病症描述：</label>
          <div class="form-right">
            <textarea
              v-model="form.symptom"
              placeholder="详细描述发病特征、外观症状"
            ></textarea>
          </div>
        </div>
        <div class="form-item">
          <label>治理方案：</label>
          <div class="form-right">
            <textarea
              v-model="form.treat"
              placeholder="药剂、物理防治、日常养护方案"
            ></textarea>
          </div>
        </div>
        <div class="dialog-btn-group">
          <button class="btn btn-default" @click="closeEditDialog">取消</button>
          <button class="btn btn-primary" @click="saveForm">保存</button>
        </div>
      </div>
    </div>

    <!-- 详情弹窗遮罩 -->
    <div class="mask" v-if="dialog.showDetail" @click.self="closeDetailDialog">
      <div class="dialog">
        <h3 class="dialog-title">病害详情</h3>
        <div class="form-item">
          <label>编号：</label>
          <span>{{ detailData.id }}</span>
        </div>
        <div class="form-item">
          <label>名称：</label>
          <span>{{ detailData.name }}</span>
        </div>
        <div class="form-item">
          <label>类型：</label>
          <span>{{ detailData.type === 0 ? '病害' : '虫害' }}</span>
        </div>
        <div class="form-item">
          <label>样例图片：</label>
          <div class="img-preview">
            <span v-if="!detailData.imgUrl">暂无样例图片</span>
            <img v-else class="preview-thumb" :src="getImageUrl(detailData.imgUrl)" alt="图例" @click="openPreview" />
          </div>
        </div>
        <div class="form-item">
          <label>病症：</label>
          <div>{{ detailData.symptom }}</div>
        </div>
        <div class="form-item">
          <label>治理方案：</label>
          <div>{{ detailData.treat }}</div>
        </div>
        <div class="dialog-btn-group">
          <button class="btn btn-default" @click="closeDetailDialog">关闭</button>
        </div>
      </div>
    </div>

    <!-- 图片放大预览 -->
    <div class="img-preview-mask" v-if="preview.show" @click="closePreview">
      <img :src="preview.url" class="img-preview-large" @click.stop />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import axios from 'axios'

// Docker 部署：不要硬编码后端地址，让 axios 用相对路径走 nginx 反向代理
// axios.defaults.baseURL = "http://127.0.0.1:8080"



// 知识库列表（后端返回数据）
const tableList = ref([])

// 搜索条件：名称、类型
const searchForm = reactive({
  name: '',
  type: ''
})

// 分页参数（传给后端）
const page = reactive({
  current: 1,     // 当前页码
    
      // 总页数
})

// 弹窗控制
const dialog = reactive({
  showEdit: false,
  showDetail: false,
  title: '新增病害'
})

// 新增/编辑表单
const form = reactive({
  id: '',
  name: '',
  type: 0,
  imgUrl: '',
  symptom: '',
  treat: ''
})

const detailData = ref({})
const tempImgSrc = ref('')
const tempImgFile = ref(null)   // 保存真实的 File 对象，用于上传
const fileRef = ref(null)
const checkedIdList = ref([])
const isCheckAll = ref(false)

// 图片放大预览
const preview = reactive({ show: false, url: '' })
const openPreview = () => {
  if (!detailData.value.imgUrl) return
  preview.url = getImageUrl(detailData.value.imgUrl)
  preview.show = true
}
const closePreview = () => {
  preview.show = false
  preview.url = ''
}

// 页面初始化加载列表
onMounted(() => {
  getKnowledgeList()
})

/**
 * 数据标准化：将后端字段映射为前端统一字段
 */
const normalizeItem = (item) => {
  return {
    id: item.id,
    name: item.disease_name,
    type: item.disease_type,
    imgUrl: item.example_url,
    symptom: item.symptom,
    treat: item.treatment
  }
}

/**
 * 核心请求：获取知识库列表
 * 后端返回格式：{msg: {list: [...]}, success: true}
 */
const getKnowledgeList = async () => {
  try {
    const res = await axios.post('/api/get_knowledge_item', {
      page: page.current,
      pageSize: page.pageSize,
      name: searchForm.name,
      type: searchForm.type
    })
    const list = res.data.msg?.list || res.data.list || []
    tableList.value = list.map(normalizeItem)
    page.total = list.length
    page.totalPage = Math.ceil(page.total / page.pageSize)
    checkedIdList.value = []
    isCheckAll.value = false
  } catch (err) {
    console.error('列表请求失败', err)
  }
}

// 图片基础地址：Docker 部署时走 nginx 代理，不需要硬编码后端地址
const BASE_URL = ''
const getImageUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return BASE_URL + path
}

// 全选监听
watch(checkedIdList, (val) => {
  isCheckAll.value = val.length === tableList.value.length && tableList.value.length > 0
})
const checkAllChange = () => {
  isCheckAll.value ? checkedIdList.value = tableList.value.map(i => i.id) : checkedIdList.value = []
}

// 图片选择：仅本地预览 + 保留 File 对象，提交时再上传
const uploadImgChange = (e) => {
  const file = e.target.files[0]
  if (!file) return
  tempImgFile.value = file
  tempImgSrc.value = URL.createObjectURL(file)
}

// 弹窗打开关闭
const openAddDialog = () => {
  dialog.title = '新增病害'
  dialog.showEdit = true
  form.id = ''
  form.name = ''
  form.type = searchForm.type
  form.imgUrl = ''
  form.symptom = ''
  form.treat = ''
  tempImgSrc.value = ''
  tempImgFile.value = null
  if (fileRef.value) fileRef.value.value = ''
}
const openEdit = (row) => {
  dialog.title = '编辑病害'
  dialog.showEdit = true
  Object.assign(form, row)
  tempImgSrc.value = row.imgUrl
  tempImgFile.value = null
}
const closeEditDialog = () => {
  dialog.showEdit = false
  tempImgSrc.value = ''
  tempImgFile.value = null
  if (fileRef.value) fileRef.value.value = ''
}
const openDetail = (row) => {
  detailData.value = { ...row }
  dialog.showDetail = true
}
const closeDetailDialog = () => dialog.showDetail = false

// 保存（新增/编辑，对接后端保存接口）
const saveForm = async () => {
  if (!form.name || !form.symptom || !form.treat) {
    alert('名称、病症、治理方案不能为空')
    return
  }
  try {
    if (!form.id) {
      // 新增：后端要求 multipart 上传 file 字段，并用 JSON 接收其余字段
      if (!tempImgFile.value) {
        alert('请选择样例图片')
        return
      }
      const formData = new FormData()
      formData.append('file', tempImgFile.value)
      formData.append('name', form.name)
      formData.append('type', form.type)
      formData.append('symptom', form.symptom)
      formData.append('treat', form.treat)
      await axios.post('/api/knowledge/add', formData)
    } else {
      // 编辑：后端同样要求 multipart。若没换图片，则把原图 URL 传给后端作为 img_url 字段
      const formData = new FormData()
      formData.append('id', form.id)
      if (tempImgFile.value) {
        formData.append('file', tempImgFile.value)
      }
      // 把原图片路径也传给后端（用于未换图时保留）
      formData.append('img_url', form.imgUrl || '')
      formData.append('name', form.name)
      formData.append('type', form.type)
      formData.append('symptom', form.symptom)
      formData.append('treat', form.treat)
      await axios.post('/api/knowledge/update', formData)
    }
    closeEditDialog()
    getKnowledgeList()
  } catch (err) {
    alert('保存失败')
  }
}

// 删除
const singleDelete = async (id) => {
  if (!confirm('确定删除该记录？')) return
  await axios.post('/api/knowledge/del', { id })
  getKnowledgeList()
}
//多条数据的删除
const batchDelete = async () => {
  if (!checkedIdList.value.length) return alert('勾选要删除数据')
  if (!confirm(`删除${checkedIdList.value.length}条数据？`)) return
  await axios.post('/api/knowledge/batch_del', { ids: checkedIdList.value })
  checkedIdList.value = []
  getKnowledgeList()
}

// 搜索&重置
const searchList = () => {
  page.current = 1
  getKnowledgeList()
}
const resetSearch = () => {
  searchForm.name = ''
  searchForm.type = ''
  page.current = 1
  getKnowledgeList()
}

// 分页切换
const prevPage = () => {
  if (page.current > 1) {
    page.current--
    getKnowledgeList()
  }
}
const nextPage = () => {
    page.current++
    getKnowledgeList()
  
}
</script>

<style scoped src="./Knowledge.css"></style>