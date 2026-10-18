---
type: guide
updated: 2026-10-18
---

# Patch workflow

`upstream/pdfcraft` is a clean immutable base; only `work/pdfcraft` is editable. Export every external-source modification as a patch into `patches/pdfcraft`, list it in `series`, and record base, rationale, platform, verification and upstream status. Commit patches and metadata in this owned repository; work-copy commits alone are insufficient.

The initial series is empty. Reconstruct in a fresh temporary checkout and compare the resulting source tree before claiming reproduction. Preserve untracked files, branches and stashes before any work-copy replacement. Do not submit upstream or publish without separate authorization.
