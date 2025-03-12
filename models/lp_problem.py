import numpy as np
from enum import Enum
from typing import List, Tuple, Optional

class ConstraintType(Enum):
    LESS_EQUAL = "≤"
    EQUAL = "="
    GREATER_EQUAL = "≥"

class Constraint:
    """Представляет ограничение в задаче линейного программирования"""
    
    def __init__(self, a1: float, a2: float, b: float, constraint_type: ConstraintType):
        """
        Инициализирует ограничение вида a1·x1 + a2·x2 {≤,=,≥} b
        
        Args:
            a1: Коэффициент при x1
            a2: Коэффициент при x2
            b: Правая часть
            constraint_type: Тип ограничения (≤, =, ≥)
        """
        self.a1 = a1
        self.a2 = a2
        self.b = b
        self.constraint_type = constraint_type
    
    def is_satisfied(self, x1: float, x2: float, eps: float = 1e-10) -> bool:
        """Проверяет, удовлетворяет ли точка (x1, x2) данному ограничению"""
        left_side = self.a1 * x1 + self.a2 * x2
        
        if self.constraint_type == ConstraintType.LESS_EQUAL:
            return left_side <= self.b + eps
        elif self.constraint_type == ConstraintType.EQUAL:
            return abs(left_side - self.b) <= eps
        else:  # GREATER_EQUAL
            return left_side >= self.b - eps
    
    def get_line_points(self, x_range: Tuple[float, float]) -> Tuple[List[float], List[float]]:
        """
        Возвращает точки для построения линии ограничения в заданном диапазоне x1
        
        Args:
            x_range: Диапазон значений x1 (мин, макс)
            
        Returns:
            Кортеж из двух списков (x1_points, x2_points)
        """
        x1_min, x1_max = x_range
        x1_points = [x1_min, x1_max]
        
        # Проверяем, не параллельна ли линия оси x1
        if abs(self.a2) < 1e-10:
            if abs(self.a1) < 1e-10:
                return [], []  # Некорректное ограничение (0 = b или 0 ≤/≥ b)
            
            # Линия вертикальная (x1 = b/a1)
            x1_val = self.b / self.a1
            if x1_min <= x1_val <= x1_max:
                return [x1_val, x1_val], [x1_min, x1_max]
            return [], []
        
        # Вычисляем соответствующие значения x2
        x2_points = [(self.b - self.a1 * x1) / self.a2 for x1 in x1_points]
        return x1_points, x2_points
    
    def __str__(self) -> str:
        """Строковое представление ограничения"""
        return f"{self.a1}·x₁ + {self.a2}·x₂ {self.constraint_type.value} {self.b}"


class LPProblem:
    """Представляет задачу линейного программирования"""
    
    def __init__(self, c1: float = 0.0, c2: float = 0.0):
        """
        Инициализирует задачу линейного программирования с целевой функцией c1·x1 + c2·x2 → max
        
        Args:
            c1: Коэффициент при x1 в целевой функции
            c2: Коэффициент при x2 в целевой функции
        """
        self.c1 = c1
        self.c2 = c2
        self.constraints: List[Constraint] = []
        # Массив угловых точек в формате [(x1, x2, [indices]), ...], где indices - индексы ограничений
        self.corner_points: List[Tuple[float, float, List[int]]] = []
    
    def add_constraint(self, a1: float, a2: float, b: float, constraint_type: ConstraintType) -> None:
        """Добавляет ограничение в задачу"""
        constraint = Constraint(a1, a2, b, constraint_type)
        self.constraints.append(constraint)
    
    def remove_constraint(self, index: int) -> None:
        """Удаляет ограничение по индексу"""
        if 0 <= index < len(self.constraints):
            self.constraints.pop(index)
    
    def objective_value(self, x1: float, x2: float) -> float:
        """Вычисляет значение целевой функции в точке (x1, x2)"""
        return self.c1 * x1 + self.c2 * x2
    
    def gradient(self) -> Tuple[float, float]:
        """Возвращает градиент целевой функции"""
        return (self.c1, self.c2)
    
    def is_feasible(self, x1: float, x2: float) -> bool:
        """Проверяет, принадлежит ли точка (x1, x2) области допустимых решений"""
        return all(constraint.is_satisfied(x1, x2) for constraint in self.constraints)
    
    def find_corner_points(self) -> List[Tuple[float, float, List[int]]]:
        """
        Находит все угловые точки области допустимых решений
        
        Returns:
            Список кортежей (x1, x2, [indices]), где indices - индексы формирующих ограничений
        """
        n = len(self.constraints)
        corner_points = []
        
        # Перебираем все пары ограничений
        for i in range(n):
            for j in range(i + 1, n):
                constr1 = self.constraints[i]
                constr2 = self.constraints[j]
                
                # Формируем систему уравнений A * x = b
                A = np.array([[constr1.a1, constr1.a2], 
                              [constr2.a1, constr2.a2]])
                b = np.array([constr1.b, constr2.b])
                
                # Проверяем определитель (линейную независимость)
                if abs(np.linalg.det(A)) < 1e-10:
                    continue  # Прямые параллельны или совпадают
                
                # Решаем систему
                try:
                    x1, x2 = np.linalg.solve(A, b)
                    
                    # Проверяем, удовлетворяет ли точка всем ограничениям
                    if self.is_feasible(x1, x2):
                        corner_points.append((x1, x2, [i, j]))
                except np.linalg.LinAlgError:
                    continue  # Если система не имеет решения
        
        self.corner_points = corner_points
        return corner_points
    
    def move_in_gradient_direction(self, x1: float, x2: float, step: float, 
                                  anti_gradient: bool = False) -> Tuple[float, float]:
        """
        Перемещает точку в направлении градиента или антиградиента
        
        Args:
            x1, x2: Текущие координаты точки
            step: Размер шага
            anti_gradient: Если True, движение происходит в направлении антиградиента
            
        Returns:
            Новые координаты точки (x1_new, x2_new)
        """
        grad_x1, grad_x2 = self.gradient()
        
        if anti_gradient:
            grad_x1 = -grad_x1
            grad_x2 = -grad_x2
        
        # Нормализуем градиент
        norm = (grad_x1**2 + grad_x2**2)**0.5
        if norm < 1e-10:
            return x1, x2  # Градиент близок к нулю
        
        grad_x1 /= norm
        grad_x2 /= norm
        
        # Вычисляем новую точку
        x1_new = x1 + step * grad_x1
        x2_new = x2 + step * grad_x2
        
        return x1_new, x2_new
    
    def to_dict(self) -> dict:
        """Преобразует задачу в словарь для сериализации"""
        return {
            "c1": self.c1,
            "c2": self.c2,
            "constraints": [
                {
                    "a1": constraint.a1,
                    "a2": constraint.a2,
                    "b": constraint.b,
                    "type": constraint.constraint_type.value
                }
                for constraint in self.constraints
            ]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LPProblem':
        """Создает задачу из словаря"""
        problem = cls(data["c1"], data["c2"])
        
        for constr_data in data["constraints"]:
            if constr_data["type"] == "≤":
                constr_type = ConstraintType.LESS_EQUAL
            elif constr_data["type"] == "=":
                constr_type = ConstraintType.EQUAL
            else:
                constr_type = ConstraintType.GREATER_EQUAL
                
            problem.add_constraint(
                constr_data["a1"],
                constr_data["a2"],
                constr_data["b"],
                constr_type
            )
        
        return problem