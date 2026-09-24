# Pair-wise GSB 基线：外部 k 路归并排序

题目（feature 迭代）：实现内存受限的外部 k 路归并排序。

- 骨架：`externalsort.py`（ExternalSorter 方法均 `raise NotImplementedError`）
- 验收：`python -m pytest tests/test_externalsort.py -q` 全绿
- 约束：只 import 标准库；必须真实分块 + 多路归并（不能整体排序）
