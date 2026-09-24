import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from externalsort import ExternalSorter  # noqa: E402


def test_single_chunk():
    s = ExternalSorter(chunk_size=64)
    s.load([5, 3, 1, 2, 4])
    assert s.sort() == [1, 2, 3, 4, 5]
    assert s.stats()["chunks"] == 1


def test_multiple_chunks():
    s = ExternalSorter(chunk_size=64)
    data = list(range(199, -1, -1))      # 200 条递减
    s.load(data)
    out = s.sort()
    assert out == list(range(200))
    assert s.stats()["chunks"] == 4      # 200 / 64 -> 4 块


def test_reverse_input_500():
    s = ExternalSorter(chunk_size=128)
    s.load(list(range(499, -1, -1)))
    assert s.sort() == list(range(500))


def test_duplicates_preserved():
    s = ExternalSorter(chunk_size=16)
    s.load([3, 1, 2, 1, 3, 2, 1])
    out = s.sort()
    assert out == sorted([3, 1, 2, 1, 3, 2, 1])
    assert len(out) == 7                 # 元素数不丢


def test_k_way_multipass():
    # 20 块、k=4 -> 至少 2 趟归并
    s = ExternalSorter(chunk_size=10, k=4)
    s.load(list(range(199, -1, -1)))
    out = s.sort()
    assert out == list(range(200))
    assert s.stats()["chunks"] == 20
    assert s.stats()["passes"] >= 2


def test_empty_input():
    s = ExternalSorter()
    s.load([])
    assert s.sort() == []
    assert s.stats()["chunks"] == 0


def test_random_against_sorted():
    import random
    random.seed(42)
    data = [random.randint(0, 10000) for _ in range(1000)]
    s = ExternalSorter(chunk_size=37, k=3)
    s.load(data)
    out = s.sort()
    assert out == sorted(data)


def test_stats_fields():
    s = ExternalSorter(chunk_size=10, k=4)
    s.load([i for i in range(50, 0, -1)])
    s.sort()
    st = s.stats()
    assert set(st.keys()) >= {"chunks", "passes", "comparisons"}
    assert st["chunks"] == 5


def test_stable_within_merge():
    # 等值元素跨块归并后数量与元素完全一致
    s = ExternalSorter(chunk_size=8)
    s.load([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
    out = s.sort()
    assert out.count(1) == 6
    assert out.count(0) == 6
