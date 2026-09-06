#!/usr/bin/env python3
"""Build a single self-contained ECharts HTML report for the theophylline popPK
example, covering BOTH engines in this repository:

  * NONMEM 7.6 / FOCE-I   -> examples/nonmem-theophylline/
  * Monolix 2024R1 / SAEM -> examples/monolix-theophylline/

Everything rendered comes from the committed result files (no re-running of
NONMEM or Monolix). Usage:

    python3 scripts/build_theophylline_report.py             # write the HTML
    python3 scripts/build_theophylline_report.py --dump-json # also print data
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NM = os.path.join(ROOT, "examples", "nonmem-theophylline")
MX = os.path.join(ROOT, "examples", "monolix-theophylline")
MX_WT = os.path.join(MX, "theophylline_walkthrough")
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(DOCS, "theophylline_nonmem_monolix_report.html")

LN2 = math.log(2.0)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def r(x, n=4):
    """Round for JSON payload; keep payload small but faithful."""
    if x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    if math.isnan(v) or math.isinf(v):
        return None
    return round(v, n)


def num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def cv_from_var(omega2):
    """IIV variance -> CV% on the natural scale (log-normal)."""
    if omega2 is None or omega2 <= 0:
        return None
    return math.sqrt(math.exp(omega2) - 1.0) * 100.0


def sd_pct(omega):
    """omega given as an SD (log-normal) -> CV%."""
    if omega is None:
        return None
    return math.sqrt(math.exp(omega ** 2) - 1.0) * 100.0


# --------------------------------------------------------------------------
# NONMEM
# --------------------------------------------------------------------------
def read_ext(path):
    """Parse run1.ext -> (iterations, final, se, eigen)."""
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    header = lines[1].split()          # ITERATION THETA1 ... OBJ
    rows = []
    for ln in lines[2:]:
        parts = ln.split()
        if len(parts) != len(header):
            continue
        rows.append(dict(zip(header, [num(p) for p in parts])))

    iters, final, se, eigen = [], None, None, None
    for row in rows:
        it = row["ITERATION"]
        if it >= 0:
            iters.append({"iter": int(it), "obj": row["OBJ"]})
        elif it == -1000000000:
            final = row
        elif it == -1000000001:
            se = row
        elif it == -1000000002:
            eigen = row
    return iters, final, se, eigen


def read_cor(path):
    """Parse run1.cor -> (names, matrix). Fixed off-diagonals come as 0."""
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    names = lines[1].split()[1:]
    mat = []
    for ln in lines[2:]:
        parts = ln.split()
        mat.append([num(p) for p in parts[1:]])
    return names, mat


def read_phi(path):
    """Parse run1.phi -> per-subject EBEs with posterior SDs."""
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh if ln.strip()]
    header = lines[1].split()
    out = []
    for ln in lines[2:]:
        parts = ln.split()
        if len(parts) != len(header):
            continue
        d = dict(zip(header, parts))
        out.append({
            "id": int(num(d["ID"])),
            "eta1": num(d["ETA(1)"]),
            "eta2": num(d["ETA(2)"]),
            "eta3": num(d["ETA(3)"]),
            "sd1": math.sqrt(max(num(d["ETC(1,1)"]) or 0.0, 0.0)),
            "sd2": math.sqrt(max(num(d["ETC(2,2)"]) or 0.0, 0.0)),
            "sd3": math.sqrt(max(num(d["ETC(3,3)"]) or 0.0, 0.0)),
            "obj": num(d["OBJ"]),
        })
    return out


def read_sdtab(path):
    """Parse sdtab1 ($TABLE output). Banner line + header, '.' -> NA."""
    with open(path) as fh:
        lines = [ln for ln in fh if ln.strip()]
    header = lines[1].split()          # lines[0] is the "TABLE NO. 1" banner
    rows = []
    for ln in lines[2:]:
        parts = ln.split()
        if len(parts) != len(header):
            continue
        rows.append(dict(zip(header, [num(p) for p in parts])))
    return rows


def read_lst_bits(path):
    """Scrape shrinkage / ETABAR / constants out of run1.lst."""
    txt = open(path, errors="replace").read()
    out = {}

    def grab(label, n):
        m = re.search(re.escape(label) + r"\s*((?:[-+0-9.eE]+\s*){%d})" % n, txt)
        return [num(v) for v in m.group(1).split()] if m else [None] * n

    out["etabar"] = grab("ETABAR:", 3)
    out["etabar_se"] = grab("SE:", 3)
    out["etabar_p"] = grab("P VAL.:", 3)
    out["eta_shrink_sd"] = grab("ETASHRINKSD(%)", 3)
    out["eta_shrink_vr"] = grab("ETASHRINKVR(%)", 3)
    out["ebv_shrink_sd"] = grab("EBVSHRINKSD(%)", 3)
    out["eps_shrink_sd"] = grab("EPSSHRINKSD(%)", 2)
    out["rel_info"] = grab("RELATIVEINF(%)", 3)

    m = re.search(r"N\*LOG\(2PI\) CONSTANT TO OBJECTIVE FUNCTION:\s*([0-9.eE+-]+)", txt)
    out["obj_const"] = num(m.group(1)) if m else None
    m = re.search(r"OBJECTIVE FUNCTION VALUE WITH CONSTANT:\s*([0-9.eE+-]+)", txt)
    out["obj_with_const"] = num(m.group(1)) if m else None
    m = re.search(r"NO\. OF FUNCTION EVALUATIONS USED:\s*(\d+)", txt)
    out["nfe"] = int(m.group(1)) if m else None
    m = re.search(r"NO\. OF SIG\. DIGITS IN FINAL EST\.:\s*([0-9.]+)", txt)
    out["sigdig"] = num(m.group(1)) if m else None
    out["minimization_successful"] = "MINIMIZATION SUCCESSFUL" in txt
    out["covariance_completed"] = bool(
        re.search(r"EIGENVALUES OF COR MATRIX OF ESTIMATE", txt))
    m = re.search(r"Elapsed estimation\s+time in seconds:\s*([0-9.]+)", txt)
    out["t_est"] = num(m.group(1)) if m else None
    m = re.search(r"Elapsed covariance\s+time in seconds:\s*([0-9.]+)", txt)
    out["t_cov"] = num(m.group(1)) if m else None
    m = re.search(r"NONMEM\) VERSION ([0-9.]+)", txt)
    out["version"] = m.group(1) if m else None
    m = re.search(r"TOT\. NO\. OF OBS RECS:\s*(\d+)", txt)
    out["n_obs"] = int(m.group(1)) if m else None
    m = re.search(r"TOT\. NO\. OF INDIVIDUALS:\s*(\d+)", txt)
    out["n_id"] = int(m.group(1)) if m else None
    return out


def nonmem_block():
    iters, final, se, eigen = read_ext(os.path.join(NM, "run1.ext"))
    cor_names, cor_mat = read_cor(os.path.join(NM, "run1.cor"))
    phi = read_phi(os.path.join(NM, "run1.phi"))
    tab = read_sdtab(os.path.join(NM, "sdtab1"))
    lst = read_lst_bits(os.path.join(NM, "run1.lst"))

    ka, cl, v = final["THETA1"], final["THETA2"], final["THETA3"]
    om_ka, om_cl, om_v = final["OMEGA(1,1)"], final["OMEGA(2,2)"], final["OMEGA(3,3)"]
    sg_prop, sg_add = final["SIGMA(1,1)"], final["SIGMA(2,2)"]

    # ---- observations only (drop the dose record at t=0 written into $TABLE)
    obs = [row for row in tab if not (row["TIME"] == 0 and row["DV"] == 0)]

    # ---- per subject series
    by_id = {}
    for row in obs:
        by_id.setdefault(int(row["ID"]), []).append([
            r(row["TIME"], 3), r(row["DV"], 3), r(row["IPRED"], 4),
            r(row["PRED"], 4), r(row["CWRES"], 3)])

    subjects = []
    for row in tab:
        sid = int(row["ID"])
        if any(s["id"] == sid for s in subjects):
            continue
        subjects.append({"id": sid, "wt": row["WT"],
                         "sex": "M" if row["SEX"] == 1 else "F",
                         "ka": row["KA"], "cl": row["CL"], "v": row["V"]})

    # ---- parameters table (estimated ones only, i.e. SE != 1e10 sentinel)
    def se_ok(key):
        return se[key] is not None and se[key] < 1e9

    params = []

    def add(name, label, est, se_key, unit, kind, ci_log=False):
        if not se_ok(se_key):
            return
        s = se[se_key]
        lo = hi = None
        if kind == "theta":
            if ci_log:  # bounded positive theta -> CI on the log scale
                lo, hi = est * math.exp(-1.96 * s / est), est * math.exp(1.96 * s / est)
            else:
                lo, hi = est - 1.96 * s, est + 1.96 * s
        elif kind == "omega_var":       # variance -> CI then sqrt
            lo, hi = max(s and est - 1.96 * s or 0, 0), est + 1.96 * s
            lo, hi = math.sqrt(max(lo, 0)) * 100, math.sqrt(hi) * 100  # SD %
            est = math.sqrt(est) * 100
        elif kind == "sigma_prop":
            lo, hi = math.sqrt(max(est - 1.96 * s, 0)) * 100, math.sqrt(est + 1.96 * s) * 100
            est = math.sqrt(est) * 100
        elif kind == "sigma_add":
            lo, hi = math.sqrt(max(est - 1.96 * s, 0)), math.sqrt(est + 1.96 * s)
            est = math.sqrt(est)
        params.append({
            "name": name, "label": label, "unit": unit,
            "est": r(est, 5), "se": r(s if kind == "theta" else None, 5),
            "rse": r(abs(s / (final[se_key] or 1)) * 100, 2),
            "lo": r(lo, 5), "hi": r(hi, 5),
        })

    add("KA", "KA (THETA1)", ka, "THETA1", "1/h", "theta", ci_log=True)
    add("CL", "CL (THETA2)", cl, "THETA2", "L/h/kg", "theta", ci_log=True)
    add("V", "V (THETA3)", v, "THETA3", "L/kg", "theta", ci_log=True)
    add("OM11", "IIV on KA", om_ka, "OMEGA(1,1)", "% (SD)", "omega_var")
    add("OM22", "IIV on CL", om_cl, "OMEGA(2,2)", "% (SD)", "omega_var")
    add("OM33", "IIV on V", om_v, "OMEGA(3,3)", "% (SD)", "omega_var")
    add("SG11", "Residual proportional", sg_prop, "SIGMA(1,1)", "% (CV)", "sigma_prop")
    add("SG22", "Residual additive", sg_add, "SIGMA(2,2)", "mg/L", "sigma_add")

    # ---- correlation heatmap: keep only the estimated parameters
    estimated = ("THETA1", "THETA2", "THETA3", "OMEGA(1,1)", "OMEGA(2,2)",
                 "OMEGA(3,3)", "SIGMA(1,1)", "SIGMA(2,2)")
    keep = [i for i, n in enumerate(cor_names)
            if n in estimated and se.get(n) is not None and se.get(n) < 1e9]
    short = {"THETA1": "KA", "THETA2": "CL", "THETA3": "V",
             "OMEGA(1,1)": "ω²_KA", "OMEGA(2,2)": "ω²_CL", "OMEGA(3,3)": "ω²_V",
             "SIGMA(1,1)": "σ²_prop", "SIGMA(2,2)": "σ²_add"}
    corr = {
        "names": [short[cor_names[i]] for i in keep],
        "mat": [[r(cor_mat[i][j], 3) for j in keep] for i in keep],
    }

    k = cl / v
    return {
        "engine": "NONMEM 7.6.0 (nm760)",
        "algorithm": "FOCE-I (First Order Conditional Estimation with Interaction)",
        "version": lst.get("version"),
        "n_id": lst.get("n_id"),
        "n_obs": lst.get("n_obs"),
        "n_dose": (lst.get("n_obs") or 0) // 10 if lst.get("n_obs") else 12,
        "ofv": r(final["OBJ"], 4),
        "ofv_with_const": r(lst.get("obj_with_const"), 4),
        "obj_const": r(lst.get("obj_const"), 4),
        "nfe": lst.get("nfe"),
        "sigdig": lst.get("sigdig"),
        "minimization_successful": lst.get("minimization_successful"),
        "covariance_completed": lst.get("covariance_completed"),
        "t_est": lst.get("t_est"),
        "t_cov": lst.get("t_cov"),
        # row -1000000002 holds the 8 correlation-matrix eigenvalues, padded
        # with zeros for the unused off-diagonal slots -> ignore zeros.
        "eigen_min": r(min([v for k, v in (eigen or {}).items()
                            if k != "ITERATION" and isinstance(v, (int, float))
                            and v > 0] or [0]), 6),
        "eigen_max": r(max([v for k, v in (eigen or {}).items()
                            if k != "ITERATION" and isinstance(v, (int, float))] or [0]), 6),
        "iters": iters,
        "params": params,
        "raw": {
            "ka": r(ka, 5), "cl": r(cl, 5), "v": r(v, 5),
            "om_ka": r(om_ka, 5), "om_cl": r(om_cl, 5), "om_v": r(om_v, 5),
            "sg_prop": r(sg_prop, 6), "sg_add": r(sg_add, 6),
            "sd_ka": r(math.sqrt(om_ka), 5), "sd_cl": r(math.sqrt(om_cl), 5),
            "sd_v": r(math.sqrt(om_v), 5),
            "cv_ka": r(cv_from_var(om_ka), 2), "cv_cl": r(cv_from_var(om_cl), 2),
            "cv_v": r(cv_from_var(om_v), 2),
            "res_prop_cv": r(math.sqrt(sg_prop) * 100, 3),
            "res_add_sd": r(math.sqrt(sg_add), 4),
            "k": r(k, 6), "t_half": r(LN2 / k, 3),
            "cl_70": r(cl * 70, 4), "v_70": r(v * 70, 3),
            "t_max_typ": r(math.log(ka / k) / (ka - k), 3),
        },
        "etabar": [r(x, 5) for x in lst["etabar"]],
        "etabar_se": [r(x, 5) for x in lst["etabar_se"]],
        "etabar_p": [r(x, 4) for x in lst["etabar_p"]],
        "eta_shrink_sd": [r(x, 2) for x in lst["eta_shrink_sd"]],
        "eta_shrink_vr": [r(x, 2) for x in lst["eta_shrink_vr"]],
        "ebv_shrink_sd": [r(x, 2) for x in lst["ebv_shrink_sd"]],
        "eps_shrink_sd": [r(x, 2) for x in lst["eps_shrink_sd"]],
        "rel_info": [r(x, 2) for x in lst["rel_info"]],
        "phi": [{k2: r(vv, 5) if isinstance(vv, float) else vv
                 for k2, vv in p.items()} for p in phi],
        "subjects": [{k2: r(vv, 4) if isinstance(vv, float) else vv
                      for k2, vv in s.items()} for s in subjects],
        "by_id": {str(k2): v2 for k2, v2 in sorted(by_id.items())},
        "gof": [[r(x["IPRED"], 4), r(x["PRED"], 4), r(x["DV"], 3),
                 r(x["CWRES"], 3), r(x["TIME"], 3), int(x["ID"])] for x in obs],
        "corr": corr,
    }


# --------------------------------------------------------------------------
# Monolix
# --------------------------------------------------------------------------
def read_pop_params(path):
    out = []
    with open(path) as fh:
        for row in csv.DictReader(fh):
            cv = num(row.get("CV"))
            out.append({
                "parameter": row["parameter"],
                "value": num(row["value"]),
                "cv": r(cv, 2) if cv else None,
                "se": num(row.get("se_lin")),
                "rse": num(row.get("rse_lin")),
                "lo": num(row.get("P2.5_lin")),
                "hi": num(row.get("P97.5_lin")),
            })
    return out


def read_ll(path):
    """logLikelihood.txt is long-format: header 'criteria,<method>' then one row
    per criterion (OFV, AIC, BIC, BICc, standardError)."""
    out = {}
    with open(path) as fh:
        for row in csv.reader(fh):
            if len(row) >= 2 and row[0] != "criteria":
                out[row[0]] = num(row[1])
    return out


def read_csv_rows(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def read_corr_lin(path):
    """FisherInformation/correlationEstimatesLin.txt — headerless CSV,
    first column is the row name."""
    names, mat = [], []
    with open(path) as fh:
        for row in csv.reader(fh):
            if not row:
                continue
            names.append(row[0])
            mat.append([num(v) for v in row[1:]])
    return names, mat


def parse_model_building(path):
    txt = open(path, errors="replace").read()
    models = []
    chunks = re.split(r"\nModel (\d+)", txt)
    for i in range(1, len(chunks), 2):
        idx, body = chunks[i], chunks[i + 1]
        ofv = num(re.search(r"-2 \* LL\s*:\s*([0-9.]+)", body).group(1)) \
            if re.search(r"-2 \* LL\s*:\s*([0-9.]+)", body) else None
        bicc = num(re.search(r"BICc\s*:\s*([0-9.]+)", body).group(1)) \
            if re.search(r"BICc\s*:\s*([0-9.]+)", body) else None
        covs = []
        for param in ("ka", "V", "Cl"):
            m = re.search(r"\|\s*%s\s*\|([^\n]*)\|" % re.escape(param), body)
            if m:
                cells = [c.strip() for c in m.group(1).split("|")]
                # cells align with SEX, WEIGHT, logtWEIGHT
                for name, cell in zip(("SEX", "WEIGHT", "logtWEIGHT"), cells):
                    if cell == "X":
                        covs.append("%s~%s" % (param, name))
        models.append({"model": int(idx), "ofv": ofv, "bicc": bicc,
                       "cov": ", ".join(covs) if covs else "none"})
    best = re.search(r"Best Model:\s*(\d+)", txt)
    return models, int(best.group(1)) if best else None


def parse_wald(folder):
    """beta_* significance tests: scan Tests/*.txt for the section that starts
    with 'parameter,statistics(lin),p-value(lin)' (it may not be line 1)."""
    out = []
    tdir = os.path.join(folder, "Tests")
    if not os.path.isdir(tdir):
        return out
    header = "parameter,statistics(lin),p-value(lin)"
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".txt"):
            continue
        lines = [ln.strip() for ln in
                 open(os.path.join(tdir, fn), errors="replace")]
        if header not in lines:
            continue
        i = lines.index(header) + 1
        while i < len(lines) and lines[i] and "," in lines[i]:
            parts = lines[i].split(",")
            if len(parts) == 3 and num(parts[1]) is not None:
                out.append({"param": parts[0], "stat": num(parts[1]),
                            "p": num(parts[2])})
                i += 1
            else:
                break
    return out


def monolix_block():
    base = read_pop_params(os.path.join(MX_WT, "populationParameters.txt"))
    ll = read_ll(os.path.join(MX_WT, "LogLikelihood", "logLikelihood.txt"))
    indiv_ll = read_csv_rows(os.path.join(MX_WT, "LogLikelihood", "individualLL.txt"))
    preds = read_csv_rows(os.path.join(MX_WT, "predictions.txt"))
    ipar = read_csv_rows(os.path.join(MX_WT, "IndividualParameters",
                                      "estimatedIndividualParameters.txt"))
    eta = read_csv_rows(os.path.join(MX_WT, "IndividualParameters",
                                     "estimatedRandomEffects.txt"))
    shrink = read_csv_rows(os.path.join(MX_WT, "IndividualParameters", "shrinkage.txt"))
    corr_names, corr_mat = read_corr_lin(
        os.path.join(MX_WT, "FisherInformation", "correlationEstimatesLin.txt"))
    mb, mb_best = parse_model_building(
        os.path.join(MX, "theophylline_project", "ModelBuilding", "modelBuilding.txt"))

    bmap = {p["parameter"]: p for p in base}
    ka, cl, v = bmap["ka_pop"]["value"], bmap["Cl_pop"]["value"], bmap["V_pop"]["value"]
    k = cl / v

    by_id, gof, iwres = {}, [], []
    for p in preds:
        sid, t = p["id"], num(p["time"])
        obs, pop, ind = num(p["CONC"]), num(p["popPred"]), num(p["indivPred_SAEM"])
        iwr = num(p["indWRes_SAEM"])
        by_id.setdefault(sid, []).append([r(t, 3), r(obs, 3), r(ind, 4), r(pop, 4)])
        gof.append([r(pop, 4), r(ind, 4), r(obs, 3), sid])
        iwres.append([r(t, 3), r(iwr, 4), sid])

    subjects = [{
        "id": x["id"], "ka": num(x["ka_SAEM"]), "V": num(x["V_SAEM"]),
        "Cl": num(x["Cl_SAEM"]), "wt": num(x["WEIGHT"]), "sex": x["SEX"],
    } for x in ipar]

    etas = [{
        "id": x["id"], "ka": num(x["eta_ka_SAEM"]), "V": num(x["eta_V_SAEM"]),
        "Cl": num(x["eta_Cl_SAEM"]),
        "sd_ka": num(x["eta_ka_sd"]), "sd_V": num(x["eta_V_sd"]),
        "sd_Cl": num(x["eta_Cl_sd"]),
    } for x in eta]

    # ---- covariate-model variants (each has its own result folder)
    variants = []
    for folder, label, note in (
            ("theophylline_project", "Base", "无协变量（walkthrough 主模型）"),
            ("theophylline_final_kaWT", "ka ~ WEIGHT", "COSSAC 选出，未中心化"),
            ("theophylline_final_ka_cWT", "ka ~ (WT−70)", "COSSAC 选出 + 中心化（最终模型）"),
            ("theophylline_allometric", "V,Cl ~ log(WT/70)", "异速生长假设，β 自由估计")):
        d = os.path.join(MX, folder)
        if not os.path.isfile(os.path.join(d, "LogLikelihood", "logLikelihood.txt")):
            continue
        vll = read_ll(os.path.join(d, "LogLikelihood", "logLikelihood.txt"))
        variants.append({
            "name": label, "folder": folder, "note": note,
            "ofv": r(vll.get("OFV"), 3), "aic": r(vll.get("AIC"), 3),
            "bic": r(vll.get("BIC"), 3), "bicc": r(vll.get("BICc"), 3),
            "se": r(vll.get("standardError"), 4),
            "params": [{k2: r(vv, 5) if isinstance(vv, float) else vv
                        for k2, vv in p.items()}
                       for p in read_pop_params(os.path.join(d, "populationParameters.txt"))],
            "wald": parse_wald(d),
        })

    shrink_out = [{
        "parameter": x["parameters"],
        "mode": r(num(x["shrinkage_mode"]), 2),
        "mean": r(num(x["shrinkage_mean"]), 2),
        "condDist": r(num(x["shrinkage_condDist"]), 2),
    } for x in shrink]

    return {
        "engine": "MonolixSuite 2024R1 (headless, monolix.sh --no-gui)",
        "algorithm": "SAEM (Stochastic Approximation EM)",
        "n_id": 12, "n_obs": len(preds), "n_dose": 12,
        "ofv": r(ll.get("OFV"), 3), "aic": r(ll.get("AIC"), 3),
        "bic": r(ll.get("BIC"), 3), "bicc": r(ll.get("BICc"), 3),
        "ll_se": r(ll.get("standardError"), 4),
        "indiv_ll": [[x["id"], r(num(x["importanceSampling"]), 3)] for x in indiv_ll],
        "saem": {"exploratory": 218, "smoothing": 111, "autostop": True,
                 "elapsed_s": 1.4, "cpu_s": 5.0},
        "params": [{k2: r(vv, 5) if isinstance(vv, float) else vv
                    for k2, vv in p.items()} for p in base],
        "raw": {
            "ka": r(ka, 5), "cl": r(cl, 5), "v": r(v, 5),
            "om_ka": r(bmap["omega_ka"]["value"], 5),
            "om_cl": r(bmap["omega_Cl"]["value"], 5),
            "om_v": r(bmap["omega_V"]["value"], 5),
            "cv_ka": r(sd_pct(bmap["omega_ka"]["value"]), 2),
            "cv_cl": r(sd_pct(bmap["omega_Cl"]["value"]), 2),
            "cv_v": r(sd_pct(bmap["omega_V"]["value"]), 2),
            "a": r(bmap["a"]["value"], 5), "b": r(bmap["b"]["value"], 5),
            "k": r(k, 6), "t_half": r(LN2 / k, 3),
            "cl_70": r(cl * 70, 4), "v_70": r(v * 70, 3),
            "t_max_typ": r(math.log(ka / k) / (ka - k), 3),
        },
        "subjects": subjects,
        "etas": etas,
        "shrinkage": shrink_out,
        "by_id": {k2: v2 for k2, v2 in sorted(by_id.items(), key=lambda kv: int(kv[0]))},
        "gof": gof,
        "iwres": iwres,
        "corr": {"names": corr_names,
                 "mat": [[r(x, 4) for x in row] for row in corr_mat]},
        "model_building": {"models": mb, "best": mb_best,
                           "strategy": "COSSAC", "lin": True,
                           "stopping": "LRT (0.05, 0.01) / correlation (0.3, 0.01)",
                           "selected_params": ["ka", "V", "Cl"],
                           "selected_covs": ["WEIGHT", "SEX"]},
        "variants": variants,
    }


# --------------------------------------------------------------------------
# cross-engine
# --------------------------------------------------------------------------
def cross_block(nm, mx):
    nmr, mxr = nm["raw"], mx["raw"]

    typ = []
    for key, label, unit in (("ka", "KA", "1/h"),
                             ("cl", "CL", "L/h/kg"),
                             ("v", "V", "L/kg")):
        a, b = nmr[key], mxr[key]
        typ.append({
            "key": key, "label": label, "unit": unit,
            "nm": a, "mx": b,
            "diff_pct": r((a - b) / b * 100, 2),
            "nm_lo": next((p["lo"] for p in nm["params"] if p["name"] == key.upper()), None),
            "nm_hi": next((p["hi"] for p in nm["params"] if p["name"] == key.upper()), None),
            "mx_lo": next((p["lo"] for p in mx["params"]
                           if p["parameter"] == {"ka": "ka_pop", "cl": "Cl_pop",
                                                 "v": "V_pop"}[key]), None),
            "mx_hi": next((p["hi"] for p in mx["params"]
                           if p["parameter"] == {"ka": "ka_pop", "cl": "Cl_pop",
                                                 "v": "V_pop"}[key]), None),
        })

    iiv = []
    for key, label in (("ka", "KA"), ("cl", "CL"), ("v", "V")):
        iiv.append({"label": label, "nm": nmr["cv_" + key], "mx": mxr["cv_" + key],
                    "nm_sd": nmr["sd_" + key] if "sd_" + key in nmr else None,
                    "mx_omega": mxr["om_" + key]})

    # ---- EBE comparison (NONMEM POSTHOC vs Monolix conditional estimate)
    mx_eta = {e["id"]: e for e in mx["etas"]}
    ebe = []
    for p in nm["phi"]:
        m = mx_eta.get(str(p["id"]))
        if not m:
            continue
        ebe.append({"id": p["id"],
                    "nm_ka": r(p["eta1"], 4), "mx_ka": r(m["ka"], 4),
                    "nm_cl": r(p["eta2"], 4), "mx_cl": r(m["Cl"], 4),
                    "nm_v": r(p["eta3"], 4), "mx_v": r(m["V"], 4)})

    # ---- matched individual predictions (same ID + TIME)
    mx_pred = {}
    for sid, rows in mx["by_id"].items():
        for t, obs, ind, pop in rows:
            mx_pred[(int(sid), round(t, 2))] = (ind, pop, obs)
    ipred_pairs, pop_pairs = [], []
    for sid, rows in nm["by_id"].items():
        for t, dv, ipred, pred, cwres in rows:
            hit = mx_pred.get((int(sid), round(t, 2)))
            if not hit:
                continue
            ipred_pairs.append([r(ipred, 4), r(hit[0], 4), int(sid), r(t, 2)])
            pop_pairs.append([r(pred, 4), r(hit[1], 4), int(sid), r(t, 2)])

    def rmse(pairs):
        if not pairs:
            return None
        return r(math.sqrt(sum((a - b) ** 2 for a, b, *_ in pairs) / len(pairs)), 4)

    return {
        "typical": typ,
        "iiv": iiv,
        "ebe": ebe,
        "ipred_pairs": ipred_pairs,
        "pop_pairs": pop_pairs,
        "n_matched": len(ipred_pairs),
        "rmse_ipred": rmse(ipred_pairs),
        "rmse_pred": rmse(pop_pairs),
        "t_half": {"nm": nmr["t_half"], "mx": mxr["t_half"]},
        "cl_70": {"nm": nmr["cl_70"], "mx": mxr["cl_70"]},
        "v_70": {"nm": nmr["v_70"], "mx": mxr["v_70"]},
        "t_max": {"nm": nmr["t_max_typ"], "mx": mxr["t_max_typ"]},
        "ofv": {
            "nm": nm["ofv"], "nm_const": nm["obj_const"],
            "nm_with_const": nm["ofv_with_const"],
            "mx": mx["ofv"], "mx_aic": mx["aic"], "mx_bic": mx["bic"],
        },
        "residual": {
            "nm_prop_cv": nmr["res_prop_cv"], "nm_add_sd": nmr["res_add_sd"],
            "mx_a": mxr["a"], "mx_b": mxr["b"],
        },
    }


# --------------------------------------------------------------------------
def build():
    nm = nonmem_block()
    mx = monolix_block()
    data = {
        "meta": {
            "drug": "Theophylline",
            "dataset": "经典 theophylline 数据集（Monolix 内置格式）",
            "dose": "单次口服 4.02 mg/kg",
            "dose_amt": "4.02 mg/kg",
            "n_id": nm["n_id"] or 12,
            "n_obs": nm["n_obs"] or 120,
            "n_dose": 12,
            "wt_range": [min(s["wt"] for s in nm["subjects"]),
                         max(s["wt"] for s in nm["subjects"])],
            "sex_counts": {
                "M": sum(1 for s in nm["subjects"] if s["sex"] == "M"),
                "F": sum(1 for s in nm["subjects"] if s["sex"] == "F")},
            "generated_from": "committed NONMEM + Monolix result files (no re-run)",
        },
        "nonmem": nm,
        "monolix": mx,
        "cross": cross_block(nm, mx),
        "sources": {
            "mod": open(os.path.join(NM, "run1.mod")).read(),
            "mlxtran": open(os.path.join(MX, "theophylline_project.mlxtran")).read(),
            "mlxtran_final": open(os.path.join(MX, "theophylline_final_ka_cWT.mlxtran")).read(),
            "prep": open(os.path.join(NM, "prep_data.R")).read(),
            "gof": open(os.path.join(NM, "gof_plots.R")).read(),
        },
    }
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-json", action="store_true")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    data = build()

    if args.dump_json:
        print(json.dumps(data, indent=2, ensure_ascii=False)[:4000])

    html = render_html(data)
    with open(args.out, "w") as fh:
        fh.write(html)

    nm, mx, x = data["nonmem"], data["monolix"], data["cross"]
    print("wrote %s (%.1f KB)" % (args.out, os.path.getsize(args.out) / 1024))
    print("  NONMEM : OFV %.3f  KA %.4f  CL %.5f  V %.4f  t½ %.2f h  (%d obs, %d subj)"
          % (nm["ofv"], nm["raw"]["ka"], nm["raw"]["cl"], nm["raw"]["v"],
             nm["raw"]["t_half"], len(nm["gof"]), nm["n_id"]))
    print("  Monolix: OFV %.3f  KA %.4f  CL %.5f  V %.4f  t½ %.2f h  (%d obs, %d subj)"
          % (mx["ofv"], mx["raw"]["ka"], mx["raw"]["cl"], mx["raw"]["v"],
             mx["raw"]["t_half"], len(mx["gof"]), mx["n_id"]))
    print("  cross  : %d matched predictions, RMSE(IPRED) %s"
          % (x["n_matched"], x["rmse_ipred"]))
    for t in x["typical"]:
        print("    %-3s NM %-8.4g  MLX %-8.4g  Δ %+.2f%%"
              % (t["label"], t["nm"], t["mx"], t["diff_pct"]))


# render_html is defined in the sibling template module to keep this file small.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from theophylline_report_template import render_html  # noqa: E402

if __name__ == "__main__":
    main()
