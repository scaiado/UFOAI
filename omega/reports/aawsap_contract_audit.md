# The AAWSAP contract: bought, delivered, assessed

*Project Omega, session 4. §5 item 3. Three primary documents, on disk since
session 3, never compared. Script: `omega/aawsap_contract_audit.py`. Data:
`evidence_vault/01_PURSUE_PRIMARY/aawsap_contract_audit.json`.*

---

## The loop

| document | what it is |
|---|---|
| **D182** | AAWSAP Statement of Objectives, 18 July 2008, solicitation HHM402-08-R-0211. Names 12 technical areas and 5 deliverable classes. |
| **D111 / D112 / D113** | the order and modifications P00001/P00002 — the deliverables **priced**, as contract line items |
| **D117–D153** | the 37 delivered technical reports (DIRDs) |
| **D188** | "Review of Advanced Aerospace Contract Deliverables", INFO MEMO U-429-09/DWO, 30 Oct 2009, DIA Directorate for Analysis → **DIRECTOR, DIA**. States the delivery count and lists every title. |

What was bought, what arrived, and what the buyer said about it.

## 1. The contract line items are the Statement of Work, priced

The CLIN tables map one-to-one onto D182 §11's deliverables, and the line
"**Research Report for Tasks 3.a.1 – 3.a.12**" independently confirms the
twelve-area reading of D182 §3(a), whose own OCR is destroyed
(`2. propusia'1; 3.oontrof; 4. powerge,ea1b,,`).

**Base year, 22 Sep 2008 – 29 Sep 2009 (D111):**

| CLIN | item | amount | share |
|---|---|---|---|
| 0001 | Monthly Status Reports (qty 12) | $2,887,000 | 32.7% |
| 0002 | Project Management Plan for Tasks 3.a.1–3.a.12 | $3,600,000 | 40.8% |
| 0003 | Research Report for Tasks 3.a.1–3.a.12 | $2,100,000 | 23.8% |
| **0004** | **Comprehensive Integrated Threat Assessment** | **$240,000** | **2.7%** |

**Option year 1, 22 Sep 2009 – 21 Sep 2010 (D113, mod P00002):**

| CLIN | item | amount | share |
|---|---|---|---|
| 1001 | Monthly Status Reports (qty 12) | $1,549,100 | 16.4% |
| 1002 | Project Management Plan for Tasks 3.a.1–3.a.12 | $4,759,300 | 50.4% |
| 1003 | Research Report for Tasks 3.a.1–3.a.12 | $2,870,600 | 30.4% |
| **1004** | **Comprehensive Integrated Threat Assessment** | **$220,200** | **2.3%** |
| 1005 | Travel | $36,700 | 0.4% |

Two things fall out of the pricing itself.

**The 60-day overview papers cost more than the reports they preview.** CLIN
0002 ($3.60M) exceeds CLIN 0003 ($2.10M); in the option year CLIN 1002 ($4.76M)
is 1.66× CLIN 1003 ($2.87M) and the single largest item in the contract. The
*Project Management Plan* — defined in D182 §11(b) as, per technical area, "an
overview paper identifying the scope of the final report, a Plan of Action and
Milestones, and the composition of the analytical team" — was priced above the
comprehensive technical studies themselves.

**The deliverable that answers the contract's question is 2.7% of it.** The
objective in D182 §2 is "to understand the physics and engineering of these
applications *as they apply to the foreign threat* out to the far term". Only
CLIN 0004/1004 delivers a threat judgement. It is the smallest substantive line
in both years.

## 2. All 26 FY2009 deliverables are present — confirmed by the release's own identifiers

D188: *"The table in Enclosure 1 lists the 26 extensive technical reports
delivered to DIA in FY 2009."* The release holds 37 DIRDs, **D117–D142 being
exactly 26 of them**.

Reconciling Enclosure 1 against the release by title gives 14 exact matches, 4
strong retitles, and 8 pairs too weak to call on title alone — because DIA
retitled on publication (`Wormholes in Space Time` → `Traversable Wormholes,
Stargates, and Negative Energy`; `Vacuum Energy Applications` → `Concepts for
Extracting Energy from the Quantum Vacuum`).

Title matching cannot settle those, and a square 26×26 assignment matches
everything by construction, so the count proves nothing on its own. An
**independent identifier** settles it.

**The release pseudonymised authors consistently across documents.** D188's
Enclosure 1 gives an author per title as `MP Person NN`; each DIRD names its
author as `AAP Person NN`. The numbering is the same namespace, and it was
assigned by the releasing authority, not by me.

