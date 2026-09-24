import sys
import os
import random
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from externalsort import ExternalSorter  # noqa: E402


def _mkwork():
    return tempfile.mkdtemp(prefix="gsb_esort_")


def _listfiles(d):
    return sorted(f for f in os.listdir(d) if f.startswith("run_"))


def test_single_run_no_merge():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=1024, k=4, workdir=w)
        s.load([5, 3, 1, 2, 4])
        assert s.sort() == [1, 2, 3, 4, 5]
        st = s.stats()
        assert st["runs"] == 1
        assert st["passes"] == 0
        assert st["disk_writes"] == 1
        assert st["disk_reads"] == 0
        # 结束后目录已清空
        assert _listfiles(w) == []
        assert st["files_cleaned"] == 1
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_multiple_runs_int():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=64, k=4, workdir=w)
        s.load(list(range(199, -1, -1)))
        out = s.sort()
        assert out == list(range(200))
        st = s.stats()
        assert st["runs"] >= 2
        assert st["passes"] >= 1
        assert st["disk_writes"] >= st["runs"]
        assert st["disk_reads"] >= st["runs"]
        assert st["disk_bytes"] > 0
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_reverse_input_500():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=128, workdir=w)
        s.load(list(range(499, -1, -1)))
        assert s.sort() == list(range(500))
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_duplicates_preserved():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=32, workdir=w)
        s.load([3, 1, 2, 1, 3, 2, 1])
        out = s.sort()
        assert out == sorted([3, 1, 2, 1, 3, 2, 1])
        assert len(out) == 7
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_k_way_multipass():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=32, k=4, workdir=w)
        s.load(list(range(199, -1, -1)))
        out = s.sort()
        assert out == list(range(200))
        st = s.stats()
        assert st["runs"] >= 4
        assert st["passes"] >= 2
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_files_real_during_sort():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=64, k=4, workdir=w)
        s.load(list(range(199, -1, -1)))
        s.flush()
        files = _listfiles(w)
        assert len(files) >= 2                 # 真实文件落盘
        for f in files:
            assert os.path.getsize(os.path.join(w, f)) > 0
        s.sort()
        assert _listfiles(w) == []             # 全部清理
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_string_records():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=64, workdir=w)
        s.load(["banana", "apple", "cherry", "date", "fig", "elderberry"])
        assert s.sort() == sorted(["banana", "apple", "cherry", "date",
                                   "fig", "elderberry"])
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_generator_input():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=64, workdir=w)

        def gen():
            for i in range(99, -1, -1):
                yield i

        s.load(gen())
        assert s.sort() == list(range(100))
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_empty_input():
    w = _mkwork()
    try:
        s = ExternalSorter(workdir=w)
        s.load([])
        assert s.sort() == []
        assert _listfiles(w) == []
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_key_function():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=64, workdir=w)
        s.load([3, 1, -2, 4, 0, -3], key=abs)
        # 同 abs=3 的 3 与 -3 保持输入相对顺序（3 在前）
        assert s.sort() == [0, 1, -2, 3, -3, 4]
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_descending():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=64, workdir=w)
        s.load([5, 3, 1, 2, 4])
        assert s.sort(descending=True) == [5, 4, 3, 2, 1]
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_stability_same_key():
    w = _mkwork()
    try:
        # 同 key（绝对值）元素保持输入相对顺序
        s = ExternalSorter(block_size=32, k=2, workdir=w)
        s.load([-3, 3, -2, 2, 1, -1], key=abs)
        out = s.sort()
        assert out == [1, -1, -2, 2, -3, 3]
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_random_large_roundtrip():
    w = _mkwork()
    try:
        random.seed(42)
        data = [random.randint(-100000, 100000) for _ in range(3000)]
        s = ExternalSorter(block_size=128, k=3, workdir=w)
        s.load(data)
        assert s.sort() == sorted(data)
        st = s.stats()
        assert st["runs"] >= 10
        assert st["disk_bytes"] > 0
        assert st["files_cleaned"] >= st["runs"]
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_stats_fields():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=64, workdir=w)
        s.load([i for i in range(50, 0, -1)])
        s.sort()
        st = s.stats()
        assert set(st.keys()) >= {"runs", "passes", "comparisons",
                                  "disk_writes", "disk_reads",
                                  "disk_bytes", "files_cleaned"}
        assert st["comparisons"] >= 0
    finally:
        shutil.rmtree(w, ignore_errors=True)


def test_auto_workdir_cleaned():
    # 不传 workdir：自动创建临时目录并在 sort 后清理
    s = ExternalSorter(block_size=64)
    s.load(list(range(49, -1, -1)))
    assert s.sort() == list(range(50))
    assert s.stats()["files_cleaned"] > 0
    assert not os.path.exists(s.workdir)


def test_interleaved_flush_merge():
    w = _mkwork()
    try:
        s = ExternalSorter(block_size=32, k=3, workdir=w)
        s.load(list(range(29, -1, -1)))
        s.flush()
        n0 = len(_listfiles(w))
        assert n0 >= 2
        while s.merge_once():
            pass
        assert len(_listfiles(w)) == 1
        assert list(s.sort()) == list(range(30))
    finally:
        shutil.rmtree(w, ignore_errors=True)
