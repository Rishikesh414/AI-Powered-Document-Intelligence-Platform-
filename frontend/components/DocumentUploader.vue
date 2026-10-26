<template>
  <div class="uploader-container">
    <!-- Drop Zone -->
    <div
      class="dropzone glass-card"
      :class="{ 'is-dragging': isDragging, 'is-loading': isUploading }"
      @dragover.prevent="onDragOver"
      @dragleave.prevent="onDragLeave"
      @drop.prevent="onDrop"
      @click="triggerFileInput"
    >
      <input
        ref="fileInputRef"
        type="file"
        accept=".pdf,.txt,.text,.md,.docx"
        class="hidden-input"
        @change="onFileSelected"
      />

      <div class="dropzone-content">
        <div class="icon-bubble">
          <svg v-if="!isUploading" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <div v-else class="spinner animate-spin"></div>
        </div>

        <div class="dropzone-text">
          <h3 class="dropzone-title">
            <span v-if="!isUploading">Drag & Drop Document Here or <span class="highlight">Browse</span></span>
            <span v-else>Extracting Document Content...</span>
          </h3>
          <p class="dropzone-sub">Supports PDF, TXT, MD, and DOCX files (up to 10MB)</p>
        </div>

        <div class="format-pills">
          <span class="badge badge-primary">PDF (Structured & Scanned)</span>
          <span class="badge badge-cyan">Plain Text / Markdown</span>
          <span class="badge badge-emerald">DOCX</span>
        </div>
      </div>
    </div>

    <!-- Active Document Banner (if loaded) -->
    <div v-if="currentDoc" class="active-doc-banner glass-card slide-up">
      <div class="active-doc-info">
        <div class="doc-file-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
        </div>
        <div>
          <div class="doc-name">{{ currentDoc.filename }}</div>
          <div class="doc-meta">
            ID: <span class="font-mono">{{ currentDoc.document_id }}</span> • 
            Extracted: <strong>{{ currentDoc.extracted_text_length.toLocaleString() }} chars</strong> • 
            Size: {{ formatBytes(currentDoc.size_bytes) }}
          </div>
        </div>
      </div>
      <div class="active-doc-badge">
        <span class="badge badge-emerald">Ready for Analysis</span>
      </div>
    </div>

    <!-- Error Alert Banner -->
    <div v-if="errorMessage" class="error-banner glass-card slide-up">
      <div class="error-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <div class="error-content">
        <div class="error-title">{{ errorCode || 'Upload Error' }}</div>
        <div class="error-message">{{ errorMessage }}</div>
        <div v-if="errorRemediation" class="error-remediation">
          <strong>Suggested Action:</strong> {{ errorRemediation }}
        </div>
      </div>
      <button class="error-close-btn" @click="clearError">×</button>
    </div>

    <!-- Pre-Seeded Sample Documents Section -->
    <div class="samples-section">
      <div class="samples-header">
        <div class="samples-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
            <polyline points="2 17 12 22 22 17"></polyline>
            <polyline points="2 12 12 17 22 12"></polyline>
          </svg>
          <span>Pre-Seeded Test Fixtures</span>
        </div>
        <span class="samples-caption">Instant one-click loading across all 3 document domains & edge cases</span>
      </div>

      <div class="samples-grid">
        <button
          v-for="sample in sampleList"
          :key="sample.document_id"
          class="sample-card glass-card"
          :class="{
            'is-active': currentDoc?.document_id === sample.document_id,
            'is-edge': sample.document_id.includes('empty'),
            'is-missing': sample.document_id.includes('missing')
          }"
          :disabled="isUploading"
          @click="loadSample(sample)"
        >
          <div class="sample-top">
            <span
              class="badge"
              :class="{
                'badge-primary': sample.document_type === 'resume' && !sample.document_id.includes('missing'),
                'badge-amber': sample.document_id.includes('missing'),
                'badge-cyan': sample.document_type === 'research_paper',
                'badge-emerald': sample.document_type === 'business_analytics_report',
                'badge-rose': sample.document_id.includes('empty')
              }"
            >
              {{ getBadgeLabel(sample) }}
            </span>
            <span class="sample-format font-mono">{{ getFileExt(sample.filename) }}</span>
          </div>

          <div class="sample-name">{{ sample.title || sample.filename }}</div>
          <div class="sample-desc">{{ sample.description }}</div>

          <div class="sample-footer">
            <span class="click-to-load">Click to load →</span>
          </div>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits(['document-loaded', 'doc-type-detected'])

