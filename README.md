# blog

Static blog. Plain HTML, black theme from the rest of my sites.

- `python3 tools/build.py` regenerates `index.html` and `posts/*/index.html`. Charts are drawn by `tools/figures.py` from the files in `data/`.
- Deployed on Vercel as a static site, no build step (the generated HTML is committed).
