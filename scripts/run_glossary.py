"""30 용어 정의 batch + HTML 사전 사이트.

실행:
    uv run python scripts/run_glossary.py
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from src.glossary.define import define


def main():
    root = Path(__file__).resolve().parents[1]
    terms = yaml.safe_load((root / "config" / "terms.yaml").read_text(encoding="utf-8"))["terms"]

    print(f"[1] {len(terms)} 용어 정의\n")
    results = []
    t_start = time.time()

    for i, t in enumerate(terms, 1):
        t0 = time.time()
        d = define(t["name"], t["en"], t["category"])
        elapsed = time.time() - t0
        results.append({
            **t,
            "definition": d.get("definition", ""),
            "example": d.get("example", ""),
            "related": d.get("related", []),
            "elapsed_sec": round(elapsed, 1),
        })
        print(f"  [{i:>2}/{len(terms)}] {t['code']} {t['name']:18}  {elapsed:.1f}초")

    elapsed_total = time.time() - t_start

    # 저장
    out_dir = root / "data" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y%m%d")
    json_path = out_dir / f"glossary_{today}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"generated_at": datetime.now().isoformat(),
                   "n_terms": len(results),
                   "total_elapsed_sec": round(elapsed_total, 1),
                   "results": results},
                  f, ensure_ascii=False, indent=2)
    print(f"\n[JSON] {json_path}")
    print(f"[총 소요] {elapsed_total:.1f}초")

    # HTML
    html = _render(results, elapsed_total)
    html_path = root / "docs" / "index.html"
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")
    print(f"[site] {html_path}")


def _render(results, total_sec) -> str:
    by_cat = defaultdict(list)
    for r in results:
        by_cat[r["category"]].append(r)

    sections = []
    for cat, items in by_cat.items():
        cards = "\n".join(_card(it) for it in items)
        sections.append(f'<section><h2>{cat}</h2>{cards}</section>')

    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="UTF-8"><title>보험 + AI 거버넌스 용어집 v0</title>
<style>
  body {{ font-family: -apple-system, "Apple SD Gothic Neo", sans-serif;
          max-width: 880px; margin: 30px auto; padding: 0 20px; line-height: 1.65; color: #222; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 4px; }}
  h2 {{ font-size: 1.2rem; margin: 32px 0 12px; padding-bottom: 6px; border-bottom: 2px solid #305496; color: #305496; }}
  .meta {{ color: #777; font-size: 0.88rem; margin-bottom: 28px; }}
  .term {{ background: white; border: 1px solid #e0e0e0;
           border-radius: 6px; padding: 16px 20px; margin-bottom: 12px; }}
  .name {{ font-weight: 600; font-size: 1.08rem; }}
  .en {{ color: #888; font-size: 0.9rem; font-weight: normal; }}
  .def {{ margin: 8px 0; }}
  .ex {{ background: #f5f5f5; padding: 8px 12px; border-radius: 4px; font-size: 0.9rem; color: #555; margin: 6px 0; }}
  .related {{ font-size: 0.85rem; color: #1976d2; margin-top: 6px; }}
  .footer {{ color: #888; font-size: 0.82rem; margin-top: 40px; padding-top: 16px; border-top: 1px solid #ddd; }}
</style></head><body>
<h1>보험 + AI 거버넌스 용어집 v0</h1>
<p class="meta">{len(results)} 용어  ·  MLX Qwen3.5-122B-A10B 자동 정의  ·  생성 {datetime.now().strftime('%Y-%m-%d %H:%M')}  ·  소요 {total_sec:.0f}초</p>
{body}
<div class="footer">
v0 한계 — 30 용어, 단일 LLM, 출처 X. 본인 검수 미완료.<br/>
<a href="https://github.com/Incheonkirin/insurance-ai-glossary-v0">github.com/Incheonkirin/insurance-ai-glossary-v0</a>
</div>
</body></html>"""


def _card(t):
    related = "  ·  ".join(t.get("related", []))
    return f"""<div class="term">
  <div class="name">{t['name']} <span class="en">({t['en']})</span></div>
  <div class="def">{t['definition']}</div>
  <div class="ex">예: {t['example']}</div>
  <div class="related">관련: {related}</div>
</div>"""


if __name__ == "__main__":
    main()
