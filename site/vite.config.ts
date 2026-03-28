import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  base: process.env.BASE_URL || '/participation-electorale/',
  plugins: [vue()],
  server: {
    port: 3000,
    host: true,
    hmr: true,
  },
})
