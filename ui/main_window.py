"""
Главное окно программы для решения задач линейного программирования
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QDockWidget, QAction, QFileDialog, QMessageBox,
                            QTabWidget, QSplitter, QLabel)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QIcon

from ui.graph_widget import GraphWidget
from ui.input_widgets import (ObjectiveFunctionWidget, ConstraintsTableWidget, 
                             CornerPointsWidget, GradientControlWidget)
from models.lp_problem import LPProblem
from modules.calc_module import Calculator
from modules.storage_module import StorageManager

class MainWindow(QMainWindow):
    """Главное окно программы"""
    
    def __init__(self):
        """Инициализирует главное окно"""
        super().__init__()
        
        self.setWindowTitle("Решение задач линейного программирования")
        self.setMinimumSize(1000, 700)
        
        # Создаем объекты для работы с задачей ЛП
        self.lp_problem = LPProblem()
        self.calculator = Calculator(self.lp_problem)
        
        # Инициализируем интерфейс
        self.init_ui()
        
        # Устанавливаем текущую точку по умолчанию
        self.current_point = (0, 0)
        self.graph_widget.set_current_point(*self.current_point)
    
    def init_ui(self):
        """Инициализирует пользовательский интерфейс"""
        # Создаем центральный виджет
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Создаем разделитель для рабочей области
        splitter = QSplitter(Qt.Horizontal)
        
        # Левая часть - виджет графика
        self.graph_widget = GraphWidget()
        splitter.addWidget(self.graph_widget)
        
        # Правая часть - панель управления
        control_panel = QTabWidget()
        
        # Вкладка ввода задачи
        input_tab = QWidget()
        input_layout = QVBoxLayout(input_tab)
        
        # Добавляем виджеты на вкладку ввода
        self.objective_widget = ObjectiveFunctionWidget()
        self.constraints_widget = ConstraintsTableWidget()
        
        input_layout.addWidget(self.objective_widget)
        input_layout.addWidget(self.constraints_widget)
        
        # Вкладка анализа
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout(analysis_tab)
        
        # Добавляем виджеты на вкладку анализа
        self.corner_points_widget = CornerPointsWidget()
        self.gradient_control_widget = GradientControlWidget()
        
        analysis_layout.addWidget(self.corner_points_widget)
        analysis_layout.addWidget(self.gradient_control_widget)
        analysis_layout.addStretch()
        
        # Добавляем вкладки в панель управления
        control_panel.addTab(input_tab, "Условие задачи")
        control_panel.addTab(analysis_tab, "Анализ")
        
        splitter.addWidget(control_panel)
        
        # Добавляем разделитель в главный макет
        main_layout.addWidget(splitter)
        
        # Устанавливаем центральный виджет
        self.setCentralWidget(central_widget)
        
        # Создаем меню
        self.create_menus()
        
        # Подключаем сигналы
        self.connect_signals()
        
        # Обновляем задачу ЛП с начальными данными
        self.update_lp_problem()
    
    def create_menus(self):
        """Создает строку меню приложения"""
        # Меню "Файл"
        file_menu = self.menuBar().addMenu("Файл")
        
        new_action = QAction("Новая задача", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.on_new_problem)
        file_menu.addAction(new_action)
        
        open_action = QAction("Открыть...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.on_open_problem)
        file_menu.addAction(open_action)
        
        save_action = QAction("Сохранить...", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.on_save_problem)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_graph_action = QAction("Экспорт графика...", self)
        export_graph_action.triggered.connect(self.on_export_graph)
        file_menu.addAction(export_graph_action)
        
        export_latex_action = QAction("Экспорт в LaTeX...", self)
        export_latex_action.triggered.connect(self.on_export_latex)
        file_menu.addAction(export_latex_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Вид"
        view_menu = self.menuBar().addMenu("Вид")
        
        show_grid_action = QAction("Показать сетку", self)
        show_grid_action.setCheckable(True)
        show_grid_action.setChecked(True)
        show_grid_action.triggered.connect(self.on_toggle_grid)
        view_menu.addAction(show_grid_action)
        
        # Меню "Решение"
        solve_menu = self.menuBar().addMenu("Решение")
        
        find_corner_points_action = QAction("Найти угловые точки", self)
        find_corner_points_action.triggered.connect(self.on_find_corner_points)
        solve_menu.addAction(find_corner_points_action)
        
        find_optimal_action = QAction("Найти оптимальное решение", self)
        find_optimal_action.triggered.connect(self.on_find_optimal)
        solve_menu.addAction(find_optimal_action)
        
        # Меню "Помощь"
        help_menu = self.menuBar().addMenu("Помощь")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.on_about)
        help_menu.addAction(about_action)
    
    def connect_signals(self):
        """Подключает сигналы для виджетов"""
        # Сигналы виджета целевой функции
        self.objective_widget.coefficientsChanged.connect(self.on_coefficients_changed)
        
        # Сигналы виджета ограничений
        self.constraints_widget.constraintsChanged.connect(self.on_constraints_changed)
        
        # Сигналы виджета угловых точек
        self.corner_points_widget.pointSelected.connect(self.on_point_selected)
        
        # Сигналы виджета управления градиентным методом
        self.gradient_control_widget.moveRequested.connect(self.on_move_requested)
    
    def update_lp_problem(self):
        """Обновляет объект задачи ЛП на основе введенных данных"""
        # Получаем коэффициенты целевой функции
        c1, c2 = self.objective_widget.get_coefficients()
        self.lp_problem.c1 = c1
        self.lp_problem.c2 = c2
        
        # Получаем ограничения
        constraints_data = self.constraints_widget.get_constraints()
        
        # Очищаем текущие ограничения
        self.lp_problem.constraints.clear()
        
        # Добавляем новые ограничения
        for a1, a2, b, constraint_type in constraints_data:
            self.lp_problem.add_constraint(a1, a2, b, constraint_type)
        
        # Обновляем график
        self.graph_widget.set_problem(self.lp_problem)
        
        # Обновляем виджет угловых точек
        self.corner_points_widget.set_problem(self.lp_problem)
        
        # Обновляем калькулятор
        self.calculator.lp_problem = self.lp_problem
    
    def on_coefficients_changed(self):
        """Обработчик изменения коэффициентов целевой функции"""
        self.update_lp_problem()
    
    def on_constraints_changed(self):
        """Обработчик изменения ограничений"""
        self.update_lp_problem()
    
    def on_point_selected(self, x1, x2):
        """Обработчик выбора точки"""
        self.current_point = (x1, x2)
        self.graph_widget.set_current_point(x1, x2)
    
    def on_move_requested(self, step_size, anti_gradient):
        """
        Обработчик запроса на перемещение точки в направлении градиента/антиградиента
        
        Args:
            step_size: Размер шага
            anti_gradient: Если True, движение происходит в направлении антиградиента
        """
        if not self.current_point:
            return
        
        x1, x2 = self.current_point
        x1_new, x2_new = self.lp_problem.move_in_gradient_direction(x1, x2, step_size, anti_gradient)
        
        # Проверяем, принадлежит ли новая точка ОДР
        if self.lp_problem.is_feasible(x1_new, x2_new):
            self.current_point = (x1_new, x2_new)
            self.graph_widget.set_current_point(x1_new, x2_new)
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Движение в данном направлении невозможно:\n"
                "точка выходит за пределы области допустимых решений."
            )
    
    def on_new_problem(self):
        """Обработчик создания новой задачи"""
        reply = QMessageBox.question(
            self,
            "Новая задача",
            "Вы уверены, что хотите создать новую задачу?\n"
            "Все несохраненные данные будут потеряны.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Создаем новую задачу
            self.lp_problem = LPProblem()
            self.calculator = Calculator(self.lp_problem)
            
            # Очищаем виджеты
            self.objective_widget.set_coefficients(1.0, 1.0)
            self.constraints_widget.set_constraints([])  # Пустой список ограничений
            
            # Добавляем одно пустое ограничение для удобства
            self.constraints_widget.add_constraint()
            
            # Обновляем задачу и интерфейс
            self.update_lp_problem()
            
            # Сбрасываем текущую точку
            self.current_point = (0, 0)
            self.graph_widget.set_current_point(*self.current_point)
    
    def on_open_problem(self):
        """Обработчик открытия задачи из файла"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Открыть задачу",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not filepath:
            return
        
        # Загружаем задачу из файла
        problem = StorageManager.load_problem(filepath)
        
        if problem:
            # Устанавливаем загруженную задачу
            self.lp_problem = problem
            self.calculator = Calculator(self.lp_problem)
            
            # Обновляем виджеты на основе загруженной задачи
            self.objective_widget.set_coefficients(problem.c1, problem.c2)
            
            # Преобразуем ограничения в формат для виджета
            constraints_data = [
                (constr.a1, constr.a2, constr.b, constr.constraint_type)
                for constr in problem.constraints
            ]
            self.constraints_widget.set_constraints(constraints_data)
            
            # Обновляем интерфейс
            self.update_lp_problem()
            
            # Сбрасываем текущую точку
            self.current_point = (0, 0)
            self.graph_widget.set_current_point(*self.current_point)
            
            QMessageBox.information(
                self,
                "Информация",
                f"Задача успешно загружена из файла:\n{filepath}"
            )
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Не удалось загрузить задачу из файла:\n{filepath}"
            )
    
    def on_save_problem(self):
        """Обработчик сохранения задачи в файл"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить задачу",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not filepath:
            return
        
        # Убеждаемся, что расширение файла правильное
        if not filepath.lower().endswith('.json'):
            filepath += '.json'
        
        # Сохраняем задачу в файл
        if StorageManager.save_problem(self.lp_problem, filepath):
            QMessageBox.information(
                self,
                "Информация",
                f"Задача успешно сохранена в файл:\n{filepath}"
            )
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Не удалось сохранить задачу в файл:\n{filepath}"
            )
    
    def on_export_graph(self):
        """Обработчик экспорта графика в файл изображения"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт графика",
            "",
            "PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)"
        )
        
        if not filepath:
            return
        
        # Убеждаемся, что расширение файла правильное
        if not (filepath.lower().endswith('.png') or filepath.lower().endswith('.jpg')):
            filepath += '.png'
        
        # Сохраняем график в файл
        if self.graph_widget.save_figure(filepath):
            QMessageBox.information(
                self,
                "Информация",
                f"График успешно экспортирован в файл:\n{filepath}"
            )
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Не удалось экспортировать график в файл:\n{filepath}"
            )
    
    def on_export_latex(self):
        """Обработчик экспорта задачи в формат LaTeX"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт в LaTeX",
            "",
            "LaTeX Files (*.tex);;All Files (*)"
        )
        
        if not filepath:
            return
        
        # Убеждаемся, что расширение файла правильное
        if not filepath.lower().endswith('.tex'):
            filepath += '.tex'
        
        # Экспортируем задачу в формат LaTeX
        if StorageManager.export_to_latex(self.lp_problem, filepath):
            QMessageBox.information(
                self,
                "Информация",
                f"Задача успешно экспортирована в формат LaTeX:\n{filepath}"
            )
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                f"Не удалось экспортировать задачу в формат LaTeX:\n{filepath}"
            )
    
    def on_toggle_grid(self, checked):
        """Обработчик переключения отображения сетки"""
        config = {'grid': checked}
        self.graph_widget.update_config(config)
    
    def on_find_corner_points(self):
        """Обработчик поиска угловых точек"""
        self.corner_points_widget.update_corner_points()
    
    def on_find_optimal(self):
        """Обработчик поиска оптимального решения"""
        result = self.calculator.find_optimal_solution()
        
        if result:
            x1, x2, value, indices = result
            
            # Устанавливаем найденную точку как текущую
            self.current_point = (x1, x2)
            self.graph_widget.set_current_point(x1, x2)
            
            # Формируем сообщение с результатом
            message = (
                f"Найдено оптимальное решение:\n\n"
                f"x₁ = {x1:.4f}\n"
                f"x₂ = {x2:.4f}\n\n"
                f"Значение целевой функции: {value:.4f}\n\n"
                f"Активные ограничения: {', '.join(f'C{i+1}' for i in indices)}"
            )
            
            QMessageBox.information(self, "Результат", message)
        else:
            QMessageBox.warning(
                self,
                "Предупреждение",
                "Не удалось найти оптимальное решение.\n"
                "Возможно, область допустимых решений пуста или не ограничена."
            )
    
    def on_about(self):
        """Обработчик показа информации о программе"""
        QMessageBox.about(
            self,
            "О программе",
            "<h3>Решение задач линейного программирования</h3>"
            "<p>Программа для решения задач линейного программирования "
            "графическим методом в двумерном пространстве.</p>"
            "<p>Версия 1.0</p>"
            "<p>&copy; 2023</p>"
        )
    
    def keyPressEvent(self, event):
        """Обработчик нажатий клавиш"""
        # Обработка нажатий стрелок для перемещения точки
        if event.key() == Qt.Key_Up:
            # Стрелка вверх - движение в направлении антиградиента
            self.on_move_requested(0.5, True)
        elif event.key() == Qt.Key_Down:
            # Стрелка вниз - движение в направлении градиента
            self.on_move_requested(0.5, False)
        else:
            super().keyPressEvent(event)