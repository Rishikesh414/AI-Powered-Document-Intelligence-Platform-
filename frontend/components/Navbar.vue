<template>
  <header class="navbar-wrapper">
    <div class="app-container navbar-content">
      <!-- Brand Logo -->
      <div class="brand-section">
        <div class="brand-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10 9 9 9 8 9"></polyline>
          </svg>
        </div>
        <div class="brand-text">
          <span class="brand-name">DocuIntel <span class="gradient-text">AI</span></span>
          <span class="brand-tagline">Polymorphic Document Analytics</span>
        </div>
        <span class="badge badge-primary version-badge">v1.0 Pro</span>
      </div>

      <!-- Action Items & Server Status -->
      <div class="nav-actions">
        <!-- Live System Status -->
        <div class="status-pill" :class="{ 'is-healthy': isHealthy, 'is-warning': !isHealthy }">
          <span class="status-dot"></span>
          <span class="status-label">{{ isHealthy ? 'API Online' : 'Connecting...' }}</span>
          <span v-if="llmMode" class="status-mode">({{ llmMode }})</span>
        </div>

        <!-- Settings / API Key Button -->
        <button class="btn btn-secondary btn-sm" @click="$emit('open-settings')">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          <span>LLM Config</span>
        </button>

        <!-- API Docs link -->
        <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm">
          <span>API Docs</span>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
        </a>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

defineEmits(['open-settings'])

const isHealthy = ref(false)
const llmMode = ref('')

async function checkHealth() {
  try {
    const res = await fetch('/api/v1/health')
    if (res.ok) {
      const data = await res.json()
      isHealthy.value = data.status === 'healthy'
      llmMode.value = data.gemini_configured ? 'Gemini 2.0' : 'Mock Mode'
    } else {
      isHealthy.value = false
    }
  } catch (e) {
    isHealthy.value = false
  }
}

onMounted(() => {
  checkHealth()
  // Refresh health every 15 seconds
  setInterval(checkHealth, 15000)
})
</script>

<style scoped>
.navbar-wrapper {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(7, 9, 14, 0.85);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border-subtle);
  padding: 14px 0;
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  background: var(--gradient-brand);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: 0 4px 16px var(--primary-glow);
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 18px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.brand-tagline {
  font-size: 11px;
  color: var(--text-dim);
  font-weight: 500;
}

.version-badge {
  font-size: 11px;
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 12px;
  background: var(--surface-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 500;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--accent-rose);
}

.status-pill.is-healthy .status-dot {
  background: var(--accent-emerald);
  box-shadow: 0 0 8px var(--accent-emerald);
}

.status-label {
  color: var(--text-muted);
}

.status-mode {
  color: var(--primary-light);
  font-weight: 600;
  font-size: 11px;
}

.btn-sm {
  padding: 7px 14px;
  font-size: 13px;
}

@media (max-width: 640px) {
  .brand-tagline, .version-badge {
    display: none;
  }
}
</style>
