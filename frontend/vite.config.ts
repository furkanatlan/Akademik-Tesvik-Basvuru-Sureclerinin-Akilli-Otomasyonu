import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// /api istekleri backend container'ına yönlendirilir (CORS gerekmez)
export default defineConfig({
  plugins: [react()],
  server: {
    watch: { usePolling: true },
    proxy: {
      "/api": { target: process.env.BACKEND_URL ?? "http://localhost:8000", changeOrigin: true },
    },
  },
});
