# 涂色/放置类逻辑谜题连通性约束的几种表示方法及效果对比

## 什么是连通性约束

在许多逻辑谜题中，**连通性约束**（Connectivity Constraint）要求某个特定类型的所有单元格（涂黑的/未涂黑的/包含数字的等）形成一个**单一连通区域**。换句话说，从该集合中的任意一个元素出发，都可以通过相邻元素，到达集合中的任意其他元素。

【补充图片】

> 这里的“相邻”，主要分“正交相邻(Orthogonal，上下左右四方向)”和“对角线相邻(Diagonal，上下左右以及对角线方向)”。


### 典型谜题场景

aqre, canal view, cave, creek, fobidoshi, kuroshute, kuromasu, heyawake, LITS, nurimisaki, paint_area, shimaguni, yajikabe, yin-yang, uso-one 


连通性是一个**全局约束**（Global Constraint），它不能简单地通过局部条件来表达。利用可满足性SAT求解器进行解算的时候，我们需要将这个全局性质编码为一组局部约束的组合，同时保证：

- **正确性**：满足约束的解一定是连通的
- **完备性**：所有连通解都能被找到
- **效率**：约束数量可控，求解器能够高效处理

---

## 数学表示

给定一个网格图 $G = (V, E)$，其中：

- $V$ 是单元格（或节点）的集合，也就是点；
- $E$ 是相邻关系的集合，（通常为正交相邻），也就是边；

**连通性约束**要求：集合 $S = \{v \in V \mid x_v = 1\}$ 诱导的子图 $G[S]$ 是连通的。

**我们把“需要连通”统一用“是否激活”来描述**。这是因为不同谜题中，对于“什么样的子图应该是连通的”有不同的条件：

1. Kuroshute 和 Nurimisaki中，**未涂黑**的格子应该是连通的；
2. 在Aqre, Canal View, LITS 这类谜题中，**涂黑**的格子应该是连通的；
3. 在 yin-yang 中，黑圈和白圈格子都要是连通的；

一般而言，我们只需要规定“符合某条件的格子被激活”，就能分别表述这些杂七杂八的约束了。

----

### 静态的洪水泛滥法 + 高度流法

一种常见的方法是洪水泛滥思路：从唯一根节点向外传播连通性信号，用高度变量替代传统迭代式洪水填充，比如每一个节点的高度，都等于相邻的最大高度 - 1；

核心规则：

- 选**规范根**（字典序第一个活跃节点，对称性破缺）
- 根的高度设为最大值 $|V|$
- 活跃节点高度 = 相邻最大高度 - 1
- 非活跃节点高度 = 0
- 活跃节点高度必须 > 0（保证连通到根）


对于每个节点 $v \in V$：

- $x_v \in \{0, 1\}$：节点 $v$ 是否为活跃节点（未涂黑，输入变量）
- $h_v \in \{0, |V|\}$：节点 $v$ 的高度
- $\text{is\_root}_v \in \{0, 1\}$：节点 $v$ 是否为规范根
- $\text{prefix\_zero}_v \in \{0, 1\}$：辅助变量，表示「之前所有节点都不活跃」
- $H^{\max}_v \in \{0, |V|\}$：$v$ 邻居中的最大高度

| 约束公式                                       | 约束作用（核心含义）                               |
| ---------------------------------------------- | -------------------------------------------------- |
| 1. 规范根递归定义                              | 按顺序定义「前缀全不活跃」，锁定第一个活跃节点为根 |
| 2. $\sum is\_root_v ≤ 1$                       | 强制最多一个规范根（对称性破缺）                   |
| 3. $H^{\max}_v = \max\{h_u\}$                  | 计算节点邻居的最大高度                             |
| 4. $is\_root_v ⇒ h_v = \|V\|$                  | 根节点高度设为最大值                               |
| 5. $(x_v ∧ ¬is\_root_v) ⇒ h_v = H^{\max}_v -1$ | 活跃节点高度逐级递减                               |
| 6. $¬x_v ⇒ h_v = 0$                            | 非活跃节点高度清零                                 |
| 7. $x_v ⇒ h_v > 0$                             | 所有活跃节点必须连通到根                           |


| 指标     | 数量级     | 说明                                       |
| -------- | ---------- | ------------------------------------------ |
| 布尔变量 | $O(V)$     | is_root + prefix_zero 变量（无父节点变量） |
| 整数变量 | $O(V)$     | 节点高度 + 邻居最大高度变量                |
| 约束数量 | $O(V + E)$ | 节点约束 + 邻域最大高度计算                |

