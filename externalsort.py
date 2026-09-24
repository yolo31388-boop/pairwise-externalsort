"""外部 k 路归并排序（内存受限模拟，含显式磁盘块管理与 IO 统计）。

模型：
- ExternalSorter(chunk_size, k)：内存一次最多 hold chunk_size 条记录。
- load(data) 只登记数据流；flush() 把数据按 chunk_size 切块"落盘"
  （内存 list 模拟磁盘块），每次落盘 disk_writes+1。
- merge_once() 对当前块集执行一趟 k 路归并：小根堆 + 游标逐条取
  最小，每组 k 块合并成 1 块；读回每个输入块 disk_reads+1，
  写出每个输出块 disk_writes+1；块数 <= k 时返回 False。
- sort() = 全部 flush + 反复 merge_once 直到只剩 1 块。
- 归并必须逐条比较（禁止把整组块合成 list 再 sorted）。
"""
from __future__ import annotations

import heapq


class ExternalSorter:
    def __init__(self, chunk_size: int = 64, k: int = 4):
        self.chunk_size = chunk_size
        self.k = k
        self.chunks: list[list] = []
        self._pending: list = []
        self._comparisons = 0
        self._disk_writes = 0
        self._disk_reads = 0

    # -------------------------------------------------- 接口
    def load(self, data) -> None:
        """登记数据流（不排序、不驻留内存）。"""
        raise NotImplementedError

    def flush(self) -> None:
        """把已登记数据切成 chunk_size 的块写入 chunks（清空缓冲）。"""
        raise NotImplementedError

    def merge_once(self) -> bool:
        """执行一趟 k 路归并。块数 > k 时返回 True，否则 False。"""
        raise NotImplementedError

    def sort(self) -> list:
        """全部 flush 后反复归并到 1 块，返回全排序结果。"""
        raise NotImplementedError

    def stats(self) -> dict:
        """返回 {chunks, passes, comparisons, disk_writes, disk_reads}。"""
        raise NotImplementedError
