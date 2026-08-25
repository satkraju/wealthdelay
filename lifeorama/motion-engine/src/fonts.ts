import { staticFile, delayRender, continueRender } from "remotion";

// Load Plus Jakarta Sans (WealthDelay brand face) from public/fonts, dependency-free.
// LOR templates don't use this — they keep the system font in theme.ts. Loading it
// here is harmless for LOR renders (the @font-face just goes unused).
let loaded = false;

export const ensureBrandFonts = () => {
  if (loaded || typeof window === "undefined") return;
  loaded = true;
  const handle = delayRender("Loading Plus Jakarta Sans");
  const face = new FontFace(
    "Plus Jakarta Sans",
    `url(${staticFile("fonts/PlusJakartaSans.ttf")}) format("truetype")`,
    { weight: "400 800" },
  );
  face
    .load()
    .then((f) => {
      (document.fonts as FontFaceSet).add(f);
      continueRender(handle);
    })
    .catch(() => {
      // Fall back to the system stack rather than blocking the render forever.
      continueRender(handle);
    });
};
