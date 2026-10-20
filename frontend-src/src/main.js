import { createApp } from 'vue'
//从vue框架导入createApp,用来创建vue应用实例
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
//导入组件库各种按钮输入框等
import router from './router/index.js'

//main.js  是vue3项目的入口文件,整个项目启动的起点,


createApp(App).use(ElementPlus).use(router).mount('#app')
//创建一个vue应用实例,根组件是app.vue
//.use(ElementPlus) 是vue的固定写法   全局注册ElementPlus
//.use(router) 注册路由插件
//.mount('#app')  把整个vue项目,渲染到页面中id="app"的DOM标签上
