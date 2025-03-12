"""
Модуль хранения для сохранения и загрузки задач линейного программирования
"""
import os
import json
from typing import Optional
from models.lp_problem import LPProblem, ConstraintType

class StorageManager:
    """Класс для управления сохранением и загрузкой задач линейного программирования"""
    
    @staticmethod
    def save_problem(problem: LPProblem, filepath: str) -> bool:
        """
        Сохраняет задачу линейного программирования в JSON-файл
        
        Args:
            problem: Задача линейного программирования
            filepath: Путь к файлу для сохранения
            
        Returns:
            True, если сохранение успешно, иначе False
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(problem.to_dict(), file, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения задачи: {e}")
            return False
    
    @staticmethod
    def load_problem(filepath: str) -> Optional[LPProblem]:
        """
        Загружает задачу линейного программирования из JSON-файла
        
        Args:
            filepath: Путь к файлу для загрузки
            
        Returns:
            Задача линейного программирования или None в случае ошибки
        """
        try:
            if not os.path.exists(filepath):
                print(f"Файл '{filepath}' не найден")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            return LPProblem.from_dict(data)
        except Exception as e:
            print(f"Ошибка загрузки задачи: {e}")
            return None
    
    @staticmethod
    def export_to_latex(problem: LPProblem, filepath: str) -> bool:
        """
        Экспортирует задачу линейного программирования в формат LaTeX
        
        Args:
            problem: Задача линейного программирования
            filepath: Путь к файлу для сохранения
            
        Returns:
            True, если экспорт успешен, иначе False
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as file:
                # Заголовок документа
                file.write("\\documentclass{article}\n")
                file.write("\\usepackage{amsmath}\n")
                file.write("\\begin{document}\n\n")
                
                # Целевая функция
                file.write("\\section*{Задача линейного программирования}\n\n")
                file.write("\\subsection*{Целевая функция}\n\n")
                file.write("\\begin{equation}\n")
                file.write(f"f(x_1, x_2) = {problem.c1}x_1 + {problem.c2}x_2 \\to \\max\n")
                file.write("\\end{equation}\n\n")
                
                # Ограничения
                file.write("\\subsection*{Ограничения}\n\n")
                file.write("\\begin{align}\n")
                
                for i, constraint in enumerate(problem.constraints):
                    sign = ""
                    if constraint.constraint_type == ConstraintType.LESS_EQUAL:
                        sign = "\\leq"
                    elif constraint.constraint_type == ConstraintType.EQUAL:
                        sign = "="
                    else:  # GREATER_EQUAL
                        sign = "\\geq"
                    
                    file.write(f"{constraint.a1}x_1 + {constraint.a2}x_2 {sign} {constraint.b}")
                    if i < len(problem.constraints) - 1:
                        file.write(" \\\\\n")
                    else:
                        file.write("\n")
                
                file.write("\\end{align}\n\n")
                
                # Дополнительные ограничения неотрицательности
                file.write("\\subsection*{Дополнительные ограничения}\n\n")
                file.write("\\begin{align}\n")
                file.write("x_1 \\geq 0, x_2 \\geq 0\n")
                file.write("\\end{align}\n\n")
                
                file.write("\\end{document}\n")
            
            return True
        except Exception as e:
            print(f"Ошибка экспорта в LaTeX: {e}")
            return False