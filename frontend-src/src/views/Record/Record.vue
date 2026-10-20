<template>
    <div class="container">
        <h2 class="page-title">检测历史记录查询</h2>
        <!-- 筛选栏 -->
        <div class="search-bar">
            <div class="search-item">
                <label>起止时间：</label>
                <input type="date" v-model="startTime">
                <span>~</span>
                <input type="date" v-model="endTime">
            </div>
            <div class="search-item">
                <label>病虫害类型：</label>
                <select v-model="typeSelect" style="height: 40px;">
                    <option value="">全部</option>
                    <option value="0">病害</option>
                    <option value="1">虫害</option>
                </select>
            </div>
            <div class="search-item">
                <label>状态：</label>
                <select v-model="auditSelect" style="height: 40px;">
                    <option value="">全部</option>
                    <option value="0">待确认</option>
                    <option value="1">已确认</option>
                    <option value="2">误报</option>
                    <option value="3">治理中</option>
                    <option value="4">治理完成</option>

                </select>
            </div>
            <div class="search-item">
                <label>关键词：</label>
                <input type="text" v-model="keyword" placeholder="病害名称/用户名搜索">
            </div>
            <div class="search-item">
                <button class="btn btn-primary" @click="searchData">查询</button>
                <button class="btn btn-default" @click="resetSearch">重置</button>
                <button class="btn btn-primary" @click="refreshData">刷新</button>
            </div>
        </div>

        <!-- 表格 -->
        <div class="table-box">
            <table>
                <thead>
                    <tr>
                        <th>序号</th>
                        <th>病害名称</th>
                        <th>病虫害类型</th>
                        <th>置信度</th>
                        <th>审核人</th>
                        <th>状态</th>
                        <th>检测时间</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody id="tableBody">

                    <tr v-for="(item, idx) in filterData" :key="idx">
                        <td>{{ idx + 1 }}</td>
                        <td>{{ item.final_result || item.disease_name  }}</td>
                        <td>

                            <span class="tag" :class="Number(item.disease_type) === 0 ? 'tag-disease' : 'tag-pest'">{{
                                Number(item.disease_type) == 0 ? '病害' : '虫害' }}</span>
                        </td>
                        <td>{{ item.confidence }}</td>

                        <td>{{ item.auditor_user || '未审核' }}</td>
                        <td>

                            <span class="tag"
                                :class="Number(item.item_audit_status) === 0 ? 'tag-audit0' : Number(item.item_audit_status) === 1 ? 'tag-audit1' : Number(item.item_audit_status) === 2 ? 'tag-audit2' : Number(item.item_audit_status) === 3 ? 'tag-disease' : Number(item.item_audit_status) === 4 ? 'tag-audit3' : 'tag-audit4'">
                                {{ item.audit_status_text }}
                            </span>

                        </td>
                        <td>{{ item.update_time_str }}</td>
                        <td>
                            <button class="btn btn-primary" style="height:28px;padding:0 8px"
                                @click="showDetail(idx)">查看详情</button>
                        </td>
                    </tr>
                </tbody>
            </table>
            <!-- 分页 -->
            <div class="page-wrap">
                <button class="btn btn-default" @click="prevPage()">上一页</button>
                <span id="pageInfo">第{{ page }}页</span>
                <button class="btn btn-default" @click="nextPage()">下一页</button>
            </div>
        </div>
    </div>

    <!-- 详情弹窗 -->
    <div class="mask" v-if="maskShow" @click="closeDialog">
        <div class="detail-dialog" @click.stop>
            <h3 class="dialog-title">记录详情</h3>
            <div id="detailContent">

                <div class="img-wrap">
                    <div class="img-item">
                        <h4>样例图片</h4>
                        <!-- src替换成你的原图地址，本地/网络图片均可 -->
                        <img :src="getImageUrl(currentDetail.example_url)" alt="样例原图">
                    </div>
                    <div class="img-item">
                        <h4>模型检测结果图</h4>
                        <!-- src替换成模型推理标注图地址 -->
                        <img :src="getImageUrl(currentDetail.image_url)" alt="模型图">
                    </div>
                </div>


                <table class="table-box">
                    <thead>
                        <tr>
                            <th>序号</th>
                            <th>病害名称</th>
                            <th>病虫害类型</th>
                            <th>置信度</th>
                            <th>审核人</th>
                            <th>状态</th>
                            <th>检测时间</th>

                        </tr>
                    </thead>

                    <tbody id="tableBody">

                        <tr>
                            <td>{{ num }}</td>
                            <td>{{ currentDetail.final_result }}</td>
                            <td>

                                <span class="tag"
                                    :class="Number(currentDetail.disease_type) === 0 ? 'tag-disease' : 'tag-pest'">{{
                                        Number(currentDetail.disease_type) == 0 ? '病害' : '虫害' }}</span>
                            </td>
                            <td>{{ currentDetail.confidence }}</td>

                            <td>{{ currentDetail.auditor_user || '未审核' }}</td>





                            <td>
                                <select style="width: 100px; height: 40px;" v-model="currentDetail.item_audit_status">
                                    <option value="0">待确认</option>
                                    <option value="1">已确认</option>
                                    <option value="2">误报</option>
                                    <option value="3">治理中</option>
                                    <option value="4">治理完成</option>

                                </select>

                            </td>






                            <td>{{ currentDetail.update_time_str }}</td>
                        </tr>
                    </tbody>
                </table>

                <!-- 原有信息展示 -->
                <div class="info-block" >
                    <div class="info-item">
                        <span class="info-label">模型审核结果：</span>
                        <span class="info-text">{{ currentDetail.final_result }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">典型特征：</span>
                        <span class="info-text">{{ currentDetail.symptom }}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">治理方式：</span>
                        <span class="info-text">{{ currentDetail.treatment }} </span>
                    </div>
                </div>

                <!-- 新增：最终检测结果下拉框（后端动态渲染option） -->
                <div class="form-row">
                    <label class="form-label">最终检测结果：</label>
                    <select v-model="currentDetail.disease_name" style="height: 40px;" @change="onDiseaseChange">
                        <option v-for="(item, idx) in knowledge" :key="item.id" :value="item.disease_name">
                            {{ item.disease_name }}
                        </option>
                    </select>
                </div>

                <!-- 新增：备注输入框 -->
                <div class="form-row">
                    <label class="form-label">备注：</label>
                    <textarea v-model="currentDetail.auditremark" placeholder="请填写审核备注、复检说明、修改意见等内容..."></textarea>
                </div>

            </div>
            <div class="dialog-footer">
  <button class="btn btn-primary close-btn" @click="closeDialog()">关闭</button>
  <button class="btn btn-primary close-btn" @click="submitAudit">修改</button>
</div>



        </div>
    </div>


</template>


<script setup>

import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'


// 分页全局变量
const page = ref(1)
let allData = ref([])
let filterData = ref([])
const num = ref()
// 筛选绑定
const startTime = ref('')
const endTime = ref('')
const typeSelect = ref('')
const auditSelect = ref('')
const keyword = ref('')

const isSearchMode = ref(false)
// 弹窗
const maskShow = ref(false)
const currentDetail = ref({})
const knowledge = ref([])
// 初始化日期
onMounted(async () => {
    get_knowledge()
    setDefaultTime()
    await getRecordList()
})
// 抽出来公共方法：设置默认7天时间
const setDefaultTime = () => {
  const now = new Date();
  endTime.value = now.toISOString().split('T')[0];
  let sevenBefore = new Date(Date.now() - 7 * 24 * 60 * 1000);
  startTime.value = sevenBefore.toISOString().split('T')[0];
}




// 数据标准化：确保两个接口返回的字段名统一
const normalizeItem = (item) => {
    return {
        ...item,
        item_id: item.item_id ?? item.id ?? item.detect_item_id,
        record_main_id: item.record_main_id ?? item.record_id ?? item.main_id,
        auditor_user: item.auditor_user ?? item.audit_user,
        example_url: item.example_url ?? item.original_url ?? item.img_url,
        update_time_str: item.update_time_str ?? item.updateTime ?? item.create_time
    }
}

// 请求接口
const getRecordList = async () => {
    const res = await axios.post('/api/all_record', {
        page: page.value

    });
    allData.value = (res.data.msg || []).map(normalizeItem);
    filterData.value = [...allData.value]
}
const get_knowledge = async () => {
    const res = await axios.post('/api/get_knowledge', {})
    knowledge.value = res.data.msg
}



//筛选接口
const getRecordItemList = async () => {
    const res = await axios.post('/api/detectItem/list', {
        info: {
            page: page.value,
            startTime: startTime.value || undefined,
            endTime: endTime.value || undefined,
            disease_type: typeSelect.value,
            item_audit_status: auditSelect.value,
            keyword: keyword.value
        }
    }
    );
    allData.value = (res.data.msg || []).map(normalizeItem);
    filterData.value = [...allData.value]
}

// 查询按钮
const searchData = () => {
    isSearchMode.value = true
    getRecordItemList()
    page.value = 1;
}




// 重置所有筛选条件
const resetSearch = async () => {
  typeSelect.value = ''
  auditSelect.value = ''
  keyword.value = ''
  isSearchMode.value = false
  page.value = 1
  setDefaultTime()
  await getRecordList()
}


// 刷新
const refreshData = async () => {
    page.value = 1;
    if (isSearchMode.value) {
        await getRecordItemList();
    } else {
        await getRecordList();
    }
}

// 分页
const prevPage = () => {
    if (page.value > 1)
        page.value--;

    if (isSearchMode.value)
        getRecordItemList()
    else
        getRecordList()
}
const nextPage = () => {
    if (filterData.value.length < 10 && page.value > 1) {
        return
    }
    page.value++;

    if (isSearchMode.value)
        getRecordItemList()
    else
        getRecordList()
}

// 详情弹窗
const showDetail = (idx) => {
    currentDetail.value = filterData.value[idx];
    num.value = idx + 1;
    maskShow.value = true;
    currentDetail.value.final_disease_id = currentDetail.value.final_disease_id || currentDetail.value.disease_id
    currentDetail.value.final_result = currentDetail.value.final_result || currentDetail.value.disease_name
    // 关键：根据ID匹配下拉框选中项
    currentDetail.value.disease_name = currentDetail.value.final_result
    // 根据当前病害同步典型特征和治理方式
    const matched = knowledge.value.find(k => k.disease_name === currentDetail.value.final_result)
    if (matched) {
        currentDetail.value.symptom = matched.symptom || ''
        currentDetail.value.treatment = matched.treatment || ''
        currentDetail.value.final_disease_id = matched.id
    }
}

//关闭弹窗
const closeDialog = () => {
    maskShow.value = false;
    currentDetail.value = {}
}
const getImageUrl = (path) => {
    if (!path) return ''
    if (path.startsWith('http')) return path
    return path
}


// 选中病害同步名称、特征和治理方式
const onDiseaseChange = () => {
    const selectedName = currentDetail.value.disease_name
    const target = knowledge.value.find(item => item.disease_name === selectedName)
    if (target) {
        currentDetail.value.final_result = target.disease_name
        currentDetail.value.symptom = target.symptom || ''
        currentDetail.value.treatment = target.treatment || ''
        currentDetail.value.final_disease_id = target.id
    }
}

// 审核提交函数
const submitAudit = async () => {
    // 非空简单校验
    if (!currentDetail.value.final_disease_id) {
        alert("请选择最终检测病害");
        return
    }
    if (!currentDetail.value.item_audit_status && currentDetail.value.item_audit_status !== 0) {
        alert("请选择审核状态");
        return
    }
    // 组装提交参数，和后端接口一一对应
    const submitParam = {
        itemId: currentDetail.value.item_id,
        recordId: currentDetail.value.record_main_id,
        finalDiseaseId: currentDetail.value.final_disease_id,
        finalResult: currentDetail.value.disease_name,
        itemAuditStatus: Number(currentDetail.value.item_audit_status),
        auditRemark: currentDetail.value.auditremark || "",
        loginUserId: localStorage.getItem("user1") // 当前登录审核人ID
    }
    try {
        const res = await axios.post("/api/detect/updateAudit", submitParam)
        if (res.data.success) {
            alert(res.data.msg)
            maskShow.value = false
            // 提交后刷新列表
            refreshData()
        } else {
            alert(res.data.msg)
        }
    } catch (err) {
        alert("网络提交失败")
        console.error(err)
    }
}






















</script>
<style scoped src="./Record.css"></style>