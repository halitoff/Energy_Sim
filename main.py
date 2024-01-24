import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QSlider, QMainWindow
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QSplineSeries
import db


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        # Настройка окна
        self.setGeometry(200, 200, 800, 800)
        self.setWindowTitle("Фотон-Энергетика")
        self.number = 0

        # Создание главного виджета
        self.main_widget = QWidget()
        # Создание виджета графика
        self.graph = Graph()
        # Создание вертикального размещения
        self.vbox = QVBoxLayout(self.main_widget)

        # Наполнение окна
        self.vbox.addWidget(self.graph.chart_view)  # Расположение графика

        # Создание и расположение Label
        self.people_label = QLabel(self.main_widget)
        self.people_label.setText("Население (тыс. чел.) —")
        self.vbox.addWidget(self.people_label)

        # Создание и расположение слайдера населения
        self.people_slider = QSlider(Qt.Horizontal, self.main_widget)
        self.vbox.addWidget(self.people_slider)

        # Создание и расположение Label
        self.power_label = QLabel(self.main_widget)
        self.power_label.setText("Мощность ТЭС (КВт) —")
        self.vbox.addWidget(self.power_label)

        # Создание и расположение слайдера мощности
        self.power_slider = QSlider(Qt.Horizontal, self.main_widget)
        self.vbox.addWidget(self.power_slider)

        # Создание и расположение Label
        self.temp_label = QLabel(self.main_widget)
        self.temp_label.setText("Температура воздуха на улице (Цельсий) —")
        self.vbox.addWidget(self.temp_label)

        # Создание и расположение слайдера температуры
        self.temp_slider = QSlider(Qt.Horizontal, self.main_widget)
        self.vbox.addWidget(self.temp_slider)

        # Создание и расположение Label
        self.night_label = QLabel(self.main_widget)
        self.night_label.setText("Продолжительность ночи (час) —")
        self.vbox.addWidget(self.night_label)

        # Создание и расположение слайдера продолжительности ночи
        self.night_slider = QSlider(Qt.Horizontal, self.main_widget)
        self.vbox.addWidget(self.night_slider)

        # Создание поля кнопок
        self.buttons = QHBoxLayout(self.main_widget)

        self.save_result_btn = QPushButton("Сохранить результат", self.main_widget)
        self.buttons.addWidget(self.save_result_btn)

        self.best_result_btn = QPushButton("Лучший результат", self.main_widget)
        self.buttons.addWidget(self.best_result_btn)

        self.vbox.addLayout(self.buttons)

        # Установка размещений окна
        self.main_widget.setLayout(self.vbox)
        self.setCentralWidget(self.main_widget)

        # Запуск настроечных функций
        self.setup_sliders()
        self.setup_buttons()

    def setup_sliders(self):
        """Настройка слайдеров, их диапазонов, шагов и сигналов"""
        self.people_slider.setRange(1, 100)
        self.people_slider.valueChanged[int].connect(lambda value: self.label_edit(value, self.people_label))
        self.people_slider.valueChanged[int].connect(self.math)

        self.power_slider.setRange(90, 100000)
        self.power_slider.setPageStep(50)
        self.power_slider.setSingleStep(5)
        self.power_slider.valueChanged[int].connect(lambda value: self.label_edit(value * 1000, self.power_label))
        self.power_slider.valueChanged[int].connect(self.setup_power_line)

        self.temp_slider.setRange(-40, +40)

        def temp(value):
            return f"{'+' if value >= 1 else ''}{value} ℃"

        self.temp_slider.setPageStep(5)
        self.temp_slider.valueChanged[int].connect(lambda value: self.label_edit(temp(value), self.temp_label))
        self.temp_slider.valueChanged[int].connect(self.math)

        self.night_slider.setRange(40, 80)
        self.night_slider.valueChanged[int].connect(lambda value: self.label_edit(value / 10, self.night_label))
        self.night_slider.valueChanged[int].connect(self.math)

    def setup_power_line(self, value):
        """Реализация этой функции также необязательна, как и класса MyQChartView"""
        try:
            self.power_line.deleteLater()
        except Exception as e:
            print(e)

        self.power_line = QLineSeries()
        self.power_line.setName(f"{value} МВт")
        self.power_line.setPen(QPen(QColor("white"), 3))
        self.power_line.append(self.graph.chart.axisX().min(), value*1000)
        self.power_line.append(self.graph.chart.axisX().max(), value*1000)

        self.graph.chart.addSeries(self.power_line)
        self.power_line.attachAxis(self.graph.chart.axisY())

    def analyze(self, people, power, temp, night):
        # Вычисляем потребление энергии
        energy_usage = (people * (1 - temp / 100)) + (night * people / 2)

        # Проверяем, хватает ли мощности ТЭС
        if energy_usage > power:
            return 0  # Недостаточно мощности

        # Вычисляем оценку эффективности
        effectiveness = power / energy_usage

        return effectiveness

    def best_result(self):
        data = db.read_all()
        temp = {}
        for row in data:
            temp[row.number] = (self.analyze(
                row.people, row.power,
                row.temp, row.night)
            )
        best = max(temp.values())
        for key, k in temp.items():
            if k == best:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText(f"Лучший показатель — номер {key}")
                msgBox.setWindowTitle("Лучшее значение")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec()

    def setup_buttons(self):
        def write():
            db.write([
                self.number,
                self.people_slider.value(),
                self.power_slider.value(),
                self.temp_slider.value(),
                self.night_slider.value()
            ])
            self.number += 1
        self.save_result_btn.clicked.connect(write)
        self.best_result_btn.clicked.connect(self.best_result)

    def math(self):
        """Функция расчётов"""
        parts = range(0, 25)
        morning_range = range(4, 11)
        evening_range = range(18, 24)
        night_range = range(23, 5)
        people = self.people_slider.value()
        power = self.power_slider.value()
        temp = self.temp_slider.value()
        night = self.night_slider.value() / 10

        one_people_power = (people * 1000 * (350 if temp <= -35 else (350 / 4 if -35 < temp <= -10 else 0))
                            + people * 2500) * (0 if temp >= -10 else 1)

        data = []
        for time in parts:
            if time in morning_range:
                data.append((one_people_power / (4 / night), time))
            elif time in evening_range:
                data.append((one_people_power / (4 / night), time))
            elif time in night_range:
                data.append((one_people_power * (4 / night), time))
            else:

                data.append((one_people_power, time))

        self.graph.changeValue(data)

    def label_edit(self, value, label: QLabel):
        text = label.text()[:label.text().find("—") - 1]
        label.setText(f"{text} — {value}")


