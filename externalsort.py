"""外部 k 路归并排序（内存受限模拟）。

模型：
- ExternalSorter(chunk_size, k)：内存一次最多 hold chunk_size 条记录；
  数据超过内存时，先分块内存排序（每块一个 chunk，写"磁盘"即内存
  列表模拟），再用 k 路归并（小根堆 + 游标）合并出全排序结果。
- 块数超过 k 时需多趟归并（每趟把 k 块合并成 1 块），stats 里
  passes 记录趟数。
- 只允许在 chunk 边界内用内存排序：load() 只登记数据流，
  sort() 内部严格按 chunk_size 分批。
"""
from __future__ import annotations

import heapq


class ExternalSorter:
    def __init__(self, chunk_size: int = 64, k: int = 4):
        self.chunk_size = chunk_size
        self.k = k
        self.chunks: list[list] = []  # 内存模拟的"磁盘块"
        self._pending: list = []

    # -------------------------------------------------- 接口
    def load(self, data) -> None:
        """登记数据流（不排序，不全部进内存）。"""
        raise NotImplementedError

    def sort(self) -> list:
        """外部归并排序，返回全排序结果。"""
        raise NotImplementedError

    def stats(self) -> dict:
        """返回 {chunks, passes, comparisons}。"""
        raise NotImplementedError
