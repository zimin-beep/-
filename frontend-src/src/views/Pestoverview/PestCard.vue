<template>
  <div class="category-card card-pest">
    <div class="card-top">
      <div class="card-title">
        <span class="emoji">🐛</span>
        <div>
          <h2>虫害</h2>
          <div class="sub">Pest</div>
          <span class="trend-badge trend-down">
            {{ or }} 较上周 {{ pestDiff >= 0 ? '+' : '' }}{{ pestDiff }}
          </span>
        </div>
      </div>
       <!-- SVG环形治理率 -->
      <div class="ring-wrap">
        <svg width="72" height="72">
          <circle class="ring-bg" cx="36" cy="36" r="30" />
          <circle 
            class="ring-fg pest-ring" 
            cx="36" cy="36" r="30"
            :style="{ strokeDashoffset: ringOffset }"
          />
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
        {{ pestTotal }} <span style="font-size:16px;font-weight:500;color:#95a5a6;">例</span>
      </div>
    </div>
    <div class="divider"></div>

    <div class="status-row">
      <div class="status-item treated">
        <div class="s-label">✅ 已治理完成</div>
        <div class="s-value">{{ treated }} <span style="font-size:13px;font-weight:500;color:#7f8c8d;">例</span></div>
      </div>
      <div class="status-item pending">
        <div class="s-label">⏳ 待治理</div>
        <div class="s-value">{{ pending }} <span style="font-size:13px;font-weight:500;color:#7f8c8d;">例</span></div>
      </div>
    </div>

    <div class="progress-section">
      <div class="progress-bar">
        <div 
          class="segment-treated"
          :style="{ width: treatRate + '%', background: 'linear-gradient(90deg,#2d8a4e,#66bb6a)' }"
        ></div>
        <div 
          class="segment-pending"
          :style="{ width: (100 - treatRate) + '%', background: '#e8f5e9' }"
        ></div>
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
  pestTotal: Number,
  treated: Number,
  pending: Number,
  lastWeekNum: Number
})

const treatRate = computed(() => {
  if (props.pestTotal === 0) return 0
  return Math.round(props.treated / props.pestTotal * 100)
  
})

const C = 188.5
const ringOffset = computed(() => C - (treatRate.value / 100) * C)
const pestDiff = computed(() => props.pestTotal - props.lastWeekNum)
const or = computed(() => (props.pestTotal > props.lastWeekNum)  ? '▲' : '▼')




</script>
<style scoped src="./PestCard.css"></style>