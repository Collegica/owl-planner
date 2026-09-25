## 1. Identification

- [x] 1.1 `detect_bank` counts each text marker and returns the bank with the most matches, `None` on a tie; verify `pixi run test` passes, including the existing test that reads Ultimate from its text
- [x] 1.2 Tests on the invented fixtures: RBC plus a `PAYMENT CIBC VISA` line is RBC and reconciles; CIBC plus a `PAYMENT FROM RBC` line is CIBC; one mention of each is `None` and `convert` reports `unknown layout`; verify `pixi run test`

## 2. No movement elsewhere

- [x] 2.1 Re-run the tool on the sample; verify `pixi run sample-check` prints "sample output unchanged"
- [x] 2.2 Verify `pixi run check-all` passes (specs, ideas index, tests, sample, web parity)
