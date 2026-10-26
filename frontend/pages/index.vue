<template>
  <div class="page-wrapper">
    <!-- Navigation Bar -->
    <Navbar @open-settings="isSettingsOpen = true" />

    <!-- Main Content Area -->
    <main class="app-container main-content">
      <!-- Hero Header -->
      <section class="hero-section">
        <div class="hero-badge">
          <span class="badge badge-primary pulse-glow">Multi-Domain Intelligence Engine</span>
          <span class="badge badge-cyan">Pydantic v2 Validated</span>
          <span class="badge badge-emerald">Gemini 2.0 Flash</span>
        </div>
        <h1 class="hero-title">
          Intelligent Document Analysis & <span class="gradient-text">Visual Insights</span>
        </h1>
        <p class="hero-subtitle">
          Extract structured entities, compute weighted completeness metrics, synthesize dynamic multi-style summaries,
          and generate domain-tailored visual insights across Resumes, Research Papers, and Business Reports.
        </p>
      </section>

      <!-- Step 1 & 2: Ingestion & Adaptive Controls Grid -->
      <section class="pipeline-setup-grid">
        <!-- Ingestion Column -->
        <div class="pipeline-column">
          <div class="column-header">
            <span class="step-num font-mono">01</span>
            <h2 class="column-title">Document Ingestion</h2>
          </div>
          <DocumentUploader
            @document-loaded="onDocumentLoaded"
            @doc-type-detected="onDocTypeDetected"
          />
        </div>

        <!-- Controls Column -->
        <div class="pipeline-column">
          <div class="column-header">
            <span class="step-num font-mono">02</span>
            <h2 class="column-title">Adaptive Intelligence Controls</h2>
          </div>
          <AdaptiveControls
            v-model="controlsState"
            :has-document="!!currentDocumentId"
            :is-analyzing="isAnalyzing"
            @run-analysis="executeAnalysis"
          />
        </div>
      </section>

      <!-- Step 3: Analysis Results Section -->
      <section ref="resultsSectionRef" class="results-section">
        <div class="column-header mb-4">
          <span class="step-num font-mono">03</span>
          <div class="results-header-text">
            <h2 class="column-title">Analysis & Synthesis Dashboard</h2>
            <span v-if="analysisResult" class="results-timestamp font-mono">
              Processed: {{ lastAnalyzedTime }} • Document ID: {{ analysisResult.document_id }}
            </span>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isAnalyzing" class="analysis-loading-card glass-panel slide-up">
          <div class="loading-spinner-wrapper">
            <div class="spinner-large animate-spin"></div>
            <div class="loading-glow"></div>
          </div>
          <h3 class="loading-title">Synthesizing Document Intelligence...</h3>
          <p class="loading-subtitle">
            Compiling parameterized prompt for <strong class="text-white">{{ controlsState.document_type }}</strong>,
            enforcing Pydantic schemas, computing C_total completeness score, and generating domain visual insights.
          </p>
          <div class="loading-steps">
            <span class="loading-step active">1. Ingest Text</span>
            <span class="step-arrow">→</span>
            <span class="loading-step active">2. LLM Extraction</span>
            <span class="step-arrow">→</span>
            <span class="loading-step active">3. Pydantic Coercion</span>
            <span class="step-arrow">→</span>
            <span class="loading-step active">4. Completeness Scoring</span>
            <span class="step-arrow">→</span>
            <span class="loading-step active">5. Visual Generation</span>
          </div>
        </div>

        <!-- Results Display Grid -->
        <div v-else-if="analysisResult" class="results-grid slide-up">
          <!-- Row 1: Completeness Gauge + Executive Summary -->
          <div class="results-row-duo">
            <CompletenessGauge
              :score="analysisResult.completeness_score"
              :breakdown="analysisResult.completeness_breakdown"
              :uncertainty-flags="analysisResult.uncertainty_flags"
            />
            <SummaryCard
              :summary="analysisResult.summary"
              :style="analysisResult.summary_style"
            />
          </div>

          <!-- Row 2: AI Visual Insights & Infographics -->
          <VisualInsightsPanel
            :document-type="analysisResult.document_type"
            :charts-data="analysisResult.visual_insights.charts_data"
            :infographic-url="analysisResult.visual_insights.ai_infographic_url"
          />

          <!-- Row 3: Structured Data Extraction (Clean Cards + Raw JSON) -->
          <StructuredDataViewer
            :extraction="analysisResult.extraction"
          />
        </div>

        <!-- Empty State Prompt -->
        <div v-else class="empty-results-card glass-card">
          <div class="empty-icon-bubble">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
          </div>
          <h3 class="empty-title">Awaiting Document Analysis</h3>
          <p class="empty-subtitle">
            Upload your document or click any of the pre-seeded test fixtures above,
            customize your adaptive analysis options, and click <strong>"Run Intelligent Analysis"</strong>.
          </p>
        </div>
      </section>
    </main>

    <!-- Footer -->
    <footer class="app-footer">
      <div class="app-container footer-content">
        <div class="footer-left">
          <span>DocuIntel AI Platform • Production Architecture Blueprint</span>
        </div>
        <div class="footer-right font-mono">
          <span>FastAPI + Nuxt 3 + Gemini 2.0 Flash + Pydantic v2</span>
        </div>
      </div>
    </footer>

    <!-- API Key / Settings Modal -->
    <ApiKeyModal
      :is-open="isSettingsOpen"
      @close="isSettingsOpen = false"
      @key-updated="onKeyUpdated"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const isSettingsOpen = ref(false)
