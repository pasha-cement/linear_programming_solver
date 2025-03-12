"""
Модуль расчета для решения задач линейного программирования
"""
from typing import List, Tuple, Optional
import numpy as np
from models.lp_problem import LPProblem, ConstraintType

class Calculator:
    """Класс, отвечающий за математические расчеты в задаче линейного программирования"""
    
    def __init__(self, lp_problem: LPProblem):
        """
        Инициализирует калькулятор с заданной задачей
        
        Args:
            lp_problem: Задача линейного программирования
        """
        self.lp_problem = lp_problem
        
    def find_optimal_solution(self) -> Optional[Tuple[float, float, float, List[int]]]:
        """
        Находит оптимальное решение задачи линейного программирования
        
        Returns:
            Кортеж (x1, x2, value, [indices]) или None, если решения нет
            x1, x2 - координаты оптимальной точки
            value - значение целевой функции
            indices - индексы ограничений, формирующих оптимальную точку
        """
        corner_points = self.lp_problem.find_corner_points()
        
        if not corner_points:
            return None  # Нет угловых точек (ОДР пуста или неограничена)
        
        # Находим точку с максимальным значением целевой функции
        best_point = max(
            corner_points,
            key=lambda p: self.lp_problem.objective_value(p[0], p[1])
        )
        
        x1, x2, indices = best_point
        value = self.lp_problem.objective_value(x1, x2)
        
        return x1, x2, value, indices
    
    def is_bounded(self) -> bool:
        """
        Проверяет, является ли область допустимых решений ограниченной
        
        Returns:
            True, если ОДР ограничена, иначе False
        """
        # В 2D задаче ОДР ограничена, если для каждой координатной оси 
        # есть ограничения, ограничивающие значения переменных сверху и снизу
        
        has_x1_lower_bound = False
        has_x1_upper_bound = False
        has_x2_lower_bound = False
        has_x2_upper_bound = False
        
        for constraint in self.lp_problem.constraints:
            # Проверяем ограничения на x1
            if abs(constraint.a2) < 1e-10:  # Коэффициент при x2 близок к нулю
                if constraint.a1 > 0:
                    if constraint.constraint_type == ConstraintType.LESS_EQUAL:
                        has_x1_upper_bound = True
                    elif constraint.constraint_type == ConstraintType.GREATER_EQUAL:
                        has_x1_lower_bound = True
                elif constraint.a1 < 0:
                    if constraint.constraint_type == ConstraintType.LESS_EQUAL:
                        has_x1_lower_bound = True
                    elif constraint.constraint_type == ConstraintType.GREATER_EQUAL:
                        has_x1_upper_bound = True
            
            # Проверяем ограничения на x2
            if abs(constraint.a1) < 1e-10:  # Коэффициент при x1 близок к нулю
                if constraint.a2 > 0:
                    if constraint.constraint_type == ConstraintType.LESS_EQUAL:
                        has_x2_upper_bound = True
                    elif constraint.constraint_type == ConstraintType.GREATER_EQUAL:
                        has_x2_lower_bound = True
                elif constraint.a2 < 0:
                    if constraint.constraint_type == ConstraintType.LESS_EQUAL:
                        has_x2_lower_bound = True
                    elif constraint.constraint_type == ConstraintType.GREATER_EQUAL:
                        has_x2_upper_bound = True
        
        return (has_x1_lower_bound and has_x1_upper_bound and 
                has_x2_lower_bound and has_x2_upper_bound)
    
    def suggest_initial_point(self) -> Optional[Tuple[float, float]]:
        """
        Предлагает начальную точку в области допустимых решений
        
        Returns:
            Координаты начальной точки (x1, x2) или None, если область пуста
        """
        corner_points = self.lp_problem.find_corner_points()
        
        if corner_points:
            # Предлагаем первую угловую точку
            return corner_points[0][0], corner_points[0][1]
        
        # Если угловых точек нет, пробуем найти произвольную внутреннюю точку
        # Для простоты, можно брать произвольные точки и проверять их допустимость
        for x1 in np.linspace(0, 10, 20):
            for x2 in np.linspace(0, 10, 20):
                if self.lp_problem.is_feasible(x1, x2):
                    return x1, x2
        
        return None  # Не удалось найти допустимую точку