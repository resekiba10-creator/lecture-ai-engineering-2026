"""第5回：前後ページ取得機能のテスト。"""

from contextlib import nullcontext
from app import retrieval


def test_search_with_neighbors(monkeypatch):
    hits = [
        {
            "page_id": f"lec03-main-p{n:03d}",
            "document_id": "lec03-main",
            "page": n,
            "content": f"本文{n}",
            "distance": 0.1,
        }
        for n in (39, 41)
    ]

    pages = [
        {
            "page_id": f"lec03-main-p{n:03d}",
            "document_id": "lec03-main",
            "page": n,
            "content": f"本文{n}",
        }
        for n in (38, 39, 40, 41, 42)
    ]

    class FakeDB:
        def execute(self, *args):
            return hits

    monkeypatch.setattr(
        retrieval, "open_index",
        lambda *_: nullcontext(FakeDB())
    )
    monkeypatch.setattr(
        retrieval, "embed_text",
        lambda *_: [1.0, 0.0]
    )
    monkeypatch.setattr(
        retrieval, "load_pages",
        lambda: pages
    )

    normal = retrieval.search("メモリ")
    expanded = retrieval.search(
        "メモリ", include_neighbors=True
    )

    assert len(normal) == 2
    assert len(expanded) == 5
    assert len({p["page_id"] for p in expanded}) == 5
    assert {p["page"] for p in expanded} == {
        38, 39, 40, 41, 42
    }
    assert sum(
        p["distance"] is None for p in expanded
    ) == 3
