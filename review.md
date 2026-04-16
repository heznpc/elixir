# elixir — Review (2026-04-11)

## 1. 커밋 톤이 주장을 일관되게 지지하는가?

**판정: 평가 불가 (commit 1개) — 그러나 단일 commit의 *내부 정합성*은 매우 높음.**

```
ec4523d init: The Elixir Problem — systematic review of hoarding behaviors in digital games  (2026-04-07)
```

- **단 1 commit, 25 files, 7,150 insertions** — 외부에서 *완성도 높은* PRISMA systematic review가 한 번에 들어옴.
- 약점: aichemist/babel과 같은 패턴. *진화 과정*이 git에 없다. PRISMA 1차 → 2차 query 개선 결정이 commit history에 보이지 않음 (v1, v2 파일 양쪽 보존됨으로 *간접 추적*만 가능).
- 강점: 단일 스냅샷이지만 *PRISMA 2020 표준 준수*가 매우 깔끔. 두 query (broad + targeted) → 227 unique records → 156 eligible. 이 워크플로 자체가 학술 표준.
- 5개 domain(D1-D6) 매핑이 README → CLAUDE → manuscript → outline → main.tex 모두에서 동일.
- 자기 비판: D2(consumable hoarding, "elixir problem") + D6(backlog accumulation)이 *evidence void*임을 abstract와 §1에서 *대놓고* 명시. 자신의 paper title이 가리키는 그 현상이 *peer-reviewed evidence가 0편*이라는 것을 첫 페이지에서 인정. 이는 매우 정직한 framing.
- *PRIMARY (D3/D4/D5)와 EXPLORATORY (D2/D6) 구분*: 6 over-pathologization risks 형식적으로 list. **dimensional perspective + categorical 거부** 명시: "this paper does not argue that in-game hoarding-related behavior constitutes hoarding disorder."

## 2. 부가 서비스 품질

**판정: 부가 서비스 = PRISMA 자동화 파이프라인. 본 survey 21개 paper 중 *학술 자동화* TOP.**

서비스 1: **`experiments/prisma_search_v2.py` (737줄)**
- 표준 라이브러리만 (no requests/biopython). NCBI Entrez E-utilities 직접 호출.
- Dual-query 전략: broad (game terms × hoarding terms) + targeted (gacha/loot box × gambling/addiction).
- Rate limiting, deduplication, CSV export.
- v1 (542줄)도 보존 (reproducibility).

서비스 2: **`experiments/screening_v2.py` (1,201줄)**
- 자동 title/abstract screening. Include / Maybe / Exclude 분류 heuristics.
- 156 eligible 결정이 *코드로* 재현 가능.
- 도메인 자동 매핑(D1-D6).

서비스 3: **결과물 8개 markdown**
- domain_counts_v2.md, prisma_flow_v2.md, evidence_synthesis.md (452줄), top_papers_v2.md (352줄), screening_summary.md (119줄), search_comparison.md (42줄), search_log.md (56줄)
- PRISMA flow diagram, 도메인별 paper count, top 10 papers per domain, screening 결정 로그.

서비스 4: **CSV 데이터셋**
- pubmed_results.csv (501 rows), pubmed_results_v2.csv (227 rows), screening_results.csv (227 rows)
- 즉시 *secondary analysis 가능*한 raw data.

서비스 5: **`pyproject.toml` + `requirements.txt`**: 패키지 설정. 표준 lib only이므로 사실상 dependency 없음.

서비스 6: **`.zenodo.json`**: DOI minting 준비.

