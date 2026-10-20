<template>
    <div class="category-card card-disease">
        <div class="card-top">
            <div class="card-title">
                <span class="emoji">🦠</span>
                <div>
                    <h2>病害</h2>
                    <div class="sub">Disease</div>
                    <span class="trend-badge trend-up">
                        {{ or }} 较上周 {{ diseaseDiff >= 0 ? '+' : '' }}{{ diseaseDiff }}
                    </span>
                </div>
            </div>
            <!-- SVG环形治理率 -->
            <div class="ring-wrap">
                <svg width="72" height="72">
                    <circle class="ring-bg" cx="36" cy="36" r="30" />
                    <circle class="ring-fg disease-ring" cx="36" cy="36" r="30"
                        :style="{ strokeDashoffset: ringOffset }" />
                </svg>
                <div class="ring-text">
                    <span class="pct">{{ treatRate }}%</span>
                    <span class="pct-label">治理率</span>
                </div>
            </div>
        </div>

        <div class="found-section">
            <div class="label">已发现</div>
            <div class="big-number">
                {{ diseaseTotal }} <span style="font-size:16px;font-weight:500;color:#95a5a6;">例</span>
            </div>
        </div>
        <div class="divider"></div>

        <div class="status-row">
            <div class="status-item treated">
                <div class="s-label">✅ 已治理完成</div>
                <div class="s-value">{{ treated }} <span style="font-size:13px;font-weight:500;color:#7f8c8d;">例</span>
                </div>
            </div>
            <div class="status-item pending alert">
                <div class="s-label">⏳ 待治理</div>
                <div class="s-value">{{ pending }} <span style="font-size:13px;font-weight:500;color:#7f8c8d;">例</span>
                </div>
            </div>
        </div>

        <div class="progress-section">
            <div class="progress-bar">
                <div class="segment-treated"
                    :style="{ width: treatRate + '%', background: 'linear-gradient(90deg,#ef5350,#ff8a65)' }"></div>
                <div class="segment-pending" :style="{ width: (100 - treatRate) + '%', background: '#fce4ec' }"></div>
            </div>
            <div class="progress-labels">
                <span>已治理 {{ treated }} ({{ treatRate }}%)</span>
                <span>待治理 {{ pending }} ({{ 100 - treatRate }}%)</span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
    diseaseTotal: Number,
    treated: Number,
    pending: Number,
    lastWeekNum: Number
})
// 治理百分比
const treatRate = computed(() => {
    if (props.diseaseTotal === 0) return 0
    return Math.round(props.treated / props.diseaseTotal * 100)
})
// 环形周长 2*PI*30 ≈ 188.5
const C = 188.5
const ringOffset = computed(() => C - (treatRate.value / 100) * C)
// 周差值
const diseaseDiff = computed(() => props.diseaseTotal - props.lastWeekNum)
const or = computed(() => (props.diseaseTotal > props.lastWeekNum) ? '▲' : '▼')

</script>
<style scoped src="./DiseaseCard.css"></style>