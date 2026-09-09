## 1. Engine

- [x] 1.1 Add `--config` and fall back per file to the examples; verified by `pixi run sample` using `sample/` while the tool's own personal files are untouched
- [x] 1.2 Add `run(argv) -> str` capturing the console output; verified by `python -c "import budget; print(budget.run(['--dir','sample/statements','--config','sample','--out','sample/budget.md']))"`

## 2. The household

- [x] 2.1 Write `scripts/make_sample.py`, deterministic, three dialects, every kind of money movement; verified by `python scripts/make_sample.py` producing 4 files and the importer reading all four
- [x] 2.2 Write the sample configuration exercising every rules section and a partly repaid loan; verified by the LEVELLED, ONE-OFF, LENDING and pass-through lines appearing in the output
- [x] 2.3 Record `sample/expected.txt` and add `sample`, `sample-check`, `sample-regen` tasks with `sample-check` in `check-all`; verified by `pixi run check-all`
