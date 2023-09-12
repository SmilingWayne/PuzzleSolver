# Python | ortools整数规划的求解

!!! abstract "ORtools" 

    这个系列的第一篇文章大概讲了Ortools的基本概况，安装和在线性规划问题上的使用场景。本部分涉及整数规划(Integer Programming)的部分，代码则涉及基础的IP问题求解，以及一种用数组形式代入求解器进行求解的方法。


- 混合整数规划：要求一些**决策变量是整数的线性优化问题**（Mixed Integer Programming, MIP）
    - 这些变量可能是一些无法切分的物品数量（电视机、汽车等）；
    - 也可以是0-1布尔变量，比如考虑一个人是否被分配到某个工作岗位；

- Google 提供了几种解决MIP问题的方法：
    - MPSolver：是多个第三方MIP求解器的包装，这些求解器使用标准的分支定界（Branch and Bound）技术。
    - CP-SAT 求解器：使用 SAT方法的约束规划求解器。
    - CP求解器：原始的Constraint Programming求解器。

- 使用场景：
    - MIP求解器更适合可以转化成具有任意整数变量的标准线性规划的问题；
    - CP-SAT更适合大多数变量为布尔值的问题。
    - 同样的，用于解决最小费用流问题的网络流求解器也是一个不错的解决方案。


-------


## 解决整数规划问题实战

给出如下整数规划问题：
$$\max x + 10y$$

$$\text{s.t.} \begin{align}\begin{equation*}
\begin{cases}
x + 7y \leq 17.5  \\
0 \leq x \leq 3.5  \\
0 \leq y  \\
\end{cases}
\end{equation*}\end{align} \\ 
x, y \in \text{Integers}
$$

我们使用MIP求解器来求解这个问题。默认的 OR-Tools 使用SCIP来求解 MIP 问题。代码思路和前一篇的类似，这里不重复，直接给出代码和注释（见图三及后续）

----------


对于一些参数较多的整数规划问题，我们可以使用数组形式代入求解器求解。

给出如下问题：

$$\max \hspace{5pt} 7x_1 + 8x_2 + 2x_3 + 9x_4 + 6x_5 \\ 
\text{s.t.} \begin{align}\begin{equation*}
\begin{cases}
5 x_1 + 7 x_2 + 9 x_3 + 2 x_4 +  x5  & \leq 250 \\
18 x_1 + 4 x_2 - 9 x_3 + 10 x_4 + 12 x_5  & \leq 285 \\
4 x_1 + 7x_2 + 3 x_3 + 8 x_4 + 5 x_5 &  \leq 211 \\
5 x_1 + 13 x_2 + 16 x_3 + 3 x_4 - 7 x_5  & \leq 315 \\
\end{cases}
\end{equation*}\end{align} \\ x_1, x_2 ... x_5 \in \text{non-negative integers}$$

这一部分的变量声明等都和前面的类似，不同的在于后面的代码使用`MakeRowConstraint` 方法（Python下，具体取决于编码语言）为示例创建约束。该方法的前两个参数是约束的下限和上限。第三个参数（约束的名称）是可选的。

对于每个约束，可以使用方法 `SetCoefficient` 定义变量的系数。该方法将约束 $i$ 中变量 $x[j]$ 的系数指定为数组 constraint_coeffs 的 $[i][j]$ 条目。