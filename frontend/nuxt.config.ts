// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },

  css: [
    '~/assets/css/main.css'
  ],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'
    }
  },

  nitro: {
    routeRules: {
      '/api/**': {
        proxy: 'http://localhost:8000/api/**'
      }
    }
  },

  build: {
    transpile: ['echarts', 'vue-echarts', 'resize-detector']
  },

  app: {
    head: {
      title: 'DocuIntel AI — Intelligent Document Analytics & Visual Insights',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content: 'Enterprise AI document intelligence platform for polymorphic structured extraction, dynamic summary synthesis, completeness scoring, and visual insights.'
        },
        { name: 'theme-color', content: '#0b0f19' }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap'
        }
      ]
    }
  }
})
