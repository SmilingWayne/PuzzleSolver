# Slitherlink 推理算法分析

基于 `pzprjs/Puzzlink_Assistance.js` 中的 `SlitherlinkAssist()` 函数实现分析。

---

## 1. 核心数据结构

### 1.1 边标记 (Border QSUB)

```javascript
const BQSUB = {
    none: 0,   // 无标记
    link: 1,   // 连线（边经过）
    cross: 2,  // 叉（边不经过）
};
```

### 1.2 单元格标记 (Cell QSUB)

```javascript
const CQSUB = {
    none: 0,    // 无标记
    green: 1,   // 绿色（环路内部）
    yellow: 2,  // 黄色（环路外部）
};
```

### 1.3 辅助函数

```javascript
// 边的状态查询
isLine(b)  // 边是否为连线
isCross(b) // 边是否为叉

// 边的操作
add_line(b)  // 标记为连线
add_cross(b) // 标记为叉

// 单元格颜色操作
add_green(c)  // 标记为内部（绿色）
add_yellow(c) // 标记为外部（黄色）
isGreen(c)    // 是否为绿色
isYellow(c)   // 是否为黄色（包括边界外）
```

---

## 2. 推理流程架构

`SlitherlinkAssist()` 函数按以下顺序执行推理：

```
┌─────────────────────────────────────────┐
│  1. SingleLoopInBorder()                │
│     → 单一环路约束（边界传播）             │
├─────────────────────────────────────────┤
│  2. CellConnected() × 2                 │
│     → 单元格连通性分析（Tarjan 算法）       │
├─────────────────────────────────────────┤
│  3. 数字规则遍历所有单元格               │
│     → 0/3 规则、剩余计数、双 3 模式         │
├─────────────────────────────────────────┤
│  4. 颜色推理遍历所有单元格               │
│     → 数字 - 颜色约束、对角线推理          │
└─────────────────────────────────────────┘
```

---

## 3. 单一环路约束 (SingleLoopInBorder)

### 3.1 功能概述

确保最终形成的路径是**单一闭合环路**，不产生多个小环或断开的线段。

### 3.2 核心逻辑

```javascript
function SingleLoopInBorder() {
    // (1) 颜色连通性分析 - 两次调用 CellConnected
    CellConnected({
        isShaded: isGreen,      // 绿色区域视为"阴影"
        isUnshaded: isYellow,   // 黄色区域视为"非阴影"
        isLinked: (c, nb, nc) => isCross(nb),  // 叉视为"连通"
        isNotPassable: (c, nb, nc) => isLine(nb), // 线视为"不可通过"
    });
    
    CellConnected({
        isShaded: isYellow,
        isUnshaded: isGreen,
        OutsideAsShaded: true,  // 边界外视为黄色区域
    });
    
    // (2) 叉的候选约束（Cross QSUB）
    // (3) 交叉点连通性约束
    // (4) 多环检测
    // (5) 颜色推理
}
```

### 3.3 交叉点连通性规则

在四个边交汇的交叉点（cross）处：

| 连线数 | 叉数 | 推论 |
|--------|------|------|
| 2      | -    | 剩余两边必为叉 |
| 1      | 2    | 剩余一边必为连线 |
| -      | 3    | 剩余一边必为连线 |

```javascript
forEachCross(cross => {
    let blist = adjlist(cross.adjborder);  // 获取四条边
    let linecnt = blist.filter(b => isLine(b)).length;
    let crosscnt = blist.filter(b => isCross(b)).length;
    
    if (linecnt === 2 || crosscnt === 3) {
        blist.forEach(b => add_cross(b));  // 全标记为叉
    }
    if (linecnt === 1 && crosscnt === 2) {
        blist.forEach(b => add_line(b));   // 全标记为连线
    }
});
```

### 3.4 多环检测

```javascript
// 如果添加某条边会形成独立小环，则标记为叉
forEachBorder(border => {
    if (isCross(border) || isLine(border)) return;
    
    let cr1 = border.sidecross[0];
    let cr2 = border.sidecross[1];
    
    // 如果两端已在同一连通分量中，添加此边会形成环
    if (cr1.path !== null && cr1.path === cr2.path) {
        add_cross(border);
    }
});
```

### 3.5 叉候选约束 (Cross QSUB)

对每个交叉点维护**有效的连线对组合**：

