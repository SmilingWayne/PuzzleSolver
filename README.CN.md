# 逻辑谜题求解器

本仓库为多种**逻辑谜题**提供了**可靠、高效且定制化的求解器**。底层求解引擎主要基于成熟的开源工具，如 ortools 和 z3.

与其他依赖逻辑/演绎方法的求解器不同，本项目的求解器主要基于**约束编程**。虽然我非常钦佩那些能够找出纯逻辑解的人，但本项目**并非**旨在用自动求解取代人类推理：**我这么做纯粹是因为好玩**。

该仓库还包含一个结构化的数据集（超过 28,000 个实例），覆盖 80 多种特定且流行的谜题类型（如 Nonogram、Slitherlink、Akari、Fillomino、Hitori、Kakuro 等），

更多数据及相关分析将随时间推移逐步添加。

近期（约 2025 年 11 月起），仓库进行了重构，采用了统一的 [网格](./Puzzles/Common/Board/Grid.py) 数据结构和解析-求解-验证流程。部分实现细节深受类似但更复杂的仓库启发，如：为90+种逻辑谜题提供求解接口的 [puzzle_solver](https://github.com/Ar-Kareem/puzzle_solver) 以及 一款能够实时操作解谜的 [Puzzles-Solver](https://github.com/newtomsoft/Puzzles-Solver)。

