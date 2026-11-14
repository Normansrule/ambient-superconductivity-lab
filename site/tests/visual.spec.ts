import { expect, test } from "@playwright/test";

/**
 * Visual proof for Stage 0: the hero WebGL canvas renders a non-blank image,
 * the page shows its sections, and a full-page screenshot is saved as a CI
 * artifact (test-results/).
 */

test("hero canvas renders a non-blank WebGL image", async ({ page }, info) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));

  await page.goto("./");
  const canvas = page.locator("canvas").first();
  await expect(canvas).toBeVisible();
  await page.waitForTimeout(1500); // let a few frames draw

  const stats = await canvas.evaluate((el) => {
    const src = el as HTMLCanvasElement;
    const w = 160;
    const h = Math.max(1, Math.round((src.height / src.width) * w));
    const probe = document.createElement("canvas");
    probe.width = w;
    probe.height = h;
    const ctx = probe.getContext("2d")!;
    ctx.drawImage(src, 0, 0, w, h);
    const px = ctx.getImageData(0, 0, w, h).data;
    const colors = new Set<number>();
    let bright = 0;
    for (let i = 0; i < px.length; i += 4) {
      colors.add(((px[i] >> 3) << 10) | ((px[i + 1] >> 3) << 5) | (px[i + 2] >> 3));
      if (px[i] + px[i + 1] + px[i + 2] > 300) bright++;
    }
    return { distinct: colors.size, brightFraction: bright / (w * h) };
  });

  await page.screenshot({ path: info.outputPath("hero.png") });
  await page.screenshot({ path: info.outputPath("home.png"), fullPage: true });
  await info.attach("hero", { path: info.outputPath("hero.png"), contentType: "image/png" });
  await info.attach("home", { path: info.outputPath("home.png"), contentType: "image/png" });

  // A blank or single-color canvas has a handful of colors and no bright pixels.
  expect(stats.distinct, `distinct colors: ${stats.distinct}`).toBeGreaterThan(20);
  expect(stats.brightFraction, `bright fraction: ${stats.brightFraction}`).toBeGreaterThan(0.002);
  expect(errors).toEqual([]);
});

test("page shows the vocabulary, proof loop, and stages", async ({ page }) => {
  await page.goto("./");
  await expect(page.getByRole("heading", { level: 1 })).toHaveText("Ambient Superconductivity Lab");
  await expect(page.getByRole("heading", { name: "Four words, used precisely" })).toBeVisible();
  await expect(page.locator(".katex").first()).toBeVisible();
  await expect(page.locator(".stage-card")).toHaveCount(9);
});
