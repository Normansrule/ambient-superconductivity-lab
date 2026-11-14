import { defineConfig, devices } from "@playwright/test";

const base = "http://localhost:4173/ambient-superconductivity-lab/";

export default defineConfig({
  testDir: "tests",
  outputDir: "test-results",
  timeout: 60_000,
  reporter: [["list"], ["html", { open: "never" }]],
  use: { baseURL: base, viewport: { width: 1280, height: 800 } },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        launchOptions: {
          // Optional override for machines with a preinstalled browser.
          executablePath: process.env.PW_CHROMIUM_PATH || undefined,
          // Software WebGL so headless CI machines without a GPU still render.
          args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"],
        },
      },
    },
  ],
  webServer: {
    command: "npm run preview",
    url: base,
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