```python
def add_connected_subgraph_by_height(
    model: cp.CpModel, 
    active_nodes: Dict[Hashable, cp.IntVar], 
    adjacency_map: Dict[Hashable, List[Hashable]],
    prefix: str = 'graph'
) -> Tuple[Dict[Hashable, cp.IntVar], Dict[Hashable, cp.IntVar]]:
    """
    Enforce that the set of nodes where active_nodes[n] is True forms a single 
    connected component.
    
    This implementation uses the "Canonical Root + Height Flow" method, which is 
    significantly faster for large/sparse grids than the Spanning Tree method.
    
    Args:
        model: The OR-Tools CpModel.
        active_nodes: Mapping from node identifier to its BoolVar.
        adjacency_map: Pre-computed neighbor list for each node. 
                       Format: {node: [neighbor_node_1, neighbor_node_2, ...]}
        prefix: Prefix of string to avoid duplicated variable names.
        
    Returns:
        (node_height, is_root): Dictionaries of internal variables for debugging/visualization.
                                node_height replaces the 'rank' from the old implementation.
    """
    # 1. Prepare Nodes
    # We must convert dict keys to a list to ensure a deterministic order for the 
    # canonical root selection logic.
    nodes = list(active_nodes.keys())
    num_nodes = len(nodes)
    
    # Tiny optimization: 0 or 1 active node is trivially connected.
    if num_nodes <= 1: 
        return {}, {}
    
    # 2. Define Variables
    is_root: Dict[Hashable, cp.IntVar] = {} 
    prefix_zero: Dict[Hashable, cp.IntVar] = {} 
    node_height: Dict[Hashable, cp.IntVar] = {} 
    max_neighbor_height: Dict[Hashable, cp.IntVar] = {} 
    
    for n in nodes:
        is_root[n] = model.NewBoolVar(f"{prefix}_is_root_{n}")
        # Height ranges from 0 to num_nodes
        node_height[n] = model.NewIntVar(0, num_nodes, f"{prefix}_height_{n}")
        max_neighbor_height[n] = model.NewIntVar(0, num_nodes, f"{prefix}_max_nh_{n}")
    
    # 3. Canonical Root Selection (Symmetry Breaking)
    # The Root MUST be the *first* active node in the ordered list 'nodes'.
    # prefix_zero[i] is True iff ALL previous nodes in the list are Inactive.
    prev_n = None
    for n in nodes:
        b = model.NewBoolVar(f"{prefix}_prefix_zero_{n}")
        prefix_zero[n] = b
        
        if prev_n is None:
            # First node: prefix_zero is always True (no predecessors)
            model.Add(b == 1)
        else:
            # Recursive: prefix_zero[n] <-> prefix_zero[prev] AND NOT active[prev]
            ortools_and_constr(model, b, [prefix_zero[prev_n], active_nodes[prev_n].Not()])
        prev_n = n 
    
    # Link is_root: Can only be root IFF (Active AND prefix_zero)
    for n in nodes:
        ortools_and_constr(model, is_root[n], [active_nodes[n], prefix_zero[n]])
    
    # At most one root (it ensures single component logic)
    model.Add(sum(is_root.values()) <= 1)
    
    # 4. Height Propagation (Sink-based Flow)
    for n in nodes:
        # Filter neighbors: only consider those that are part of the active_nodes set
        # (Adjacency map might contain nodes not currently involved in this subgraph constraint)
        raw_neighbors = adjacency_map.get(n, [])
        valid_neighbors = [nbr for nbr in raw_neighbors if nbr in node_height]
        
        neighbor_heights = [node_height[nbr] for nbr in valid_neighbors]
        
        # Calculate Max Neighbor Height
        if neighbor_heights:
            model.AddMaxEquality(max_neighbor_height[n], neighbor_heights)
        else:
            model.Add(max_neighbor_height[n] == 0)
        
        # Rule A: Active Node, NOT Root -> Height = Max_Neighbor - 1
        model.Add(node_height[n] == max_neighbor_height[n] - 1).OnlyEnforceIf(
            [active_nodes[n], is_root[n].Not()]
        )
        
        # Rule B: Root Node -> Height = num_nodes (Source of flow)
        model.Add(node_height[n] == num_nodes).OnlyEnforceIf(is_root[n])
        
        # Rule C: Inactive Node -> Height = 0
        model.Add(node_height[n] == 0).OnlyEnforceIf(active_nodes[n].Not())
        
    # 5. Final Connectivity Check
    # If a node is active, it MUST be able to trace a path of heights back to the Root.
    # Therefore, its height must be > 0.
    for n in nodes:
        model.Add(node_height[n] > 0).OnlyEnforceIf(active_nodes[n])
        
    # Return matched signature variables
    # node_height functionally replaces the old 'rank'
    return node_height, is_root

```


----

### 生成树法 (Spinning Tree Method)

我们把这些谜题的格子以及相邻关系构成的图抽象成一个无向图。一个观察是：**这里的激活点集连通当且仅当它存在一棵生成树**。这引出了第一种编码方法的核心思想。

**定理**：设 $S$ 是非空点集，则 $G[S]$ 连通 $\iff$ 存在以 $S$ 中节点为顶点的树 $T$，使得：

1. $T$ 的所有顶点都在 $S$ 中
2. $T$ 的每条边都对应 $G$ 中的边
3. $S$ 中的每个节点都在 $T$ 中

