<template>
  <div class="summary-card glass-card">
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="21" y1="10" x2="3" y2="10"></line>
            <line x1="21" y1="6" x2="3" y2="6"></line>
            <line x1="21" y1="14" x2="3" y2="14"></line>
            <line x1="21" y1="18" x2="7" y2="18"></line>
          </svg>
        </div>
        <div>
          <h3 class="card-title">AI Executive Summary</h3>
          <span class="card-meta">
            Style: <strong class="text-white">{{ styleLabel }}</strong> • 
            {{ wordCount }} words • 
            ~{{ readingTime }} min read
          </span>
        </div>
      </div>

      <div class="header-actions">
        <button class="btn btn-secondary btn-sm" @click="copySummary">
          <svg v-if="!copied" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
          </svg>
          <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" class="text-emerald">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
          <span>{{ copied ? 'Copied!' : 'Copy Summary' }}</span>
        </button>
      </div>
    </div>

    <!-- Summary Content Area -->
    <div class="summary-body">
      <!-- Bullet Points View -->
      <div v-if="isBulletStyle" class="bullets-view">
        <div
          v-for="(bullet, index) in parsedBullets"
          :key="index"
          class="bullet-line"
        >
          <span class="bullet-marker">✦</span>
          <span class="bullet-text">{{ bullet }}</span>
        </div>
      </div>

      <!-- Paragraph Text View -->
      <div v-else class="text-view">
        <p
          v-for="(para, index) in paragraphs"
          :key="index"
          class="summary-paragraph"
        >
          {{ para }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  summary: string
  style: string
}>()

const copied = ref(false)

const isBulletStyle = computed(() => {
  return props.style === 'bullet_point' || props.summary.includes('•') || props.summary.includes('- ')
})

const styleLabel = computed(() => {
  if (props.style === 'brief') return 'Concise Brief'
  if (props.style === 'bullet_point') return 'Bullet Highlights'
  return 'Detailed Synthesis'
})

const wordCount = computed(() => {
  if (!props.summary) return 0
  return props.summary.trim().split(/\s+/).length
})

const readingTime = computed(() => {
  return Math.max(1, Math.ceil(wordCount.value / 200))
})

const paragraphs = computed(() => {
  if (!props.summary) return []
  return props.summary.split('\n\n').filter(p => p.trim())
})

const parsedBullets = computed(() => {
  if (!props.summary) return []
  return props.summary
    .split('\n')
    .map(line => line.replace(/^[•\-\*\d\.]+\s*/, '').trim())
    .filter(line => line.length > 0)
})

async function copySummary() {
  if (!props.summary) return
  try {
    await navigator.clipboard.writeText(props.summary)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (e) {
    console.error('Failed to copy', e)
  }
}
</script>

<style scoped>
.summary-card {
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-subtle);
  gap: 16px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: rgba(99, 102, 241, 0.15);
  color: var(--primary-light);
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-title {
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.card-meta {
  font-size: 12px;
  color: var(--text-dim);
}

.summary-body {
  font-size: 14.5px;
  line-height: 1.7;
  color: #e2e8f0;
}

.summary-paragraph {
  margin-bottom: 14px;
}

.summary-paragraph:last-child {
  margin-bottom: 0;
}

/* Bullets View */
.bullets-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bullet-line {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: rgba(255, 255, 255, 0.02);
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
}

.bullet-marker {
  color: var(--secondary);
  font-size: 12px;
  margin-top: 3px;
}

.bullet-text {
  flex: 1;
}

.text-emerald {
  color: var(--accent-emerald);
}

.btn-sm {
  padding: 7px 14px;
  font-size: 13px;
}
</style>
