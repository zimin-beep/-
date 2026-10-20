<template>
    <div class="page page-overview active">
        <div v-for="(item, idx) in total_count" :key="idx" class="welcome-banner">
            <h2>👋 欢迎回来，{{ username }}！</h2>
            <p>今天是{{ year }} 年{{ month }}月{{ day }}日，系统运行正常。当前发现病虫害{{ Number(item.this_week_disease) + Number(item.this_week_pest) }} 例需要关注，请查看下方数据概览了解详细信息。</p>
        </div>


        <!-- 病害、虫害双卡片区 -->
         <div class="category-cards">
    <DiseaseCard v-for="(item, idx) in total_count" :key="idx"
      :disease-total="item.this_week_disease"
      :treated="item.disease_treated"
      :pending="item.disease_untreated"
      :last-week-num="item.last_week_disease"
    />
    <PestCard v-for="(item, idx) in total_count" :key="idx" 
      :pest-total="item.this_week_pest"
      :treated="item.pest_treated"
      :pending="item.pest_untreated"
      :last-week-num="item.last_week_pest"
    />
  </div>




        <div class="stats-grid">


            <div class="stat-card">
                <div class="icon-box icon-red">🍂</div>
                <div v-for="(item, idx) in total_count" :key="idx" class="info">
                    <h3>本周已审核病害</h3>
                    <div class="number">{{ item.this_week_disease_audited }}</div>
                    <div class="trend"
                        :class="Number(item.this_week_disease_audited) > Number(item.last_week_disease_audited) ? 'trend-up' : 'trend-down'">
                        {{ Number(item.this_week_disease_audited) > Number(item.last_week_disease_audited) ? '↑' : '↓' }}
                        较上周 {{ Number(item.this_week_disease_audited) - Number(item.last_week_disease_audited) >= 0 ? '+' : '' }}
                        {{ Number(item.this_week_disease_audited) - Number(item.last_week_disease_audited) }}

                    </div>
                </div>
            </div>



             <div class="stat-card">
                <div class="icon-box icon-red">⚠️</div>
                <div v-for="(item, idx) in total_count" :key="idx" class="info">
                    <h3>本周未经审核病害</h3>
                    <div class="number">{{ item.this_week_disease_pending }}</div>
                    <div class="trend"
                        :class="Number(item.this_week_disease_pending) > Number(item.last_week_disease_pending) ? 'trend-up' : 'trend-down'">
                        {{ Number(item.this_week_disease_pending) > Number(item.last_week_disease_pending) ? '↑' : '↓' }}
                        较上周 {{ Number(item.this_week_disease_pending) - Number(item.last_week_disease_pending) >= 0 ? '+' : '' }}
                        {{ Number(item.this_week_disease_pending) - Number(item.last_week_disease_pending) }}

                    </div>
                </div>
            </div>

            <div class="stat-card">
                <div class="icon-box icon-red">🐛</div>
                <div v-for="(item, idx) in total_count" :key="idx" class="info">
                    <h3>本周已审核虫害</h3>
                    <div class="number">{{ item.this_week_pest_audited }}</div>
                    <div class="trend"
                        :class="Number(item.this_week_pest_audited) > Number(item.last_week_pest_audited) ? 'trend-up' : 'trend-down'">
                        {{ Number(item.this_week_pest_audited) > Number(item.last_week_pest_audited) ? '↑' : '↓' }}
                        较上周 {{ Number(item.this_week_pest_audited) - Number(item.last_week_pest_audited) >= 0 ? '+' : '' }}
                        {{ Number(item.this_week_pest_audited) - Number(item.last_week_pest_audited) }}

                    </div>
                </div>
            </div>


             <div class="stat-card">
                <div class="icon-box icon-red">⚠️</div>
                <div v-for="(item, idx) in total_count" :key="idx" class="info">
                    <h3>本周未经审核虫害</h3>
                    <div class="number">{{ item.this_week_pest_pending }}</div>
                    <div class="trend"
                        :class="Number(item.this_week_pest_pending ) > Number(item.last_week_pest_pending) ? 'trend-up' : 'trend-down'">
                        {{ Number(item.this_week_pest_pending ) > Number(item.last_week_pest_pending) ? '↑' : '↓' }}
                        较上周 {{ Number(item.this_week_pest_pending ) - Number(item.last_week_pest_pending) >= 0 ? '+' : '' }}
                        {{ Number(item.this_week_pest_pending ) - Number(item.last_week_pest_pending) }}

                    </div>
                </div>
            </div>

           
           
        </div>

        <div class="charts-row">
            <div class="chart-card">


                <div class="chart-header">
                    <div class="title">
                        <span class="title-bar"></span>
                        <span class="title-text">{{ chartTitle }}</span>
                    </div>

                    <div class="period-switcher" @click.stop="toggleDropdown">
                        <span class="period-label">{{ periodLabel }}</span>
                        <svg class="chevron" :class="{ open: dropdownOpen }" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="6 9 12 15 18 9" />
                        </svg>

                        <transition name="dropdown">
                            <ul v-if="dropdownOpen" class="dropdown-menu">
                                <li v-for="opt in periodOptions" :key="opt.value"
                                    :class="{ active: currentPeriod === opt.value }" @click.stop="selectPeriod(opt)">
                                    <span class="dot" :style="{ background: opt.color }"></span>
                                    {{ opt.label }}
                                    <svg v-if="currentPeriod === opt.value" class="check" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round">
                                        <polyline points="20 6 9 17 4 12" />
                                    </svg>
                                </li>
                            </ul>
                        </transition>
                    </div>
                </div>

                <!-- ECharts 容器（保留你的 bar-chart 外层） -->
                <div ref="chartRef" class="chart-container"></div>
            </div>


            <div class="panel-card">
                <h3>病虫害类型 TOP 5</h3>
                <ul class="disease-list">
                    <li v-for="(item, idx) in disease.slice(0, 5)" :key="idx">
                        <span class="disease-name">{{ item.disease_name }}</span>
                        <span class="disease-count" :class="item.level">{{ item.total }} 例</span>
                    </li>

                </ul>
            </div>
        </div>




        
    </div>

