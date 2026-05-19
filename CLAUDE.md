# CLAUDE.md — Insurance + AI Glossary v0

## Mission

보험 + AI 거버넌스 30 용어 자동 정의 사전. SEO + 본인 전문 영역 시각화.

## Voice

- 평어체
- "박다" 금지
- "책임" 금지
- 회사 자료 X

## 본인 카드 매칭

KP손보 1순위 → 본인 사이트 들어왔을 때 *규제 도메인 에이전트 AI 아키텍트* 시각화 자료.
헤드라인이 강조하는 영역(가명처리·RUAI·금감원 대응·NRS·FDS·LLM 거버넌스) 30 용어로 커버.

## 구조

```
config/terms.yaml          # 30 용어 + 카테고리
src/glossary/define.py     # MLX Qwen 정의
scripts/run_glossary.py    # batch + HTML
docs/index.html
```
