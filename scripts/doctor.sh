#!/usr/bin/env bash
#
# doctor.sh — environment checks and smoke tests for pk-modeling-skills.
#
# Usage:
#   ./scripts/doctor.sh                 check toolchain only (read-only, safe)
#   ./scripts/doctor.sh --run-examples  additionally run end-to-end smoke tests
#
set -uo pipefail

REPO="$(cd "$(dirname "$0")/.." && pwd)"
RUN_EXAMPLES=false
[[ "${1:-}" == "--run-examples" ]] && RUN_EXAMPLES=true

OK='[OK]      '
MISS='[MISSING] '
WARN='[WARN]    '
SKIP='[SKIP]    '

table=()
add() { table+=("$1|$2|$3"); }

# ---------------------------------------------------------------- platform
os_name="$(uname -s)"
arch="$(uname -m)"
if [[ "$os_name" != "Darwin" ]]; then
  echo "$WARN pk-modeling-skills targets macOS; continuing anyway."
fi

# ------------------------------------------------------------------- checks
check() { # name, command...
  local name="$1"; shift
  local out
  if out="$("$@" 2>/dev/null)"; then
    out="$(head -n1 <<<"$out")"
    if [[ -n "$out" ]]; then
      add "$name" "OK" "$out"
      return 0
    fi
  fi
  add "$name" "MISSING" "not found"
  return 1
}

check "brew (Homebrew)"     bash -c 'command -v brew'
check "gfortran"            bash -c 'command -v gfortran && gfortran -dumpversion'
check "R"                   bash -c 'command -v R && R --version | head -1'
check "python3"             bash -c 'command -v python3 && python3 --version'
check "ggplot2 (R package)" Rscript -e 'if(!requireNamespace("ggplot2",quietly=TRUE)) quit(status=1); cat("ggplot2", as.character(packageVersion("ggplot2")))'

have_nmfe=false
if check "nmfe76 (NONMEM driver)" bash -c 'command -v nmfe76'; then have_nmfe=true; fi

# PsN execute: prefer plain `execute`, fall back to newest versioned execute-*
EXEC_BIN="$(command -v execute 2>/dev/null || true)"
if [[ -z "$EXEC_BIN" ]]; then
  EXEC_BIN="$(ls /usr/local/bin/execute-* /opt/homebrew/bin/execute-* 2>/dev/null | sort -V | tail -n1 || true)"
fi
have_execute=false
if [[ -n "$EXEC_BIN" ]]; then
  ver="$("$EXEC_BIN" -version 2>&1 | head -n1)"
  add "execute (PsN)" "OK" "$EXEC_BIN (${ver:-unknown version})"
  have_execute=true
else
  add "execute (PsN)" "MISSING" "not found (install PsN, see SETUP.md step 4.2)"
fi
check "psn" bash -c 'command -v psn && psn -version | head -1'

if [[ "$arch" == "arm64" ]]; then
  if /usr/bin/arch -x86_64 /usr/bin/true 2>/dev/null; then
    add "Rosetta 2 (x86_64)" "OK" "arch -x86_64 works"
  else
    add "Rosetta 2 (x86_64)" "MISSING" "softwareupdate --install-rosetta --agree-to-license"
  fi
else
  add "Rosetta 2 (x86_64)" "OK" "n/a on $arch"
fi

monolix_app="$(ls -d /Applications/MonolixSuite*.app 2>/dev/null | head -n1 || true)"
monolix_sh=""
if [[ -n "$monolix_app" ]]; then
  monolix_sh="$monolix_app/Contents/Resources/monolixSuite/bin/monolix.sh"
  if [[ -x "$monolix_sh" ]]; then
    add "MonolixSuite" "OK" "$monolix_app"
  else
    add "MonolixSuite" "WARN" "app found but monolix.sh missing: $monolix_app"
    monolix_sh=""
  fi
else
  add "MonolixSuite" "MISSING" "not in /Applications"
fi

