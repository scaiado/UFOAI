# CADA request — undisclosed GEIPAN class-D dossiers

**STATUS: DRAFTED, NOT FILED.** Per the standing constraints. Nothing here has
been sent. Article references are given as drafted and **require verification
by whoever files**; CRPA numbering has changed since the 1978 loi it replaced.

## Why this request has a measured basis

GEIPAN publishes the primary dossier for **94%** of its explained cases (A+B
document-attachment 0.9794) but only **45%** of the cases it classifies as
unexplained-despite-adequate-information (D, 0.4528); z = −25.83, and the gap
survives within-era stratification (§1.3).

Within class D, non-disclosure is almost perfectly predicted by one flag:

| | `Cas revisité` = Oui | = Non | total |
|---|---|---|---|
| dossier published | 8 | 42 | 50 |
| **no dossier published** | **55** | **1** | **56** |

z = +8.605; Mantel-Haenszel OR stratified by decade = 209.10
(`omega/geipan_revisit_disclosure.py`).

**The argument for the request:** the privacy exception (CRPA L311-6) is a
lawful ground for withholding witness identity, and it plainly applies to
parts of these files. But **witness privacy does not depend on whether a case
was explained.** A privacy rationale predicts a disclosure rate roughly
constant across A, B, C and D. The observed rate is not: it is 0.9794 for A+B
and 0.4528 for D, concentrated in the re-examined subset. Whatever is driving
that pattern, it is not the privacy of witnesses — so **L311-7 partial access
by occultation should reach these files.**

The request therefore asks for **redacted** dossiers from the outset. That
concedes the privacy interest in full and removes the obvious refusal ground.

## Procedure

