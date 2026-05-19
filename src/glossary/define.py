"""MLX Qwen3.5-122B 용어 자동 정의."""

from __future__ import annotations

import json
import os
import re
from typing import Any

DEFAULT_MODEL = "mlx-community/Qwen3.5-122B-A10B-4bit"
_cache: dict[str, Any] = {}


def _load():
    if "model" not in _cache:
        from mlx_lm import load
        name = os.environ.get("MLX_MODEL", DEFAULT_MODEL)
        print(f"  [MLX] {name} 로드 ...")
        _cache["model"], _cache["tokenizer"] = load(name)
    return _cache["model"], _cache["tokenizer"]


SYSTEM = """너는 한국 보험·AI 거버넌스 분야 사전 편찬자다.

주어진 용어에 대해 정의·예시·관련 용어를 JSON 한 덩어리로 출력해라.

규칙:
1. 정의: 2-3 문장. 한국 보험 도메인 또는 한국 금융 AI 거버넌스 맥락 우선
2. 예시: 한 문장. 실무에서 어떻게 쓰이는지 구체적
3. 관련 용어: 한국어 명사 3개 (이 용어와 함께 나오는 개념)
4. 한국어 평어체
5. JSON만, 다른 텍스트·코드 블록 표시 없음

형식:
{
  "definition": "...",
  "example": "...",
  "related": ["...", "...", "..."]
}"""


def define(term: str, en: str, category: str) -> dict[str, Any]:
    from mlx_lm import generate

    user = f"[용어] {term}\n[영문] {en}\n[카테고리] {category}\n\n위 용어의 정의·예시·관련 용어 3개를 JSON으로 출력."
    model, tokenizer = _load()
    msgs = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}]
    try:
        prompt = tokenizer.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True,
            enable_thinking=False,
        )
    except TypeError:
        prompt = tokenizer.apply_chat_template(
            msgs, tokenize=False, add_generation_prompt=True,
        )
    raw = generate(model, tokenizer, prompt=prompt,
                   max_tokens=400, verbose=False).strip()

    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return {"definition": raw[:300], "example": "", "related": [], "_parse_error": True}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return {"definition": raw[:300], "example": "", "related": [], "_parse_error": True}
