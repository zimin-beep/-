<template>
    <div class="container">
        <h2>用户管理</h2>

        <!-- 工具栏 -->
        <div class="toolbar">
            <button class="btn btn-success" @click="openAdd()">新增用户</button>
        </div>

        <!-- 表格 -->
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>用户名</th>
                    <th>手机号</th>
                    <th>角色</th>
                   
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="item in userlist" :key="item.user_id">
                    <td>{{ item.user_id }}</td>
                    <td>{{ item.username }}</td>
                    <td>{{ item.phone }}</td>
                    <td>{{ item.role }}</td>
                    
                    <td>
                        <button class="btn btn-primary btn-sm" @click="openEdit(item)">编辑</button>
                        <button class="btn btn-danger btn-sm" @click="deleteUser(item.user_id)">删除</button>
                    </td>
                </tr>
                <tr v-if="userlist.length === 0">
                    <td colspan="5" class="empty-tip">暂无数据</td>
                </tr>
            </tbody>
        </table>

        <!-- 分页 -->
        <div class="pagination">
            <button class="btn btn-primary btn-sm" @click="prevPage()" :disabled="page <= 1">上一页</button>
            <span style="margin:0 10px">第{{ page }}页</span>
            <button class="btn btn-primary btn-sm" @click="nextPage()">下一页</button>
        </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div class="mask" v-if="dialog.show" @click.self="closeDialog()">
        <div class="dialog">
            <h3>{{ dialog.title }}</h3>
            <div class="form-item">
                <label>用户名 *</label>
                <input v-model="form.username" placeholder="请输入用户名">
            </div>
            <div class="form-item">
                <label>手机号 *</label>
                <input v-model="form.phone" placeholder="请输入手机号">
            </div>
            <div class="form-item">
                <label>角色</label>
                <select v-model.number="form.role">
                    <option :value="0">普通用户</option>
                    <option :value="1">系统管理员</option>
                </select>
            </div>
           
            <div class="form-item">
                <label>密码</label>
                <input v-model="form.password" type="password" placeholder="请输入密码">
            </div>
            <div class="actions">
                <button class="btn btn-danger btn-sm" @click="closeDialog()">取消</button>
                <button class="btn btn-primary btn-sm" @click="saveUser()">保存</button>
            </div>
        </div>
    </div>
</template>

<script setup>
import axios from 'axios'
import { onMounted, ref, reactive } from 'vue'

const page = ref(1)
const userlist = ref([])

const dialog = reactive({
    show: false,
    title: '新增用户'
})

const form = reactive({
    user_id: '',
    username: '',
    phone: '',
    role: 0,
    password: ''
})

// 页面初始化加载列表
onMounted(() => {
    getUserList()
})

const getUserList = async () => {
    try {
        const res = await axios.post('/api/userlist', {
            page: page.value
        })
        userlist.value = res.data.msg || []
    } catch (err) {
        console.error('获取用户列表失败', err)
        userlist.value = []
    }
}

const prevPage = () => {
    if (page.value > 1) {
        page.value--
        getUserList()
    }
}

const pageSize = 10
const totalPages = ref(1)

const nextPage = () => {
    if (page.value >= totalPages.value && userlist.value.length < pageSize) {
        return
    }
    page.value++
    getUserList()
}

const openAdd = () => {
    dialog.title = '新增用户'
    form.user_id = ''
    form.username = ''
    form.phone = ''
    form.role = 0
    form.password = ''
    dialog.show = true
}

// 角色映射：后端字符串 → 前端数字
const roleToNumber = (role) => {
    if (role === '系统管理员' || role === 1 || role === '1') return 1
    return 0
}

const openEdit = (item) => {
    dialog.title = '编辑用户'
    form.user_id = item.user_id
    form.username = item.username
    form.phone = item.phone
    form.role = roleToNumber(item.role)
    form.password = ''
    dialog.show = true
}

const closeDialog = () => {
    dialog.show = false
}

const saveUser = async () => {
    if (!form.username) {
        alert('用户名不能为空')
        return
    }
    // 新增时密码必填
    if (!form.user_id && !form.password) {
        alert('密码不能为空')
        return
    }
    try {
        if (form.user_id) {
            // 编辑时：只在用户输入了新密码时才传 password 字段，空值表示不修改
            const payload = {
                id: form.user_id,
                username: form.username,
                phone: form.phone,
                role: form.role,
            }
            if (form.password) {
                payload.password = form.password
            }
            await axios.post('/api/user/update', payload)
        } else {
            await axios.post('/api/user/add', {
                username: form.username,
                phone: form.phone,
                role: form.role,
                password: form.password
            })
        }
        closeDialog()
        getUserList()
    } catch (err) {
        alert('保存失败')
    }
}

const deleteUser = async (id) => {
    if (!confirm('确定删除该用户？')) return
    try {
        await axios.post('/api/user/delete', { id })
        getUserList()
    } catch (err) {
        alert('删除失败')
    }
}
</script>

<style scoped src="./UserList.css"></style>