</template>

<script setup>
import * as echarts from 'echarts'
import axios from 'axios'
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import DiseaseCard from '../Pestoverview/DiseaseCard.vue'
import PestCard from '../Pestoverview/PestCard.vue'
const username = localStorage.getItem('user')
// 响应式日期变量
const year = ref('')
const month = ref('')
const day = ref('')

const record = ref([])
const disease = ref([])
const total_count = ref([])


const chartRef = ref(null)
const dropdownOpen = ref(false)
const currentPeriod = ref('week')
const periodLabel = ref('本月')
const chartTitle = ref('当月每周病虫害趋势')
const trendChartRef = ref(null)
let chartInstance = null
const chartDates = ref([])
const chartDisease = ref([])
const chartPest = ref([])



// 获取当前日期 格式 YYYY-MM-DD
const gettime = async () => {
    const res = await axios.post('/api/gettime', {},)
    const dateStr = res.data.time
    const arr = dateStr.split('-')
    year.value = arr[0]
    month.value = arr[1]
    day.value = arr[2]

}
// 获取当前时间
onMounted(() => {
    
    gettime()
    diseasesum()
    get_total()
    nextTick(() => {
        chartInstance = echarts.init(chartRef.value)
        loadChartData()

        window.addEventListener('resize', onResize)
        document.addEventListener('click', handleClickOutside)
    })

})

onUnmounted(() => {
    window.removeEventListener('resize', onResize)
    document.removeEventListener('click', handleClickOutside)
    chartInstance?.dispose()
})




// 病虫害出现次数统计
const diseasesum = async () => {
    const res = await axios.post('/api/sum', {})
    disease.value = res.data.msg
}
//病虫害各自出现的次数
const get_total = async () => {
    const res = await axios.post('/api/total', {})
    total_count.value = res.data.msg
}


//病虫害的折线统计图
//病虫害的折线统计图接口
const loadChartData = async () => {
    const res = await axios.post('/api/total_record', {
        period: currentPeriod.value
    })
    const list = res.data.msg || []
    chartDates.value = list.map(item => item.period_label)
    chartDisease.value = list.map(item => Number(item.disease_cnt))
    chartPest.value = list.map(item => Number(item.pest_cnt))
    renderChart()
}


const periodOptions = [
    { value: 'week', label: '本月', title: '当月每周病虫害趋势', color: '#409EFF' },
    { value: 'month', label: '本年', title: '本年度每个月病虫害趋势', color: '#67C23A' },
    { value: 'year', label: '每年', title: '每年病虫害趋势', color: '#E6A23C' }
]
// 下拉交互
const toggleDropdown = () => {
    dropdownOpen.value = !dropdownOpen.value
}

const selectPeriod = (opt) => {
    currentPeriod.value = opt.value
    periodLabel.value = opt.label
    chartTitle.value = opt.title
    dropdownOpen.value = false
    loadChartData()
}

const handleClickOutside = (e) => {
    if (!e.target.closest('.period-switcher')) {
        dropdownOpen.value = false
    }
}

const renderChart = () => {
    if (!chartInstance) return

    const option = {
        tooltip: { trigger: 'axis' },
        legend: {
            data: ['病害', '虫害'],
            top: 0,
            right: 10,
            textStyle: { fontSize: 12 }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '5%',
            top: '18%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: chartDates.value,
            boundaryGap: false,
            axisLine: { lineStyle: { color: '#ddd' } },
            axisLabel: { color: '#666', fontSize: 12 }
        },
        yAxis: {
            type: 'value',
            minInterval: 1,
            splitLine: { lineStyle: { color: '#f0f0f0' } },
            axisLabel: { color: '#666', fontSize: 12 }
        },
        series: [
            {
                name: '病害',
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                data: chartDisease.value,
                lineStyle: { width: 3, color: '#409EFF' },
                itemStyle: { color: '#409EFF' },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(64,158,255,0.3)' },
                        { offset: 1, color: 'rgba(64,158,255,0.02)' }
                    ])
                }
            },
            {
                name: '虫害',
                type: 'line',
                smooth: true,
                symbol: 'circle',
                symbolSize: 6,
                data: chartPest.value,
                lineStyle: { width: 3, color: '#F56C6C' },
                itemStyle: { color: '#F56C6C' },
                areaStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(245,108,108,0.3)' },
                        { offset: 1, color: 'rgba(245,108,108,0.02)' }
                    ])
                }
            }
        ]
    }

    chartInstance.setOption(option)
}

const onResize = () => chartInstance?.resize()








</script>

<style scoped src="./Overview.css"></style>