interface UploadResponse {
  document_id: string
  filename: string
  size_bytes: number
  extracted_text_length: number
  message: string
}

interface SampleDoc {
  document_id: string
  filename: string
  title?: string
  document_type?: string
  description?: string
  size_bytes?: number
}

const fileInputRef = ref<HTMLInputElement | null>(null)
const isDragging = ref(false)
const isUploading = ref(false)
const currentDoc = ref<UploadResponse | null>(null)
const sampleList = ref<SampleDoc[]>([])

const errorCode = ref('')
const errorMessage = ref('')
const errorRemediation = ref('')

function clearError() {
  errorCode.value = ''
  errorMessage.value = ''
  errorRemediation.value = ''
}

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onDragOver() {
  isDragging.value = true
}

function onDragLeave() {
  isDragging.value = false
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
    uploadFile(e.dataTransfer.files[0])
  }
}

function onFileSelected(e: Event) {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    uploadFile(target.files[0])
  }
}

async function uploadFile(file: File) {
  clearError()
  isUploading.value = true

  const formData = new FormData()
  formData.append('file', file)

  try {
    const res = await fetch('/api/v1/documents/upload', {
      method: 'POST',
      body: formData,
    })

    if (!res.ok) {
      const err = await res.json()
      const detail = err.detail || {}
      errorCode.value = detail.error_code || 'UPLOAD_FAILED'
      errorMessage.value = detail.message || 'Failed to process document.'
      errorRemediation.value = detail.remediation || 'Please verify the file format and content.'
      return
    }

    const data: UploadResponse = await res.json()
    currentDoc.value = data
    emit('document-loaded', data)

    // Auto-detect probable type from filename
    const fn = file.name.toLowerCase()
    if (fn.includes('research') || fn.includes('paper') || fn.includes('arxiv')) {
      emit('doc-type-detected', 'research_paper')
    } else if (fn.includes('report') || fn.includes('analytics') || fn.includes('financial') || fn.includes('business')) {
      emit('doc-type-detected', 'business_analytics_report')
    } else {
      emit('doc-type-detected', 'resume')
    }
  } catch (e: any) {
    errorCode.value = 'NETWORK_ERROR'
    errorMessage.value = e.message || 'Unable to reach document server.'
    errorRemediation.value = 'Ensure the backend server is running on http://localhost:8000'
  } finally {
    isUploading.value = false
  }
}

async function loadSample(sample: SampleDoc) {
  clearError()
  isUploading.value = true

  try {
    const res = await fetch(`/api/v1/documents/samples/${sample.document_id}/load`)

    if (!res.ok) {
      const err = await res.json()
      const detail = err.detail || {}
      errorCode.value = detail.error_code || 'SAMPLE_ERROR'
      errorMessage.value = detail.message || 'Failed to load sample document.'
      errorRemediation.value = detail.remediation || 'Select another test fixture or upload a custom file.'
      return
    }

    const data: UploadResponse = await res.json()
    currentDoc.value = data
    emit('document-loaded', data)

    if (sample.document_type) {
      emit('doc-type-detected', sample.document_type)
    }
  } catch (e: any) {
    errorCode.value = 'LOAD_ERROR'
    errorMessage.value = e.message || 'Network error loading sample.'
  } finally {
    isUploading.value = false
  }
}

async function fetchSamples() {
  try {
    const res = await fetch('/api/v1/documents/samples')
    if (res.ok) {
      sampleList.value = await res.json()
    }
  } catch (e) {
    console.warn('Could not fetch sample list:', e)
  }
}

