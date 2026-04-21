import path from 'node:path'
import { defineConfig } from 'vitest/config'

/** Separate from Vite config so tests do not load Tailwind native bindings. */
export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    globals: true,
    environment: 'node',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
  },
})