**Author ID agrees on 26 of 26. Zero disagreements. Zero missing.**

The three pairs title similarity could not resolve are resolved outright:

| DIRD | person | D188 title | released as |
|---|---|---|---|
| D121 | 64 | Pulse-Power-Based Weaponry | Pulsed High Power Microwave Source Technology |
| D132 | 57 | Space-Time Modifications for Spaceflight Applications | Advanced Space Propulsion Based on Vacuum (Spacetime Metric) Engineering |
| D119 | 65 | Novel MEMS-Based Biosensors | Biomaterials |

**Every FY2009 deliverable the government recorded as delivered is in the public
release.** At the research-report level there is no suppression to find. Reported
as a negative.

### A side observation on the pseudonymisation

Because the numbering is consistent across documents, the scheme permits
cross-document authorship linkage: Person 58 appears as author of D135, D139,
D142, D143 and D153 and as co-author of D138 — six documents, a coherent
thematic cluster. **I am not resolving any pseudonym to a person.** The
numbering was applied under the (b)(6) privacy exemption and defeating it is
not in scope. The structural point is that consistent pseudonymisation across a
multi-document release leaks an authorship graph the per-document redaction was
presumably meant to withhold.

## 3. The capstone deliverable is absent

**The Comprehensive Integrated Threat Assessment does not exist in the release.**

- D182 §11(d) requires "a final report and briefing that assesses the foreign
  threat from advanced aerospace [platforms] incorporating the technologies
  discussed in the individual research reports … at the end of the period of
  performance", plus an executive version.
- It carries its own CLIN and its own money in both years: **0004 at $240,000
  and 1004 at $220,200 — $460,200 contracted.**
- A corpus-wide search for `integrated threat assessment` returns **4 hits, all
  of them in the contract documents themselves** (D111, D112, D113). There is
  no such report, no briefing, and not one reference to it in any other
  document — D188 included.
- D188 reviews only the 26 research reports. The memo to the DIRECTOR, DIA
  assessing contract deliverables **does not mention the capstone deliverable at
  all.**

This is the most specific checkable gap found since the `DOW-UAP-D66`–`D73`
block, and it is nameable in a request: a deliverable identified by CLIN, priced,
with a defined period of performance, in a release that contains all 37 of the
subsidiary reports it was supposed to integrate.

### The trigger for it was reached

D182 §11(d) ties the capstone to "the end of the period of performance". That
end is documented. **D116, modification P00005, 28 September 2010:** *"Pursuant
to FAR clause 52.217-8 Option to Extend Services, this contract is extended from
09/22/2010 TO 12/21/2010."*

So the period of performance ended **21 December 2010** — and D150/D151 (Dec
2010) and D152/D153 (Jan 2011) were published either side of that boundary. The
condition that obliges the final assessment was met, and the two later DIRDs show
work continuing up to it.

**A gap is still a gap, not a suppression.** It may have been produced and
withheld, produced and classified above the release's threshold, or never
produced. Nothing here distinguishes those. What is established is that it was
contracted, priced twice, its due condition occurred, and it is absent.

### The contract ran two of its five anticipated years

D182 anticipated "a base year of 12 months from date of award plus four (4) 12
month option years", the solicitation stating a term "from September 29, 2008
through September 30, 2013". What actually ran:

| period | instrument | through |
|---|---|---|
| base year | D111, original order | 21 Sep 2009 |
| option year 1 | D112/D113, P00001/P00002 | 21 Sep 2010 |
| 3-month extension | **D116, P00005, FAR 52.217-8** | **21 Dec 2010** |

FAR 52.217-8 is the short-term *Option to Extend Services* clause, not an option
year. Option years 2–4 were never exercised. **The five-year program was ended
after roughly 2.25 years**, three months past its first option year.

## 4. What was released is DIA's published version, not the contractor's

Every one of the 26 bears a date **after** the fiscal year in which D188 says it
was delivered: D117/D118 at 14 Dec 2009, the bulk in March 2010, the last on 6
April 2010 — and D188 itself is dated 30 Oct 2009, six weeks before the earliest.

This is not a contradiction. It is the delivery/publication distinction, and the
documents carry the evidence: each is a *Defense Intelligence Reference Document*
stamped `ICOD: 1 December 2009` (intelligence cut-off date) over a DIA control
number (`DIA-08-1003-015`), and D188 states "DWO intends to publish them in
coming weeks as Defense Intelligence Studies."