품질 평가:
- *PRISMA 2020 + 자동화 코드 + 결과 데이터 + manuscript + LaTeX*가 한 monorepo에서 일치. 학술 systematic review의 *가장 reproducible한 형태*.
- 본 survey 21개 중 caching과 함께 **claim ↔ code 일치도 가장 높음**. README의 "227 records, 156 eligible, D2/D6 zero evidence"가 *코드 재실행으로 검증 가능*.
- LaTeX 컴파일 검증 (main.pdf 299KB).
- 한계: 수동 screening (2nd reviewer, Cohen's kappa)이 없음. 자동 screening만으로는 PRISMA 표준에서 약함.

## 3. 고도화 가능 파트

높은 우선순위:
1. **2nd reviewer + Cohen's kappa** — PRISMA 표준은 *2명 독립 screener + 일치도*. 현재는 자동 heuristic 1번. 본인 + 1명 친구/공동저자가 random 50개 sample을 수동 screen → kappa 보고 → automated screen의 sensitivity/specificity 검증. **이게 빠지면 reviewer가 reject 가능**.
2. **PROSPERO pre-registration** — paper가 명시하는데 실제 등록은 안 된 듯. PROSPERO 등록 후 제출.
3. **PubMed only → PsycINFO + Scopus + Web of Science 추가** — peer-reviewed systematic review는 보통 4-6 database. PubMed only는 약점. 게임 연구는 ACM DL/IEEE Xplore도 중요.
4. **Game Hoarding Inventory 초안** — abstract가 명시. paper §결론에 핵심 contribution으로 약속하지만 실제 척도 문항 없음. caching repo의 TSI처럼 12-15 문항 초안 + content validity 패널.
5. **D2/D6 evidence void에 대한 후속 empirical study 제안** — paper의 가장 큰 finding이 *2개 도메인 evidence가 0편*이라는 것. 이를 future work로 *공식 제안*하고 *예비 데이터*(예: r/JRPG 카테고리에서 elixir hoarding self-report 100명)를 수집하면 evidence void에 대한 *first contribution*.

중간 우선순위:
6. **Frost-Hartl CBT 모델 적용표** — paper가 주장만 하는데, DSM-5 hoarding criteria 4개 × 5개 도메인의 *형식적 매핑 매트릭스*가 1쪽 표로 들어가면 reviewer 호감도 +1.
7. **Cross-cultural evidence 강화** — 한국/일본 게임 문화의 elixir hoarding(*rasuto erikusaa shoukougun*, *mottainai*)을 paper가 인용하는데 *영어 학술 데이터베이스에는 없는 것*이 evidence void의 한 원인. 한국어/일본어 학술 검색을 보조로 추가하면 D2 void 부분 보강.
8. **Gacha 97편 paper의 sub-classification** — 97편이 D3에 몰려 있는데 sub-cluster 분석 (LDA topic model)이 없음. 1쪽 figure로 reviewer 가독성 향상.
9. **Manuscript ↔ main.tex 동기화 검증** — 둘 다 진화하는 중인지, manuscript.md가 main.tex의 markdown export인지 명확화.

낮은 우선순위:
10. ASReview 또는 Rayyan 같은 PRISMA 도구와의 호환성 (XML export).
11. PRISMA-S (search reporting) 체크리스트 별첨.
12. CC BY 4.0 + Zenodo DOI 자동 발급.

## 4. 학술적 / 시장 가치 (글로벌, 2026-04-11 기준)

### 학술적 가치: **상위권 (working paper 기준 top ~15%, systematic review 한정 시 top ~10%)**

차별점:
- **첫 unified framework**: 5(또는 6) 도메인을 하나로 묶는 systematic review는 기존에 없음. 학술적 niche가 명확히 비어 있음. paper의 §1에서 "no prior review has unified this evidence"를 명시.
- **Evidence void identification**: D2(elixir problem) + D6(backlog accumulation)이 *peer-reviewed evidence 0편*이라는 finding은 systematic review의 가장 가치 있는 결과. 향후 5년 게임심리학 연구의 *agenda-setting paper* 가능.
- **Cross-cultural recognition**: 한국/일본/영어권 모두 동일 현상 명명 — *cross-cultural validation*이 되어 있음. *culture-specific* artifact가 아님.
- **Frost-Hartl CBT 모델 + DSM-5 hoarding criteria**의 명확한 적용. 임상 framework와 게임 행동의 bridge.
- **PRISMA 2020 준수 + 자동화 코드 공개**: reproducibility가 본 survey 21개 중 최상위. reviewer가 즉시 재실행 가능.
- **방어적 framing**: "we do not claim hoarding disorder", "dimensional not categorical", "6 over-pathologization risks". paper §1에서 가능한 비판을 모두 선제 흡수. 매우 성숙한 톤.

위험:
- **Single reviewer + automated screening** — PRISMA 표준 미달. 가장 큰 reject 위험.
- **PubMed only** — game studies는 ACM DL/IEEE Xplore/PsycINFO도 필수. *Games and Culture* 리뷰어가 즉시 짚는 약점.
- **Independent researcher 단독 저자** — 임상 영역. clinical psychology / game studies 공동저자 부재.
- **Game Hoarding Inventory가 promise만 있고 instrument 미작성** — abstract가 약속한 future work가 paper 안에 0개.
- **D2/D6 evidence void의 *원인* 분석 부재**: 왜 peer-reviewed evidence가 0편인가? (1) academic 관심 부재, (2) measurement difficulty, (3) 게임 산업 자체 데이터 미공개 등. 분석이 1단락 정도 들어가야 함.

게재 전망:
- *Games and Culture* (SAGE, IF 3.4): **realistic, 50-60%**. 적합도 가장 높음. Cross-cultural game behavior + clinical bridge.
- *Computers in Human Behavior* (Elsevier, IF 9.0): **40-50%**. 시의성 강함.
- *International Journal of Mental Health and Addiction* (Springer, IF 7.7): **40-50%**. gacha/loot box 영역이 강하면.
- *Journal of Behavioral Addictions* (Akadémiai, IF 8.6): **30-40%**. addictive 측면 강조 시.
- *Cyberpsychology, Behavior, and Social Networking* (Mary Ann Liebert): **40-50%**.
- 1차 reject 시 2nd reviewer + 추가 database로 보강 후 재투고 권장.

### 시장 가치: **중상위 (게임 산업 + 임상 컨설팅에서 강함)**

- **게임 디자인**: Bycer Game Wisdom, Game Developer (구 Gamasutra)에 paper 요약 게시 시 즉시 픽업. 게임 디자이너에게 *왜 player가 elixir를 안 쓰는가*에 대한 학술적 framework 제공.
- **Loot box/gacha 정책**: EU 벨기에/네덜란드/한국의 loot box 규제 논의에 인용 가능. UK Gambling Commission, ESRB 정책 문서 자료.
- **임상 컨설팅**: hoarding disorder 임상의가 *게임 행동을 differential diagnosis*로 고려할 때 참고. CHADD/IOCDF 자료.
- **언론**: Polygon, Kotaku, IGN, Wired Games가 즉시 픽업 가능. "왜 우리는 elixir를 안 쓰는가" 헤드라인. viral potential 매우 강력.
- **한국/일본 게임 시장**: gacha 시장(연 $20B+)의 윤리적 framing. 한국 게임물관리위원회/일본 컴퓨터엔터테인먼트협회 자문 가능.
- **재현가능 코드**: 다른 학술 그룹이 prisma_search_v2.py를 *즉시 reuse*하여 다른 도메인 systematic review에 적용 가능. 본 paper의 인용을 *방법론적 재사용*으로 누적.

### 종합 평점 (2026-04-11)

| 축 | 점수 | 코멘트 |
|---|---|---|
| Originality of framing | 9/10 | 첫 unified hoarding framework for games |
| PRISMA rigor | 7/10 | dual-query, automation, but 1 reviewer + 1 db |
| Reproducibility | 10/10 | code + data + manuscript 일치 |
| Evidence void identification | 10/10 | D2/D6 zero papers는 가장 가치있는 finding |
| Self-criticism | 9/10 | dimensional, 6 over-pathologization risks |
| Cross-cultural framing | 8/10 | 한/일/영 cross-validation |
| Repo health | 6/10 | 1 commit, but excellent organisation |
| Code quality | 9/10 | 1,943 lines Python (stdlib only) |
| Submission readiness | 7/10 | LaTeX 빌드 완료, 2nd reviewer 부족 |
| Timing | 8/10 | gacha 규제 + game studies 활성 |
| Practical applicability | 8/10 | game industry + clinical 모두 |
| **Overall (systematic review)** | **8.0/10** | "PRISMA 표준 1-2 게이트만 보강하면 published" |

핵심 격언: **"2nd reviewer + 1개 추가 database만 있으면 *Games and Culture* publication ready."** caching과 함께 본 survey 21개 중 *코드/데이터/manuscript 일치도 TOP*. D2 evidence void는 향후 5년 게임심리학 agenda-setting paper가 될 가능성. 단일 commit이 유일한 절차적 약점이지만 monorepo 내적 정합성은 흠잡을 데 없음.
