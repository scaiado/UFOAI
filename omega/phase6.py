"""PROJECT OMEGA - Phase 6: the behavioural-intelligence hypothesis, 7 tests.

THE CONTROLLING CONFOUND. A verbose, detailed report receives more attribute
codes than a terse one. Any observer class that writes detailed reports will
therefore co-occur with more behaviour codes from verbosity alone. Every null
in this phase is permuted WITHIN CODE-COUNT STRATA so that the number of codes
per event is held fixed. An unstratified version is reported alongside, to show
how much of each effect is verbosity.

CODE PROVENANCE. Hatch's taxonomy mixes observations (LND landing, SUB
submerges, VEH vehicle affected, RDR radar, TRC traces) with INTERPRETATIONS
(PRB 'possibly remote controlled', CMF 'camouflage/disguise', TLP telepathy,
SIG 'signals/responses'). The interpretive codes are one compiler's
adjudications of intent, so a test built on them measures his coding process.
They are tested separately and labelled.
"""
from __future__ import annotations
import sys, re, json, math, collections
import numpy as np
from scipy import stats
sys.path.insert(0, "/home/user/UFOAI/omega")
import corpus

RNG = np.random.default_rng(606060)
NPERM = 4000

OBSERVER = {"MIL": "military observer", "CIV": "civilian", "AIR": "on aircraft",
            "SEA": "at sea", "GND": "on ground", "RDR": "radar", "SCI": "scientist",
            "HQO": "high-quality observer", "OGA": "government agency",
            "CST": "coastal"}
ACTION   = {"OBS": "chasing/pursuit", "PHT": "photographed", "SIG": "signal exchange",
            "CVS": "conversation"}
BEHAV_OBS = {"LND": "landed", "SUB": "submerged/emerged", "VEH": "vehicle affected",
             "EME": "EM effects", "RAY": "beam emitted", "SND": "sound",
             "TRC": "physical trace", "VEG": "plants affected", "ANI": "animals affected",
             "HUM": "humans affected", "SMP": "sampling", "MST": "missing time"}
BEHAV_INT = {"PRB": "probe/remote-controlled [INTERPRETIVE]",
             "CMF": "camouflage/disguise [INTERPRETIVE]",
             "SIG": "signals/responses [INTERPRETIVE]",
             "TLP": "telepathy [INTERPRETIVE]",
             "CVS": "conversation [INTERPRETIVE]",
             "ABD": "abduction", "OPR": "operations on humans"}
# kinematic vs shape codes, for Test 5
SHAPE = ["SCR", "CIG", "DLT", "NLT", "FBL", "OID", "PSH", "MON", "GNT", "RBT"]
KINEM_TXT = {
 "k_hover": r"\bhover|stationar|motionless|suspend",
 "k_fast": r"\bquickly|high speed|very fast|tremendous|shoots?\s+(away|up)|speeds?\s+off",
 "k_erratic": r"\bzig-?zag|erratic|dart|jerk|bob(s|bing|bed)?\b|wobbl|oscillat",
 "k_rotate": r"\brotat|spin|revolv|whirl",
 "k_ascend": r"\bgoing up|rises|ascend|climb|shot upward",
 "k_descend": r"\bgoing down|descend|drops|lowers|settles",
 "k_pace": r"\bpace[sd]?|parallel|follow|chase|escort|accompan",
 "k_turn": r"\bturns?\b|right.?angle|90|sharp turn|arcs?\b|curves?\b|veers?",
 "k_split": r"\bsplit|divid|separat|exits?\b|drops? smaller|ejects?",
 "k_vanish": r"\bvanish|disappear|blinks? out|winks? out",
}
KRX = {k: re.compile(v, re.I) for k, v in KINEM_TXT.items()}

def load():
    recs, ner = corpus.load_all()
    H = [r for r in recs if r.catalog == "Hatch_UDB"]
    nerkey = {}
    for (src, sid), v in ner.items(): nerkey[sid] = v
    rows = []
    for r in H:
        codes = set(r.attrs)
        kin = {k for k, rx in KRX.items() if rx.search(r.desc or "")}
        rows.append(dict(uid=r.uid, year=r.year, codes=codes, kin=kin,
                         cred=r.credibility, ncodes=len(codes),
                         nchar=len(r.desc or ""), desc=r.desc,
                         lat=r.lat, lon=r.lon, month=r.month, day=r.day))
    return rows

def strata(rows, nbins=6):
    nc = np.array([r["ncodes"] for r in rows])
    q = np.quantile(nc, np.linspace(0, 1, nbins + 1))
    q[0] -= 1
    s = np.digitize(nc, q[1:-1])
    return s

def perm_within(labels, s):
    out = labels.copy()
    for g in np.unique(s):
        idx = np.flatnonzero(s == g)
        out[idx] = labels[idx][RNG.permutation(idx.size)]
    return out

def cramers_v(tab):
    chi2, p, dof, _ = stats.chi2_contingency(tab)
    n = tab.sum()
    return math.sqrt(chi2 / (n * (min(tab.shape) - 1))), chi2, p, dof

def mi_bits(x, y):
    n = len(x); mi = 0.0
    for a in (0, 1):
        for b in (0, 1):
            pab = ((x == a) & (y == b)).mean()
            pa, pb = (x == a).mean(), (y == b).mean()
            if pab > 0 and pa > 0 and pb > 0: mi += pab * math.log2(pab / (pa * pb))
    return mi

def perm_assoc(x, y, s, nperm=NPERM):
    """Association between binary x and binary y, null = permute y within strata."""
    obs = mi_bits(x, y)
    a = int(((x == 1) & (y == 1)).sum()); b = int(((x == 1) & (y == 0)).sum())
    c = int(((x == 0) & (y == 1)).sum()); d = int(((x == 0) & (y == 0)).sum())
    orat = (a * d) / max(1, b * c)
    null = np.empty(nperm)
    for i in range(nperm):
        null[i] = mi_bits(x, perm_within(y, s))
    p = (1 + int((null >= obs).sum())) / (nperm + 1)
    return dict(mi=obs, null_mi=float(null.mean()), p=p, odds=orat,
                a=a, b=b, c=c, d=d)
