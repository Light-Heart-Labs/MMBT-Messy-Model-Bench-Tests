"""Independent verification of the model. We replicate every formula in
plain Python from the same drivers and cross-check key values vs. what
Excel will compute.

Output is written to extracted/model_sanity.csv so the model and the
verification can be diff'd in a hostile environment without Excel.
"""
from __future__ import annotations

import csv
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent

# Same anchors as scripts/build_model.py
FY25 = {
    "rev_total": 609780,
    "am_vc": 424319, "am_pl": 62731, "am_oth": 21723,
    "intl_vc": 71943, "intl_pl": 25951, "intl_oth": 3113,
    "gp_americas": 187309, "gp_intl": 35286, "gp_total": 222595,
    "sga": 140063, "op_inc": 82532, "non_op": 10439, "pretax": 92971,
    "tax": 21651, "ni": 71320, "da": 1072, "sbc": 10843,
    "shares_dil": 59.967691, "eps_dil": 1.19,
    "cash": 196873,
}

# Driver assumptions for each scenario, FY26/27/28
SCEN = {
    1: "Bear", 2: "Base", 3: "Bull",
}

DRIVERS = {
    "growth": {
        # (segment, brand) -> (Y1[bear,base,bull], Y2[...], Y3[...])
        ("Americas", "Vita Coco Coconut Water"):    [(0.06, 0.12, 0.18), (0.06, 0.10, 0.15), (0.05, 0.09, 0.13)],
        ("Americas", "Private Label"):              [(0.05, 0.22, 0.35), (0.04, 0.10, 0.18), (0.03, 0.07, 0.12)],
        ("Americas", "Other"):                      [(-0.10, 0.10, 0.30), (0.05, 0.10, 0.20), (0.05, 0.08, 0.15)],
        ("International", "Vita Coco Coconut Water"): [(0.18, 0.30, 0.40), (0.15, 0.25, 0.35), (0.12, 0.22, 0.30)],
        ("International", "Private Label"):         [(0.05, 0.15, 0.25), (0.05, 0.12, 0.20), (0.05, 0.10, 0.15)],
        ("International", "Other"):                 [(-0.20, 0.00, 0.20), (0.00, 0.05, 0.15), (0.00, 0.05, 0.10)],
    },
    "gm_americas": [(0.355, 0.385, 0.400), (0.355, 0.390, 0.410), (0.355, 0.390, 0.415)],
    "gm_intl":     [(0.330, 0.360, 0.385), (0.335, 0.370, 0.400), (0.340, 0.375, 0.405)],
    "sga_pct":     [(0.235, 0.220, 0.210), (0.230, 0.215, 0.205), (0.225, 0.210, 0.200)],
    "tax_rate":    [(0.250, 0.230, 0.215), (0.250, 0.230, 0.215), (0.250, 0.230, 0.215)],
    "da_pct":      [(0.0020, 0.0020, 0.0020)] * 3,
    "sbc_pct":     [(0.018, 0.018, 0.018)] * 3,
    "non_op_M":    [(0.0, 5.0, 10.0)] * 3,
    "shares_M":    [(60.0, 60.0, 60.0), (60.5, 60.0, 59.5), (61.0, 60.0, 59.0)],
    "exit_mult":   [(12.0, 17.0, 22.0)] * 3,
    "wacc":        [(0.10, 0.09, 0.08)] * 3,
    "tg":          [(0.020, 0.025, 0.030)] * 3,
    "capex_pct":   [(0.0020, 0.0020, 0.0020)] * 3,
    "nwc_pct":     [(0.20, 0.20, 0.20)] * 3,
}


