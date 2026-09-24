"""外部 k 路归并排序（内存受限模拟，含显式磁盘块管理与 IO 统计）。

模型：
- ExternalSorter(chunk_size, k)：内存一次最多 hold chunk_size 条记录。
- load(data, key=None)：key 为排序键函数（元素可为任意可比较对象）。
- flush() 把数据按 chunk_size 切块"落盘"（内存 list 模拟磁盘块），
  每块按 key 排序，每次落盘 disk_writes+1。
- merge_once() 执行一趟 k 路归并：小根堆 + 游标逐条取最小；
  同 key 时取组序靠前的块（稳定性）；读回/写出各计
  disk_reads/disk_writes；块数 <= k 时返回 False。
- sort(descending=False) = 全部 flush + 反复 merge_once 到 1 块。
"""
from __future__ import annotations

import heapq


class ExternalSorter:
    def __init__(self, chunk_size: int = 64, k: int = 4):
        self.chunk_size = chunk_size
        self.k = k
        self.chunks: list[list] = []
        self._pending: list = []
        self._key = None
        self._reverse = False
        self._comparisons = 0
        self._disk_writes = 0
        self._disk_reads = 0

    # -------------------------------------------------- 接口
    def load(self, data, key=None) -> None:
        """登记数据流（key 为可选排序键函数）。"""
        raise NotImplementedError

    def flush(self) -> None:
        """把已登记数据切成 chunk_size 的块写入 chunks（清空缓冲）。"""
        raise NotImplementedError

    def merge_once(self) -> bool:
        """执行一趟 k 路归并。块数 > k 时返回 True，否则 False。"""
        raise NotImplementedError

    def sort(self, descending: bool = False) -> list:
        """全部 flush 后反复归并到 1 块，返回全排序结果。"""
        raise NotImplementedError

    def stats(self) -> dict:
        """返回 {chunks, passes, comparisons, disk_writes, disk_reads,
        max_chunk_size}。"""
        raise NotImplementedError
