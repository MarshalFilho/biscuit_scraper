import path from 'path'
import dotenv from 'dotenv'

dotenv.config({ path: path.resolve(process.cwd(), '../.env') })
dotenv.config()

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: true,
  compatibilityDate: '2026-07-14',
  css: [
    '~/assets/css/main.css'
  ],
  runtimeConfig: {
    githubToken: process.env.GITHUB_PAT || '',
    geminiApiKey: process.env.GEMINI_API_KEY || '',
    public: {
      supabaseUrl: process.env.NUXT_PUBLIC_SUPABASE_URL || '',
      supabaseAnonKey: process.env.NUXT_PUBLIC_SUPABASE_ANON_KEY || ''
    }
  },
  app: {
    baseURL: '/',
    head: {
      title: 'Biscuit Scraper Dashboard',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ]
    }
  },
  devtools: { enabled: false },
  experimental: {
    appManifest: false
  },
  modules: [
    '@nuxtjs/i18n'
  ],
  i18n: {
    vueI18n: './i18n.config.ts',
    locales: [
      { code: 'pt', name: 'Português' },
      { code: 'en', name: 'English' }
    ],
    defaultLocale: 'pt',
    strategy: 'no_prefix'
  }
})