1. Send request 1 to CNES (GEIPAN's parent). 
2. Silence for **one month** is an implicit refusal (CRPA L311-2 / R311-12).
3. CADA may then be seized within **two months** of the refusal (CRPA R343-1).
4. CADA issues an advisory opinion; it does not compel.

---

## Letter 1 — initial request to CNES / GEIPAN

> **Objet : Demande de communication de documents administratifs — dossiers
> GEIPAN de classification D (CRPA, art. L300-1 et suivants)**
>
> Madame, Monsieur,
>
> Dans le cadre de travaux de recherche académique non commerciaux portant sur
> les archives publiques relatives aux phénomènes aérospatiaux non identifiés,
> je sollicite, au titre du droit d'accès aux documents administratifs (code
> des relations entre le public et l'administration, art. L311-1), la
> communication des dossiers d'enquête correspondant aux **56 cas de
> classification D** dont la liste d'identifiants figure en annexe.
>
> Ces 56 cas sont, à la date de la présente demande, les cas classés D pour
> lesquels aucune pièce n'est publiée sur le site du GEIPAN, alors que
> l'ensemble de la base publie des pièces pour la grande majorité des cas
> classés A et B.
>
> Pour chacun de ces cas, je sollicite la communication :
>
> 1. des **procès-verbaux de gendarmerie** et comptes rendus d'enquête ;
> 2. des **questionnaires de témoignage** renseignés ;
> 3. des **rapports d'analyse** technique ou scientifique éventuels ;
> 4. de la **fiche de synthèse** et, le cas échéant, des pièces relatives au
>    **réexamen** du cas (le champ « Cas revisité » de l'export public
>    indiquant « Oui » pour 55 des 56 cas visés).
>
> **Je sollicite expressément la communication de versions occultées**, en
> application de l'article L311-7, de sorte que soient retirés les noms,
> adresses, coordonnées et toute mention permettant l'identification des
> témoins ou des tiers. La présente demande **ne porte pas sur des données à
> caractère personnel** et ne vise que le contenu factuel et technique des
> dossiers : description de l'observation, conditions d'observation, mesures,
> analyses et conclusions.
>
> Je sollicite une communication par voie électronique (art. L311-9), au
> format PDF, à l'adresse indiquée ci-dessous.
>
> Si certaines pièces ne pouvaient être communiquées même après occultation,
> je vous remercie de bien vouloir **préciser, pour chaque pièce, le fondement
> juridique du refus**, et de communiquer les pièces restantes.
>
> Je vous rappelle qu'à défaut de réponse dans le délai d'un mois, le silence
> gardé vaut décision de refus (art. L311-2), susceptible d'être soumise à
> l'avis de la Commission d'accès aux documents administratifs.
>
> Je vous prie d'agréer, Madame, Monsieur, l'expression de ma considération
> distinguée.
>
> **Annexe :** liste des 56 identifiants de cas
> (`data/processed/geipan/cada_targets.json` — identifiant, date
> d'observation, département, région).

---

## Letter 2 — saisine of CADA, if refused or after one month's silence

> **Objet : Saisine pour avis — refus de communication de dossiers d'enquête
> GEIPAN (CNES)**
>
> Commission d'accès aux documents administratifs
> TSA 50730 — 75334 PARIS CEDEX 07
>
> Madame, Monsieur,
>
> Par courrier du [DATE], j'ai sollicité du Centre national d'études
> spatiales la communication, en versions occultées, des dossiers d'enquête
> correspondant à 56 cas de classification D du GEIPAN (copie en annexe 1).
>
> [**Variante A — refus exprès :** Par décision du [DATE], le CNES a refusé
> cette communication au motif de [MOTIF] (copie en annexe 2).]
>
> [**Variante B — refus implicite :** Aucune réponse ne m'étant parvenue dans
> le délai d'un mois, un refus implicite est né le [DATE] en application de
> l'article L311-2 du CRPA.]
>
> Je sollicite l'avis de la Commission sur le caractère communicable de ces
> documents, en soulignant les éléments suivants.
>
> **1. Les documents sollicités sont des documents administratifs.** Il s'agit
> de pièces produites ou reçues par un établissement public dans le cadre de
> sa mission de service public (art. L300-2), dont le GEIPAN publie
> habituellement des pièces équivalentes pour d'autres cas de la même base.
>
> **2. La demande ne porte pas sur des données personnelles.** Elle sollicite
> d'emblée des versions occultées au sens de l'article L311-7. L'intérêt des
> témoins à la protection de leur identité est donc intégralement préservé.
>
> **3. L'occultation est praticable, puisqu'elle est déjà pratiquée.** Le
> GEIPAN publie des procès-verbaux de gendarmerie occultés pour un grand
> nombre de cas de sa base. La demande ne requiert donc aucun traitement
> nouveau ni charge disproportionnée.
>
> **4. Le motif tiré de la vie privée n'explique pas la répartition
> observée.** Sur l'ensemble de la base publique, des pièces sont publiées
> pour environ 97,9 % des cas classés A ou B, contre 45,3 % des cas classés D.
> Or la protection de la vie privée d'un témoin ne dépend pas de ce que
> l'observation a, ou n'a pas, reçu une explication. Au sein même de la classe
> D, l'absence de pièces publiées coïncide presque exactement avec le réexamen
> du cas : 55 des 56 cas sans pièce publiée portent la mention « Cas
> revisité : Oui », contre 8 des 50 cas avec pièces. Cette répartition ne
> paraît pas explicable par les exceptions de l'article L311-6.
>
> Je me tiens à la disposition de la Commission pour tout élément
> complémentaire.
>
> **Annexes :** 1. demande initiale et liste des 56 identifiants —
> 2. décision de refus, le cas échéant — 3. note méthodologique sur les
> taux de publication par classification.

---

## English gloss of the substantive argument

The request asks CNES for the investigation files of the 56 class-D cases that
currently have no published document, **in redacted form from the outset**,
citing partial access by occultation. It concedes witness privacy entirely and
asks only for factual and technical content.

If refused, the CADA submission makes four points: the files are
administrative documents; the request seeks no personal data; redaction is
already routine practice for GEIPAN on comparable files, so no disproportionate
burden arises; and the privacy exception does not account for the observed
pattern, because privacy cannot depend on whether a sighting was explained —
yet publication runs at 97.9% for explained cases against 45.3% for the
unexplained ones, with the gap concentrated almost entirely in the re-examined
subset.

**Caveat to carry:** the re-examination association is directional-ambiguous
(see `omega/reports/geipan_revisit_disclosure.md`). "Cases are reopened
*because* the file is thin" fits the data as well as "reopening withholds the
file." The letter states the association as an association and asks CADA to
assess communicability — it does not assert a motive, and should not be
rewritten to do so.
