# Art checklist: blog.worldwidewebb.co

Read this before touching the look of the site, and tick it off before opening a design PR. Not deployed (see `.vercelignore`).

## Locked requirements (set by Calum, do not trade away)
1. **Black background.** Set Oct 27, 2026 after round 1: concepts B (Ultramarine) and C (Highlighter) were the closest, but the page ground must be black. Every concept, mockup and shipped design uses a black ground (`#000000`, or a black that reads as black on a calibrated screen). Colour lives in type, flat fields, art and icons on top of that black, never by lifting the ground to blue, white, cream or yellow.
2. Links to X (@worldwidewebbco) and GitHub (0x63616c) with real brand icons, plus a pixel-W favicon. These stay in every round. They do not live in top-right header buttons (see Never again); the treatment is still being chosen in round 3.
3. **Direction: R2-2 Autumn Chapters.** Chosen by Calum on Oct 27, 2026: black ground, flat full-bleed chapter bands in amber, moss and slate taken from the cottage render, bone ink, Epilogue plus Literata, brick code rule, contents rail on posts. Later rounds refine this; they do not swap it for another concept.
4. The studio's voxel cottage render stays the hero asset.

Black is not what Calum rejected in the original. The original failed on template look (tile card, system sans, self-describing footer). Black done with a point of view is the brief.

## Target
A small studio's own publication. It should look like someone with taste made it for these specific posts, not like a theme. Closest in spirit: Panic's blog, Cultured Code, Hundred Rabbits, Rauno, iA. Warm, confident, specific, with one strong idea per page.

## References (screenshots in `design/refs/`, captured Oct 27, 2026)
| File | Site | What to steal |
|---|---|---|
| `panic-blog.png` | panic.com/blog | Brand colour used with conviction, product art that carries the page |
| `cultured-code.png` | culturedcode.com/things | Calm, crafted product presentation, generous space |
| `hundred-rabbits.png` | 100r.co | Unapologetic personality, tiny studio voice, no template feel |
| `rauno.png` | rauno.me | Small precise type, restraint, details that reward a second look |
| `ia-writer.png` | ia.net | Typography as the whole design |
| `maggie-appleton.png` | maggieappleton.com | Illustration and long-form reading in one voice |
| `josh-comeau.png` | joshwcomeau.com | Colour and playfulness in a technical blog |
| `inessential.png` | inessential.com | A plain page can be good when the writing and type are right |

## Before (what Calum rejected)
`design/home-before.png`, `design/post-before.png`: Vercel-style tile card, system sans, a footer that described its own tech. Do not drift back toward it.

## Rules
1. One distinctive idea per concept (colour, type, or the cottage render), stated in a sentence before building.
2. Real content only: real post titles, real numbers, real images. No lorem, no invented posts, no placeholder stats.
3. The voxel cottage render is the studio's best asset. Use the cutout (`image-rendering: pixelated` when scaling), never a blurred or smoothed version.
4. Two typefaces at most, self-hosted (the site promises no third-party requests). Not Inter, Roboto, Fraunces, Geist, Instrument Serif, Space Grotesk.
5. Pass `npx impeccable detect` with zero findings before showing anything.
6. X (@worldwidewebbco) and GitHub (0x63616c) brand SVG icons, placed per the round-3 treatment (never as boxed or round icon buttons at the top right of the header), with visible focus and hover states and aria-labels.
7. Favicon is the pixel W in the concept's palette, with SVG, 16/32 PNG, 180 apple-touch, 512, and `.ico`. Check it at 16px.
8. Mobile at 390px and desktop at 1440px both reviewed as screenshots before merge.
9. On black: check contrast of body text (>= 7:1 preferred), the favicon on a dark tab and a light tab, and that no surface is lifted to grey cards to fake depth.
10. Review harshly against a commercial bar: would a paid studio ship this? If the answer is "it's fine", it isn't done.

## Never again
- No top-right header buttons. Calum, Oct 27, 2026: "hate the top right buttons". That means the boxed X and GitHub icon buttons in the header nav. No bordered, round or filled icon buttons in the top right of the masthead, in any form.
- No self-describing meta copy like "plain html, black themed" (Oct 27, 2026). The site never talks about how it was built, its theme, or its lack of tracking.
- No filler phrasing: "sad spreadsheet" style quips, "this is not a tutorial", "words only go so far", "let's dive in", "in this post we will".
- No generic dark template: black background plus Vercel-style bordered tiles plus small monospace labels. (Black itself is required, see Locked requirements.)
- No near-black plus a single acid accent (lime, neon green, electric yellow) as the whole identity. On the required black ground, build identity from type, scale, the cottage render and more than a lone accent dot.
- No cream plus serif plus terracotta default "editorial" look.
- No SaaS card grids for a one-post blog.
- No ALL-CAPS eyebrows, mono micro-labels, or middle-dot meta strings ("Oct 26 · updated · renderer notes").
- No `→` appended to links; no spaced em dashes as separators.
- No accent colour on a single headline word.
- No decorative grid or gradient backgrounds outside a real measurement surface.
- No mentioning private projects publicly.
