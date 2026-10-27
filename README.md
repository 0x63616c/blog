# blog

Static blog for World Wide Webb, served at blog.worldwidewebb.co.

- `python3 tools/build.py` regenerates `index.html` and `posts/*/index.html`. Charts are drawn by `tools/figures.py` from the files in `data/`.
- Deployed on Vercel as a static site, no build step (the generated HTML is committed).