```javascript
// 每个交叉点有 4 条边，合法状态是其中 2 条为连线（且相邻）
// 初始候选：所有 C(4,2)=6 种相邻边对
qsub = [
    [边0, 边1],  // 右上相邻
    [边1, 边2],  // 右下相邻
    [边2, 边3],  // 左下相邻
    [边3, 边0],  // 左上相邻
    [边0, 边2],  // 对角（非法，会被过滤）
    [边1, 边3],  // 对角（非法，会被过滤）
];

// 随着推理进行，过滤掉包含已标记为叉的边的组合
qsub = qsub.filter(s => s.every(i => !isCross(board.border[i])));

// 如果所有剩余候选都包含某条边 → 该边必为连线
if (qsub.every(s => s.includes(nb.id))) { 
    add_line(nb); 
}

// 如果所有剩余候选都不包含某条边 → 该边必为叉
if (qsub.every(s => !s.includes(nb.id))) { 
    add_cross(nb); 
}
```

---

## 4. 单元格连通性分析 (CellConnected)

### 4.1 算法原理

使用**Tarjan 割点算法**进行连通性分析，判断哪些单元格**必须**属于同一颜色区域。

### 4.2 核心参数

```javascript
CellConnected({
    isShaded: (c) => ...,      // 定义什么是"阴影"单元格
    isUnshaded: (c) => ...,    // 定义什么是"非阴影"单元格
    add_shaded: (c) => ...,    // 标记为阴影的回调
    add_unshaded: (c) => ...,  // 标记为非阴影的回调
    isLinked: (c, nb, nc) => ...,   // 定义什么是"连通"（通常是对边为叉）
    isNotPassable: (c, nb, nc) => ..., // 定义什么是"不可通过"（通常是对边为线）
    OutsideAsShaded: false,    // 是否将边界外视为阴影
});
```

### 4.3 在 Slitherlink 中的应用

**第一次调用**（绿色区域分析）：
```javascript
CellConnected({
    isShaded: c => isGreen(c) && c.qnum !== 3,
    isUnshaded: c => isYellow(c) || c.qsub === CQSUB.none && c.qnum === 3,
    add_shaded: add_green,
    add_unshaded: add_yellow,
    isLinked: (c, nb, nc) => isCross(nb),      // 叉视为连通
    isNotPassable: (c, nb, nc) => isLine(nb),  // 线视为阻断
});
```

**第二次调用**（黄色区域分析）：
```javascript
CellConnected({
    isShaded: c => isYellow(c) && c.qnum !== 3,
    isUnshaded: c => isGreen(c) || c.qsub === CQSUB.none && c.qnum === 3,
    add_shaded: add_yellow,
    add_unshaded: add_green,
    isLinked: (c, nb, nc) => isCross(nb),
    isNotPassable: (c, nb, nc) => isLine(nb),
    OutsideAsShaded: true,  // 边界外视为黄色
});
```

### 4.4 Tarjan 算法流程

```
1. DFS 遍历所有阴影单元格
2. 维护 ord[] (访问顺序) 和 low[] (可回溯的最小序)
3. 对于每个单元格 c：
   - 如果存在子节点 nc 满足 low[nc] >= ord[c]，则 c 是割点
   - 移除割点会使图不连通
4. 如果某个区域被判定为"无法与主区域连通"，则标记为对应颜色
```

### 4.5 推理规则

- **绿色区域必须连通**：所有绿色单元格通过叉边相连
- **黄色区域必须连通**：所有黄色单元格通过叉边相连（包括边界外）
- **线是屏障**：连线不能穿过同色区域
- **如果某单元格无法与对应颜色区域连通 → 必为另一颜色**

---

## 5. 数字规则

### 5.1 基础规则（遍历所有单元格）

```javascript
forEachCell(cell => {
    let blist = adjlist(cell.adjborder);  // 获取四条边
    
    // 规则 1：已确定连线数 = 数字 → 其余边全为叉
    if (blist.filter(b => isLine(b)).length === cell.qnum) {
        blist.forEach(b => add_cross(b));
    }
    
    // 规则 2：剩余未确定边数 = 数字 → 全为连线
    if (blist.filter(b => !isCross(b)).length === cell.qnum) {
        blist.forEach(b => add_line(b));
    }
});
```

### 5.2 0 的特殊处理

```javascript
// 0 周围四条边全为叉（在初始化时已处理）
if (cell.qnum === 0) {
    blist.forEach(b => add_cross(b));
}
```

### 5.3 双 3 模式 (3-3 Pattern)

```
    ×
┌─┬─┬─┐
│3│3│
└─┴─┴─┘
    ×
```

**条件**：
- 两个相邻单元格都是 3
- 全盘 3 的数量 > 2 或存在 2

