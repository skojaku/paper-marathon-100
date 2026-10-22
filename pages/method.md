---
title: Method
---
# How the paper list was made

The list is a *screening* of recent conference papers, not a hand-picked canon. It is meant to be a good place to look for papers, not a ranking. Every step below is automated and imperfect; the notes on reliability at the end say how much.

## 1. Venues and years

14 venues, 2023–2026: ACL, EMNLP, NAACL, EACL (including Findings), AAAI, IJCAI, AAMAS, NeurIPS, ICLR, ICML, KDD, WWW, CHI and CSCW. The list of every paper in these venues came from the DBLP bibliography dump, which gave 93,925 titles.

## 2. Abstracts

Abstracts were collected per paper from OpenAlex (by DOI), the official proceedings pages of NeurIPS, ICLR and PMLR, and the ACL Anthology. 81,519 papers had an abstract of at least 250 characters; the rest could not be screened by abstract.

## 3. Screening by abstract

A language model (Gemini 3.8 Flash) read every abstract and answered *yes*, *maybe* or *no* to "does this paper study a system of several LLM agents?", with the instruction to answer *maybe* when unsure. About 4% of papers passed. On 1,500 papers that a stronger model (Gemini 4 Argon) also judged, the screener found 99% of the stronger model's *yes* papers (as yes or maybe) and agreed with it at Cohen's kappa 0.87. Result: **3,776 candidates**.

## 4. Classification from the full text

Full texts were fetched from arXiv or open-access copies where possible. For the 3,461 candidates that were fetched, Gemini 4 Argon read the full text and coded each paper with a codebook (version 0.8, still a draft) that asks:

- **Eligible?** Is it really a system of several LLM agents at inference time (not a single model, and not agents used only to create training data)? **2,552 papers** are eligible and form the paper list on this site.
- **Purpose:** task solving, behavioral study, simulation, other.
- **Relation:** cooperative, competitive or mixed-motive.
- **Structure:** *pipeline* (outputs flow one way), *interactive* (agents respond to one another), *integration* (outputs are combined) or *comprehensive*.
- **Tags:** design and social constructs the paper deals with, e.g. roles and specialization, communication topology, aggregation rule, persuasion, trust, deception. Every tag is backed by a quote from the paper that was checked mechanically against the full text.

## How far to trust the tags

In an audit of an earlier codebook version (v0.6), a second model (Claude Opus) coded 36 papers independently and then graded the tags. Agreement on *eligible* was kappa 0.82; about two thirds of the tags it graded were judged correct, and the model tended to add too many tags rather than miss them. The structure label was the weakest (kappa about 0.6) because the codebook's own rules for pipeline versus interactive conflict in places. Treat tags as a way to *find* papers, and check the abstract before relying on one.

About 5% of the listed papers have no abstract on this site because none could be retrieved; their tags come from the full text.

## Weekly pages

Each week's page records the papers read, a summary of each, what we learned, and the questions we raised. Papers outside this list are welcome and are written up in the same way.
