"""
Модуль ввода для обработки пользовательского ввода задачи линейного программирования
"""
from typing import List, Tuple, Optional, Dict, Any
from models.lp_problem import LPProblem, ConstraintType

class InputParser:
    """Класс для парсинга пользовательского ввода задачи линейного программирования"""
    
    @staticmethod
    def parse_objective_function(text: str) -> Tuple[float, float]:
        """
        Разбирает строку целевой функции и извлекает коэффициенты
        
        Args:
            text: Строка вида "c1*x1 + c2*x2"
            
        Returns:
            Кортеж (c1, c2) с коэффициентами целевой функции
        """
        text = text.strip().replace(" ", "")
        
        try:
            # Инициализируем значения по умолчанию
            c1, c2 = 0.0, 0.0
            
            # Разбиваем строку по '+' и '-'
            parts = []
            current_part = ""
            for i, char in enumerate(text):
                if char in ('+', '-') and i > 0:
                    parts.append(current_part)
                    current_part = char
                else:
                    current_part += char
            parts.append(current_part)
            
            # Обрабатываем каждую часть
            for part in parts:
                part = part.strip()
                if not part:
                    continue
                
                if "x1" in part:
                    # Извлекаем коэффициент при x1
                    c1_str = part.replace("x1", "").strip()
                    if c1_str in ("+", ""):
                        c1 = 1.0
                    elif c1_str == "-":
                        c1 = -1.0
                    else:
                        c1 = float(c1_str)
                elif "x2" in part:
                    # Извлекаем коэффициент при x2
                    c2_str = part.replace("x2", "").strip()
                    if c2_str in ("+", ""):
                        c2 = 1.0
                    elif c2_str == "-":
                        c2 = -1.0
                    else:
                        c2 = float(c2_str)
                elif part:
                    # Если нет переменной, это свободный член, который не используется
                    pass
            
            return c1, c2
        except Exception as e:
            # Если возникла ошибка при разборе, возвращаем нулевые коэффициенты
            print(f"Ошибка разбора целевой функции: {e}")
            return 0.0, 0.0
    
    @staticmethod
    def parse_constraint(text: str) -> Optional[Tuple[float, float, float, ConstraintType]]:
        """
        Разбирает строку ограничения и извлекает коэффициенты и тип ограничения
        
        Args:
            text: Строка вида "a1*x1 + a2*x2 {<=,=,>=} b"
            
        Returns:
            Кортеж (a1, a2, b, constraint_type) с коэффициентами и типом ограничения,
            или None в случае ошибки
        """
        text = text.strip()
        
        try:
            # Определяем тип ограничения
            if "<=" in text:
                constraint_type = ConstraintType.LESS_EQUAL
                parts = text.split("<=")
            elif ">=" in text:
                constraint_type = ConstraintType.GREATER_EQUAL
                parts = text.split(">=")
            elif "=" in text:
                constraint_type = ConstraintType.EQUAL
                parts = text.split("=")
            else:
                print(f"Ошибка: неверный тип ограничения в строке '{text}'")
                return None
            
            if len(parts) != 2:
                print(f"Ошибка: неверный формат ограничения '{text}'")
                return None
            
            # Разбираем левую часть (коэффициенты при переменных)
            left_part = parts[0].strip()
            a1, a2 = InputParser.parse_objective_function(left_part)
            
            # Разбираем правую часть (свободный член)
            right_part = parts[1].strip()
            b = float(right_part)
            
            return a1, a2, b, constraint_type
        except Exception as e:
            print(f"Ошибка разбора ограничения: {e}")
            return None
    
    @staticmethod
    def create_problem_from_text(objective_text: str, constraints_text: str) -> LPProblem:
        """
        Создает задачу линейного программирования из текстового описания
        
        Args:
            objective_text: Строка целевой функции
            constraints_text: Строки ограничений, разделенные переносом строки
            
        Returns:
            Объект задачи линейного программирования
        """
        # Создаем целевую функцию
        c1, c2 = InputParser.parse_objective_function(objective_text)
        problem = LPProblem(c1, c2)
        
        # Добавляем ограничения
        for line in constraints_text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            
            constraint_data = InputParser.parse_constraint(line)
            if constraint_data:
                a1, a2, b, constraint_type = constraint_data
                problem.add_constraint(a1, a2, b, constraint_type)
        
        return problem