# x86shim location (repo copy always exists after clone)
x86shim="$REPO/skills/monolix-cli/x86shim"
[[ -x "$x86shim/g++" ]] || chmod +x "$x86shim/g++" "$x86shim/clang++" 2>/dev/null

# ------------------------------------------------------------------ report
echo "pk-modeling-skills environment report"
echo "====================================="
printf '%-28s %-9s %s\n' "ITEM" "STATUS" "DETAIL"
printf '%-28s %-9s %s\n' "----" "------" "------"
for row in "${table[@]}"; do
  IFS='|' read -r name status detail <<<"$row"
  case "$status" in
    OK) tag="$OK" ;; MISSING) tag="$MISS" ;; WARN) tag="$WARN" ;; *) tag="$SKIP" ;;
  esac
  printf '%-28s %s%s\n' "$name" "$tag" "$detail"
done

if ! $RUN_EXAMPLES; then
  echo
  echo "Toolchain check only. Run with --run-examples for end-to-end smoke tests."
  exit 0
fi

# ------------------------------------------------------------ smoke tests
echo
echo "Smoke tests"
echo "==========="
fail=0
work="$(mktemp -d /tmp/pkms_doctor.XXXXXX)"
trap 'rm -rf "$work"' EXIT

# 1) NONMEM: PsN execute on examples/nonmem-pop-pk/run1.mod
if $have_nmfe && $have_execute; then
  echo "-- NONMEM smoke test (examples/nonmem-pop-pk/run1.mod)"
  cp "$REPO/examples/nonmem-pop-pk/run1.mod" "$REPO/examples/nonmem-pop-pk/data.csv" "$work/"
  ( cd "$work" && "$EXEC_BIN" run1.mod -directory=smoke_nm >/dev/null 2>"$work/nm.log" )
  lst="$work/run1.lst"
  if [[ -s "$lst" ]] && grep -qE "MINIMIZATION SUCCESSFUL|ESTIMATION STEP OMITTED|SUCCESSFUL" "$lst"; then
    echo "   PASS: run1.lst finished normally"
  else
    echo "   FAIL: see $work/nm.log and $lst"
    fail=1
  fi

  # 2) R plotting smoke test (bundled example data)
  echo "-- R/ggplot2 smoke test"
  if Rscript "$REPO/scripts/smoke_plot.R" "$REPO/examples/nonmem-pop-pk/data.csv" \
       "$work/smoke.png" >/dev/null 2>&1 && [[ -s "$work/smoke.png" ]]; then
    echo "   PASS: ggplot2 figure rendered ($work/smoke.png)"
  else
    echo "   FAIL: ggplot2 render error"
    fail=1
  fi
else
  echo "-- NONMEM smoke test: SKIPPED (nmfe76 or execute missing)"
fi

# 3) Monolix headless smoke test
if [[ -n "$monolix_sh" ]]; then
  echo "-- Monolix smoke test (examples/monolix-theophylline/theophylline_project.mlxtran)"
  mlx="$work/theophylline_project.mlxtran"
  cp "$REPO/examples/monolix-theophylline/theophylline_project.mlxtran" "$mlx"
  cp "$REPO/examples/monolix-theophylline/theophylline_data.csv" "$work/"
  outdir="$work/mlx_out"; mkdir -p "$outdir"
  PATH="$x86shim:$PATH" "$monolix_sh" --no-gui -p "$mlx" -o "$outdir" \
    >/dev/null 2>"$work/mlx.log"
  if find "$outdir" -name populationParameters.txt | grep -q .; then
    echo "   PASS: populationParameters.txt produced"
  else
    echo "   FAIL: see $work/mlx.log"
    fail=1
  fi
else
  echo "-- Monolix smoke test: SKIPPED (MonolixSuite not installed)"
fi

echo
if [[ $fail -eq 0 ]]; then
  echo "All executed smoke tests passed."
else
  echo "Some smoke tests FAILED — inspect the logs printed above."
fi
exit $fail
