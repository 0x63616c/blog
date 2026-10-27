# Art checklist: blog.worldwidewebb.co

Read this before touching the look of the site, and tick it off before opening a design PR. Not deployed (see `.vercelignore`).

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
`design/home-before.png`, `design/post-before.png`: black page, Vercel-style tile card, system sans, a footer that described its own tech. Do not drift back toward it.

## Rules
1. One distinctive idea per concept (colour, type, or the cottage render), stated in a sentence before building.
2. Real content only: real post titles, real numbers, real images. No lorem, no invented posts, no placeholder stats.
3. The voxel cottage render is the studio's best asset. Use the cutout (`image-rendering: pixelated` when scaling), never a blurred or smoothed version.
4. Two typefaces at most, self-hosted (the site promises no third-party requests). Not Inter, Roboto, Fraunces, Geist, Instrument Serif, Space Grotesk.
5. Pass `npx impeccable detect` with zero findings before showing anything.
6. X (@worldwidewebbco) and GitHub (0x63616c) brand SVG icons, in the header and footer, with visible focus and hover states and aria-labels.
7. Favicon is the pixel W in the concept's palette, with SVG, 16/32 PNG, 180 apple-touch, 512, and `.ico`. Check it at 16px.
8. Mobile at 390px and desktop at 1440px both reviewed as screenshots before merge.
9. Review harshly against a commercial bar: would a paid studio ship this? If the answer is "it's fine", it isn't done.

## Never again
- No self-describing meta copy like "plain html, black themed" (Oct 27, 2026). The site never talks about how it was built, its theme, or its lack of tracking.
- No filler phrasing: "sad spreadsheet" style quips, "this is not a tutorial", "words only go so far", "let's dive in", "in this post we will".
- No generic dark template: black background plus Vercel-style bordered tiles plus small monospace labels.
- No near-black plus a single acid accent as the whole identity.
- No cream plus serif plus terracotta default "editorial" look.
- No SaaS card grids for a one-post blog.
- No ALL-CAPS eyebrows, mono micro-labels, or middle-dot meta strings ("Oct 26 · updated · renderer notes").
- No `→` appended to links; no spaced em dashes as separators.
- No accent colour on a single headline word.
- No decorative grid or gradient backgrounds outside a real measurement surface.
- No mentioning private projects publicly.
