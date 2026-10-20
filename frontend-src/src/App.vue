<template>
    <!-- 导航栏改用路由跳转 -->
    <div v-if="$route.path !== '/login'">

        <Navbar />
        <div class="main-content">
            <router-view />
        </div>

    </div>

    <router-view v-else />



    <!-- 路由页面渲染出口 -->



</template>

<script setup>

import Navbar from './components/Navbar/Navbar.vue';

</script>

<style>
@import './assets/global.css';
</style>