const isAnalyzing = ref(false)
const currentDocumentId = ref<string | null>(null)
const analysisResult = ref<any>(null)
const lastAnalyzedTime = ref('')
const resultsSectionRef = ref<HTMLElement | null>(null)

const controlsState = ref<{
  document_type: 'resume' | 'research_paper' | 'business_analytics_report'
  summary_style: 'brief' | 'detailed' | 'bullet_point'
  analysis_level: 'basic' | 'standard' | 'detailed'
  focus_topics: string[]
}>({
  document_type: 'resume',
  summary_style: 'detailed',
  analysis_level: 'standard',
  focus_topics: ['skills', 'work_experience'],
})

function onDocumentLoaded(doc: any) {
  currentDocumentId.value = doc.document_id
}

function onDocTypeDetected(type: 'resume' | 'research_paper' | 'business_analytics_report') {
  controlsState.value.document_type = type
  if (type === 'resume') {
    controlsState.value.focus_topics = ['skills', 'work_experience']
  } else if (type === 'research_paper') {
    controlsState.value.focus_topics = ['methodology_summary', 'benchmark_results']
  } else {
    controlsState.value.focus_topics = ['executive_kpis', 'segment_breakdown']
  }
}

async function executeAnalysis() {
  if (!currentDocumentId.value) return
  isAnalyzing.value = true

  // Scroll to results section smoothly
  setTimeout(() => {
    resultsSectionRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, 100)

  try {
    const payload = {
      document_id: currentDocumentId.value,
      document_type: controlsState.value.document_type,
      summary_style: controlsState.value.summary_style,
      analysis_level: controlsState.value.analysis_level,
      focus_topics: controlsState.value.focus_topics,
    }

    const res = await fetch('/api/v1/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const err = await res.json()
      alert(err.detail?.message || 'Analysis failed')
      return
    }

    const data = await res.json()
    analysisResult.value = data
    lastAnalyzedTime.value = new Date().toLocaleTimeString()

    // Trigger celebratory confetti if score is high
    if (data.completeness_score >= 80) {
      triggerConfetti()
    }
  } catch (e: any) {
    alert('Error connecting to analysis engine: ' + e.message)
  } finally {
    isAnalyzing.value = false
  }
}

async function triggerConfetti() {
  try {
    const confetti = (await import('canvas-confetti')).default
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#6366f1', '#06b6d4', '#10b981', '#8b5cf6'],
    })
  } catch (e) {
    // Ignore if confetti fails to load
  }
}

function onKeyUpdated(key: string) {
  console.log('Gemini key updated')
}
</script>

<style scoped>
.page-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  padding-top: 36px;
  padding-bottom: 60px;
  display: flex;
  flex-direction: column;
  gap: 40px;
}

/* Hero Section */
.hero-section {
  text-align: center;
  max-width: 860px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.hero-badge {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.hero-title {
  font-size: 42px;
  font-weight: 800;
  line-height: 1.15;
  letter-spacing: -0.03em;
  color: #fff;
}

.hero-subtitle {
  font-size: 16px;
  color: var(--text-muted);
  line-height: 1.6;
}

/* Pipeline Grid */
.pipeline-setup-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}

.pipeline-column {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.column-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.step-num {
  font-size: 13px;
  font-weight: 800;
  color: var(--primary);
  background: rgba(99, 102, 241, 0.12);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  border: 1px solid rgba(99, 102, 241, 0.25);
}

.column-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

/* Results Section */
.results-section {
  display: flex;
  flex-direction: column;
}

.results-header-text {
  display: flex;
  flex-direction: column;
}

.results-timestamp {
  font-size: 12px;
  color: var(--text-dim);
}

/* Loading Card */
.analysis-loading-card {
  padding: 60px 30px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}

.loading-spinner-wrapper {
  position: relative;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner-large {
  width: 56px;
  height: 56px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--primary-light);
  border-radius: 50%;
  position: relative;
  z-index: 2;
}

.loading-glow {
  position: absolute;
  width: 70px;
  height: 70px;
  background: var(--primary-glow);
  filter: blur(20px);
  border-radius: 50%;
}

.loading-title {
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.loading-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  max-width: 600px;
  line-height: 1.6;
}

.loading-steps {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 10px;
}

.loading-step {
  font-size: 12px;
  font-weight: 600;
  padding: 5px 10px;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-dim);
}

.loading-step.active {
  background: rgba(99, 102, 241, 0.15);
  color: var(--primary-light);
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.step-arrow {
  color: var(--text-dim);
  font-size: 12px;
}

/* Results Grid */
.results-grid {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.results-row-duo {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px;
}

/* Empty State Card */
.empty-results-card {
  padding: 60px 30px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.empty-icon-bubble {
  width: 68px;
  height: 68px;
  border-radius: var(--radius-lg);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-dim);
}

.empty-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.empty-subtitle {
  font-size: 14px;
  color: var(--text-muted);
  max-width: 500px;
  line-height: 1.6;
}

/* Footer */
.app-footer {
  border-top: 1px solid var(--border-subtle);
  background: rgba(7, 9, 14, 0.9);
  padding: 18px 0;
  margin-top: auto;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12.5px;
  color: var(--text-dim);
  flex-wrap: wrap;
  gap: 12px;
}

@media (max-width: 1024px) {
  .pipeline-setup-grid {
    grid-template-columns: 1fr;
  }
  .results-row-duo {
    grid-template-columns: 1fr;
  }
  .hero-title {
    font-size: 32px;
  }
}
</style>
