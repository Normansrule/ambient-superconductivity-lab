import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Served from https://normansrule.github.io/ambient-superconductivity-lab/
export default defineConfig({
  base: "/ambient-superconductivity-lab/",
  plugins: [react()],
  build: { chunkSizeWarningLimit: 1500 },
});
