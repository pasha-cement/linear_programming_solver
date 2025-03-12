"""
Виджеты для ввода данных задачи линейного программирования
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QLineEdit, QPushButton, QComboBox, 
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal
from models.lp_problem import LPProblem, ConstraintType
from modules.input_module import InputParser

class ObjectiveFunctionWidget(QWidget):
    """Виджет для ввода целевой функции"""
    
    coefficientsChanged = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        """Инициализирует виджет ввода целевой функции"""
        super().__init__(parent)
        
        self.c1_input = QDoubleSpinBox()
        self.c2_input = QDoubleSpinBox()
        
        # Настраиваем спиннеры
        for spinner in (self.c1_input, self.c2_input):
            spinner.setMinimum(-1000.0)
            spinner.setMaximum(1000.0)
            spinner.setDecimals(2)
            spinner.setSingleStep(0.1)
            spinner.setValue(1.0)
        
        # Создаем компоновку
        layout = QGridLayout()
        layout.addWidget(QLabel("Целевая функция:"), 0, 0)
        layout.addWidget(self.c1_input, 0, 1)
        layout.addWidget(QLabel("· x₁ + "), 0, 2)
        layout.addWidget(self.c2_input, 0, 3)
        layout.addWidget(QLabel("· x₂ → max"), 0, 4)
        
        layout.setColumnStretch(5, 1)  # Добавляем растягивающийся пустой столбец
        self.setLayout(layout)
        
        # Подключаем сигналы
        self.c1_input.valueChanged.connect(self.on_coefficients_changed)
        self.c2_input.valueChanged.connect(self.on_coefficients_changed)
    
    def on_coefficients_changed(self):
        """Обработчик изменения коэффициентов"""
        c1 = self.c1_input.value()
        c2 = self.c2_input.value()
        self.coefficientsChanged.emit(c1, c2)
    
    def set_coefficients(self, c1: float, c2: float) -> None:
        """
        Устанавливает коэффициенты целевой функции
        
        Args:
            c1: Коэффициент при x1
            c2: Коэффициент при x2
        """
        self.c1_input.setValue(c1)
        self.c2_input.setValue(c2)
    
    def get_coefficients(self) -> tuple:
        """
        Получает коэффициенты целевой функции
        
        Returns:
            Кортеж (c1, c2) с коэффициентами целевой функции
        """
        return self.c1_input.value(), self.c2_input.value()


class ConstraintsTableWidget(QWidget):
    """Виджет для ввода и редактирования ограничений"""
    
    constraintsChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        """Инициализирует виджет таблицы ограничений"""
        super().__init__(parent)
        
        # Создаем таблицу ограничений
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['a₁', 'a₂', 'Знак', 'b'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Кнопки добавления и удаления ограничений
        self.add_button = QPushButton("Добавить ограничение")
        self.remove_button = QPushButton("Удалить выбранное")
        
        # Компоновка кнопок
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        
        # Общая компоновка
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ограничения:"))
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Подключаем сигналы
        self.add_button.clicked.connect(self.add_constraint)
        self.remove_button.clicked.connect(self.remove_constraint)
        self.table.itemChanged.connect(self.on_constraint_changed)
        
        # Добавляем первоначальное ограничение
        self.add_constraint()
    
    def add_constraint(self) -> None:
        """Добавляет новое ограничение в таблицу"""
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        
        # Создаем поля ввода коэффициентов
        for col in (0, 1, 3):  # a1, a2, b
            spinner = QDoubleSpinBox()
            spinner.setMinimum(-1000.0)
            spinner.setMaximum(1000.0)
            spinner.setDecimals(2)
            spinner.setSingleStep(0.1)
            spinner.setValue(1.0)
            self.table.setCellWidget(row_position, col, spinner)
            spinner.valueChanged.connect(self.on_constraint_changed)
        
        # Создаем комбобокс для знака
        sign_combo = QComboBox()
        sign_combo.addItems(["≤", "=", "≥"])
        self.table.setCellWidget(row_position, 2, sign_combo)
        sign_combo.currentIndexChanged.connect(self.on_constraint_changed)
    
    def remove_constraint(self) -> None:
        """Удаляет выбранное ограничение из таблицы"""
        selected_rows = sorted(set(item.row() for item in self.table.selectedItems()), reverse=True)
        
        if not selected_rows:
            current_row = self.table.currentRow()
            if current_row >= 0:
                self.table.removeRow(current_row)
                self.constraintsChanged.emit()
            return
        
        for row in selected_rows:
            self.table.removeRow(row)
        
        self.constraintsChanged.emit()
    
    def on_constraint_changed(self) -> None:
        """Обработчик изменения ограничения"""
        self.constraintsChanged.emit()
    
    def get_constraints(self) -> list:
        """
        Получает список ограничений из таблицы
        
        Returns:
            Список кортежей (a1, a2, b, constraint_type) с данными ограничений
        """
        constraints = []
        
        for row in range(self.table.rowCount()):
            # Получаем виджеты из ячеек таблицы
            a1_spinner = self.table.cellWidget(row, 0)
            a2_spinner = self.table.cellWidget(row, 1)
            sign_combo = self.table.cellWidget(row, 2)
            b_spinner = self.table.cellWidget(row, 3)
            
            if not all((a1_spinner, a2_spinner, sign_combo, b_spinner)):
                continue
            
            # Получаем значения
            a1 = a1_spinner.value()
            a2 = a2_spinner.value()
            sign_text = sign_combo.currentText()
            b = b_spinner.value()
            
            # Определяем тип ограничения
            if sign_text == "≤":
                constraint_type = ConstraintType.LESS_EQUAL
            elif sign_text == "=":
                constraint_type = ConstraintType.EQUAL
            else:  # "≥"
                constraint_type = ConstraintType.GREATER_EQUAL
            
            constraints.append((a1, a2, b, constraint_type))
        
        return constraints
    
    def set_constraints(self, constraints: list) -> None:
        """
        Устанавливает ограничения в таблицу
        
        Args:
            constraints: Список кортежей (a1, a2, b, constraint_type) с данными ограничений
        """
        # Очищаем таблицу
        self.table.setRowCount(0)
        
        # Добавляем ограничения
        for a1, a2, b, constraint_type in constraints:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # Устанавливаем значения коэффициентов
            for col, value in [(0, a1), (1, a2), (3, b)]:
                spinner = QDoubleSpinBox()
                spinner.setMinimum(-1000.0)
                spinner.setMaximum(1000.0)
                spinner.setDecimals(2)
                spinner.setSingleStep(0.1)
                spinner.setValue(value)
                self.table.setCellWidget(row_position, col, spinner)
                spinner.valueChanged.connect(self.on_constraint_changed)
            
            # Устанавливаем значение знака
            sign_combo = QComboBox()
            sign_combo.addItems(["≤", "=", "≥"])
            if constraint_type == ConstraintType.LESS_EQUAL:
                sign_combo.setCurrentIndex(0)
            elif constraint_type == ConstraintType.EQUAL:
                sign_combo.setCurrentIndex(1)
            else:  # ConstraintType.GREATER_EQUAL
                sign_combo.setCurrentIndex(2)
            self.table.setCellWidget(row_position, 2, sign_combo)
            sign_combo.currentIndexChanged.connect(self.on_constraint_changed)


class CornerPointsWidget(QWidget):
    """Виджет для отображения угловых точек и выбора начальной точки"""
    
    pointSelected = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        """Инициализирует виджет угловых точек"""
        super().__init__(parent)
        
        # Создаем таблицу угловых точек
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['№', 'Координаты (x₁, x₂)', 'Значение f'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Кнопка обновления угловых точек
        self.update_button = QPushButton("Обновить")
        
        # Кнопка выбора точки
        self.select_button = QPushButton("Выбрать как начальную")
        self.select_button.setEnabled(False)
        
        # Компоновка кнопок
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.select_button)
        
        # Общая компоновка
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Угловые точки:"))
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Подключаем сигналы
        self.update_button.clicked.connect(self.on_update_requested)
        self.select_button.clicked.connect(self.on_select_requested)
        self.table.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.lp_problem = None
    
    def set_problem(self, problem: LPProblem) -> None:
        """
        Устанавливает задачу для отображения угловых точек
        
        Args:
            problem: Задача линейного программирования
        """
        self.lp_problem = problem
        self.update_corner_points()
    
    def update_corner_points(self) -> None:
        """Обновляет список угловых точек"""
        if not self.lp_problem:
            return
        
        # Находим угловые точки
        corner_points = self.lp_problem.find_corner_points()
        
        # Очищаем таблицу
        self.table.setRowCount(0)
        
        # Заполняем таблицу
        for i, (x1, x2, indices) in enumerate(corner_points):
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            # Номер точки
            self.table.setItem(row_position, 0, QTableWidgetItem(str(i + 1)))
            
            # Координаты точки
            coord_text = f"({x1:.2f}, {x2:.2f})"
            self.table.setItem(row_position, 1, QTableWidgetItem(coord_text))
            
            # Значение целевой функции
            value = self.lp_problem.objective_value(x1, x2)
            self.table.setItem(row_position, 2, QTableWidgetItem(f"{value:.2f}"))
            
            # Сохраняем координаты в данных элемента
            for col in range(3):
                item = self.table.item(row_position, col)
                if item:
                    item.setData(Qt.UserRole, (x1, x2))
    
    def on_update_requested(self) -> None:
        """Обработчик запроса на обновление угловых точек"""
        self.update_corner_points()
    
    def on_selection_changed(self) -> None:
        """Обработчик изменения выбранной строки в таблице"""
        selected_items = self.table.selectedItems()
        self.select_button.setEnabled(len(selected_items) > 0)
    
    def on_select_requested(self) -> None:
        """Обработчик запроса на выбор точки как начальной"""
        selected_items = self.table.selectedItems()
        if not selected_items:
            return
        
        # Получаем координаты выбранной точки (они одинаковы для всех ячеек строки)
        point_data = selected_items[0].data(Qt.UserRole)
        if point_data:
            x1, x2 = point_data
            self.pointSelected.emit(x1, x2)


class GradientControlWidget(QWidget):
    """Виджет для управления градиентным методом"""
    
    moveRequested = pyqtSignal(float, bool)  # step_size, anti_gradient
    
    def __init__(self, parent=None):
        """Инициализирует виджет управления градиентным методом"""
        super().__init__(parent)
        
        # Создаем группу для управления градиентным методом
        group_box = QGroupBox("Градиентный метод")
        
        # Создаем спиннер для шага
        self.step_spinner = QDoubleSpinBox()
        self.step_spinner.setMinimum(0.01)
        self.step_spinner.setMaximum(10.0)
        self.step_spinner.setSingleStep(0.1)
        self.step_spinner.setValue(0.5)
        self.step_spinner.setDecimals(2)
        
        # Создаем кнопки для перемещения
        self.up_button = QPushButton("↑ (антиградиент)")
        self.down_button = QPushButton("↓ (градиент)")
        
        # Компоновка для группы
        group_layout = QVBoxLayout()
        
        # Компоновка для шага
        step_layout = QHBoxLayout()
        step_layout.addWidget(QLabel("Шаг:"))
        step_layout.addWidget(self.step_spinner)
        group_layout.addLayout(step_layout)
        
        # Добавляем кнопки
        group_layout.addWidget(self.up_button)
        group_layout.addWidget(self.down_button)
        
        group_box.setLayout(group_layout)
        
        # Общая компоновка
        layout = QVBoxLayout()
        layout.addWidget(group_box)
        self.setLayout(layout)
        
        # Подключаем сигналы
        self.up_button.clicked.connect(self.on_up_clicked)
        self.down_button.clicked.connect(self.on_down_clicked)
    
    def on_up_clicked(self) -> None:
        """Обработчик нажатия кнопки антиградиента (вверх)"""
        step_size = self.step_spinner.value()
        self.moveRequested.emit(step_size, True)
    
    def on_down_clicked(self) -> None:
        """Обработчик нажатия кнопки градиента (вниз)"""
        step_size = self.step_spinner.value()
        self.moveRequested.emit(step_size, False)