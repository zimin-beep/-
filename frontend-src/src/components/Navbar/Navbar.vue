<template>
  <nav class="navbar">
    <div class="logo">
      <div class="logo-icon">🌿</div>
      <div class="logo-text">病虫害检测系统</div>
    </div>
    <div class="nav-menu">
      <div class="nav-item" :class="{ active: $route.name === 'Overview' }" @click="$router.push('/overview')">
        📊 概览
      </div>


      <div class="nav-item" :class="{ active: $route.name === 'Detection' }" @click="$router.push('/detection')">
        🔍 检测
      </div>


      <div class="nav-item" :class="{ active: $route.name === 'Record' }" @click="$router.push('/record')">
        📋 记录详情
      </div>
      <div class="nav-item" :class="{ active: $route.name === 'Knowledge' }" @click="$router.push('/knowledge')">
        🌎 知识库管理
      </div>
      <div v-if="isAdmin" class="nav-item" :class="{ active: $route.name === 'UserList' }" @click="$router.push('/userlist')">
        ✉ 用户管理
      </div>





    </div>
    <div class="user-area">
      <div class="user-avatar">👤</div>
      <span class="user-name">{{ username }}</span>
      <button class="logout-btn" @click="handleLogout">退出</button>
    </div>
  </nav>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const router = useRouter()
const username = computed(() => localStorage.getItem('user') || '')
const isAdmin = computed(() => localStorage.getItem('user1') === '1')
function handleLogout() {
  if (confirm('确定退出？')) {
    localStorage.clear()
    router.push('/login')
  }
}
</script>

<style scoped src="./Navbar.css"></style>
