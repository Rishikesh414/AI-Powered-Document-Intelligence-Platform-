<template>
  <div class="gauge-card glass-card">
    <div class="card-header">
      <div class="header-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
        <span>Completeness & Certainty Audit</span>
      </div>
      <span class="badge" :class="scoreBadgeClass">{{ scoreQualityLabel }}</span>
    </div>

    <div class="gauge-layout">
      <!-- Circular Progress Meter -->
      <div class="circle-container">
        <svg class="progress-ring" width="140" height="140" viewBox="0 0 140 140">
          <circle
            class="progress-ring-track"
            cx="70"
            cy="70"
            r="54"
            stroke-width="12"
          />
          <circle
            class="progress-ring-fill"
            :class="scoreRingClass"
            cx="70"
            cy="70"
            r="54"
            stroke-width="12"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="dashOffset"
          />
        </svg>
        <div class="circle-content">
          <span class="score-value font-mono">{{ score.toFixed(1) }}<span class="pct">%</span></span>
          <span class="score-caption">Total C_index</span>
        </div>
      </div>

      <!-- Dimension Breakdown Bars -->
      <div class="breakdown-list">
        <div
          v-for="item in breakdown"
          :key="item.dimension"
          class="breakdown-item"
        >
          <div class="item-header">
            <span class="item-label">{{ item.label }}</span>
            <span class="item-score font-mono">
              {{ item.score.toFixed(0) }}%
              <span class="item-weight">(wt: {{ (item.weight * 100).toFixed(0) }}%)</span>
            </span>
          </div>
          <div class="item-progress-track">
            <div
              class="item-progress-fill"
              :class="getItemBarClass(item.score)"
              :style="{ width: `${item.score}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Missing / Uncertainty Flags Section -->
    <div v-if="uncertaintyFlags && uncertaintyFlags.length > 0" class="uncertainty-box">
      <div class="uncertainty-header">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
          <line x1="12" y1="9" x2="12" y2="13"></line>
          <line x1="12" y1="17" x2="12.01" y2="17"></line>
        </svg>
        <span>Missing / Uncertain Attributes Detected ({{ uncertaintyFlags.length }})</span>
      </div>
      <ul class="uncertainty-list">
        <li v-for="(flag, idx) in uncertaintyFlags" :key="idx" class="uncertainty-item">
          <span class="flag-dot"></span>
          <span>{{ flag }}</span>
        </li>
      </ul>
    </div>
    <div v-else class="perfect-fidelity-box">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
      </svg>
      <span>Zero null-coercion conflicts. All primary schema dimensions verified with high confidence.</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  score: number
  breakdown: Array<{
    dimension: string
    label: string
    weight: float
    score: float
  }>
  uncertaintyFlags?: string[]
}>()

const radius = 54
const circumference = 2 * Math.PI * radius

const dashOffset = computed(() => {
  const progress = Math.min(Math.max(props.score, 0), 100) / 100
  return circumference * (1 - progress)
})

const scoreQualityLabel = computed(() => {
  if (props.score >= 85) return 'High Integrity'
  if (props.score >= 60) return 'Moderate Completeness'
  return 'Missing Critical Fields'
})

const scoreBadgeClass = computed(() => {
  if (props.score >= 85) return 'badge-emerald'
  if (props.score >= 60) return 'badge-amber'
  return 'badge-rose'
})

const scoreRingClass = computed(() => {
  if (props.score >= 85) return 'ring-emerald'
  if (props.score >= 60) return 'ring-amber'
  return 'ring-rose'
})

function getItemBarClass(score: number): string {
  if (score >= 85) return 'bar-emerald'
  if (score >= 50) return 'bar-amber'
  return 'bar-rose'
}
</script>

<style scoped>
.gauge-card {
  padding: 20px 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.gauge-layout {
  display: grid;
  grid-template-columns: 160px 1fr;
  align-items: center;
  gap: 24px;
}

/* Circular Meter */
.circle-container {
  position: relative;
  width: 140px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-track {
  fill: none;
  stroke: rgba(255, 255, 255, 0.08);
}

.progress-ring-fill {
  fill: none;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.ring-emerald { stroke: var(--accent-emerald); }
.ring-amber { stroke: var(--accent-amber); }
.ring-rose { stroke: var(--accent-rose); }

.circle-content {
  position: absolute;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.score-value {
  font-size: 26px;
  font-weight: 800;
  color: #fff;
  line-height: 1;
}

.pct {
  font-size: 16px;
  color: var(--text-muted);
}

.score-caption {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Breakdown Bars */
.breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.breakdown-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.item-label {
  color: var(--text-muted);
  font-weight: 500;
}

.item-score {
  font-weight: 600;
  color: #fff;
}

.item-weight {
  color: var(--text-dim);
  font-weight: 400;
  font-size: 11px;
  margin-left: 4px;
}

.item-progress-track {
  height: 6px;
  border-radius: var(--radius-full);
  background: rgba(255, 255, 255, 0.06);
  overflow: hidden;
}

.item-progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 0.6s ease-out;
}

.bar-emerald { background: linear-gradient(90deg, #10b981, #34d399); }
.bar-amber { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.bar-rose { background: linear-gradient(90deg, #f43f5e, #fb7185); }

/* Uncertainty / Missing Attributes Box */
.uncertainty-box {
  margin-top: 20px;
  padding: 12px 16px;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: var(--radius-md);
}

.uncertainty-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  color: var(--accent-amber);
  margin-bottom: 8px;
}

.uncertainty-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.uncertainty-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #fde68a;
  font-family: var(--font-mono);
}

.flag-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent-amber);
  flex-shrink: 0;
}

.perfect-fidelity-box {
  margin-top: 18px;
  padding: 10px 14px;
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--accent-emerald);
}

@media (max-width: 640px) {
  .gauge-layout {
    grid-template-columns: 1fr;
  }
}
</style>
