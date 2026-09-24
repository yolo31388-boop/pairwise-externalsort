"""外部 k 路归并排序（真实磁盘文件版）。

模型：
- ExternalSorter(block_size, k, workdir)：block_size 为每个 run
  文件的目标字节预算；k 路归并；workdir 指定临时目录（None 时
  自动创建并在 sort 结束后清理）。
- load(iterable, key=None)：接受任意可迭代对象（含生成器），
  元素类型为 int 或 str（同批统一）；key 为可选排序键函数。
- flush()：把数据排序后按字节预算切成 run，每个 run 序列化写为
  一个真实临时文件（run_N.bin）；编码格式自定（必须可 roundtrip）。
- merge_once()：k 路归并：打开输入 run 文件逐条读回（decode），
  堆归并写出新 run 文件；消费完的输入文件立即删除。
- sort(descending=False)：flush 后反复 merge_once 到 1 个 run，
  读回全量返回；结束后删除全部临时文件（含最终文件）。
- stats()：{runs, passes, comparisons, disk_writes, disk_reads,
  disk_bytes, files_cleaned}。
"""
from __future__ import annotations


class ExternalSorter:
    def __init__(self, block_size: int = 256, k: int = 4,
                 workdir: str | None = None):
        self.block_size = block_size
        self.k = k
        self.workdir = workdir
        self._own_dir = workdir is None
        self._pending: list = []
        self._key = None
        self._reverse = False
        self._runs: list[str] = []       # 当前 run 文件路径
        self._comparisons = 0
        self._disk_writes = 0
        self._disk_reads = 0
        self._disk_bytes = 0
        self._files_cleaned = 0

    # -------------------------------------------------- 接口
    def load(self, iterable, key=None) -> None:
        """登记数据流（任意可迭代对象；元素为 int 或 str）。"""
        raise NotImplementedError

    def flush(self) -> None:
        """排序后按字节预算切成 run，每个 run 写为真实临时文件。"""
        raise NotImplementedError

    def merge_once(self) -> bool:
        """执行一趟 k 路归并（读回输入 run、写出新 run）。
        输入 run 数 > k 时返回 True，否则 False。"""
        raise NotImplementedError

    def sort(self, descending: bool = False) -> list:
        """全部 flush 后反复归并到 1 个 run，返回全排序结果，
        结束后清理全部临时文件。"""
        raise NotImplementedError

    def stats(self) -> dict:
        """返回 {runs, passes, comparisons, disk_writes, disk_reads,
        disk_bytes, files_cleaned}。"""
        raise NotImplementedError
