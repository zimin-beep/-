import { createRouter, createWebHistory } from 'vue-router'
// 引入页面组件
import Overview from '../views/Overview/Overview.vue'
import Detection from '../views/Detection/Detection.vue'
import login from '../login/login.vue'
import axios from 'axios'
import Record from '../views/Record/Record.vue'
import Knowledge from '../views/Knowledge/Knowledge.vue'
import UserList from '../UserList/UserList.vue'

const routes = [
    {
        path: '/',
        redirect: '/login'
    },
    {
        path: '/login',
        component: login
    },
    {
        path: '/overview',
        name: 'Overview',
        component: Overview,
        meta: { title: '数据概览' }
    },
    {
        path: '/detection',
        name: 'Detection',
        component: Detection,
        meta: { title: '病虫害检测' }
    },
    {
        path: '/record',
        name: 'Record',
        component: Record,
        meta: { title: '检测记录筛选' }
    },
     {
        path: '/knowledge',
        name: 'Knowledge',
        component: Knowledge,
        meta: { title: '知识库管理' }
    },
    {
        path:'/userlist',
        name:'UserList',
        component:UserList,
        meta:{title:'用户管理', requiresAdmin: true}
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// ========== 全局前置守卫：登录鉴权 + 管理员权限==========
router.beforeEach((to, from, next) => {
    document.title = to.meta.title || '病虫害检测系统'
    const token = localStorage.getItem('access_token')
    // 白名单：登录页不需要token
    const whitePath = ['/login']
    // 无token且不在白名单，强制跳登录
    if (!token && !whitePath.includes(to.path)) {
        return next('/login')
    }
    // 需要管理员权限的页面
    if (to.meta.requiresAdmin && localStorage.getItem('user1') !== '1') {
        alert('⚠️ 您没有访问该页面的权限')
        return next('/overview')
    }
    next()
})



// 全局标记：防止并发重复刷新
let isRefreshing = false
// 等待重发的请求队列
let requestQueue = []

// 请求拦截器 自动携带access_token
axios.interceptors.request.use(config => {
    const accessToken = localStorage.getItem("access_token")
    // 登录、刷新接口不需要携带access
    if (config.url.includes('/api/login') || config.url.includes('/api/refresh_token')) {
        return config
    }
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
}, err => Promise.reject(err))

// 响应拦截器：token过期自动刷新
axios.interceptors.response.use(
    res => res,
    async err => {
        const originConfig = err.config
        if (!err.response) return Promise.reject(err)
        const status = err.response.status

        // access_token过期 401 执行自动刷新逻辑
        if (status === 401 && !originConfig._retry) {
            originConfig._retry = true // 标记只重试一次，防止死循环

            // 不在刷新流程中，执行刷新
            if (!isRefreshing) {
                isRefreshing = true
                const refreshToken = localStorage.getItem('refresh_token')
                // 没有刷新凭证，只能重新登录
                if (!refreshToken) {
                    localStorage.clear()
                    router.push('/login')
                    alert("登录失效，请重新登录")
                    return Promise.reject(err)
                }
                try {
                    // 请求后端刷新接口，换新token
                    const res = await axios.post('/api/refresh_token', {}, {
                        headers: {
                            Authorization: `Bearer ${refreshToken}`
                        }
                    })
                    const newToken = res.data.new_access_token
                    // 本地替换旧token
                    localStorage.setItem('access_token', newToken)
                    // 队列里所有等待的请求统一使用新token重发
                    requestQueue.forEach(callback => callback(newToken))
                    requestQueue = []
                    // 重试当前报错的接口
                    return axios(originConfig)
                } catch (refreshErr) {
                    // refresh_token过期/失效，清空缓存跳转登录
                    localStorage.clear()
                    requestQueue = []
                    router.push('/login')
                    alert("登录凭证已过期，请重新登录")
                    return Promise.reject(refreshErr)
                } finally {
                    isRefreshing = false
                }
            } else {
                // 正在刷新，把当前请求加入队列等待
                return new Promise(resolve => {
                    requestQueue.push((token) => {
                        originConfig.headers.Authorization = `Bearer ${token}`
                        resolve(axios(originConfig))
                    })
                })
            }
        }

        if (status === 402) {
            localStorage.clear()
            router.push('/login')
            alert("请先登录账号")
        }
        return Promise.reject(err)
    }
)
export default router
