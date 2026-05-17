---
name: surveying-related-work
description: Searches and synthesizes related work for a user-specified AI research topic, project, claim, or seed paper set, then reports candidate papers and thematic clusters to the user without downloading, saving, or invoking arXiv TeX source ingestion. Use when the user asks for literature research, related work discovery, paper recommendations, or a survey before deciding what to read deeply.
---

# Surveying Related Work

This skill performs lightweight related-work discovery and synthesis. It searches for
papers, groups them by theme, identifies likely direct competitors and background work,
and reports the results to the user for review.

This skill deliberately does not download or save arXiv TeX source files. It is a survey
and triage skill, not a paper-ingestion skill.

## Hard Boundaries

- Do not call or delegate to `ingesting-arxiv-source`.
- Do not download arXiv source archives.
- Do not create `paper/<arxiv_id>/` dossiers.
- Do not save TeX source, PDFs, or extracted paper folders.
- Do not draft a final related work section before the user confirms the paper set.
- Do not invent citations, venues, years, or paper claims.
- Do not claim exhaustive coverage unless the search strategy actually supports it.

It is acceptable to return links, arXiv IDs, DOI links, Semantic Scholar URLs, and short
summaries in the chat. It is also acceptable to write a short survey note if the user
explicitly asks for a file, but the default output is a message to the user.

## Inputs

Work from any combination of:

- research topic or question;
- current project description;
- target venue;
- seed paper titles, URLs, arXiv IDs, or BibTeX entries;
- methods, datasets, tasks, or baselines the user cares about;
- exclusion criteria, such as "do not include RAG papers" or "focus after 2023".

If the request is underspecified, still start with a reasonable search plan. Ask at most
one clarifying question only when the topic is too broad to search productively.

## Search Sources

Prefer primary and scholarly sources:

- Semantic Scholar for AI/ML paper search, abstracts, references, and citations.
- arXiv search for recent preprints and arXiv IDs.
- OpenReview for ICLR, NeurIPS, and other review-context papers when relevant.
- ACL Anthology for NLP papers.
- DBLP for venue/year metadata.
- CrossRef for DOI metadata.
- Official project pages only when paper metadata needs confirmation.

Avoid relying on blog posts, social media, or uncited secondary summaries unless the user
specifically asks for community context.

## Workflow

### Step 1: Restate the Search Scope

Briefly identify:

- the user's core topic;
- any seed papers;
- constraints such as year, venue, domain, or method family;
- what counts as "related" for this request.

Do this internally or in a short progress note. Do not spend a turn asking for permission
unless the scope is genuinely ambiguous.

### Step 2: Generate Search Queries

Create several query families:

```text
<core method> <task>
<problem phrase> machine learning
<seed paper title> citations
<baseline method> comparison
<dataset/benchmark> <method family>
<key limitation> <target domain>
```

Use both broad and narrow queries. If the user provided seed papers, search:

- papers cited by each seed paper;
- papers that cite each seed paper;
- papers sharing authors, keywords, datasets, or baselines.

### Step 3: Search and Verify

For each candidate paper, verify at least the basic metadata:

- title;
- authors;
- year;
- venue or arXiv status;
- URL or DOI/arXiv ID;
- why it is related.

When possible, confirm using two sources, such as Semantic Scholar plus arXiv, DBLP,
OpenReview, ACL Anthology, or CrossRef.

If metadata is uncertain, label it clearly:

```text
Venue: Unknown / needs verification
Claim: Needs verification from full text
```

### Step 4: Classify the Papers

Group papers by research role, not by search order:

- **Direct competitors**: solve the same problem with comparable assumptions.
- **Foundational background**: define methods, architectures, datasets, or theory.
- **Adjacent methods**: solve nearby problems or use transferable techniques.
- **Evaluation and benchmark work**: provides datasets, metrics, or protocols.
- **Negative or limitation evidence**: shows failures, boundaries, or open issues.
- **Recent follow-ups**: newer papers extending or challenging seed papers.

Within each group, identify the 2-5 most important papers first.

### Step 5: Report to the User

Default output should be a concise survey report in the chat:

```markdown
## Search Scope
<one paragraph>

## High-Priority Papers
| Paper | Year | Why it matters | Link |
|---|---:|---|---|

## Related Work Clusters
### <Cluster name>
- <paper>: <one-sentence relevance>

## Likely Direct Competitors
- <paper>: <why it competes with the user's project>

## Gaps and Follow-Up Search Directions
- <missing angle or unresolved question>

## Suggested Next Papers to Read Deeply
1. <paper>
2. <paper>
3. <paper>
```

Do not download or save TeX source in this step. If the user later chooses specific arXiv
IDs for deep reading, they can explicitly ask to use `ingesting-arxiv-source`.

## User-Controlled Handoff

End with a clear handoff option, but do not perform it automatically:

```text
If you want, choose the arXiv IDs you want to inspect deeply, and then use the arXiv
source ingestion workflow on those exact IDs.
```

Do not automatically select papers and ingest them.

## Quality Criteria

A good survey report:

- separates direct competitors from broad background;
- states why each paper matters for the user's project;
- includes links or identifiers for follow-up;
- marks uncertain metadata instead of guessing;
- highlights missing evidence and likely blind spots;
- avoids overwhelming the user with dozens of weakly related papers.

## Handling Seed Papers

When the user provides seed papers:

1. Treat them as high-confidence anchors.
2. Search backward citations to recover intellectual lineage.
3. Search forward citations to find newer related work.
4. Search for shared datasets, baselines, and keywords.
5. Explain whether each discovered paper is a competitor, precursor, extension, or tool.

Do not assume the seed papers are correct or sufficient. Tell the user if the seed set
appears narrow, outdated, or missing an obvious line of work.

## Handling Target Venues

If the user targets A-level AI conferences, prioritize:

- NeurIPS, ICML, ICLR, ACL, EMNLP, AAAI, COLM, CVPR, ICCV, ECCV, KDD, SIGIR, WWW, and
  other venue-specific top conferences relevant to the topic;
- recent OpenReview discussions when available;
- accepted papers and strong preprints that shaped the area.

Do not overfit to venue prestige. A workshop or arXiv paper may be important if it is the
closest technical predecessor.

## What Not to Do

Do not write:

```text
I downloaded the sources for the top papers...
```

Do not create:

```text
paper/2510.10125/
paper/<any_arxiv_id>/source/
```

Do not run:

```bash
curl https://arxiv.org/src/<id>
python .../fetch_arxiv_source.py <id>
```

The boundary is intentional: survey first, let the user decide which papers deserve deep
local ingestion.
