<template>
  <div class="controls-panel glass-card">
    <div class="controls-header">
      <div class="controls-title">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
        <span>Adaptive Pipeline Configuration</span>
      </div>
      <span class="badge badge-cyan">Dynamic Schema Engine</span>
    </div>

    <div class="controls-grid">
      <!-- 1. Document Type Domain Selector -->
      <div class="control-group">
        <label class="form-label">1. Target Document Schema</label>
        <div class="segmented-control">
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.document_type === 'resume' }"
            @click="updateField('document_type', 'resume')"
          >
            <span class="seg-icon">👤</span>
            <span>Resume / CV</span>
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.document_type === 'research_paper' }"
            @click="updateField('document_type', 'research_paper')"
          >
            <span class="seg-icon">📑</span>
            <span>Research Paper</span>
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.document_type === 'business_analytics_report' }"
            @click="updateField('document_type', 'business_analytics_report')"
          >
            <span class="seg-icon">📈</span>
            <span>Business Report</span>
          </button>
        </div>
      </div>

      <!-- 2. Summary Style Selector -->
      <div class="control-group">
        <label class="form-label">2. Summary Synthesis Style</label>
        <div class="segmented-control">
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.summary_style === 'brief' }"
            @click="updateField('summary_style', 'brief')"
          >
            <span class="seg-icon">⚡</span>
            <span>Brief (2-3 Sentences)</span>
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.summary_style === 'detailed' }"
            @click="updateField('summary_style', 'detailed')"
          >
            <span class="seg-icon">📖</span>
            <span>Detailed Synthesis</span>
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.summary_style === 'bullet_point' }"
            @click="updateField('summary_style', 'bullet_point')"
          >
            <span class="seg-icon">📌</span>
            <span>Bullet Points</span>
          </button>
        </div>
      </div>

      <!-- 3. Analysis Depth Slider / Options -->
      <div class="control-group">
        <div class="label-with-hint">
          <label class="form-label">3. Analysis Extraction Depth</label>
          <span class="depth-hint">{{ depthDescriptions[modelValue.analysis_level] }}</span>
        </div>
        <div class="segmented-control">
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.analysis_level === 'basic' }"
            @click="updateField('analysis_level', 'basic')"
          >
            <span>Basic</span>
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.analysis_level === 'standard' }"
            @click="updateField('analysis_level', 'standard')"
          >
            <span>Standard</span>
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: modelValue.analysis_level === 'detailed' }"
            @click="updateField('analysis_level', 'detailed')"
          >
            <span>Exhaustive</span>
          </button>
        </div>
      </div>

      <!-- 4. Domain-Adaptive Focus Topics -->
      <div class="control-group">
        <label class="form-label">4. Focus Topics & Priority Weighting</label>
        <div class="topic-checkboxes">
          <label
            v-for="topic in currentTopics"
            :key="topic.id"
            class="topic-pill"
            :class="{ selected: selectedTopics.includes(topic.id) }"
          >
            <input
              type="checkbox"
              :value="topic.id"
              :checked="selectedTopics.includes(topic.id)"
              class="hidden-cb"
              @change="toggleTopic(topic.id)"
            />
            <span class="cb-checkmark"></span>
            <span class="topic-label">{{ topic.label }}</span>
          </label>
        </div>
      </div>
    </div>

    <!-- CTA Execution Bar -->
    <div class="controls-action-bar">
      <div class="action-info">
        <span class="action-caption">
          Selected: <strong class="text-white">{{ docTypeLabel }}</strong> • 
          Style: <strong>{{ summaryStyleLabel }}</strong> • 
          Depth: <strong>{{ depthLabel }}</strong>
        </span>
      </div>

      <button
        class="btn btn-primary btn-run"
        :disabled="!hasDocument || isAnalyzing"
        @click="$emit('run-analysis')"
      >
        <svg v-if="!isAnalyzing" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polygon points="5 3 19 12 5 21 5 3"></polygon>
        </svg>
        <div v-else class="spinner animate-spin"></div>
        <span v-if="!isAnalyzing">Run Intelligent Analysis</span>
        <span v-else>Analyzing Document with AI...</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  modelValue: {
    document_type: 'resume' | 'research_paper' | 'business_analytics_report'
    summary_style: 'brief' | 'detailed' | 'bullet_point'
    analysis_level: 'basic' | 'standard' | 'detailed'
    focus_topics: string[]
  }
  hasDocument: boolean
  isAnalyzing: boolean
}>()

