from AkariSolver import AkariSolver
from ShikakuSolver import ShikakuSolver
from TentSolver import TentSolver
from GappySolver import GappySolver
from TennerGridSolver import TennerGridSolver
from BinairoSolver import BinairoSolver
from PillsSolver import PillsSolver
from DominosSolver import DominosSolver
from BuraitoraitoSolver import BuraitoraitoSolver
from EuleroSolver import EuleroSolver
from MosaicSolver import MosaicSolver
from NonogramSolver import NonogramSolver

from typing import Dict, Any

class SolverFactory:
    """Solver Factory class"""
    
    _solvers = {
        'Akari': AkariSolver,
        'Shikaku': ShikakuSolver,
        'Tent': TentSolver,
        'Gappy': GappySolver,
        "TennerGrid": TennerGridSolver,
        "Binairo": BinairoSolver, 
        "Pills": PillsSolver, 
        "Dominos": DominosSolver,
        "Buraitoraito": BuraitoraitoSolver,
        "Eulero": EuleroSolver,
        "Mosaic": MosaicSolver, 
        "Nonogram": NonogramSolver
    }
    
    @classmethod
    def get_solver(cls, puzzle_name: str, puzzle_data: Dict):
        """Get Solver instance via name and input param"""
        solver_class = cls._solvers.get(puzzle_name)
        if solver_class:
            return solver_class(puzzle_data)
        raise ValueError(f"Unable to find solvers for Puzzle '{puzzle_name}'. Check spelling.")
    
    @classmethod
    def register_solver(cls, puzzle_name: str, solver_class):
        cls._solvers[puzzle_name] = solver_class
    
    @classmethod
    def get_available_puzzles(cls):
        return list(cls._solvers.keys())