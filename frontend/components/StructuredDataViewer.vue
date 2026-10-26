<template>
  <div class="viewer-card glass-card">
    <div class="card-header">
      <div class="header-left">
        <div class="header-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="16 18 22 12 16 6"></polyline>
            <polyline points="8 6 2 12 8 18"></polyline>
          </svg>
        </div>
        <div>
          <h3 class="card-title">Structured Entity Extraction</h3>
          <span class="card-meta">
            Domain: <strong class="text-white">{{ extraction?.document_type || 'Unknown' }}</strong> • 
            Pydantic v2 Validated
          </span>
        </div>
      </div>

      <!-- View Tabs & Actions -->
      <div class="header-actions">
        <div class="view-toggle">
          <button
            class="toggle-btn"
            :class="{ active: activeTab === 'visual' }"
            @click="activeTab = 'visual'"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="14" y="14" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
            </svg>
            <span>Clean Cards</span>
          </button>
          <button
            class="toggle-btn"
            :class="{ active: activeTab === 'json' }"
            @click="activeTab = 'json'"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="4 7 4 4 20 4 20 7"></polyline>
              <line x1="9" y1="20" x2="15" y2="20"></line>
              <line x1="12" y1="4" x2="12" y2="20"></line>
            </svg>
            <span>Raw JSON</span>
          </button>
        </div>

        <button class="btn btn-secondary btn-sm" @click="downloadJSON">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          <span>Export</span>
        </button>
      </div>
    </div>

    <!-- TAB 1: VISUAL STRUCTURED VIEW -->
    <div v-if="activeTab === 'visual'" class="visual-view slide-up">
      <!-- 1. RESUME DOMAIN -->
      <div v-if="isResume" class="domain-container">
        <!-- Identity & Contact Card -->
        <div class="entity-section">
          <h4 class="section-title">Identity & Contactability</h4>
          <div class="entity-grid">
            <div class="field-item">
              <span class="field-label">Candidate Name</span>
              <span class="field-value" :class="{ 'is-null': !extraction.candidate_name }">
                {{ extraction.candidate_name || 'Missing / Not Found' }}
              </span>
            </div>
            <div class="field-item">
              <span class="field-label">Email Address</span>
              <span class="field-value font-mono" :class="{ 'is-null': !extraction.email_address }">
                {{ extraction.email_address || 'Missing / Not Found' }}
              </span>
            </div>
            <div class="field-item">
              <span class="field-label">Phone Number</span>
              <span class="field-value font-mono" :class="{ 'is-null': !extraction.phone_number }">
                {{ extraction.phone_number || 'Missing / Not Found' }}
              </span>
            </div>
            <div class="field-item">
              <span class="field-label">Location</span>
              <span class="field-value" :class="{ 'is-null': !extraction.location }">
                {{ extraction.location || 'Missing / Not Found' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Categorized Skills -->
        <div class="entity-section">
          <h4 class="section-title">Competency & Skill Matrix</h4>
          <div v-if="extraction.categorized_skills && extraction.categorized_skills.length > 0" class="skill-categories">
            <div v-for="(cat, idx) in extraction.categorized_skills" :key="idx" class="skill-cat-card">
              <div class="skill-cat-name">{{ cat.category || 'Domain' }}</div>
              <div class="skill-tags">
                <span v-for="skill in cat.skills" :key="skill" class="badge badge-primary">{{ skill }}</span>
              </div>
            </div>
          </div>
          <div v-else-if="extraction.skills && extraction.skills.length > 0" class="skill-tags">
            <span v-for="skill in extraction.skills" :key="skill" class="badge badge-primary">{{ skill }}</span>
          </div>
          <div v-else class="empty-field-notice">No technical skills detected in document.</div>
        </div>

        <!-- Work Experience Timeline -->
        <div class="entity-section">
          <h4 class="section-title">Work Experience</h4>
          <div v-if="extraction.work_experience && extraction.work_experience.length > 0" class="experience-list">
            <div v-for="(exp, idx) in extraction.work_experience" :key="idx" class="experience-card">
              <div class="exp-header">
                <div>
                  <div class="exp-role">{{ exp.job_title || 'Role' }}</div>
                  <div class="exp-company">{{ exp.company }} • {{ exp.location }}</div>
                </div>
                <span class="badge badge-cyan font-mono">{{ exp.start_date }} – {{ exp.end_date }}</span>
              </div>
              <p v-if="exp.description" class="exp-desc">{{ exp.description }}</p>
              <ul v-if="exp.achievements && exp.achievements.length > 0" class="exp-achievements">
                <li v-for="(ach, aidx) in exp.achievements" :key="aidx">{{ ach }}</li>
              </ul>
            </div>
          </div>
          <div v-else class="empty-field-notice">
            ⚠️ No commercial work experience entries found. Profile flagged as early-career or incomplete.
          </div>
        </div>

        <!-- Education -->
        <div class="entity-section">
          <h4 class="section-title">Academic Qualifications</h4>
          <div v-if="extraction.educational_qualifications && extraction.educational_qualifications.length > 0" class="education-grid">
            <div v-for="(edu, idx) in extraction.educational_qualifications" :key="idx" class="edu-card">
              <div class="edu-degree">{{ edu.degree || 'Degree' }}</div>
              <div class="edu-inst">{{ edu.institution }}</div>
              <div class="edu-meta font-mono">{{ edu.start_year }} – {{ edu.end_year }} <span v-if="edu.gpa">• GPA: {{ edu.gpa }}</span></div>
            </div>
          </div>
          <div v-else class="empty-field-notice">No educational credentials detected.</div>
        </div>
      </div>

      <!-- 2. RESEARCH PAPER DOMAIN -->
      <div v-else-if="isResearchPaper" class="domain-container">
        <div class="entity-section">
          <h4 class="section-title">Paper Metadata & Objective</h4>
          <div class="field-item mb-3">
            <span class="field-label">Paper Title</span>
            <span class="field-value font-bold">{{ extraction.paper_title || 'Untitled' }}</span>
          </div>
          <div class="entity-grid">
            <div class="field-item">
              <span class="field-label">Authors</span>
              <span class="field-value">{{ (extraction.authors || []).join(', ') || 'N/A' }}</span>
            </div>
            <div class="field-item">
              <span class="field-label">Venue & Year</span>
              <span class="field-value">{{ extraction.publication_venue }} ({{ extraction.publication_year }})</span>
            </div>
          </div>
        </div>

        <div class="entity-section">
          <h4 class="section-title">Methodology & Datasets</h4>
          <p class="methodology-text">{{ extraction.methodology_summary || 'N/A' }}</p>
          <div class="datasets-box mt-3">
            <span class="field-label">Evaluated Datasets:</span>
            <div class="skill-tags mt-1">
              <span v-for="ds in extraction.datasets_used" :key="ds" class="badge badge-cyan">{{ ds }}</span>
            </div>
          </div>
        </div>

        <div class="entity-section">
          <h4 class="section-title">Benchmark Results Table</h4>
          <div v-if="extraction.benchmark_results && extraction.benchmark_results.length > 0" class="table-wrapper">
            <table class="data-table">
              <thead>
                <tr>
                  <th>Metric</th>
                  <th>Dataset</th>
                  <th>Proposed</th>
                  <th>Baseline</th>
                  <th>Unit</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(bm, idx) in extraction.benchmark_results" :key="idx">
                  <td class="font-bold">{{ bm.metric_name }}</td>
                  <td>{{ bm.dataset }}</td>
                  <td class="text-emerald font-mono font-bold">{{ bm.proposed_value }}</td>
                  <td class="text-muted font-mono">{{ bm.baseline_value }}</td>
                  <td class="text-dim font-mono">{{ bm.unit }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- 3. BUSINESS REPORT DOMAIN -->
      <div v-else class="domain-container">
        <div class="entity-section">
          <h4 class="section-title">Executive KPIs</h4>
          <div v-if="extraction.executive_kpis && extraction.executive_kpis.length > 0" class="kpi-grid">
            <div v-for="(kpi, idx) in extraction.executive_kpis" :key="idx" class="kpi-card">
              <div class="kpi-top">
                <span class="kpi-name">{{ kpi.kpi_name }}</span>
                <span class="badge" :class="kpi.change_percentage?.includes('+') ? 'badge-emerald' : 'badge-amber'">
                  {{ kpi.change_percentage }}
                </span>
              </div>
              <div class="kpi-val font-mono">{{ kpi.actual_value }} <span class="kpi-unit">{{ kpi.unit }}</span></div>
              <div class="kpi-sub">Target/Prior: {{ kpi.target_or_prior_value }} {{ kpi.unit }} • {{ kpi.status }}</div>
            </div>
          </div>
        </div>

        <div class="entity-section">
          <h4 class="section-title">Strategic Recommendations & Risks</h4>
          <div class="two-col-grid">
            <div class="recs-box">
              <div class="sub-heading text-emerald">Strategic Actions</div>
              <ul>
                <li v-for="(rec, idx) in extraction.strategic_recommendations" :key="idx">{{ rec }}</li>
              </ul>
            </div>
            <div class="risks-box">
              <div class="sub-heading text-rose">Risk Factors & Anomalies</div>
              <ul>
                <li v-for="(risk, idx) in extraction.risk_factors_and_anomalies" :key="idx">{{ risk }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: RAW JSON CODE VIEW -->
    <div v-else class="json-view slide-up">
      <div class="json-toolbar">
        <input
          v-model="jsonSearch"
          type="text"
          placeholder="Filter JSON fields..."
          class="json-search-input font-mono"
        />
        <button class="btn btn-secondary btn-sm" @click="copyRawJSON">
          <span>{{ copied ? 'Copied!' : 'Copy JSON' }}</span>
        </button>
      </div>
      <pre class="json-pre font-mono"><code>{{ formattedJSON }}</code></pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  extraction: Record<string, any>
}>()

const activeTab = ref<'visual' | 'json'>('visual')
const jsonSearch = ref('')
const copied = ref(false)

const isResume = computed(() => props.extraction?.document_type === 'resume')
const isResearchPaper = computed(() => props.extraction?.document_type === 'research_paper')

const formattedJSON = computed(() => {
  if (!props.extraction) return '{}'
  return JSON.stringify(props.extraction, null, 2)
})

function downloadJSON() {
  const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(formattedJSON.value)
  const downloadAnchor = document.createElement('a')
  downloadAnchor.setAttribute('href', dataStr)
  downloadAnchor.setAttribute('download', `${props.extraction?.document_type || 'extraction'}_result.json`)
  document.body.appendChild(downloadAnchor)
  downloadAnchor.click()
  downloadAnchor.remove()
}

async function copyRawJSON() {
  await navigator.clipboard.writeText(formattedJSON.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}
</script>

<style scoped>
.viewer-card {
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
  background: rgba(6, 182, 212, 0.15);
  color: var(--secondary);
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.view-toggle {
  display: flex;
  background: var(--surface-input);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  padding: 3px;
  gap: 3px;
}

.toggle-btn {
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

.toggle-btn.active {
  background: var(--surface-elevated);
  color: #fff;
}

/* Sections */
.domain-container {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.entity-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.entity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.field-item {
  display: flex;
  flex-direction: column;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.field-label {
  font-size: 11px;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}

.field-value {
  font-size: 14px;
  color: #fff;
  font-weight: 500;
}

.field-value.is-null {
  color: var(--accent-amber);
  font-style: italic;
  font-weight: 400;
}

/* Skills */
.skill-categories {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.skill-cat-card {
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.skill-cat-name {
  font-size: 12px;
  font-weight: 700;
  color: var(--secondary);
  margin-bottom: 8px;
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

/* Experience */
.experience-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.experience-card {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.exp-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.exp-role {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.exp-company {
  font-size: 13px;
  color: var(--text-muted);
}

.exp-desc {
  font-size: 13.5px;
  color: #cbd5e1;
  margin-bottom: 8px;
}

.exp-achievements {
  padding-left: 18px;
  font-size: 13px;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* Education */
.education-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}

.edu-card {
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.edu-degree {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.edu-inst {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 2px;
}

.edu-meta {
  font-size: 12px;
  color: var(--text-dim);
  margin-top: 4px;
}

/* Tables */
.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.data-table th, .data-table td {
  padding: 10px 14px;
  text-align: left;
  border-bottom: 1px solid var(--border-subtle);
}

.data-table th {
  color: var(--text-dim);
  font-size: 11px;
  text-transform: uppercase;
}

/* KPIs */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.kpi-card {
  padding: 14px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.kpi-name {
  font-size: 12px;
  color: var(--text-muted);
}

.kpi-val {
  font-size: 22px;
  font-weight: 800;
  color: #fff;
}

.kpi-unit {
  font-size: 13px;
  color: var(--text-muted);
}

.kpi-sub {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 4px;
}

.two-col-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.recs-box, .risks-box {
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}

.recs-box ul, .risks-box ul {
  padding-left: 18px;
  font-size: 13px;
  color: #cbd5e1;
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
}

.sub-heading {
  font-size: 13px;
  font-weight: 700;
}

.empty-field-notice {
  padding: 12px;
  background: rgba(245, 158, 11, 0.05);
  border: 1px dashed rgba(245, 158, 11, 0.3);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--accent-amber);
}

/* Raw JSON View */
.json-view {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.json-toolbar {
  display: flex;
  gap: 10px;
}

.json-search-input {
  flex: 1;
  padding: 8px 12px;
  background: var(--surface-input);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  color: #fff;
  font-size: 13px;
}

.json-pre {
  background: #090d16;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 16px;
  color: #38bdf8;
  font-size: 12.5px;
  overflow-x: auto;
  max-height: 520px;
}
</style>