**推论**：
```javascript
if (cell.qnum === 3 && offset(cell, 1, 0, d).qnum === 3) {
    // 三条竖边必为连线
    add_line(offset(cell, -.5, 0, d));
    add_line(offset(cell, .5, 0, d));
    add_line(offset(cell, 1.5, 0, d));
    // 两侧横边必为叉
    add_cross(offset(cell, .5, -1, d));
    add_cross(offset(cell, .5, 1, d));
}
```

### 5.4 叉 -2-3 模式

```
    ×
┌─┬─┬─┐
│×│2│3│
└─┴─┴─┘
    ×
```

**条件**：
- 2 和 3 相邻
- 2 的一侧已有叉

**推论**：
```javascript
if (cell.qnum === 2 && offset(cell, 1, 0, d).qnum === 3 
    && offset(cell, -.5, 0, d).qsub === BQSUB.cross) {
    add_line(offset(cell, 1.5, 0, d));  // 3 的外侧边
    add_cross(offset(cell, .5, -1, d)); // 3 的上下边
    add_cross(offset(cell, .5, 1, d));
}
```

### 5.5 隐式叉约束传播 (QSUB 传播)

对每个有数字的单元格，维护其周围四个交叉点的**合法状态组合**：

```javascript
if (cell.qnum >= 0) {
    // 获取四个交叉点的当前候选状态
    let list = [
        offset(cell, -.5, -.5),  // 左上
        offset(cell, .5, -.5),   // 右上
        offset(cell, -.5, .5),   // 左下
        offset(cell, .5, .5)     // 右下
    ];
    
    // 枚举所有合法的交叉点状态组合
    // 过滤掉不满足数字约束的组合
    // 更新每个交叉点的候选集
    
    list.forEach((cr, i) => {
        cr.setQsub(JSON.stringify(
            JSON.parse(cr.qsub).filter(s => 
                comblist.some(comb => 
                    JSON.stringify(comb[i]) === JSON.stringify(s)
                )
            )
        ));
    });
}
```

---

## 6. 颜色推理

### 6.1 颜色与数字的关系

| 数字 | 内部 (绿) 边数 | 外部 (黄) 边数 |
|------|----------------|----------------|
| 0    | 0              | 4              |
| 1    | 1              | 3              |
| 2    | 2              | 2              |
| 3    | 3              | 1              |

**关键观察**：
- 如果一个单元格是**绿色**，其周围四条边中，有 `cell.qnum` 条边连接外部（黄色单元格）
- 如果一个单元格是**黄色**，其周围四条边中，有 `4 - cell.qnum` 条边连接内部（绿色单元格）

### 6.2 基础颜色推理

```javascript
forEachCell(cell => {
    let innercnt = adjlist(cell.adjacent).filter(c => isGreen(c)).length;
    let outercnt = adjlist(cell.adjacent).filter(c => isYellow(c)).length;
    
    // 规则 1：数字 < 已知内部数 OR 4-数字 < 已知外部数 → 必为绿色
    if (cell.qnum < innercnt || 4 - cell.qnum < outercnt) {
        add_green(cell);
    }
    
    // 规则 2：数字 < 已知外部数 OR 4-数字 < 已知内部数 → 必为黄色
    if (cell.qnum < outercnt || 4 - cell.qnum < innercnt) {
        add_yellow(cell);
    }
});
```

### 6.3 颜色传播规则

```javascript
// 绿色单元格 + 外部数 = 数字 → 周围全为绿色
if (isGreen(cell) && cell.qnum === outercnt) {
    forEachSide(cell, (nb, nc) => add_green(nc));
}

// 黄色单元格 + 内部数 = 数字 → 周围全为黄色
if (isYellow(cell) && cell.qnum === innercnt) {
    forEachSide(cell, (nb, nc) => add_yellow(nc));
}

// 黄色单元格 + 外部数 = 4-数字 → 周围全为绿色
if (isYellow(cell) && cell.qnum === 4 - outercnt) {
    forEachSide(cell, (nb, nc) => add_green(nc));
}

// 绿色单元格 + 内部数 = 4-数字 → 周围全为黄色
if (isGreen(cell) && cell.qnum === 4 - innercnt) {
    forEachSide(cell, (nb, nc) => add_yellow(nc));
}
```

### 6.4 数字 2 的特殊规则

```javascript
// 外部数 = 2 → 周围全为绿色
if (cell.qnum === 2 && outercnt === 2) {
    forEachSide(cell, (nb, nc) => add_green(nc));
}

// 内部数 = 2 → 周围全为黄色
if (cell.qnum === 2 && innercnt === 2) {
    forEachSide(cell, (nb, nc) => add_yellow(nc));
}
```

### 6.5 1/3 的对角线推理

