# piergst.github.io

Blog & resume, built with [Hugo](https://gohugo.io/) + [PaperMod](https://github.com/adityatelange/hugo-PaperMod).

## Build

```bash
hugo        # output in public/
```

## Resume PDF

Generate print-ready CVs from the Hugo resume pages:

```bash
./scripts/resume-pdf.py
```

Produces `resume-fr.pdf` and `resume-en.pdf` from `content/resume.*.md`.

Requires `hugo` and `chromium` (headless).  Print styles are derived from
`~/Repositories/piergst/resume/src/style.css`.
