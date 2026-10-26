<template>
  <div v-if="isOpen" class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-card glass-panel slide-up">
      <div class="modal-header">
        <div class="header-title">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          <span>LLM Provider & API Configuration</span>
        </div>
        <button class="modal-close" @click="$emit('close')">×</button>
      </div>

      <div class="modal-body">
        <p class="modal-desc">
          DocuIntel AI runs on <strong>Google Gemini 2.0 Flash</strong> for high-throughput, structured extraction and reasoning. A free-tier API key can be obtained from Google AI Studio.
        </p>

        <div class="form-group">
          <label class="form-label">Gemini API Key</label>
          <div class="input-with-button">
            <input
              v-model="apiKeyInput"
              :type="showKey ? 'text' : 'password'"
              placeholder="AIzaSy..."
              class="text-input font-mono"
            />
            <button class="toggle-vis-btn" type="button" @click="showKey = !showKey">
              {{ showKey ? 'Hide' : 'Show' }}
            </button>
          </div>
          <span class="input-hint">
            Get a free API key at <a href="https://aistudio.google.com/" target="_blank" rel="noopener">Google AI Studio</a>. (15 RPM / 1,500 RPD free tier).
          </span>
        </div>

        <div class="callout-box">
          <div class="callout-title">Deterministic Mock Mode Available</div>
          <p class="callout-text">
            If an API key is not supplied, the platform automatically switches to deterministic mock mode so you can evaluate all polymorphic extraction schemas, completeness scoring, and visual insights without an account.
          </p>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-outline" @click="$emit('close')">Cancel</button>
        <button class="btn btn-primary" :disabled="isSaving" @click="saveKey">
          <span>{{ isSaving ? 'Saving...' : 'Save Configuration' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits(['close', 'key-updated'])

const apiKeyInput = ref('')
const showKey = ref(false)
const isSaving = ref(false)

async function saveKey() {
  isSaving.value = true
  try {
    // Save to localStorage
    if (apiKeyInput.value) {
      localStorage.setItem('docuintel_gemini_key', apiKeyInput.value)
    } else {
      localStorage.removeItem('docuintel_gemini_key')
    }
    emit('key-updated', apiKeyInput.value)
    emit('close')
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  width: 100%;
  max-width: 520px;
  padding: 24px;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-subtle);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 700;
  color: #fff;
}

.modal-close {
  background: transparent;
  border: none;
  color: var(--text-dim);
  font-size: 22px;
  cursor: pointer;
  line-height: 1;
}

.modal-close:hover {
  color: #fff;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.modal-desc {
  font-size: 13.5px;
  color: var(--text-muted);
  line-height: 1.6;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.input-with-button {
  display: flex;
  gap: 8px;
}

.toggle-vis-btn {
  padding: 0 14px;
  background: var(--surface-card);
  border: 1px solid var(--border-medium);
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
}

.toggle-vis-btn:hover {
  color: #fff;
}

.input-hint {
  font-size: 11.5px;
  color: var(--text-dim);
}

.input-hint a {
  color: var(--secondary);
  text-decoration: underline;
}

.callout-box {
  padding: 14px 16px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: var(--radius-md);
}

.callout-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--primary-light);
  margin-bottom: 4px;
}

.callout-text {
  font-size: 12.5px;
  color: #cbd5e1;
  line-height: 1.5;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-subtle);
}
</style>