function getBadgeLabel(sample: SampleDoc): string {
  if (sample.document_id.includes('empty')) return 'Edge Case / Empty'
  if (sample.document_id.includes('missing')) return 'Missing Fields Test'
  if (sample.document_type === 'resume') return 'Resume / CV'
  if (sample.document_type === 'research_paper') return 'Research Paper'
  if (sample.document_type === 'business_analytics_report') return 'Business Report'
  return 'Document'
}

function getFileExt(filename: string): string {
  const parts = filename.split('.')
  return parts.length > 1 ? parts.pop()?.toUpperCase() || 'TXT' : 'TXT'
}

function formatBytes(bytes: number): string {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

onMounted(() => {
  fetchSamples()
})
</script>

<style scoped>
.uploader-container {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.dropzone {
  border: 2px dashed rgba(255, 255, 255, 0.15);
  border-radius: var(--radius-xl);
  padding: 36px 24px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
  background: var(--surface-card);
}

.dropzone:hover {
  border-color: var(--primary);
  background: rgba(22, 32, 54, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.dropzone.is-dragging {
  border-color: var(--secondary);
  background: rgba(6, 182, 212, 0.08);
  box-shadow: 0 0 24px var(--secondary-glow);
}

.dropzone.is-loading {
  pointer-events: none;
  opacity: 0.8;
}

.hidden-input {
  display: none;
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.icon-bubble {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  background: var(--surface-elevated);
  border: 1px solid var(--border-medium);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-light);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: var(--primary-light);
  border-radius: 50%;
}

.dropzone-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-main);
}

.highlight {
  color: var(--secondary);
  text-decoration: underline;
  text-underline-offset: 4px;
}

.dropzone-sub {
  font-size: 13px;
  color: var(--text-muted);
  margin-top: 4px;
}

.format-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
  margin-top: 4px;
}

/* Active Doc Banner */
.active-doc-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(16, 185, 129, 0.06);
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.active-doc-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.doc-file-icon {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-md);
  background: rgba(16, 185, 129, 0.15);
  color: var(--accent-emerald);
  display: flex;
  align-items: center;
  justify-content: center;
}

.doc-name {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}

.doc-meta {
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 2px;
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 16px 20px;
  background: rgba(244, 63, 94, 0.08);
  border: 1px solid rgba(244, 63, 94, 0.3);
  position: relative;
}

.error-icon {
  color: var(--accent-rose);
  margin-top: 2px;
}

.error-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--accent-rose);
}

.error-message {
  font-size: 13px;
  color: #fecdd3;
  margin-top: 3px;
}

.error-remediation {
  font-size: 12px;
  color: #ffe4e6;
  margin-top: 6px;
  background: rgba(0, 0, 0, 0.25);
  padding: 6px 10px;
  border-radius: var(--radius-sm);
}

.error-close-btn {
  position: absolute;
  top: 10px;
  right: 14px;
  background: transparent;
  border: none;
  color: var(--text-dim);
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}

.error-close-btn:hover {
  color: #fff;
}

/* Samples Section */
.samples-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 6px;
}

.samples-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.samples-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text-main);
}

.samples-caption {
  font-size: 12px;
  color: var(--text-dim);
}

.samples-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.sample-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  padding: 14px 16px;
  cursor: pointer;
  background: var(--surface-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  color: inherit;
}

.sample-card:hover:not(:disabled) {
  border-color: var(--primary);
  background: var(--surface-card-hover);
  transform: translateY(-2px);
}

.sample-card.is-active {
  border-color: var(--accent-emerald);
  background: rgba(16, 185, 129, 0.08);
  box-shadow: 0 0 16px rgba(16, 185, 129, 0.2);
}

.sample-card.is-edge:hover {
  border-color: var(--accent-rose);
}

.sample-card.is-missing:hover {
  border-color: var(--accent-amber);
}

.sample-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  margin-bottom: 8px;
}

.sample-format {
  font-size: 10px;
  padding: 2px 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
}

.sample-name {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
  line-height: 1.3;
}

.sample-desc {
  font-size: 11px;
  color: var(--text-dim);
  margin-top: 4px;
  line-height: 1.4;
  flex-grow: 1;
}

.sample-footer {
  margin-top: 10px;
  font-size: 11px;
  color: var(--primary-light);
  font-weight: 600;
}
</style>