So the chain is: BAASS delivers in FY2009 → DWO reviews, Oct 2009 → **DIA
re-publishes as DIRDs, Dec 2009–Apr 2010** → that published version is what the
2026 release contains.

**Consequence: the contractor's as-delivered research reports have not been
released.** What is public is DIA's re-titled, re-formatted publication of them,
under DIA control numbers and a DIA intelligence cut-off date. The as-submitted
BAASS versions, and the executive summaries D182 §11(c) required with each
report, are a distinct body of material.

This applies to the research reports specifically. BAASS-authored documents *are*
present elsewhere in the release — `D168` Project Management Plan, `D169`–`D173`
monthly reports, `D172` the Ten Month Report, `D175` a November 2010
self-assessment of UAP analysis capabilities — so the release is not uniformly
DIA-mediated. It is the CLIN 1003 technical studies that appear only in DIA's
published form.

## 5. Delivery timing against the contract

D182 §11(c) requires each research report "by the end of the tenth month". With
award on 22 Sep 2008, month ten ends ~22 July 2009. D188, on 30 Oct 2009, treats
the reports as delivered within FY2009 and offers no complaint about lateness, so
contractor delivery was evidently near or within terms; only DIA's publication
ran later.

The option-year wave is different. D188 states "Deliverables are expected in late
summer 2010." The 11 FY2010 reports are dated **1 Nov 2010 – 11 Jan 2011** —
D143–D149 on 1–21 Nov 2010, D150/D151 in Dec 2010, D152/D153 in Jan 2011. On
publication dates, that is one to five months past the stated expectation.

## 6. Other factual findings from D188

- **Year one was unclassified only** — "within the limitation of being able to
  conduct only unclassified research in the first contract year", though D182 §5
  permitted TS/SCI.
- **Reviews were independent in part**: of the 26, 8 were reviewed by other
  authors in the table, 5 by outside reviewers "including three research staff
  members at **Sandia National Laboratories**".
- **All reviews positive**, "some exceptionally so"; "the quality hoped for in the
  reports was achieved".
- **Option year 1 was to be funded at $12 million** per draft congressional
  budget guidance — against $9,435,900 in listed CLINs.
- **FY2010 intent**: have BAASS "evaluate potential adversary exploitation
  worldwide, select studies amenable to **classified experimental verification by
  BAASS**, and conduct new classified and unclassified studies with select
  academic and industry partners."
- DWO intended to circulate the studies to "Defense Department agencies, national
  laboratories, and/or defense industries focused on **blue-force capability
  development**" — i.e. the output was routed to US capability development, not
  only to threat analysis.

## 7. Coverage of the 12 contracted areas — reported weakly, on purpose

Every one of the 11 named areas has at least one plainly on-topic deliverable
(lift → D143, D149; human effects → D128; signature reduction → D122, D148;
armament → D121, D137; human interface → D130, D144).

**The per-area counts in the JSON are not trustworthy and should not be quoted.**
Assigning 37 titles to 12 areas by keyword lets one report land in several areas
— the "power generation" regex collects the laser and wormhole reports — so the
counts are inflated. The defensible statement is the qualitative one: no
contracted area went undelivered. A clean assignment needs one area per report,
read from each document's own framing, which is a larger job than this audit.

## 8. FOIA targets this produces (drafted, not filed)

1. **The Comprehensive Integrated Threat Assessment**, CLIN 0004 (base year) and
   CLIN 1004 (option year 1), contract HHM402-08-C-0072 — the final report and
   briefing required by SOO §11(d), plus its executive version. Name the CLINs.
2. **The as-delivered BAASS versions** of the 26 FY2009 and 11 FY2010 reports,
   as distinct from the DIA-published DIRDs, plus the **executive summaries**
   required by §11(c).
3. **The per-area Project Management Plans** under CLIN 0002/1002 — the single
   largest line item in the contract at $8.36M across the two years. D182 §11(b)
   requires, *for each technical area*, a 60-day overview paper giving the scope
   of the final report, a POA&M and the analytical team's composition — 12 per
   year, so ~24 documents. The release contains **one** consolidated
   `D168 BAASS Project Management Plan, December 2008`. Request the per-area
   papers.
4. **The monthly status reports** under CLIN 0001/1001 — $4.44M for 24 reports
   (12 per year). The release contains **four**: `D169` March 2009, `D170` April
   2009, `D171` June 2009, `D173` November 2009. Request the remaining ~20,
   naming the months.
5. **The Sandia National Laboratories reviews** named in D188 Enclosure 2.
