import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import fs from 'fs'
import path from 'path'

const certPath = path.resolve(__dirname, '../certs/cert.pem')
const keyPath = path.resolve(__dirname, '../certs/key.pem')
const hasSSL = fs.existsSync(certPath) && fs.existsSync(keyPath)

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5175,
    host: true,
    ...(hasSSL ? {
      https: {
        cert: fs.readFileSync(certPath),
        key: fs.readFileSync(keyPath),
      }
    } : {}),
  },
})