const emit = defineEmits(['update:modelValue', 'run-analysis'])

const depthDescriptions: Record<string, string> = {
  basic: 'Core top-level metadata only',
  standard: 'Balanced structural extraction & chronology',
  detailed: 'Exhaustive breakdown, sub-attributes & citation trace',
}

const topicsMap = {
  resume: [
    { id: 'skills', label: 'Technical & Soft Skills' },
    { id: 'work_experience', label: 'Career Track Record' },
    { id: 'educational_qualifications', label: 'Academic Pedigree' },
    { id: 'certifications', label: 'Professional Certifications' },
  ],
  research_paper: [
    { id: 'methodology_summary', label: 'Methodology Architecture' },
    { id: 'benchmark_results', label: 'Empirical Benchmarks' },
    { id: 'key_findings', label: 'Key Contributions' },
    { id: 'limitations_and_future_work', label: 'Limitations & Open Questions' },
  ],
  business_analytics_report: [
    { id: 'executive_kpis', label: 'Executive Financial KPIs' },
    { id: 'segment_breakdown', label: 'Segment Revenue Breakdown' },
    { id: 'key_growth_drivers', label: 'Growth Catalyst Drivers' },
    { id: 'strategic_recommendations', label: 'Strategic Action Items' },
  ],
}

const currentTopics = computed(() => {
  return topicsMap[props.modelValue.document_type] || topicsMap.resume
})

const selectedTopics = computed(() => props.modelValue.focus_topics || [])

const docTypeLabel = computed(() => {
  if (props.modelValue.document_type === 'resume') return 'Resume / CV'
  if (props.modelValue.document_type === 'research_paper') return 'Research Paper'
  return 'Business Analytics'
})

const summaryStyleLabel = computed(() => {
  if (props.modelValue.summary_style === 'brief') return 'Brief'
  if (props.modelValue.summary_style === 'bullet_point') return 'Bullet Points'
  return 'Detailed'
})

const depthLabel = computed(() => {
  if (props.modelValue.analysis_level === 'basic') return 'Basic'
  if (props.modelValue.analysis_level === 'detailed') return 'Exhaustive'
  return 'Standard'
})

function updateField(key: string, value: any) {
  emit('update:modelValue', {
    ...props.modelValue,
    [key]: value,
  })
}

function toggleTopic(topicId: string) {
  const current = [...selectedTopics.value]
  const idx = current.indexOf(topicId)
  if (idx === -1) {
    current.push(topicId)
  } else {
    current.splice(idx, 1)
  }
  updateField('focus_topics', current)
}
</script>

<style scoped>
.controls-panel {
  padding: 24px;
}

.controls-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-subtle);
}

.controls-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.controls-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
}

.label-with-hint {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.depth-hint {
  font-size: 12px;
  color: var(--text-dim);
}

/* Segmented Control */
.segmented-control {
  display: flex;
  background: var(--surface-input);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  padding: 4px;
  gap: 4px;
}

.seg-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 9px 12px;
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.seg-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.seg-btn.active {
  background: var(--primary);
  color: #fff;
  box-shadow: 0 2px 8px var(--primary-glow);
}

.seg-icon {
  font-size: 14px;
}

/* Topic Checkboxes */
.topic-checkboxes {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.topic-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  background: var(--surface-card);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-full);
  font-size: 13px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  user-select: none;
}

.topic-pill:hover {
  border-color: var(--border-strong);
  color: #fff;
}

.topic-pill.selected {
  background: rgba(99, 102, 241, 0.15);
  border-color: var(--primary);
  color: var(--primary-light);
}

.hidden-cb {
  display: none;
}

.cb-checkmark {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  display: inline-block;
  position: relative;
  transition: all var(--transition-fast);
}

.topic-pill.selected .cb-checkmark {
  background: var(--primary);
  border-color: var(--primary);
}

.topic-pill.selected .cb-checkmark::after {
  content: '';
  position: absolute;
  left: 4px;
  top: 1px;
  width: 4px;
  height: 8px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* Action Bar */
.controls-action-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 18px;
  border-top: 1px solid var(--border-subtle);
  gap: 16px;
  flex-wrap: wrap;
}

.action-caption {
  font-size: 13px;
  color: var(--text-muted);
}

.btn-run {
  padding: 12px 28px;
  font-size: 15px;
  letter-spacing: -0.01em;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
}

@media (max-width: 768px) {
  .segmented-control {
    flex-direction: column;
  }
  .controls-action-bar {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-run {
    width: 100%;
  }
}
</style>
