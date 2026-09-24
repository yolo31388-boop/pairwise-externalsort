import sys
import os
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from externalsort import ExternalSorter  # noqa: E402


def test_single_chunk():
    s = ExternalSorter(chunk_size=64)
    s.load([5, 3, 1, 2, 4])
    assert s.sort() == [1, 2, 3, 4, 5]
    st = s.stats()
    assert st["chunks"] == 1
    assert st["disk_writes"] == 1        # 只落盘 1 块
    assert st["disk_reads"] == 0


def test_multiple_chunks():
    s = ExternalSorter(chunk_size=64)
    s.load(list(range(199, -1, -1)))
    out = s.sort()
    assert out == list(range(200))
    assert s.stats()["chunks"] == 4


def test_reverse_input_500():
    s = ExternalSorter(chunk_size=128)
    s.load(list(range(499, -1, -1)))
    assert s.sort() == list(range(500))


def test_duplicates_preserved():
    s = ExternalSorter(chunk_size=16)
    s.load([3, 1, 2, 1, 3, 2, 1])
    out = s.sort()
    assert out == sorted([3, 1, 2, 1, 3, 2, 1])
    assert len(out) == 7


def test_k_way_multipass():
    s = ExternalSorter(chunk_size=10, k=4)
    s.load(list(range(199, -1, -1)))
    out = s.sort()
    assert out == list(range(200))
    st = s.stats()
    assert st["chunks"] == 20
    assert st["passes"] >= 2


def test_explicit_flush_merge():
    s = ExternalSorter(chunk_size=10, k=3)
    s.load(list(range(49, -1, -1)))
    s.flush()
    assert s.stats()["chunks"] == 5
    assert s.stats()["disk_writes"] == 5
    while s.merge_once():
        pass
    assert len(s.chunks) == 1          # 当前块数归并到 1
    assert s.stats()["chunks"] == 5    # 初始块数不变
    # 手动归并后的结果正确
    assert list(s.chunks[0]) == list(range(50))


def test_disk_io_counting_large():
    # 5000 条 / chunk 16 -> 313 块；k=4 -> 5 趟
    s = ExternalSorter(chunk_size=16, k=4)
    s.load(list(range(4999, -1, -1)))
    out = s.sort()
    assert out == list(range(5000))
    st = s.stats()
    assert st["chunks"] == 313
    assert st["passes"] == 5
    # disk_writes = 初始 313 + 每趟输出块数
    # 313->79->20->5->2->1 ：写 313+79+20+5+2+1 = 420
    assert st["disk_writes"] == 420
    # disk_reads = 每趟读回输入块数：313+79+20+5+2 = 419
    assert st["disk_reads"] == 419
    # 比较次数 >= 输出条数（每条至少一次比较）
    assert st["comparisons"] >= 5000


def test_empty_input():
    s = ExternalSorter()
    s.load([])
    assert s.sort() == []
    assert s.stats()["chunks"] == 0


def test_random_against_sorted():
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
    assert set(st.keys()) >= {"chunks", "passes", "comparisons",
                              "disk_writes", "disk_reads"}
    assert st["chunks"] == 5


def test_stable_within_merge():
    s = ExternalSorter(chunk_size=8)
    s.load([1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
    out = s.sort()
    assert out.count(1) == 6
    assert out.count(0) == 6


def test_tiny_chunks_many_passes():
    # 每块 4 条、k=2 -> 多趟合并验证块级正确性
    s = ExternalSorter(chunk_size=4, k=2)
    s.load([random.Random(7).randint(0, 100) for _ in range(100)])
    data = s._pending
    assert s.sort() == sorted(data)
    assert s.stats()["passes"] >= 4