def run_scenario(scen: int, *, write_rows: list[dict] | None = None) -> dict:
    si = scen - 1  # 0/1/2 indexing
    base_rev = {
        ("Americas", "Vita Coco Coconut Water"):    FY25["am_vc"],
        ("Americas", "Private Label"):              FY25["am_pl"],
        ("Americas", "Other"):                      FY25["am_oth"],
        ("International", "Vita Coco Coconut Water"): FY25["intl_vc"],
        ("International", "Private Label"):         FY25["intl_pl"],
        ("International", "Other"):                 FY25["intl_oth"],
    }
    fy = {25: dict(base_rev), 26: {}, 27: {}, 28: {}}
    for k, b in base_rev.items():
        prev = b
        for yi, year in enumerate([26, 27, 28]):
            g = DRIVERS["growth"][k][yi][si]
            v = prev * (1 + g)
            fy[year][k] = v
            prev = v

    out = {}
    for year in [25, 26, 27, 28]:
        am = sum(fy[year][k] for k in [("Americas", "Vita Coco Coconut Water"),
                                       ("Americas", "Private Label"),
                                       ("Americas", "Other")])
        intl = sum(fy[year][k] for k in [("International", "Vita Coco Coconut Water"),
                                         ("International", "Private Label"),
                                         ("International", "Other")])
        rev = am + intl
        if year == 25:
            gp_am = FY25["gp_americas"]; gp_intl_v = FY25["gp_intl"]
        else:
            gp_am = am * DRIVERS["gm_americas"][year - 26][si]
            gp_intl_v = intl * DRIVERS["gm_intl"][year - 26][si]
        gp = gp_am + gp_intl_v
        if year == 25:
            sga = FY25["sga"]
        else:
            sga = rev * DRIVERS["sga_pct"][year - 26][si]
        op = gp - sga
        if year == 25:
            non_op = FY25["non_op"]; tax = FY25["tax"]; ni = FY25["ni"]; eps = FY25["eps_dil"]
            da = FY25["da"]; sbc = FY25["sbc"]; shares = FY25["shares_dil"]
            ebitda = op + da + sbc
        else:
            non_op = DRIVERS["non_op_M"][year - 26][si] * 1000
            pretax = op + non_op
            tax = pretax * DRIVERS["tax_rate"][year - 26][si]
            ni = pretax - tax
            da = rev * DRIVERS["da_pct"][year - 26][si]
            sbc = rev * DRIVERS["sbc_pct"][year - 26][si]
            shares = DRIVERS["shares_M"][year - 26][si]
            eps = ni / shares / 1000
            ebitda = op + da + sbc
        out[year] = {
            "rev": rev, "am_rev": am, "intl_rev": intl,
            "gp": gp, "gm_pct": gp / rev, "sga": sga, "op": op, "op_pct": op / rev,
            "ni": ni, "ebitda": ebitda, "ebitda_pct": ebitda / rev,
            "eps": eps, "shares_M": shares,
        }
        # FCF approximation
        if year == 25:
            fcf = 47174 - 8149  # actual
        else:
            d_rev = rev - out[year - 1]["rev"]
            cfo = ni + da + sbc - DRIVERS["nwc_pct"][year - 26][si] * d_rev
            capex = rev * DRIVERS["capex_pct"][year - 26][si]
            fcf = cfo - capex
        out[year]["fcf"] = fcf

        if write_rows is not None:
            write_rows.append({
                "scenario": SCEN[scen],
                "year": f"FY20{year}",
                "rev_M": round(rev / 1000, 1),
                "yoy": round(rev / out[year - 1]["rev"] - 1, 4) if year > 25 else "",
                "gm_pct": round(out[year]["gm_pct"], 4),
                "sga_pct": round(sga / rev, 4),
                "op_pct": round(out[year]["op_pct"], 4),
                "ebitda_M": round(ebitda / 1000, 1),
                "ebitda_pct": round(ebitda / rev, 4),
                "ni_M": round(ni / 1000, 1),
                "eps": round(eps, 2),
                "fcf_M": round(fcf / 1000, 1),
            })

    # Valuation
    fy27_ebitda = out[27]["ebitda"] / 1000
    em = DRIVERS["exit_mult"][1][si]
    ev_27 = fy27_ebitda * em
    cash_27 = 197 + out[26]["fcf"] / 1000 + out[27]["fcf"] / 1000 - 15 - 15
    debt = 0
    eq_27 = ev_27 + cash_27 - debt
    sh_27 = DRIVERS["shares_M"][1][si]
    px_end_27 = eq_27 / sh_27
    wacc = DRIVERS["wacc"][1][si]
    px_12m = px_end_27 / (1 + wacc) ** 0.67
    out["valuation"] = {
        "fy27_ebitda_M": round(fy27_ebitda, 1),
        "exit_mult": em,
        "ev_27_M": round(ev_27, 1),
        "cash_27_M": round(cash_27, 1),
        "eq_27_M": round(eq_27, 1),
        "px_end_27": round(px_end_27, 2),
        "wacc": wacc,
        "px_12m": round(px_12m, 2),
    }
    return out


def main() -> None:
    rows = []
    print(f"{'Scenario':10}{'Year':10}{'Rev $M':>10}{'YoY':>8}{'GM%':>8}{'OpM%':>8}{'EBITDA$M':>10}{'EPS':>8}{'FCF$M':>9}")
    val_rows = []
    for s in [1, 2, 3]:
        out = run_scenario(s, write_rows=rows)
        for y in [25, 26, 27, 28]:
            o = out[y]
            yoy = (o['rev'] / out[y-1]['rev'] - 1) if y > 25 else 0
            print(f"{SCEN[s]:10}FY20{y:<6}{o['rev']/1000:>10.1f}{yoy*100:>7.1f}%{o['gm_pct']*100:>7.1f}%{o['op_pct']*100:>7.1f}%{o['ebitda']/1000:>10.1f}{o['eps']:>8.2f}{o['fcf']/1000:>9.1f}")
        v = out["valuation"]
        val_rows.append({"scenario": SCEN[s], **v})
        print(f"  -> 12m price target: ${v['px_12m']}  (FY27 EBITDA ${v['fy27_ebitda_M']}M x {v['exit_mult']}x = ${v['ev_27_M']}M EV)")
        print()

    out_path = REPO / "extracted" / "model_sanity.csv"
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out_path.relative_to(REPO).as_posix()}")
    out_val_path = REPO / "extracted" / "model_valuation.csv"
    with out_val_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(val_rows[0].keys()))
        w.writeheader()
        for r in val_rows:
            w.writerow(r)
    print(f"Wrote {out_val_path.relative_to(REPO).as_posix()}")


if __name__ == "__main__":
    main()
