import sharp from "sharp";
import { mkdirSync, copyFileSync } from "node:fs";

const src = "public/favicon.svg";
const markSrc = "public/brand/logo-mark.svg";
const wmSrc = "public/brand/watermark.svg";

mkdirSync("public/brand", { recursive: true });
mkdirSync("web/brand", { recursive: true });

// Export icons at required resolutions: 1024, 512, 192, 64, 32
for (const s of [1024, 512, 192, 64, 32]) {
  // Use mark with spark for large sizes (1024, 512), clean favicon without spark for smaller
  const input = s >= 512 ? markSrc : src;
  const outPublic = `public/brand/cut-it-icon-${s}.png`;
  const outWeb = `web/brand/cut-it-icon-${s}.png`;

  await sharp(input, { density: 384 })
    .resize(s, s)
    .png()
    .toFile(outPublic);
  copyFileSync(outPublic, outWeb);
  console.log(`wrote cut-it-icon-${s}.png`);
}

// Generate favicon.ico (32x32)
await sharp(src, { density: 384 })
  .resize(32, 32)
  .png()
  .toFile("public/brand/favicon.ico");
copyFileSync("public/brand/favicon.ico", "web/brand/favicon.ico");
copyFileSync("public/brand/favicon.ico", "web/favicon.ico");
console.log("wrote favicon.ico");

// Generate watermark.png (512x512)
await sharp(wmSrc, { density: 384 })
  .resize(512, 512)
  .png()
  .toFile("public/brand/watermark.png");
copyFileSync("public/brand/watermark.png", "web/brand/watermark.png");
console.log("wrote watermark.png");

// Also update logo-email.png
await sharp("web/brand/logo-light.svg", { density: 384 })
  .resize(600, 180, { fit: "contain", background: { r: 0, g: 0, b: 0, alpha: 0 } })
  .png()
  .toFile("web/brand/logo-email.png");
copyFileSync("web/brand/logo-email.png", "public/brand/logo-email.png");
console.log("wrote logo-email.png");
