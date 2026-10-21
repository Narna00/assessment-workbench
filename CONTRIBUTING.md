# Contributing

Use synthetic evidence and explicit model assumptions. Include a minimal reproducer and a regression test for changed decision semantics. Preserve negative results and record protocol changes. Do not submit client artifacts, credentials, real target inventories, or unlicensed standards text.

Run `python -m unittest discover -v` on Python 3.12 or later. The assessment workbench also includes `node test_portal.cjs` for dependency-free rendering/filter unit tests. It is not a visual browser test.

Research contributions should identify the closest prior work and separate exploratory tuning from held-out evaluation. Do not claim novelty or efficacy from a tool name or a single synthetic experiment. Security reports follow SECURITY.md.
