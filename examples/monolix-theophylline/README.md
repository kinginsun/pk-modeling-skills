# examples/monolix-theophylline — theophylline popPK with covariate search

Headless MonolixSuite 2024R1 example: population PK of theophylline with
weight-based covariate modeling and allometric scaling.

| File | Purpose |
|------|---------|
| `theophylline_project.mlxtran` | Base project (1-cpt oral, ka + Cl + V; covariates: weight, sex) |
| `theophylline_final_kaWT.mlxtran` | Final model: ka scaled by weight |
| `theophylline_final_ka_cWT.mlxtran` | Final model: ka scaled by centered weight |
| `theophylline_allometric.mlxtran` | Allometric scaling variant |
| `theophylline_data.csv` | Theophylline dataset |
| `theophylline_project/`, `theophylline_final_*/`, `theophylline_allometric/` | Reference result folders (estimates, SE, tests, bootstrap) |
| `theophylline_walkthrough/` | SAEM result folder from the narrated walkthrough (`docs/walkthrough-theophylline.md`) |
| `theophylline_monolix_report.html` | Reference ECharts report built from the result folders |

Run (requires MonolixSuite 2024R1; see SETUP.md). From this examples folder,
the x86 shim ships at `../../skills/monolix-cli/x86shim`:

```bash
PATH="$PWD/../../skills/monolix-cli/x86shim:$PATH" \
/Applications/MonolixSuite2024R1.app/Contents/Resources/monolixSuite/bin/monolix.sh \
  --no-gui -p "$PWD/theophylline_project.mlxtran" -o "$PWD/theophylline_project"
```

The `plotting.md` in the `monolix-cli` skill maps each result file to the
charts used in `theophylline_monolix_report.html`.
