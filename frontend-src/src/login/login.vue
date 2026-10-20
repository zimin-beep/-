<script setup>
import axios from 'axios';
import { ref, onMounted } from 'vue';
import router from '../router/index';

const username = ref()
const password = ref()
const captchaText = ref()
const captchaId = ref()
const captchaImg = ref()
const loading = ref(false)

const loadCaptcha = async () => {
    try {
        const res = await axios.get('/api/captcha')
        if (res.data.success) {
            captchaId.value = res.data.captcha_id
            captchaImg.value = res.data.captcha_image
        }
    } catch (e) {
        console.error('获取验证码失败', e)
    }
}

const login = async () => {
    if (!captchaText.value) {
        alert('请输入验证码')
        return
    }
    loading.value = true
    try {
        const res = await axios.post('/api/login', {
            username: username.value,
            password: password.value,
            captcha_id: captchaId.value,
            captcha_text: captchaText.value
        })

        if (res.data.success) {
            localStorage.setItem('access_token', res.data.access_token)
            localStorage.setItem('refresh_token', res.data.refresh_token)
            localStorage.setItem("user", res.data.msg)
            localStorage.setItem('user1', res.data.msg1)
            localStorage.setItem('user2',res.data.user)
            router.push('/overview')
        } else {
            alert(res.data.msg)
            captchaText.value = ''
            loadCaptcha()
        }
    } catch (err) {
        const msg = err.response?.data?.msg || err.message || '登录请求失败'
        alert(msg)
        captchaText.value = ''
        loadCaptcha()
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadCaptcha()
})
</script>

<template>
    <div class="login-wrap">
        <!-- 背景动画形状 -->
        <div class="bg-shapes">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
        </div>

        <div class="login-card">
            <div class="logo">
                <div class="logo-icon">✦</div>
                <h1>病虫害管理系统</h1>
                <p>请登录您的账户以继续</p>
            </div>

            <form @submit.prevent="login">
                <div class="form-group">
                    <label>账号</label>
                    <div class="input-wrapper">
                        <span class="input-icon">👤</span>
                        <input v-model="username" placeholder="请输入账号" required />
                    </div>
                </div>

                <div class="form-group">
                    <label>密码</label>
                    <div class="input-wrapper">
                        <span class="input-icon">🔒</span>
                        <input v-model="password" type="password" placeholder="请输入密码" required />
                    </div>
                </div>

                <div class="form-group">
                    <label>验证码</label>
                    <div class="captcha-row">
                        <div class="input-wrapper captcha-input-wrap">
                            <span class="input-icon">🛡</span>
                            <input v-model="captchaText" placeholder="请输入验证码" maxlength="4" required />
                        </div>
                        <img
                            v-if="captchaImg"
                            :src="captchaImg"
                            class="captcha-img"
                            @click="loadCaptcha"
                            title="点击刷新验证码"
                        />
                        <div v-else class="captcha-loading">加载中</div>
                    </div>
                </div>

                <button type="submit" class="btn-login" :disabled="loading">
                    <span v-if="loading">登录中...</span>
                    <span v-else>登 录</span>
                </button>
            </form>
        </div>
    </div>
</template>
<style scoped src="./login.css"></style>
