// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2026-07-14',
  css: [
    '~/assets/css/main.css'
  ],
  runtimeConfig: {
    githubToken: process.env.GITHUB_PAT || '',
    public: {
      supabaseUrl: process.env.NUXT_PUBLIC_SUPABASE_URL || '',
      supabaseAnonKey: process.env.NUXT_PUBLIC_SUPABASE_ANON_KEY || ''
    }
  },
  app: {
    baseURL: '/biscuit_scraper/',
    head: {
      title: 'Biscuit Scraper Dashboard',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ]
    }
  },
  devtools: { enabled: false }
})