我们引入**秩（rank）变量**和**父节点选择变量**，强制选中的节点形成一棵有根树。


对于每个节点 $v \in V$：

- $x_v \in \{0, 1\}$：节点 $v$ **是否被激活**；
- $r_v \in \{0, |V|\}$：节点 $v$ 在树中的秩/深度
- $\text{is_root}_v \in \{0, 1\}$：节点 $v$ 是否为树根
- $p_{v,u} \in \{0, 1\}$：节点 $u$ 是否为节点 $v$ 的父节点（对于每个邻居 $u \in N(v)$）

举个例子，对于如下左的Kuroshute谜题（要求白格连通），此时**以 (2,2) 位置为根，按照一定策略生成一棵树**（树的形状不唯一，此为示例），那么这一棵树就是如右图所示的样子。通过引入**秩（rank）变量**和**父节点选择变量**，强制选中的节点形成一棵有根树。

![](https://cdn.jsdelivr.net/gh/SmilingWayne/picsrepo/20260420152804918.png)

| 约束公式                                                               | 约束作用（核心含义）                         |
| ---------------------------------------------------------------------- | -------------------------------------------- |
| 1. $\sum is\_root_v = 1$                                               | 强制连通区域**有且仅有一个根节点**           |
| 2. $is\_root_v \Rightarrow x_v, \forall v$                             | 根节点必须是**激活**的有效节点               |
| 3. $\neg x_v \Rightarrow (r_v = 0 \land is\_root_v = 0)$               | 非激活节点没有秩、<br>**禁止成为根节点**     |
| 4. $is\_root_v \Rightarrow r_v = 0$                                    | 根节点的秩**固定为 0**                       |
| 5. $(x_v \land \neg is\_root_v) \Rightarrow r_v ≥ 1$                   | 活跃的非根节点**秩至少为 1**                 |
| 6. $p_{v,u} \Rightarrow (x_u \land r_v = r_u + 1)$                     | 父节点必须活跃，子节点秩**严格比父节点大 1** |
| 7. $(x_v \land \neg is\_root_v) \Rightarrow \sum_{u∈N(v)} p_{v,u} = 1$ | 活跃非根节点**必须有且仅有一个父节点**       |
| 8. $(is\_root_v \lor \neg x_v) \Rightarrow \sum_{u∈N(v)} p_{v,u} = 0$  | 根节点、非活跃节点**没有父节点**             |

参考代码如下：

```python
def add_connected_subgraph_constraint(
    model: cp.CpModel, 
    active_nodes: Dict[Hashable, cp.IntVar], 
    adjacency_map: Dict[Hashable, List[Hashable]],
    prefix: str = 'graph'
):
    nodes = list(active_nodes.keys())
    num_nodes = len(nodes)
    
    # 1. 变量
    rank = {n: model.NewIntVar(0, num_nodes, f"rank_{n}_{prefix}") for n in nodes}
    is_root = {n: model.NewBoolVar(f"is_root_{n}_{prefix}") for n in nodes}
    
    # 2. 全局约束
    model.Add(sum(is_root.values()) == 1)
    for n in nodes:
        model.AddImplication(is_root[n], active_nodes[n])

    # 3. 节点级约束
    for curr in nodes:
        # 非活跃节点
        model.Add(rank[curr] == 0).OnlyEnforceIf(active_nodes[curr].Not())
        model.Add(is_root[curr] == 0).OnlyEnforceIf(active_nodes[curr].Not())
        
        # 根节点
        model.Add(rank[curr] == 0).OnlyEnforceIf(is_root[curr])
        
        # 活跃非根节点
        model.Add(rank[curr] >= 1).OnlyEnforceIf([active_nodes[curr], is_root[curr].Not()])
        
        # 4. 父节点逻辑
        neighbors = adjacency_map.get(curr, [])
        parent_vars = []
        
        for neighbor in neighbors:
            if neighbor not in active_nodes:
                continue
            p_var = model.NewBoolVar(f"parent_{curr}_is_{neighbor}_{prefix}")
            parent_vars.append(p_var)
            
            model.AddImplication(p_var, active_nodes[neighbor])
            model.Add(rank[curr] == rank[neighbor] + 1).OnlyEnforceIf(p_var)
        
        # 5. 父节点计数
        model.Add(sum(parent_vars) == 1).OnlyEnforceIf([active_nodes[curr], is_root[curr].Not()])
        model.Add(sum(parent_vars) == 0).OnlyEnforceIf(is_root[curr])
        model.Add(sum(parent_vars) == 0).OnlyEnforceIf(active_nodes[curr].Not())
    
    return rank, is_root
```


| 指标     | 数量级     | 说明                     |
| -------- | ---------- | ------------------------ |
| 布尔变量 | $O(V + E)$ | is_root + parent 变量    |
| 整数变量 | $O(V)$     | rank 变量                |
| 约束数量 | $O(V + E)$ | 每个节点和边有常数列约束 |

---
