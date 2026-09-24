# Pair-wise GSB 基线：外部 k 路归并排序（含磁盘 IO 统计）

题目（feature 迭代）：实现内存受限的外部 k 路归并排序，含显式磁盘块管理、多趟合并与 IO 统计。

- 骨架：`externalsort.py`（ExternalSorter 方法均 `raise NotImplementedError`）
- 验收：`python -m pytest tests/test_externalsort.py -q` 全绿
- 约束：只 import 标准库；必须真实"分块 + k 路归并"（禁止整体排序或一次性驻留内存）
