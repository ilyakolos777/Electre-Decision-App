import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QDoubleSpinBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QFrame, QTabWidget, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import pyqtgraph as pg

from electre_model import DecisionModel


class ElectreApp(QMainWindow):
    def __init__(self, model: DecisionModel, expert_scores: list):
        super().__init__()
        self.model = model
        self.expert_scores = expert_scores
        self.weights = DecisionModel.calculate_weights(expert_scores)
        self.norm_matrix = self.model.normalize()

        self.setWindowTitle("Многокритериальный выбор решений — Метод ЭЛЕКТРА (Вариант 5)")
        self.resize(1180, 780)

        pg.setConfigOption('background', '#18181b')
        pg.setConfigOption('foreground', '#a1a1aa')
        pg.setConfigOptions(antialias=True)

        self.setStyleSheet("""
            QMainWindow { background-color: #0f0f11; }
            QFrame#card {
                background-color: #18181b;
                border-radius: 12px;
                border: 1px solid #27272a;
            }
            QLabel { font-family: 'Segoe UI', sans-serif; color: #e4e4e7; }
            QDoubleSpinBox {
                border: 1px solid #3f3f46;
                border-radius: 8px;
                padding: 6px 10px;
                background-color: #09090b;
                color: #f4f4f5;
                font-size: 13px;
            }
            QDoubleSpinBox:focus { border: 1px solid #3b82f6; }
            QCheckBox {
                color: #e4e4e7;
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #3f3f46;
                background-color: #09090b;
            }
            QCheckBox::indicator:checked {
                background-color: #2563eb;
                border-color: #3b82f6;
            }
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #3b82f6; }
            QPushButton:pressed { background-color: #1d4ed8; }
            QTabWidget::pane {
                border: 1px solid #27272a;
                background: #18181b;
                border-radius: 10px;
            }
            QTabBar::tab {
                background: #09090b;
                color: #a1a1aa;
                padding: 10px 18px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #18181b;
                color: #60a5fa;
                border-bottom: 2px solid #3b82f6;
            }
        """)

        self._init_ui()
        self._calculate()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Левая панель параметров
        left_card = QFrame()
        left_card.setObjectName("card")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(20, 20, 20, 20)

        title_lbl = QLabel("Параметры анализа")
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #ffffff;")
        left_layout.addWidget(title_lbl)

        self.pareto_chk = QCheckBox("Фильтровать по Парето")
        self.pareto_chk.setChecked(True)
        left_layout.addWidget(self.pareto_chk)

        c_lbl = QLabel("Порог согласия c*:")
        c_lbl.setStyleSheet("color: #a1a1aa; margin-top: 8px;")
        left_layout.addWidget(c_lbl)
        self.c_spin = QDoubleSpinBox()
        self.c_spin.setRange(0.0, 1.0)
        self.c_spin.setSingleStep(0.05)
        self.c_spin.setValue(0.50)
        left_layout.addWidget(self.c_spin)

        d_lbl = QLabel("Порог несогласия d*:")
        d_lbl.setStyleSheet("color: #a1a1aa; margin-top: 8px;")
        left_layout.addWidget(d_lbl)
        self.d_spin = QDoubleSpinBox()
        self.d_spin.setRange(0.0, 1.0)
        self.d_spin.setSingleStep(0.05)
        self.d_spin.setValue(0.50)
        left_layout.addWidget(self.d_spin)

        btn_run = QPushButton("Выполнить расчет")
        btn_run.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_run.clicked.connect(self._calculate)
        left_layout.addWidget(btn_run)

        # Блок с результирующим ядром
        self.res_card = QFrame()
        self.res_card.setStyleSheet("""
            QFrame {
                background-color: #1e1b4b; 
                border-radius: 8px; 
                border: 1px solid #3730a3;
                margin-top: 10px;
            }
        """)
        res_layout = QVBoxLayout(self.res_card)
        self.res_label = QLabel("Ядро решений: —")
        self.res_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.res_label.setStyleSheet("color: #818cf8; background: transparent; border: none;")
        self.res_label.setWordWrap(True)
        res_layout.addWidget(self.res_label)
        left_layout.addWidget(self.res_card)

        # Блок весов критериев
        w_card = QFrame()
        w_card.setStyleSheet("background-color: #131316; border-radius: 8px; border: 1px solid #27272a; margin-top: 8px;")
        w_layout = QVBoxLayout(w_card)
        w_title = QLabel("Веса критериев (ранг):")
        w_title.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        w_layout.addWidget(w_title)
        for i, name in enumerate(self.model.criteria_names):
            lbl = QLabel(f"{name}: {self.weights[i]:.3f}")
            lbl.setStyleSheet("color: #a1a1aa; font-size: 11px;")
            w_layout.addWidget(lbl)
        left_layout.addWidget(w_card)

        left_layout.addStretch()

        # Правая панель
        right_card = QFrame()
        right_card.setObjectName("card")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(15, 15, 15, 15)

        tabs = QTabWidget()

        # Вкладка 1: Пространство индексов
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.15)
        self.plot_widget.setLabel('bottom', 'Индекс согласия (cj)')
        self.plot_widget.setLabel('left', 'Индекс несогласия (dj)')

        self.v_line = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#ef4444', style=Qt.PenStyle.DashLine, width=2))
        self.h_line = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('#ef4444', style=Qt.PenStyle.DashLine, width=2))
        self.plot_widget.addItem(self.v_line)
        self.plot_widget.addItem(self.h_line)

        chart_layout.addWidget(self.plot_widget)

        # Вкладка 2: Таблица индексов
        table_indices_widget = QWidget()
        ti_layout = QVBoxLayout(table_indices_widget)
        self.indices_table = QTableWidget()
        self.indices_table.setColumnCount(4)
        self.indices_table.setHorizontalHeaderLabels(["Альтернатива", "Индекс cj", "Индекс dj", "Входит в ядро"])
        self.indices_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._apply_table_style(self.indices_table)
        ti_layout.addWidget(self.indices_table)

        # Вкладка 3: Исходные и нормированные данные
        table_raw_widget = QWidget()
        tr_layout = QVBoxLayout(table_raw_widget)
        self.raw_table = QTableWidget()
        self.raw_table.setColumnCount(4)
        self.raw_table.setHorizontalHeaderLabels(["Альтернатива", "Сырье (норм.)", "Клиенты (норм.)", "Затраты (норм.)"])
        self.raw_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._apply_table_style(self.raw_table)
        tr_layout.addWidget(self.raw_table)

        tabs.addTab(chart_widget, "Пространство индексов (cj / dj)")
        tabs.addTab(table_indices_widget, "Сводные индексы")
        tabs.addTab(table_raw_widget, "Нормированная матрица")

        right_layout.addWidget(tabs)
        main_layout.addWidget(left_card, stretch=1)
        main_layout.addWidget(right_card, stretch=3)

    def _apply_table_style(self, table):
        table.setStyleSheet("""
            QTableWidget {
                background-color: #18181b;
                color: #f4f4f5;
                border: none;
                gridline-color: #27272a;
            }
            QTableWidget::item { padding: 6px; }
            QHeaderView::section {
                background-color: #09090b;
                color: #a1a1aa;
                font-weight: bold;
                border: none;
                border-bottom: 2px solid #27272a;
                padding: 8px;
            }
        """)

    def _calculate(self):
        c_star = self.c_spin.value()
        d_star = self.d_spin.value()

        if self.pareto_chk.isChecked():
            active_alts = self.model.pareto_filter(self.norm_matrix)
        else:
            active_alts = list(range(self.model.num_alts))

        c_mat, d_mat, c_vals, d_vals, core = self.model.electre_analysis(
            active_alts, self.norm_matrix, self.weights, c_star, d_star
        )

        core_names = [self.model.alternatives[i] for i in core]
        if core_names:
            self.res_label.setText(f"Ядро решений:\n{', '.join(core_names)}")
        else:
            self.res_label.setText("Ядро решений пусто.\nСкорректируйте пороги.")

        # Отрисовка таблицы индексов
        self.indices_table.setRowCount(len(active_alts))
        for row, idx in enumerate(active_alts):
            alt_name = self.model.alternatives[idx]
            cj = c_vals[row]
            dj = d_vals[row]
            in_core = idx in core

            item_alt = QTableWidgetItem(alt_name)
            item_c = QTableWidgetItem(f"{cj:.3f}")
            item_d = QTableWidgetItem(f"{dj:.3f}")
            item_core = QTableWidgetItem("Да" if in_core else "Нет")

            for it in [item_alt, item_c, item_d, item_core]:
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if in_core:
                    it.setBackground(QColor('#1e3a8a'))
                    it.setForeground(QColor('#93c5fd'))

            self.indices_table.setItem(row, 0, item_alt)
            self.indices_table.setItem(row, 1, item_c)
            self.indices_table.setItem(row, 2, item_d)
            self.indices_table.setItem(row, 3, item_core)

        # Отрисовка таблицы нормированных значений
        self.raw_table.setRowCount(self.model.num_alts)
        for i in range(self.model.num_alts):
            item_alt = QTableWidgetItem(self.model.alternatives[i])
            item_alt.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.raw_table.setItem(i, 0, item_alt)
            for j in range(self.model.num_crit):
                it = QTableWidgetItem(f"{self.norm_matrix[i][j]:.3f}")
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.raw_table.setItem(i, j + 1, it)

        # Отрисовка на графике
        self._plot_results(active_alts, c_vals, d_vals, core, c_star, d_star)

    def _plot_results(self, active_alts, c_vals, d_vals, core, c_star, d_star):
        self.plot_widget.clear()

        # Пороговые линии
        self.v_line = pg.InfiniteLine(pos=c_star, angle=90, movable=False, pen=pg.mkPen('#ef4444', style=Qt.PenStyle.DashLine, width=2))
        self.h_line = pg.InfiniteLine(pos=d_star, angle=0, movable=False, pen=pg.mkPen('#ef4444', style=Qt.PenStyle.DashLine, width=2))
        self.plot_widget.addItem(self.v_line)
        self.plot_widget.addItem(self.h_line)

        for row, idx in enumerate(active_alts):
            alt_name = self.model.alternatives[idx]
            cj = c_vals[row]
            dj = d_vals[row]
            in_core = idx in core

            color = '#38bdf8' if in_core else '#71717a'
            brush = '#38bdf8' if in_core else '#3f3f46'
            size = 14 if in_core else 10

            self.plot_widget.plot(
                [cj], [dj],
                pen=None,
                symbol='o',
                symbolSize=size,
                symbolBrush=brush,
                symbolPen=pg.mkPen(color, width=2)
            )

            text_item = pg.TextItem(text=f" {alt_name} ", color=color, anchor=(0.5, 1.3))
            text_item.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            text_item.setPos(cj, dj)
            self.plot_widget.addItem(text_item)