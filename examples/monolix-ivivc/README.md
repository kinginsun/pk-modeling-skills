# examples/monolix-ivivc — level-A IVIVC in Monolix

Headless MonolixSuite 2024R1 example: IVIVC for **metformin** ER tablets
(same Balan et al. 2001 dataset as `examples/nonmem-ivivc/`).

| File | Purpose |
|------|---------|
| `balan_diss_hill.mlxtran` | Monolix project linking in vitro dissolution to in vivo PK |
| `echarts_report.html` | Reference hand-crafted ECharts report (quality template for `monolix-cli/plotting.md`) |

Run (requires MonolixSuite 2024R1; see SETUP.md). From this examples folder,
the x86 shim ships at `../../skills/monolix-cli/x86shim`:

```bash
PATH="$PWD/../../skills/monolix-cli/x86shim:$PATH" \
/Applications/MonolixSuite2024R1.app/Contents/Resources/monolixSuite/bin/monolix.sh \
  --no-gui -p "$PWD/balan_diss_hill.mlxtran" -o "$PWD/results"
```
