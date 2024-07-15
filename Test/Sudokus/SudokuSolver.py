
from itertools import combinations
from ortools.sat.python import cp_model as cp
import math

class CompoundSudokuSolver:
    
    def __init__(
        self, 
        grid, 
        X = 9, 
        Y = 9, 
        std_rule = True,
        killer = None,
        petite_killer = None,
        consecutive = None,
        sandwich = None,
        anti_knight = None,
        anti_king = None,
        arrow = None,
        thermo = None, 
        greater_than = None,
        jigsaw = None,
        vudoku = None,
        all_nine = None,
        XV = None,
        diagonal = False) -> None:
        
        self.grid = grid
        self.X = X
        self.Y = Y
        self.std_rule = std_rule
        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.x = {}
        self.killer = killer
        self.petite_killer = petite_killer
        self.consecutive = consecutive
        self.sandwich = sandwich
        self.anti_knight = anti_knight
        self.anti_king = anti_king
        self.arrow = arrow
        self.thermo = thermo
        self.diagonal = diagonal
        self.greater_than = greater_than
        self.jigsaw = jigsaw
        self.vudoku = vudoku
        self.all_nine = all_nine
        self.XV = XV
        # list (tuple), 
        # 7 2
        # 8 2
        # 10 3 
        # first tuple value indicates the index of corner
        # second tuple value indicates the shape of corner:
        #     0:    ｜        2:--｜
        #         __｜            ｜
        # 
        #     1:  ｜          3: ｜--
        #         ｜__           ｜

        self.aux_sand = None
        self.vudoku_aux = None
        self.consecutive_aux = None
        self.result = ""
        
        assert X == Y

        for i in range(Y):
            for j in range(X):
                if self.grid[i * self.Y + j] == "0":
                    self.x[i, j] = self.model.NewIntVar(1, self.X, f'x[{i}, {j}]')
                else:
                    self.x[i, j] = int(self.grid[i * self.X + j])
                
    def addStandardConstr(self):
        
        """_summary_
            Add standard Sudoku Constraint
        """
        
        for i in range(self.Y):
            row = [self.x[i, j] for j in range(self.X)]
            self.model.AddAllDifferent(row)
            col = [self.x[j, i] for j in range(self.Y)]
            self.model.AddAllDifferent(col)
        
        for i in range(int(math.sqrt(self.X)) - 1):
            for j in range(int(math.sqrt(self.Y)) - 1):
                l = int(math.sqrt(self.X))
                cell = [
                    self.x[r, c]
                    for r in range(i* l, i * l + l)
                    for c in range(j* l, j * l + l)
                ]
                self.model.AddAllDifferent(cell)
    
    def addConsecutiveConstr(self):
    # c = sum([x[i] == val for i in range(len(x))])
    
    # n = len(x)
    # b = [model.NewBoolVar(f"b[{i}]")  for i in range(n)]
    # for i in range(n):
    #     model.Add((x[i] == val)).OnlyEnforceIf(b[i])
    #     model.Add((x[i] != val)).OnlyEnforceIf(b[i].Not())
    # model.Add(c == sum(b))
        self.consecutive_aux = {}
        for idx, sub_char in enumerate(self.consecutive):
            sub_a, sub_b = idx // 17, idx % 17
            if sub_char == ".":
                self.consecutive_aux[f"{sub_a}_{sub_b}_1"] = self.model.NewBoolVar(name = f"{sub_a}_{sub_b}_1")
                self.consecutive_aux[f"{sub_a}_{sub_b}_2"] = self.model.NewBoolVar(name = f"{sub_a}_{sub_b}_2")
                if sub_b <= 7:
                    self.model.Add(self.x[int(sub_a), int(sub_b)] - self.x[int(sub_a), int(sub_b) + 1] == 1).OnlyEnforceIf(self.consecutive_aux[f"{sub_a}_{sub_b}_1"])
                    self.model.Add(self.x[int(sub_a), int(sub_b)] - self.x[int(sub_a), int(sub_b) + 1] != 1).OnlyEnforceIf(self.consecutive_aux[f"{sub_a}_{sub_b}_1"].Not())
                    self.model.Add(self.x[int(sub_a), int(sub_b)] - self.x[int(sub_a), int(sub_b) + 1] == -1).OnlyEnforceIf(self.consecutive_aux[f"{sub_a}_{sub_b}_2"])
                    self.model.Add(self.x[int(sub_a), int(sub_b)] - self.x[int(sub_a), int(sub_b) + 1] != -1).OnlyEnforceIf(self.consecutive_aux[f"{sub_a}_{sub_b}_2"].Not())
                    self.model.Add(self.consecutive_aux[f"{sub_a}_{sub_b}_1"] + self.consecutive_aux[f"{sub_a}_{sub_b}_2"] == 0)
                elif sub_b <= 16:
                    self.model.Add(self.x[int(sub_a), int(sub_b) - 8] - self.x[int(sub_a) + 1, int(sub_b) - 8] == 1).OnlyEnforceIf(self.consecutive_aux[f"{sub_a}_{sub_b}_1"])
                    self.model.Add(self.x[int(sub_a), int(sub_b) - 8] - self.x[int(sub_a) + 1, int(sub_b) - 8] != 1).OnlyEnforceIf(self.consecutive_aux[f"{sub_a}_{sub_b}_1"].Not())
                    self.model.Add(self.x[int(sub_a), int(sub_b) - 8] - self.x[int(sub_a) + 1, int(sub_b) - 8] == -1).OnlyEnforceIf(self.consecutive_aux[f"{sub_a}_{sub_b}_2"])
                    self.model.Add(self.x[int(sub_a), int(sub_b) - 8] - self.x[int(sub_a) + 1, int(sub_b) - 8] != -1).OnlyEnforceIf(self.consecutive_aux[f"{sub_a}_{sub_b}_2"].Not())
                    self.model.Add(self.consecutive_aux[f"{sub_a}_{sub_b}_1"] + self.consecutive_aux[f"{sub_a}_{sub_b}_2"] == 0)
                continue
            if sub_b <= 7:
                self.model.AddAbsEquality(1, self.x[int(sub_a), int(sub_b)] - self.x[int(sub_a), int(sub_b) + 1])
            elif sub_b <= 16:
                self.model.AddAbsEquality(1, self.x[int(sub_a), int(sub_b) - 8] - self.x[int(sub_a) + 1, int(sub_b) - 8])
        # for _, cage in enumerate(self.consecutive):
        #     self.model.AddAbsEquality(1, self.x[cage[0][0], cage[0][1]] - self.x[cage[1][0], cage[1][1]])
             
    def addDiagonalConstr(self):
        
        """_summary_
            Add diagonal Constraints.
        """
        
        ltr = []
        rtl = []
        for i in range(self.Y):
            ltr.append(self.x[i, i])
            rtl.append(self.X - i - 1, i)
        self.model.AddAllDifferent(ltr)
        self.model.AddAllDifferent(rtl)
            
    def printgrid(self):    
        
        """_summary_
            Print the final grid
        """
    
        for i in range(self.Y):
            for j in range(self.X):
                print(self.solver.Value(self.x[i, j]), end=" ")
                self.result += str(self.solver.Value(self.x[i, j]))
            print()
        print()

        print("NumConflicts:", self.solver.NumConflicts())
        print("NumBranches:", self.solver.NumBranches())
        print("WallTime:", self.solver.WallTime())
        
        # for i in range(9):
        #     for j in range(6):
        #         print(self.solver.Value(self.aux_sand["R", i, j]))
    
    def addKillerConstr(self):
        """_summary_
            Add killer constraint from data
        """
        
        for (res, segment) in self.killer:
            cage = [self.x[i[0], i[1]] for i in segment]
            self.model.Add(sum(cage) == res)
            self.model.AddAllDifferent(cage)
    
    def addPetiteKillerConstr(self):
        """_summary_
            增加小杀手数独约束
        Raises:
            Exception: _description_
            Exception: _description_
        """
        if len(self.petite_killer[0]) != self.X:
            raise Exception("小杀手数独斜行和数量有误。")
        for line in self.petite_killer:
            if line[0] == "TL":
                for i in range(self.X - 1):
                    constrCages = []
                    for j in range(i + 1):
                        constrCages.append(self.x[j, i - j])
                    self.model.Add(sum(constrCages) == line[i + 1])

            elif line[0] == "RT":
                
                for i in range(self.X - 1):
                    constrCages = []
                    for j in range(i + 1):
                        constrCages.append(self.x[j, self.X - i + j - 1])
                    self.model.Add(sum(constrCages) == line[i + 1])

            elif line[0] == "BR":
                for i in range(self.X - 1):
                    constrCages = []
                    for j in range(self.X - 1 - i):
                        constrCages.append(self.x[self.X - 1 - j, 1 + i +  j])
                    self.model.Add(sum(constrCages) == line[i + 1])

                    
            elif line[0] == "LB":
            
                for i in range(self.X - 1):
                    constrCages = []
                    for j in range(self.X - 1 - i):
                        constrCages.append(self.x[1 + j + i,  j])
                    self.model.Add(sum(constrCages) == line[i + 1])

            else:
                raise Exception("检查小杀手数独位置元素字符串, 必须为TL / RT / BR / LB 中的一个")

    def addThermoConstr(self):
        """_summary_
            Thermo constraints
        """
        for thermo_ in self.thermo:
            for idx in range(len(thermo_) - 1):
                self.model.Add(self.x[thermo_[idx][0], thermo_[idx][1]] < self.x[thermo_[idx + 1][0], thermo_[idx + 1][1]])
        
    def addSandwichConstr(self):
        """
            Add sandwich Sudoku Constrs
        """
        self.aux_sand = {}
        
        # x[i,j] = 9 -> Bool = True
        # x[i,j] <= 8 -> Bool = False
        # False -> x[i, j] <= 8
        
        # True
        for nums in self.sandwich:
            if nums[0] == "R":
                for idx, num in enumerate(nums[1:]):
                    if num < 0:
                        continue
                    # cnt = 0
                    for index, cbn in enumerate(combinations([i for i in range(self.X)], 2)):

                        self.aux_sand["R", idx, index,  0] = self.model.NewBoolVar(f"R, {idx}, {index}, 0")
                        self.aux_sand["R", idx, index,  1] = self.model.NewBoolVar(f"R, {idx}, {index}, 1")
                        self.aux_sand["R", idx, index,  2] = self.model.NewBoolVar(f"R, {idx}, {index}, 2")
                        self.aux_sand["R", idx, index,  3] = self.model.NewBoolVar(f"R, {idx}, {index}, 3")
                        self.aux_sand["R", idx, index,  4] = self.model.NewBoolVar(f"R, {idx}, {index}, 4")
                        self.aux_sand["R", idx, index,  5] = self.model.NewBoolVar(f"R, {idx}, {index}, 5")

                        
                        self.model.Add(self.x[cbn[0], idx] == 1).OnlyEnforceIf(self.aux_sand["R", idx, index, 0])
                        self.model.Add(self.x[cbn[0], idx] >= 2).OnlyEnforceIf(self.aux_sand["R", idx, index, 0].Not())

                        
                        self.model.Add(self.x[cbn[1], idx] == 9).OnlyEnforceIf(self.aux_sand["R", idx, index, 1])
                        self.model.Add(self.x[cbn[1], idx] <= 8).OnlyEnforceIf(self.aux_sand["R", idx, index, 1].Not())
                        
                        self.model.Add(self.aux_sand["R", idx,  index, 0] + self.aux_sand["R", idx, index,  1] == 2).OnlyEnforceIf(self.aux_sand["R", idx, index, 4])
                        self.model.Add(self.aux_sand["R", idx,  index, 0] + self.aux_sand["R", idx, index,  1] <= 1).OnlyEnforceIf(self.aux_sand["R", idx, index, 4].Not())
                        
                        self.model.Add(sum(self.x[j, idx] for j in range(cbn[0] + 1, cbn[1] )) == num).OnlyEnforceIf(self.aux_sand["R",idx, index, 4])
                        # self.model.Add(sum(self.x[j, idx] for j in range(cbn[0] + 1, cbn[1] - 1)) != num).OnlyEnforceIf(self.aux_sand["R",idx, index, 4])
                        
                        self.model.Add(self.x[cbn[0], idx] == 9).OnlyEnforceIf(self.aux_sand["R", idx, index,  2])
                        self.model.Add(self.x[cbn[0], idx] <= 8).OnlyEnforceIf(self.aux_sand["R", idx, index,  2].Not())

                        
                        self.model.Add(self.x[cbn[1], idx] == 1).OnlyEnforceIf(self.aux_sand["R", idx, index,  3])
                        self.model.Add(self.x[cbn[1], idx] >= 2).OnlyEnforceIf(self.aux_sand["R", idx, index,  3].Not())

                        
                        self.model.Add(self.aux_sand["R", idx, index, 2] + self.aux_sand["R", idx, index,  3] == 2).OnlyEnforceIf(self.aux_sand["R", idx, index, 5])
                        self.model.Add(self.aux_sand["R", idx, index, 2] + self.aux_sand["R", idx, index,  3] <= 1).OnlyEnforceIf(self.aux_sand["R", idx, index, 5].Not())
                        
                        self.model.Add(sum(self.x[j, idx] for j in range(cbn[0] + 1, cbn[1] )) == num).OnlyEnforceIf(self.aux_sand["R",idx, index, 5])
                       
                   
                        
            elif nums[0] == "C":
                if nums[0] == "R":
                    for idx, num in enumerate(nums[1:]):
                        if num < 0:
                            continue
                        # cnt = 0
                        for index, cbn in enumerate(combinations([i for i in range(self.X)], 2)):
                            self.aux_sand["C", idx, index,  0] = self.model.NewBoolVar(f"R, {idx}, {index}, 0")
                            self.aux_sand["C", idx, index,  1] = self.model.NewBoolVar(f"R, {idx}, {index}, 1")
                            self.aux_sand["C", idx, index,  2] = self.model.NewBoolVar(f"R, {idx}, {index}, 2")
                            self.aux_sand["C", idx, index,  3] = self.model.NewBoolVar(f"R, {idx}, {index}, 3")
                            self.aux_sand["C", idx, index,  4] = self.model.NewBoolVar(f"R, {idx}, {index}, 4")
                            self.aux_sand["C", idx, index,  5] = self.model.NewBoolVar(f"R, {idx}, {index}, 5")

                            
                            self.model.Add(self.x[idx, cbn[0]] == 1).OnlyEnforceIf(self.aux_sand["C", idx, index, 0])
                            self.model.Add(self.x[idx, cbn[0]] >= 2).OnlyEnforceIf(self.aux_sand["C", idx, index, 0].Not())

                            
                            self.model.Add(self.x[idx, cbn[1]] == 9).OnlyEnforceIf(self.aux_sand["C", idx, index, 1])
                            self.model.Add(self.x[idx, cbn[1]] <= 8).OnlyEnforceIf(self.aux_sand["C", idx, index, 1].Not())
                            
                            self.model.Add(self.aux_sand["C", idx,  index, 0] + self.aux_sand["C", idx, index,  1] == 2).OnlyEnforceIf(self.aux_sand["C", idx, index, 4])
                            self.model.Add(self.aux_sand["C", idx,  index, 0] + self.aux_sand["C", idx, index,  1] <= 1).OnlyEnforceIf(self.aux_sand["C", idx, index, 4].Not())
                            
                            self.model.Add(sum(self.x[idx, j] for j in range(cbn[0] + 1, cbn[1] )) == num).OnlyEnforceIf(self.aux_sand["R",idx, index, 4])
                            # self.model.Add(sum(self.x[j, idx] for j in range(cbn[0] + 1, cbn[1] - 1)) != num).OnlyEnforceIf(self.aux_sand["R",idx, index, 4])
                            
                            self.model.Add(self.x[idx, cbn[0]] == 9).OnlyEnforceIf(self.aux_sand["C", idx, index,  2])
                            self.model.Add(self.x[idx, cbn[0]] <= 8).OnlyEnforceIf(self.aux_sand["C", idx, index,  2].Not())

                            
                            self.model.Add(self.x[idx, cbn[1]] == 1).OnlyEnforceIf(self.aux_sand["C", idx, index,  3])
                            self.model.Add(self.x[idx, cbn[1]] >= 2).OnlyEnforceIf(self.aux_sand["C", idx, index,  3].Not())

                            
                            self.model.Add(self.aux_sand["C", idx, index, 2] + self.aux_sand["C", idx, index,  3] == 2).OnlyEnforceIf(self.aux_sand["C", idx, index, 5])
                            self.model.Add(self.aux_sand["C", idx, index, 2] + self.aux_sand["C", idx, index,  3] <= 1).OnlyEnforceIf(self.aux_sand["C", idx, index, 5].Not())
                            self.model.Add(sum(self.x[idx, j] for j in range(cbn[0] + 1, cbn[1] )) == num).OnlyEnforceIf(self.aux_sand["R",idx, index, 4]) 

    def addAntiKnightConstr(self):
        
        offsets = [
            (-2, 1), 
            (-2, -1), 
            (-1, 2), 
            (-1, -2), 
            (1, 2), 
            (1, -2), 
            (2, 1), 
            (2, -1)
        ]
        for i in range(self.Y):
            for j in range(self.X):
                for offset in offsets:
                    if (i + offset[0] >= 0 and i + offset[0] < self.Y) and (j + offset[1] >= 0 and j + offset[1] < self.X):
                        self.model.Add(self.x[i, j] != self.x[i + offset[0], j + offset[1]])
        
    def addAntiKingConstr(self):
        
        offs = [-1, 0, 1]
        for i in range(self.Y):
            for j in range(self.X):
                for ofx in offs:
                    for ofy in offs:
                        if (i + ofx >= 0 and i + ofx < self.Y) and (j + ofy >= 0 and j + ofy < self.X) and (ofy != 0 and ofx != 0):
                            self.model.Add(self.x[i, j] != self.x[i + ofx, j + ofy])
        
    def addArrowConstr(self):

        for arrow_ in self.arrow:
            self.model.Add(self.x[arrow_[0][0], arrow_[0][1]] == sum([self.x[ar[0], ar[1]] for ar in arrow_[1:]]))
            
    def addGreaterThanConstr(self):
        for idx, oper in enumerate(self.greater_than):
            cage, sub_cage =  (idx ) // 12 , (idx ) % 12
            if oper == "-":
                continue
            central_x, central_y =   (cage % 3) * 3 + 1, (cage // 3) * 3  + 1
            if sub_cage == 0:
                self.model.Add(self.x[central_y - 1, central_x - 1] > self.x[ central_y - 1, central_x]) if oper == ">" else  self.model.Add(self.x[central_y - 1, central_x - 1] < self.x[central_y - 1, central_x])
            elif sub_cage == 1:
                self.model.Add(self.x[central_y - 1, central_x] > self.x[central_y - 1, central_x + 1]) if oper == ">" else  self.model.Add(self.x[central_y - 1, central_x] < self.x[central_y - 1, central_x + 1])
            elif sub_cage == 2:
                self.model.Add(self.x[central_y - 1, central_x - 1] < self.x[central_y, central_x - 1]) if oper == ">" else  self.model.Add(self.x[central_y - 1, central_x - 1 ] > self.x[central_y, central_x - 1])
            elif sub_cage == 3:
                self.model.Add(self.x[central_y - 1, central_x  ] < self.x[ central_y, central_x ]) if oper == ">" else  self.model.Add(self.x[central_y - 1, central_x ] > self.x[central_y, central_x])
            elif sub_cage == 4:
                self.model.Add(self.x[central_y - 1, central_x + 1 ] < self.x[central_y, central_x + 1 ]) if oper == ">" else  self.model.Add(self.x[central_y - 1 , central_x + 1] > self.x[central_y, central_x + 1])
            elif sub_cage == 5:
                self.model.Add(self.x[central_y, central_x - 1] > self.x[central_y, central_x]) if oper == ">" else  self.model.Add(self.x[central_y, central_x - 1] < self.x[central_y, central_x])
            elif sub_cage == 6:
                self.model.Add(self.x[central_y, central_x] > self.x[central_y, central_x + 1]) if oper == ">" else  self.model.Add(self.x[central_y, central_x] < self.x[central_y, central_x + 1])
            elif sub_cage == 7:
                self.model.Add(self.x[central_y, central_x  - 1  ] < self.x[central_y + 1, central_x  - 1  ]) if oper == ">" else  self.model.Add(self.x[central_y , central_x  - 1 ] > self.x[central_y + 1, central_x  - 1 ])
            elif sub_cage == 8:
                self.model.Add(self.x[central_y, central_x ] < self.x[central_y + 1, central_x ]) if oper == ">" else  self.model.Add(self.x[central_y, central_x ] > self.x[central_y + 1, central_x])
            elif sub_cage == 9:
                self.model.Add(self.x[central_y, central_x  + 1 ] < self.x[central_y + 1, central_x + 1 ]) if oper == ">" else  self.model.Add(self.x[central_y, central_x + 1 ] > self.x[central_y + 1, central_x + 1])
            elif sub_cage == 10:
                self.model.Add(self.x[central_y + 1, central_x - 1] > self.x[central_y + 1, central_x]) if oper == ">" else  self.model.Add(self.x[central_y + 1, central_x - 1] < self.x[central_y + 1, central_x])
            elif sub_cage == 11:
                self.model.Add(self.x[central_y + 1, central_x] > self.x[central_y + 1, central_x + 1]) if oper == ">" else  self.model.Add(self.x[central_y + 1, central_x] < self.x[central_y + 1, central_x + 1])
    
    def addJigsawConstr(self):
        for i in range(self.Y):
            row = [self.x[i, j] for j in range(self.X)]
            self.model.AddAllDifferent(row)
            col = [self.x[j, i] for j in range(self.Y)]
            self.model.AddAllDifferent(col)
        new_grid = dict()
        for idx, char_ in enumerate(self.jigsaw):
            if char_ not in new_grid:
                new_grid[char_] = []
            new_grid[char_].append(idx)
        
        for k, v in new_grid.items():
            cell = [self.x[idx // 9, idx % 9] for idx in v]
            self.model.AddAllDifferent(cell)

    def addVudokuConstr(self):
        self.vudoku_aux = [self.model.NewBoolVar(f"aux_{i}") for i in range(3 * len(self.vudoku))]
        for idx, val  in enumerate(self.vudoku):
            cornerCentral, cornerShape = val[0], val[1]
            xx, yy  = cornerCentral // self.Y, cornerCentral % self.Y
            aroundCorner = []
            if cornerShape == 0:
                aroundCorner = [(xx, yy - 1), (xx - 1, yy)]
            elif cornerShape == 1:
                aroundCorner = [(xx - 1, yy), ((xx, yy + 1))]
            elif cornerShape == 2:
                aroundCorner = [(xx, yy - 1), (xx + 1, yy )]
            else:
                aroundCorner = [(xx, yy + 1), (xx + 1, yy )]

            self.model.Add(
                (self.x[aroundCorner[0][0], aroundCorner[0][1]] + self.x[aroundCorner[1][0], aroundCorner[1][1]] == self.x[xx, yy])).OnlyEnforceIf(self.vudoku_aux[idx * 3])
            self.model.Add(
                (self.x[aroundCorner[0][0], aroundCorner[0][1]] + self.x[aroundCorner[1][0], aroundCorner[1][1]] != self.x[xx, yy])).OnlyEnforceIf(self.vudoku_aux[idx * 3].Not())
            self.model.Add(
                (self.x[aroundCorner[0][0], aroundCorner[0][1]] - self.x[aroundCorner[1][0], aroundCorner[1][1]] == self.x[xx, yy])).OnlyEnforceIf(self.vudoku_aux[idx * 3 + 1])
            self.model.Add(
                (self.x[aroundCorner[0][0], aroundCorner[0][1]] - self.x[aroundCorner[1][0], aroundCorner[1][1]] != self.x[xx, yy])).OnlyEnforceIf(self.vudoku_aux[idx * 3 + 1].Not())
            self.model.Add(
                (self.x[aroundCorner[1][0], aroundCorner[1][1]] - self.x[aroundCorner[0][0], aroundCorner[0][1]] == self.x[xx, yy])).OnlyEnforceIf(self.vudoku_aux[idx * 3 + 2])
            self.model.Add(
                (self.x[aroundCorner[1][0], aroundCorner[1][1]] - self.x[aroundCorner[0][0], aroundCorner[0][1]] != self.x[xx, yy])).OnlyEnforceIf(self.vudoku_aux[idx * 3 + 2].Not())
            self.model.Add(sum(self.vudoku_aux[idx * 3 : idx * 3 + 3]) == 1)
            
            # 限制上述情况只能取一种发生
            
    def addAllNineConstr(self):
        all_nine_dict = dict()
        for idx, cell in enumerate(self.all_nine):
            if cell == "0":
                continue
            else:
                if cell not in all_nine_dict:
                    all_nine_dict[cell] = []
                all_nine_dict[cell].append((idx // self.X, idx % self.Y))
        for _, cells in all_nine_dict.items():
            self.model.AddAllDifferent([self.x[cell[0], cell[1]] for cell in cells])
    
    def addXVConstr(self):
        # Sudoku XV(Evil) https://gridpuzzle.com/vx-sudoku/159j0
        for idx, sub_ in enumerate(self.XV):
            if sub_ == "-":
                continue
            sub_a, sub_b = idx // 17 , idx % 17 
            if sub_ == "V":
                if sub_b <= 7:
                    self.model.Add(self.x[int(sub_a), int(sub_b)] + self.x[int(sub_a), int(sub_b) + 1] == 5)
                elif sub_b <= 16:
                    self.model.Add(self.x[int(sub_a), int(sub_b) - 8] + self.x[int(sub_a) + 1, int(sub_b) - 8] == 5)
            elif sub_ == "X":
                if sub_b <= 7:
                    self.model.Add(self.x[int(sub_a), int(sub_b)] + self.x[int(sub_a), int(sub_b) + 1] == 10)
                elif sub_b <= 16:
                    self.model.Add(self.x[int(sub_a), int(sub_b) - 8] + self.x[int(sub_a) + 1, int(sub_b) - 8] == 10)
        
        
    def solveall(self):

        if self.std_rule and self.jigsaw == None:
            self.addStandardConstr()
        
        if self.jigsaw != None:
            self.addJigsawConstr()
        
        if self.diagonal:
            self.addDiagonalConstr()
        if self.killer != None:
            self.addKillerConstr()
        if self.petite_killer != None:
            self.addPetiteKillerConstr()
        if self.consecutive != None:
            self.addConsecutiveConstr()
        if self.sandwich != None:
            self.addSandwichConstr()
        if self.anti_knight != None and self.anti_knight == True:
            self.addAntiKnightConstr()
        if self.anti_king != None and self.anti_king == True:
            self.addAntiKingConstr()
        if self.thermo != None:
            self.addThermoConstr()
        if self.arrow != None:
            self.addArrowConstr()
        if self.greater_than != None:
            if len(self.greater_than) == 108:
                self.addGreaterThanConstr()
        if self.vudoku != None:
            self.addVudokuConstr()
        if self.all_nine != None:
            self.addAllNineConstr()
        if self.XV != None:
            self.addXVConstr()
        
        status = self.solver.Solve(self.model)

        if status == cp.OPTIMAL:
            self.printgrid()
            return self.result

        elif status == cp.INFEASIBLE:
            print("模型不可行")
            return ""
            # self.model.ExportToFile("./help.txt")
        else:
            print("无法在规定时间内求解")
            return ""
        # else:
        #     print("没有找到可行方案")
        #     self.model.ExportToFile("./help.txt")

if __name__ == "__main__":
    pass