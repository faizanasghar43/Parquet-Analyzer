import os
import pandas as pd
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QDialog, QGridLayout
from PyQt5.QtChart import QChart, QChartView, QPieSeries

class FileProcessor(QObject):
    processingFinished = pyqtSignal(int, int, int)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def processFiles(self):
        count_5 = 0
        count_6 = 0
        count_11 = 0

        for filename in os.listdir(self.folder_path):
            if filename.endswith('.par'):
                file_path = os.path.join(self.folder_path, filename)
                try:
                    df = pd.read_parquet(file_path, engine='auto', columns=['FCS_ModeActual'],
                                                  storage_options=None, use_nullable_dtypes=False)
                    if 'FCS_ModeActual' in df.columns:
                        counts = df['FCS_ModeActual'].value_counts()
                        count_5 += counts.get(5, 0)
                        count_6 += counts.get(6, 0)
                        count_11 += counts.get(11, 0)
                    else:
                        print(f"Column FCS_ModeActual not found in file: {file_path}")
                except Exception as e:
                    print(f"Error reading file: {file_path}. {str(e)}")

        self.processingFinished.emit(count_5, count_6, count_11)


class PieChartWindow(QDialog):
    def __init__(self, count_5, count_6, count_11):
        super().__init__()
        self.setWindowTitle('Pie Chart')
        self.layout = QGridLayout()

        self.chart = QChart()
        self.chart.setTitle("FCS_ModeActual Counts")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        series = QPieSeries()
        series.append("FCS_ModeActual==5", count_5)
        series.append("FCS_ModeActual==6", count_6)

        self.chart.addSeries(series)

        chart_view = QChartView(self.chart)
        self.layout.addWidget(chart_view, 0, 0)

        self.setLayout(self.layout)

        # Add labels to the pie chart
        self.addLabels(series)

    def addLabels(self, series):
        for slice in series.slices():
            percentage = slice.percentage() * 100
            label = f"{slice.label()} ({percentage:.2f}%)"
            slice.setLabel(label)

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Window')
        self.layout = QVBoxLayout()

        # self.button = QPushButton('Open Folder')
        # self.button.clicked.connect(self.openFolder)
        # self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    # def openFolder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Open Folder')
        if folder_path:
            self.file_processor = FileProcessor(folder_path)
            self.file_thread = QThread()
            self.file_processor.moveToThread(self.file_thread)
            self.file_thread.started.connect(self.file_processor.processFiles)
            self.file_processor.processingFinished.connect(self.showPieChart)
            self.file_processor.processingFinished.connect(self.file_thread.quit)
            self.file_processor.processingFinished.connect(self.file_processor.deleteLater)
            self.file_thread.finished.connect(self.file_thread.deleteLater)
            self.file_thread.start()

    def showPieChart(self, count_5, count_6, count_11):
        pie_chart_window = PieChartWindow(count_5, count_6, count_11)
        pie_chart_window.exec_()

if __name__ == '__main__':
    app = QApplication([])
    window = App()
    window.show()
    app.exec()