class Graph(QWidget):
    def __init__(self, title="График"):
        super().__init__()
        # Настройка параметров виджета
        self.title = title
        self.series = QSplineSeries()
        self.series.setPen(QPen(QColor("red"), 4))
        self.chart = QChart()
        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.setTitle("Синусоида")
        self.chart.setTheme(QChart.ChartThemeBlueCerulean)
        # Можно использовать QChartView
        self.chart_view = MyQChartView(self.chart)

    def changeValue(self, value):
        """Особенность функции в том, что она постоянно пересоздаёт оси так, чтобы график оставался в центре экрана"""
        # Удаление предыдущего множества данных и создание нового.
        # Это для того, чтобы график перестроил свои оси.
        self.series.deleteLater()
        self.chart.removeAllSeries()
        self.series = QSplineSeries()
        # настройка множества
        self.series.setPen(QPen(QColor("red"), 4))
        self.series.setName("Мощность")

        # Добавление данных в множество и вычисление максимума и минимума графика
        maximum = 0
        minimum = 10 ** 100
        for y, x in value:
            self.series.append(x, y)
            if y > maximum:
                maximum = y

            if y < minimum:
                minimum = y

        # Прикрепление множества к графику
        self.chart.addSeries(self.series)
        self.chart.createDefaultAxes()
        # Получение и удаление оси Y
        axisX, axisY = self.chart.axes()
        self.chart.removeAxis(axisY)
        # Создание оси Y
        axisY = QValueAxis()
        axisY.setRange(minimum // 2, maximum * 1.5)
        # Добавление оси в график
        self.chart.setAxisY(axisY)
        self.series.attachAxis(axisY)


class MyQChartView(QChartView):
    """
    Этот класс необязателен и реализует работу прямых наведения при нажатии ЛКМ и ПКМ.
    Можете реализовывать этот класс только если студент раньше обычного закончил проект и его знания дотягивают до
    необходимого уровня.
    """
    def __init__(self, chart: QChart):
        self.y_line = None
        self.x_line = None
        self.chart = chart
        super().__init__(self.chart)
        self.lines = {}

    def mousePressEvent(self, event):
        if self.chart.axisX() is None and self.chart.axisY() is None:
            return

        button = event.button()
        color = "green"
        if button == 2:
            color = "orange"
        lines = self.lines.get(color)
        if lines:
            try:
                lines[0].deleteLater()
                lines[1].deleteLater()
            except RuntimeError:
                pass


        clickPosition = self.chart.mapToValue(event.pos())
        # Определяем положение линий
        x = clickPosition.x()
        y = clickPosition.y()

        # Вертикальная линия
        self.x_line = QLineSeries()
        self.x_line.setName(f"{0 if int(x) in range(0, 10) else ''}{int(x)}:00 часов")
        self.x_line.setPen(QPen(QColor(color), 1))
        self.x_line.append(x, self.chart.axisY().min())
        self.x_line.append(x, self.chart.axisY().max())

        # Горизонтальная линия
        self.y_line = QLineSeries()
        self.y_line.setName(f"{int(y)} КВт")
        self.y_line.setPen(QPen(QColor(color), 1))
        self.y_line.append(self.chart.axisX().min(), y)
        self.y_line.append(self.chart.axisX().max(), y)

        self.chart.addSeries(self.x_line)
        self.x_line.attachAxis(self.chart.axisX())
        self.chart.addSeries(self.y_line)
        self.y_line.attachAxis(self.chart.axisY())

        self.lines[color] = (self.x_line, self.y_line)
        self.lines[color] = (self.x_line, self.y_line)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
