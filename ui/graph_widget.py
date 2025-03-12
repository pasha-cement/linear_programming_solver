"""
Виджет для графического отображения задачи линейного программирования
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

from modules.visual_module import LPVisualizer
from models.lp_problem import LPProblem

class GraphWidget(QWidget):
    """Виджет для графического отображения задачи линейного программирования"""
    
    def __init__(self, parent=None):
        """Инициализирует виджет графика"""
        super().__init__(parent)
        
        # Создаем фигуру и холст matplotlib
        self.figure = Figure(figsize=(6, 6), dpi=100, facecolor='white')
        self.canvas = FigureCanvasQTAgg(self.figure)
        
        # Создаем визуализатор
        self.visualizer = LPVisualizer(self.figure)
        
        # Создаем панель инструментов
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        
        # Добавляем элементы на виджет
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
    
    def set_problem(self, problem: LPProblem) -> None:
        """
        Устанавливает задачу для отображения
        
        Args:
            problem: Задача линейного программирования
        """
        self.visualizer.set_problem(problem)
        self.update_graph()
    
    def set_current_point(self, x1: float, x2: float) -> None:
        """
        Устанавливает текущую точку приближения
        
        Args:
            x1, x2: Координаты точки
        """
        self.visualizer.set_current_point(x1, x2)
        self.update_graph()
    
    def update_graph(self) -> None:
        """Обновляет график"""
        self.visualizer.draw()
    
    def update_config(self, config: dict) -> None:
        """
        Обновляет конфигурацию визуализации
        
        Args:
            config: Словарь с параметрами конфигурации
        """
        self.visualizer.update_config(config)
        self.update_graph()
    
    def clear(self) -> None:
        """Очищает график"""
        self.visualizer.clear()
        self.canvas.draw_idle()
    
    def save_figure(self, filepath: str) -> bool:
        """
        Сохраняет график в файл
        
        Args:
            filepath: Путь к файлу для сохранения
            
        Returns:
            True, если сохранение успешно, иначе False
        """
        try:
            self.figure.savefig(filepath, dpi=300, bbox_inches='tight')
            return True
        except Exception as e:
            print(f"Ошибка сохранения графика: {e}")
            return False