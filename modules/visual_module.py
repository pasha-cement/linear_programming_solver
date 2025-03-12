"""
Модуль визуализации для графического представления задач линейного программирования
"""
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional, Dict, Any
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.patches import Polygon
from models.lp_problem import LPProblem, ConstraintType

class LPVisualizer:
    """Класс для визуализации задач линейного программирования"""
    
    def __init__(self, figure: Figure):
        """
        Инициализирует визуализатор с заданной фигурой matplotlib
        
        Args:
            figure: Фигура matplotlib для отрисовки
        """
        self.fig = figure
        self.ax = self.fig.add_subplot(111)
        self.lp_problem: Optional[LPProblem] = None
        self.current_point: Optional[Tuple[float, float]] = None
        self.level_line: Optional[plt.Line2D] = None
        self.config = {
            'x_range': (-10, 10),
            'y_range': (-10, 10),
            'grid': True,
            'constraint_colors': plt.cm.tab20.colors,
            'constraint_alpha': 0.2,
            'feasible_region_color': 'lightblue',
            'feasible_region_alpha': 0.5,
            'current_point_color': 'red',
            'corner_point_color': 'green',
            'gradient_color': 'orange',
            'level_line_color': 'purple',
            'line_width': 1.5
        }
    
    def set_problem(self, lp_problem: LPProblem) -> None:
        """
        Устанавливает задачу для визуализации
        
        Args:
            lp_problem: Задача линейного программирования
        """
        self.lp_problem = lp_problem
    
    def set_current_point(self, x1: float, x2: float) -> None:
        """
        Устанавливает текущую точку приближения
        
        Args:
            x1, x2: Координаты точки
        """
        self.current_point = (x1, x2)
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """
        Обновляет настройки визуализации
        
        Args:
            config: Словарь с новыми настройками
        """
        self.config.update(config)
    
    def clear(self) -> None:
        """Очищает график"""
        if hasattr(self, 'ax') and self.ax is not None:
            self.ax.clear()
            self.level_line = None
    
    def draw_axes(self) -> None:
        """Отрисовывает оси координат и сетку"""
        x_min, x_max = self.config['x_range']
        y_min, y_max = self.config['y_range']
        
        # Устанавливаем пределы осей
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        
        # Добавляем сетку
        if self.config['grid']:
            self.ax.grid(True, linestyle='--', alpha=0.6)
        
        # Настраиваем оси
        self.ax.spines['left'].set_position('zero')
        self.ax.spines['bottom'].set_position('zero')
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        
        # Добавляем подписи к осям
        self.ax.set_xlabel(r'$x_1$', fontsize=12)
        self.ax.set_ylabel(r'$x_2$', fontsize=12)
        self.ax.xaxis.set_label_coords(0.98, 0.01)
        self.ax.yaxis.set_label_coords(0.01, 0.98)
    
    def draw_constraints(self) -> None:
        """Отрисовывает ограничения и области, соответствующие каждому ограничению"""
        if not self.lp_problem:
            return
        
        x_min, x_max = self.config['x_range']
        y_min, y_max = self.config['y_range']
        
        for i, constraint in enumerate(self.lp_problem.constraints):
            # Рисуем линию ограничения
            color_idx = i % len(self.config['constraint_colors'])
            color = self.config['constraint_colors'][color_idx]
            
            x1_points, x2_points = constraint.get_line_points((x_min, x_max))
            if x1_points:  # Если линия пересекает область отображения
                line = self.ax.plot(
                    x1_points, x2_points,
                    color=color,
                    linewidth=self.config['line_width'],
                    label=f'Ограничение {i+1}'
                )
                
                # Добавляем надпись
                mid_idx = len(x1_points) // 2
                self.ax.annotate(
                    f'C{i+1}',
                    (x1_points[mid_idx], x2_points[mid_idx]),
                    xytext=(5, 5),
                    textcoords='offset points',
                    color=color
                )
                
                # Заштриховываем допустимую область для ограничения
                vertices = []
                
                if constraint.constraint_type == ConstraintType.LESS_EQUAL:
                    # Добавляем точки для полуплоскости ax + by ≤ c
                    if constraint.a2 != 0:
                        # Находим точки пересечения с границами окна
                        x1_left = x_min
                        x2_left = (constraint.b - constraint.a1 * x1_left) / constraint.a2
                        x1_right = x_max
                        x2_right = (constraint.b - constraint.a1 * x1_right) / constraint.a2
                        
                        if constraint.a2 > 0:
                            vertices = [
                                (x1_left, x2_left),
                                (x1_right, x2_right),
                                (x1_right, y_min),
                                (x1_left, y_min)
                            ]
                        else:
                            vertices = [
                                (x1_left, x2_left),
                                (x1_right, x2_right),
                                (x1_right, y_max),
                                (x1_left, y_max)
                            ]
                    elif constraint.a1 != 0:
                        # Вертикальная линия
                        x1_val = constraint.b / constraint.a1
                        if constraint.a1 > 0:
                            vertices = [
                                (x1_val, y_min),
                                (x1_val, y_max),
                                (x_min, y_max),
                                (x_min, y_min)
                            ]
                        else:
                            vertices = [
                                (x1_val, y_min),
                                (x1_val, y_max),
                                (x_max, y_max),
                                (x_max, y_min)
                            ]
                
                elif constraint.constraint_type == ConstraintType.GREATER_EQUAL:
                    # Добавляем точки для полуплоскости ax + by ≥ c
                    if constraint.a2 != 0:
                        # Находим точки пересечения с границами окна
                        x1_left = x_min
                        x2_left = (constraint.b - constraint.a1 * x1_left) / constraint.a2
                        x1_right = x_max
                        x2_right = (constraint.b - constraint.a1 * x1_right) / constraint.a2
                        
                        if constraint.a2 < 0:
                            vertices = [
                                (x1_left, x2_left),
                                (x1_right, x2_right),
                                (x1_right, y_min),
                                (x1_left, y_min)
                            ]
                        else:
                            vertices = [
                                (x1_left, x2_left),
                                (x1_right, x2_right),
                                (x1_right, y_max),
                                (x1_left, y_max)
                            ]
                    elif constraint.a1 != 0:
                        # Вертикальная линия
                        x1_val = constraint.b / constraint.a1
                        if constraint.a1 < 0:
                            vertices = [
                                (x1_val, y_min),
                                (x1_val, y_max),
                                (x_min, y_max),
                                (x_min, y_min)
                            ]
                        else:
                            vertices = [
                                (x1_val, y_min),
                                (x1_val, y_max),
                                (x_max, y_max),
                                (x_max, y_min)
                            ]
                
                if vertices:
                    polygon = Polygon(
                        vertices,
                        closed=True,
                        alpha=self.config['constraint_alpha'],
                        color=color,
                        fill=True,
                        edgecolor=None
                    )
                    self.ax.add_patch(polygon)
    
    def draw_feasible_region(self) -> None:
        """Отрисовывает область допустимых решений"""
        if not self.lp_problem or not self.lp_problem.constraints:
            return
        
        x_min, x_max = self.config['x_range']
        y_min, y_max = self.config['y_range']
        
        # Создаем сетку для проверки точек
        x1_grid = np.linspace(x_min, x_max, 100)
        x2_grid = np.linspace(y_min, y_max, 100)
        X1, X2 = np.meshgrid(x1_grid, x2_grid)
        
        # Маска для допустимых точек
        mask = np.ones_like(X1, dtype=bool)
        
        for constraint in self.lp_problem.constraints:
            for i in range(X1.shape[0]):
                for j in range(X1.shape[1]):
                    if not constraint.is_satisfied(X1[i, j], X2[i, j]):
                        mask[i, j] = False
        
        # Отрисовываем допустимую область
        self.ax.imshow(
            mask,
            origin='lower',
            extent=(x_min, x_max, y_min, y_max),
            alpha=self.config['feasible_region_alpha'],
            cmap=plt.cm.Blues,
            aspect='auto'
        )
    
    def draw_corner_points(self) -> None:
        """Отрисовывает угловые точки области допустимых решений"""
        if not self.lp_problem:
            return
        
        corner_points = self.lp_problem.corner_points
        if not corner_points:
            # Если угловые точки еще не найдены, находим их
            corner_points = self.lp_problem.find_corner_points()
        
        for i, point in enumerate(corner_points):
            x1, x2, _ = point
            self.ax.plot(
                x1, x2,
                marker='o',
                markersize=6,
                color=self.config['corner_point_color'],
                label=f'Точка {i+1}' if i == 0 else ""
            )
            self.ax.annotate(
                f'P{i+1}',
                (x1, x2),
                xytext=(5, 5),
                textcoords='offset points'
            )
    
    def draw_current_point(self) -> None:
        """Отрисовывает текущую точку приближения"""
        if not self.current_point:
            return
        
        x1, x2 = self.current_point
        self.ax.plot(
            x1, x2,
            marker='X',
            markersize=10,
            color=self.config['current_point_color'],
            label='Текущая точка'
        )
        
        if self.lp_problem:
            value = self.lp_problem.objective_value(x1, x2)
            self.ax.annotate(
                f'f = {value:.2f}',
                (x1, x2),
                xytext=(10, -10),
                textcoords='offset points',
                color=self.config['current_point_color'],
                fontweight='bold'
            )
    
    def draw_gradient(self) -> None:
        """Отрисовывает градиент целевой функции в текущей точке"""
        if not self.lp_problem or not self.current_point:
            return
        
        x1, x2 = self.current_point
        grad_x1, grad_x2 = self.lp_problem.gradient()
        
        # Нормализуем градиент для отображения
        norm = (grad_x1**2 + grad_x2**2)**0.5
        if norm < 1e-10:
            return  # Градиент близок к нулю
        
        scale = 1.0  # Масштабирующий коэффициент для длины стрелки
        
        self.ax.arrow(
            x1, x2,
            scale * grad_x1 / norm, scale * grad_x2 / norm,
            head_width=0.2,
            head_length=0.3,
            fc=self.config['gradient_color'],
            ec=self.config['gradient_color'],
            label='Градиент'
        )
    
    def draw_level_line(self) -> None:
        """Отрисовывает линию уровня целевой функции, проходящую через текущую точку"""
        if not self.lp_problem or not self.current_point:
            return
        
        x1, x2 = self.current_point
        grad_x1, grad_x2 = self.lp_problem.gradient()
        
        if abs(grad_x1) < 1e-10 and abs(grad_x2) < 1e-10:
            return  # Градиент близок к нулю
        
        # Значение целевой функции в текущей точке
        value = self.lp_problem.objective_value(x1, x2)
        
        x_min, x_max = self.config['x_range']
        y_min, y_max = self.config['y_range']
        
        # Находим точки пересечения линии уровня с границами окна
        if abs(grad_x1) < 1e-10:  # Линия параллельна оси x1
            x1_points = [x_min, x_max]
            x2_points = [x2, x2]
        elif abs(grad_x2) < 1e-10:  # Линия параллельна оси x2
            x1_points = [x1, x1]
            x2_points = [y_min, y_max]
        else:
            # Общий случай: c1*x1 + c2*x2 = value
            # x2 = (value - c1*x1) / c2
            x1_left = x_min
            x2_left = (value - grad_x1 * x1_left) / grad_x2
            x1_right = x_max
            x2_right = (value - grad_x1 * x1_right) / grad_x2
            
            x1_points = [x1_left, x1_right]
            x2_points = [x2_left, x2_right]
        
        # Отрисовываем линию уровня
        if self.level_line:
            self.level_line.set_data(x1_points, x2_points)
        else:
            self.level_line = self.ax.plot(
                x1_points, x2_points,
                '--',
                color=self.config['level_line_color'],
                linewidth=1.0,
                label='Линия уровня'
            )[0]
    
    def draw(self) -> None:
        """Отрисовывает всю задачу линейного программирования"""
        self.clear()
        self.draw_axes()
        
        if self.lp_problem:
            # Отрисовываем задачу
            self.draw_constraints()
            self.draw_feasible_region()
            self.draw_corner_points()
            
            if self.current_point:
                self.draw_current_point()
                self.draw_level_line()
                self.draw_gradient()
        
        # Добавляем легенду
        self.ax.legend(loc='upper right')
        
        # Обновляем холст
        self.fig.canvas.draw_idle()