```
    ?
┌─┬─┬─┐
│G│3│Y│  G=绿色, Y=黄色 → 上下边必为叉/连线
└─┴─┴─┘
    ?
```

```javascript
if ((cell.qnum === 1 || cell.qnum === 3) && 
    innercnt === 1 && outercnt === 1) {
    forEachSide(cell, (nb, nc) => {
        if (!nc.isnull && nc.qsub === CQSUB.none) {
            if (cell.qnum === 1) { add_cross(nb); }  // 1 → 叉
            if (cell.qnum === 3) { add_line(nb); }   // 3 → 连线
        }
    });
}
```

### 6.6 3 的对角线同色推理

```javascript
// 如果 3 已有颜色，且对角单元格同色 → 两条夹边为连线
if (cell.qnum === 3 && cell.qsub !== CQSUB.none) {
    for (let d = 0; d < 4; d++) {
        if (offset(cell, 1, 1, d).qsub === cell.qsub) {
            add_line(offset(cell, -.5, 0, d));
            add_line(offset(cell, 0, -.5, d));
        }
    }
}
```

### 6.7 2 的 L 型推理

```
  ×
×· ·
  2 A   → A 和 B 同色
 · ·a
  Bb
```

```javascript
if (cell.qnum === 2) {
    for (let d = 0; d < 4; d++) {
        let b1 = offset(cell, -.5, -1, d);  // 左上叉
        let b2 = offset(cell, -1, -.5, d);  // 左下叉
        
        if (!(b1.isnull || isCross(b1))) continue;
        if (!(b2.isnull || isCross(b2))) continue;
        
        let c1 = offset(cell, 1, 0, d);
        let c2 = offset(cell, 0, 1, d);
        
        // A = B (同色)
        add_bg_color(c1, (c2.isnull ? CQSUB.yellow : c2.qsub));
        add_bg_color(c2, (c1.isnull ? CQSUB.yellow : c1.qsub));
    }
}
```

---

## 7. 可借鉴的设计模式

### 7.1 查询/更新分离

```javascript
// 查询函数（纯函数，无副作用）
isLine(b) => boolean
isGreen(c) => boolean

// 更新函数（触发重绘和步数检查）
add_line(b) { 
    b.setQsub(BQSUB.link); 
    b.draw(); 
    stepcheck(true); 
}
```

**优点**：
- 推理逻辑清晰，易于调试
- 可以追踪每一步推理
- 支持撤销/回溯

### 7.2 回调式 API 设计

```javascript
CellConnected({
    isShaded: ...,      // 策略模式
    isUnshaded: ...,
    add_shaded: ...,
    add_unshaded: ...,
});
```

**优点**：
- 同一算法可复用于不同谜题类型
- 易于扩展新规则

### 7.3 候选集约束传播

```javascript
// 维护每个交叉点的合法状态组合
qsub.filter(s => /* 过滤条件 */);

// 当候选集缩小到一定程度时触发新推理
if (qsub.every(s => s.includes(nb.id))) { 
    add_line(nb); 
}
```

**优点**：
- 自动传播约束
- 无需手动编写大量 if-else

### 7.4 迭代式推理

```javascript
let stepcnt = 0;
do {
    stepcnt = 0;
    SlitherlinkAssist();  // 执行一轮推理
} while (stepcnt > 0);    // 直到没有新推断
```

**优点**：
- 每轮推理都基于最新状态
- 避免复杂的依赖排序

---

## 8. 总结

### 8.1 推理层次

```
┌──────────────────────────────────────┐
│ Layer 4: 全局约束（单环、连通性）      │
├──────────────────────────────────────┤
│ Layer 3: 颜色传播（对角线、邻域）      │
├──────────────────────────────────────┤
│ Layer 2: 数字规则（3-3、2-3 模式）     │
├──────────────────────────────────────┤
│ Layer 1: 基础规则（0、剩余计数）       │
└──────────────────────────────────────┘
```

### 8.2 关键算法

| 算法 | 用途 | 复杂度 |
|------|------|--------|
| Tarjan 割点 | 连通性分析 | O(V+E) |
| 并查集 | 路径连通分量 | O(α(n)) |
| 候选集枚举 | 交叉点约束 | O(2^4) |
| 迭代传播 | 全局收敛 | 取决于谜题 |

### 8.3 对 puzzlekit 的启示

1. **分离状态层**：将 `edge_values`（实际值）和 `edge_marks`（推理标记）分开
2. **使用回调模式**：推理引擎不直接修改状态，而是通过回调通知
3. **候选集传播**：引入类似 Cross QSUB 的机制处理复杂约束
4. **迭代执行**：每轮推理后检查是否有新推断，直到收敛
