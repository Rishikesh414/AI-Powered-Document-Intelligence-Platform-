<template>
  <div class="visuals-card glass-card">
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="20" x2="18" y2="10"></line>
            <line x1="12" y1="20" x2="12" y2="4"></line>
            <line x1="6" y1="20" x2="6" y2="14"></line>
          </svg>
        </div>
        <div>
          <h3 class="card-title">AI Visual Insights & Infographics</h3>
          <span class="card-meta">
            Domain Analytics & Synthesis Visualization
          </span>
        </div>
      </div>

      <div class="header-tabs">
        <button
          class="tab-btn"
          :class="{ active: activeSection === 'charts' }"
          @click="activeSection = 'charts'"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
            <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
          </svg>
          <span>Domain Charts</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: activeSection === 'infographic' }"
          @click="activeSection = 'infographic'"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
            <circle cx="8.5" cy="8.5" r="1.5"></circle>
            <polyline points="21 15 16 10 5 21"></polyline>
          </svg>
          <span>AI Infographic</span>
        </button>
      </div>
    </div>

    <!-- 1. DOMAIN CHARTS VIEW -->
    <div v-if="activeSection === 'charts'" class="charts-view slide-up">
      <!-- 1A. RESUME CHARTS -->
      <div v-if="documentType === 'resume'" class="charts-grid">
        <!-- Skills Distribution Donut Chart -->
        <div class="chart-box">
          <div class="chart-header">
            <span class="chart-title">Skills Distribution by Category</span>
            <span class="badge badge-primary">Competency Matrix</span>
          </div>

          <div v-if="skillDonutData.length > 0" class="donut-chart-layout">
            <div class="donut-svg-wrapper">
              <svg viewBox="0 0 120 120" class="donut-svg">
                <circle
                  v-for="(seg, idx) in skillDonutSegments"
                  :key="idx"
                  cx="60"
                  cy="60"
                  r="45"
                  fill="transparent"
                  :stroke="seg.color"
                  stroke-width="18"
                  :stroke-dasharray="`${seg.dash} ${seg.gap}`"
                  :stroke-dashoffset="seg.offset"
                  class="donut-segment"
                />
              </svg>
              <div class="donut-center">
                <span class="donut-total font-mono">{{ totalSkillsCount }}</span>
                <span class="donut-sub">Skills</span>
              </div>
            </div>

            <div class="donut-legend">
              <div
                v-for="(item, idx) in skillDonutData"
                :key="idx"
                class="legend-item"
              >
                <span class="legend-dot" :style="{ backgroundColor: getChartColor(idx) }"></span>
                <span class="legend-name">{{ item.name }}</span>
                <span class="legend-val font-mono">{{ item.value }} ({{ getSkillPct(item.value) }}%)</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-chart">No skill categories available to chart.</div>
        </div>

        <!-- Career Progression Timeline -->
        <div class="chart-box">
          <div class="chart-header">
            <span class="chart-title">Career Progression & Roles</span>
            <span class="badge badge-cyan">Chronology</span>
          </div>

          <div v-if="experienceTimeline.length > 0" class="timeline-container">
            <div
              v-for="(item, idx) in experienceTimeline"
              :key="idx"
              class="timeline-item"
            >
              <div class="timeline-marker"></div>
              <div class="timeline-content">
                <div class="timeline-dates font-mono">{{ item.start }} – {{ item.end }}</div>
                <div class="timeline-role">{{ item.role }}</div>
                <div class="timeline-company">{{ item.company }}</div>
              </div>
            </div>
          </div>
          <div v-else class="empty-chart">No career timeline documented.</div>
        </div>
      </div>

      <!-- 1B. RESEARCH PAPER CHARTS -->
      <div v-else-if="documentType === 'research_paper'" class="charts-grid">
        <!-- Benchmark Grouped Bar Chart -->
        <div class="chart-box full-width">
          <div class="chart-header">
            <span class="chart-title">Benchmark Results: Proposed Model vs Baseline</span>
            <div class="legend-row">
              <span class="legend-tag proposed"><span class="dot"></span> Proposed Architecture</span>
              <span class="legend-tag baseline"><span class="dot"></span> Baseline Benchmark</span>
            </div>
          </div>

          <div v-if="benchmarkData.categories.length > 0" class="bar-chart-container">
            <div
              v-for="(cat, idx) in benchmarkData.categories"
              :key="idx"
              class="bar-row"
            >
              <div class="bar-label">{{ cat }}</div>
              <div class="bar-lanes">
                <!-- Proposed Bar -->
                <div class="lane">
                  <div
                    class="bar-fill proposed-bar"
                    :style="{ width: `${getBarPct(benchmarkData.proposed[idx], benchmarkMaxVal)}%` }"
                  >
                    <span class="bar-val font-mono">{{ benchmarkData.proposed[idx] }}</span>
                  </div>
                </div>
                <!-- Baseline Bar -->
                <div class="lane">
                  <div
                    class="bar-fill baseline-bar"
                    :style="{ width: `${getBarPct(benchmarkData.baseline[idx], benchmarkMaxVal)}%` }"
                  >
                    <span class="bar-val font-mono">{{ benchmarkData.baseline[idx] }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-chart">No empirical benchmark metrics found in document.</div>
        </div>
      </div>

      <!-- 1C. BUSINESS REPORT CHARTS -->
      <div v-else class="charts-grid">
        <!-- KPI Actual vs Target Performance -->
        <div class="chart-box">
          <div class="chart-header">
            <span class="chart-title">Executive KPIs: Actual vs Target</span>
            <div class="legend-row">
              <span class="legend-tag proposed"><span class="dot"></span> Actual</span>
              <span class="legend-tag baseline"><span class="dot"></span> Target/Prior</span>
            </div>
          </div>

          <div v-if="kpiChartData.categories.length > 0" class="bar-chart-container">
            <div
              v-for="(cat, idx) in kpiChartData.categories"
              :key="idx"
              class="bar-row"
            >
              <div class="bar-label">{{ cat }}</div>
              <div class="bar-lanes">
                <div class="lane">
                  <div
                    class="bar-fill proposed-bar"
                    :style="{ width: `${getBarPct(kpiChartData.actual[idx], kpiMaxVal)}%` }"
                  >
                    <span class="bar-val font-mono">{{ kpiChartData.actual[idx] }}</span>
                  </div>
                </div>
                <div class="lane">
                  <div
                    class="bar-fill baseline-bar"
                    :style="{ width: `${getBarPct(kpiChartData.target[idx], kpiMaxVal)}%` }"
                  >
                    <span class="bar-val font-mono">{{ kpiChartData.target[idx] }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="empty-chart">No executive KPIs found in document.</div>
        </div>

        <!-- Segment Revenue Breakdown Donut -->
        <div class="chart-box">
          <div class="chart-header">
            <span class="chart-title">Segment Revenue Share</span>
            <span class="badge badge-emerald">Q3 Contribution</span>
          </div>

          <div v-if="segmentData.length > 0" class="donut-chart-layout">
            <div class="donut-svg-wrapper">
              <svg viewBox="0 0 120 120" class="donut-svg">
                <circle
                  v-for="(seg, idx) in segmentDonutSegments"
                  :key="idx"
                  cx="60"
                  cy="60"
                  r="45"
                  fill="transparent"
                  :stroke="seg.color"
                  stroke-width="18"
                  :stroke-dasharray="`${seg.dash} ${seg.gap}`"
                  :stroke-dashoffset="seg.offset"
                  class="donut-segment"
                />
              </svg>
              <div class="donut-center">
                <span class="donut-total font-mono">100<span class="pct">%</span></span>
                <span class="donut-sub">Revenue</span>
              </div>
            </div>

            <div class="donut-legend">
              <div
                v-for="(item, idx) in segmentData"
                :key="idx"
                class="legend-item"
              >
                <span class="legend-dot" :style="{ backgroundColor: getSegmentColor(idx) }"></span>
                <span class="legend-name">{{ item.name }}</span>
                <span class="legend-val font-mono">{{ item.value }}%</span>
              </div>
            </div>
          </div>
          <div v-else class="empty-chart">No segment breakdown metrics available.</div>
        </div>
      </div>
    </div>

    <!-- 2. AI INFOGRAPHIC CARD VIEW (POLLINATIONS.AI) -->
    <div v-else class="infographic-view slide-up">
      <div class="infographic-container">
        <div class="infographic-header">
          <div>
            <div class="info-title">Zero-Cost AI Synthesized Visual Card</div>
            <div class="info-caption">Real-time contextual visual generated via Pollinations.ai API</div>
          </div>
          <a
            v-if="infographicUrl"
            :href="infographicUrl"
            target="_blank"
            rel="noopener noreferrer"
            class="btn btn-secondary btn-sm"
          >
            <span>Open High-Res</span>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
              <polyline points="15 3 21 3 21 9"></polyline>
              <line x1="10" y1="14" x2="21" y2="3"></line>
            </svg>
          </a>
        </div>

        <div class="image-wrapper">
          <img
            v-if="infographicUrl"
            :src="infographicUrl"
            alt="AI Visual Summary Infographic"
            class="ai-image"
            loading="lazy"
          />
          <div v-else class="image-placeholder">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
              <circle cx="8.5" cy="8.5" r="1.5"></circle>
              <polyline points="21 15 16 10 5 21"></polyline>
            </svg>
            <span>AI Infographic ready upon document analysis</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  documentType: string
  chartsData: Record<string, any>
  infographicUrl?: string
}>()

const activeSection = ref<'charts' | 'infographic'>('charts')

const chartColors = ['#6366f1', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ec4899']
const segmentColors = ['#6366f1', '#06b6d4', '#10b981', '#f59e0b']

function getChartColor(idx: number): string {
  return chartColors[idx % chartColors.length]
}

function getSegmentColor(idx: number): string {
  return segmentColors[idx % segmentColors.length]
}

// 1. Resume Skills Donut Computations
const skillDonutData = computed(() => {
  const dist = props.chartsData?.skills_distribution
  if (dist && dist.type === 'pie' && Array.isArray(dist.data)) {
    return dist.data
  }
  return []
})

const totalSkillsCount = computed(() => {
  return skillDonutData.value.reduce((acc: number, item: any) => acc + (item.value || 0), 0)
})

function getSkillPct(val: number): string {
  if (!totalSkillsCount.value) return '0'
  return ((val / totalSkillsCount.value) * 100).toFixed(0)
}

const skillDonutSegments = computed(() => {
  const total = totalSkillsCount.value
  if (!total) return []
  const c = 2 * Math.PI * 45 // 282.74
  let currentOffset = 0
  return skillDonutData.value.map((item: any, idx: number) => {
    const fraction = item.value / total
    const dash = fraction * c
    const gap = c - dash
    const offset = -currentOffset
    currentOffset += dash
    return {
      dash,
      gap,
      offset,
      color: getChartColor(idx),
    }
  })
})

const experienceTimeline = computed(() => {
  const t = props.chartsData?.experience_timeline
  if (t && Array.isArray(t.data)) {
    return t.data
  }
  return []
})

// 2. Research Paper Benchmark Computations
const benchmarkData = computed(() => {
  const bm = props.chartsData?.benchmark_comparison
  if (bm && bm.categories && bm.series) {
    const proposedSeries = bm.series.find((s: any) => s.name === 'Proposed')?.data || []
    const baselineSeries = bm.series.find((s: any) => s.name === 'Baseline')?.data || []
    return {
      categories: bm.categories,
      proposed: proposedSeries,
      baseline: baselineSeries,
    }
  }
  return { categories: [], proposed: [], baseline: [] }
})

const benchmarkMaxVal = computed(() => {
  const all = [...benchmarkData.value.proposed, ...benchmarkData.value.baseline]
  return Math.max(...all, 100)
})

// 3. Business Report KPI Computations
const kpiChartData = computed(() => {
  const kpi = props.chartsData?.kpi_dashboard
  if (kpi && kpi.categories && kpi.series) {
    const actual = kpi.series.find((s: any) => s.name === 'Actual')?.data || []
    const target = kpi.series.find((s: any) => s.name.includes('Target'))?.data || []
    return {
      categories: kpi.categories,
      actual,
      target,
    }
  }
  return { categories: [], actual: [], target: [] }
})

const kpiMaxVal = computed(() => {
  const all = [...kpiChartData.value.actual, ...kpiChartData.value.target]
  return Math.max(...all, 100)
})

const segmentData = computed(() => {
  const seg = props.chartsData?.segment_breakdown
  if (seg && Array.isArray(seg.data)) {
    return seg.data
  }
  return []
})

const segmentDonutSegments = computed(() => {
  const total = segmentData.value.reduce((acc: number, item: any) => acc + (item.value || 0), 0) || 100
  const c = 2 * Math.PI * 45
  let currentOffset = 0
  return segmentData.value.map((item: any, idx: number) => {
    const fraction = item.value / total
    const dash = fraction * c
    const gap = c - dash
    const offset = -currentOffset
    currentOffset += dash
    return {
      dash,
      gap,
      offset,
      color: getSegmentColor(idx),
    }
  })
})

function getBarPct(val: number, max: number): number {
  if (!max || !val) return 0
  return Math.min(100, Math.max(5, (val / max) * 100))
}
</script>

<style scoped>
.visuals-card {
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
  background: rgba(139, 92, 246, 0.15);
  color: var(--accent-purple);
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

.header-tabs {
  display: flex;
  background: var(--surface-input);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  padding: 3px;
  gap: 3px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn.active {
  background: var(--surface-elevated);
  color: #fff;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
}

.chart-box {
  padding: 18px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  display: flex;
  flex-direction: column;
}

.chart-box.full-width {
  grid-column: 1 / -1;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 8px;
}

.chart-title {
  font-size: 13.5px;
  font-weight: 700;
  color: #fff;
}

/* Donut Chart */
.donut-chart-layout {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 20px;
  flex-wrap: wrap;
  padding: 8px 0;
}

.donut-svg-wrapper {
  position: relative;
  width: 130px;
  height: 130px;
}

.donut-svg {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.donut-segment {
  transition: stroke-dasharray 0.8s ease-out;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.donut-total {
  font-size: 22px;
  font-weight: 800;
  color: #fff;
  line-height: 1;
}

.donut-sub {
  font-size: 10px;
  color: var(--text-dim);
  text-transform: uppercase;
}

.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  color: var(--text-muted);
}

.legend-val {
  color: #fff;
  font-weight: 600;
  margin-left: auto;
}

/* Timeline */
.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-left: 12px;
  position: relative;
}

.timeline-container::before {
  content: '';
  position: absolute;
  left: 17px;
  top: 8px;
  bottom: 8px;
  width: 2px;
  background: var(--border-medium);
}

.timeline-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  position: relative;
}

.timeline-marker {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--secondary);
  border: 2px solid var(--bg-primary);
  margin-top: 3px;
  flex-shrink: 0;
  box-shadow: 0 0 8px var(--secondary-glow);
}

.timeline-dates {
  font-size: 11px;
  color: var(--secondary);
  font-weight: 600;
}

.timeline-role {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.timeline-company {
  font-size: 12px;
  color: var(--text-dim);
}

/* Bar Chart */
.legend-row {
  display: flex;
  gap: 14px;
  font-size: 12px;
}

.legend-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-muted);
}

.legend-tag .dot {
  width: 8px;
  height: 8px;
  border-radius: 2px;
}

.legend-tag.proposed .dot { background: var(--primary); }
.legend-tag.baseline .dot { background: rgba(255, 255, 255, 0.25); }

.bar-chart-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 6px;
}

.bar-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bar-label {
  font-size: 12px;
  color: #cbd5e1;
  font-weight: 600;
}

.bar-lanes {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lane {
  background: rgba(255, 255, 255, 0.04);
  border-radius: var(--radius-sm);
  height: 22px;
  position: relative;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}

.proposed-bar {
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
}

.baseline-bar {
  background: rgba(255, 255, 255, 0.18);
}

.bar-val {
  font-size: 11px;
  font-weight: 700;
  color: #fff;
}

/* Infographic Card */
.infographic-container {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.infographic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-title {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.info-caption {
  font-size: 12px;
  color: var(--text-dim);
}

.image-wrapper {
  width: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border-medium);
  background: #090d16;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.ai-image {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.ai-image:hover {
  transform: scale(1.01);
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: var(--text-dim);
  font-size: 13px;
  padding: 40px;
}

.empty-chart {
  padding: 30px;
  text-align: center;
  color: var(--text-dim);
  font-size: 13px;
}
</style>
