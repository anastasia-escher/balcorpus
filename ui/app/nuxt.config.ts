// https://nuxt.com/docs/api/configuration/nuxt-config

export default defineNuxtConfig({
  ssr: false,
  nitro: {
    static: true,
    devProxy: {
      '/api/v1': 'http://api:5000/api/v1',
      '/swagger': 'http://api:5000/api/v1/swagger',
      '/admin': 'http://api:5000/admin',
      '/media': 'http://api:5000/media',
      '/static': 'http://api:5000/static',
    },
  },
  runtimeConfig: {
    public: {
      baseURL: process.env.NUXT_PUBLIC_API_BASE_URL || 'https://balgram.iling.spb.ru',
    },
  },
  compatibilityDate: '2024-11-01',
  devtools: {enabled: true},
  colorMode: {
    preference: 'light',
    fallback: 'light',
    storageKey: 'balcorpus-color-mode',
  },
  modules: [
    '@pinia/nuxt',
    [
      'pinia-plugin-persistedstate/nuxt',
      {
        storage: 'localStorage', // ← switch from cookies to Web‑storage
        debug: true, // optional: console traces for hydrate/save
      },
    ],
    '@nuxt/ui',
    '@nuxtjs/i18n',
    '@nuxtjs/leaflet',
  ],

  i18n: {
    vueI18n: './i18n.config.ts',
    defaultLocale: 'en',
    locales: [
      {
        code: 'en',
        name: 'English',
        file: 'en.json',
      },
    ],
    langDir: 'locales',
    strategy: 'no_prefix',
    skipSettingLocaleOnNavigate: true,
  },
  css: ['~/assets/css/styles.css'],
})
