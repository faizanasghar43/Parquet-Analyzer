import subprocess
import sys

from PyQt5.QtChart import QPieSeries, QChart, QChartView
from PyQt5.QtGui import QPixmap, QIcon, QPainter
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QLabel, \
    QGridLayout, QDialog
from PyQt5.QtCore import pyqtSlot, Qt
import pandas as pd
from datetime import datetime
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parquent Analyzer")
        self.setGeometry(100, 100, 400, 300)
        icon = QIcon("icon-.png")
        self.setWindowIcon(icon)
        # Set the background color
        self.setStyleSheet("background-color: #1D1D1D;")

        # Create a vertical layout to hold the logo, heading, and buttons
        layout = QVBoxLayout()

        # Create the logo
        logo_label = QLabel()
        pixmap = QPixmap("icon-.png")  # Replace "icon-.png" with the path to your logo image
        pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)  # Adjust the size here
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        # Create the heading
        heading_label = QLabel("Parquent Analyzer")
        heading_label.setStyleSheet("color: white; font-size: 20px;")
        heading_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(heading_label)

        # Create the buttons
        button_names = [
            "Serial number of the stack (Fuel Cell)",
            "Bipolar plates",
            "Type de MEA",
            "Cells number",
            "Surface active",
            # "Fsm swVersion",
            "First Operation Day",
            # "First Operation Month",
            "First Operation Year",
            "SUSD number",
            "Cumul number of Cold StartUp",
            "Cumul number of StartUp underH2",
            "Cumul number of StartUp underAir",
            "Running time",
            "Initial running",
            # "Cold Start Ready",
            "PieChart FCC_34sysState",
            "PieChart FCC_Model_Actual"
        ]

        for name in button_names:
            button = QPushButton(name)
            button.setStyleSheet("background-color: #2272FF; color: white;")
            button.clicked.connect(self.button_clicked)  # Connect the clicked signal to button_clicked slot
            layout.addWidget(button)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    @pyqtSlot()
    def show_pie_chart(self):
        subprocess.run(["python", "pie.py"])

    @pyqtSlot()
    def show_pie_chart_actual(self):
        subprocess.run(["python", "histogram.py"])

    @pyqtSlot()  # Decorator for slot method
    def button_clicked(self):
        button = self.sender()  # Get the sender of the clicked signal (in this case, the button)
        button_name = button.text()
        if button_name == "PieChart":
            self.show_pie_chart()
            return
        if button_name == "PieChart FCC_Model_Actual":
            self.show_pie_chart_actual()
            return


        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        col = ""
        saving_directory = ""
        operation = None

        if button_name == "Serial number of the stack (Fuel Cell)":
            col = "fuelcellSystem_firstOperationDay_int"
            saving_directory = "SerialNumberStackFuelCell"
        elif button_name == "Bipolar plates":
            col = "fuelcellStack_bipolarPlateType_str"
            saving_directory = "BipolarPlates"
        elif button_name == "Type de MEA":
            col = "fuelcellStack_meaType_str"
            saving_directory = "TypeDeMEA"
        elif button_name == "Cells number":
            col = "fuelcellStack_cellNumber_int"
            saving_directory = "CellsNumber"
        elif button_name == "Surface active":
            col = "fuelcellStack_activeArea_cm2"
            saving_directory = "SurfaceActive"
        # elif button_name == "Fsm swVersion":
        #     col = "fsm_swVersion_str"
        #     saving_directory = "FSMSWVersion"
        elif button_name == "First Operation Day":
            col = "fuelcellSystem_firstOperationDay_int"
            saving_directory = "FirstOperationDay"
        elif button_name == "First Operation Month":
            col = "fuelcellSystem_firstOperationMonth_int"
            saving_directory = "FirstOperationMonth"
        elif button_name == "First Operation Year":
            col = "fuelcellSystem_firstOperationYear_int"
            saving_directory = "FirstOperationYear"
        elif button_name == "SUSD number":
            col = "fuelcellSystem_cumulStartUp_int"
            saving_directory = "SUSDNumber"
            operation = "max"
        elif button_name == "Cumul number of Cold StartUp":
            col = "fuelcellSystem_cumulColdStart_int"
            saving_directory = "CumulNumberColdStartUp"
            operation = "max"
        elif button_name == "Cumul number of StartUp underH2":
            col = "fuelcellSystem_h2StartUp_counter_int"
            saving_directory = "CumulNumberStartUpUnderH2"
            operation = "max"
        elif button_name == "Cumul number of StartUp underAir":
            col = "fuelcellSystem_airStartUp_counter_int"
            saving_directory = "CumulNumberStartUpUnderAir"
            operation = "max"
        elif button_name == "Running time":
            col = "fuelcellSystem_cumulRuntime_s"
            saving_directory = "RunningTime"
            operation = "running_time"
        elif button_name == "Initial running":
            col = "fuelcellSystem_cumulColdStart_int"
            saving_directory = "InitialRunning"
            operation = "initial_running"
        elif button_name == "Cold Start Ready":
            col = "fuelcellSystem_coldStartReady_int"
            saving_directory = "ColdStartReady"
            operation = "cold_start_ready"
        else:
            return

        data = []

        if operation == "cold_start_ready":
            total_files = 0
            ready_files = 0

            for file_name in os.listdir(folder_path):
                if file_name.endswith(".par"):
                    file_path = os.path.join(folder_path, file_name)
                    try:
                        file_df = pd.read_parquet(file_path, engine='auto', columns=[col],
                                                  storage_options=None, use_nullable_dtypes=False)
                        total_files += 1
                        if col in file_df.columns:
                            if file_df[col].sum() > 0:
                                ready_files += 1
                    except Exception as e:
                        pass

            if total_files > 0:
                percentage = (ready_files / total_files) * 100
                data.append({"Total Files": total_files, "Ready Files": ready_files, "Percentage": percentage})

        else:
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".par"):
                    file_path = os.path.join(folder_path, file_name)
                    try:
                        file_df = pd.read_parquet(file_path, engine='auto', columns=[col],
                                                  storage_options=None, use_nullable_dtypes=False)
                        if col in file_df.columns:
                            if operation == "running_time":
                                value = (file_df[col].max() - file_df[col].min()) / 3600
                                data.append({"Filename": file_name, "Column Value": value})
                            elif operation == "initial_running":
                                value = file_df[col].min() / 3600
                                data.append({"Filename": file_name, "Column Value": value})
                            elif operation == "max":
                                value = file_df[col].max()
                                data.append({"Filename": file_name, "Column Value": value})

                            else:
                                values = file_df[col].unique()
                                data.append({"Filename": file_name, "Column Values": values})
                    except Exception as e:
                        pass
        if operation == "max" :
            data = max(data, key=lambda x: x["Column Value"])

            df = pd.DataFrame([data])
        else:
            df = pd.DataFrame(data)

        # Extract the serial number from the first filename
        serial_number = df["Filename"].iloc[0].split("_")[0]

        # Generate the current date and time for the Excel file name
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"data_{current_datetime}.xlsx"

        # Create the directory based on the serial number and button name if it doesn't exist
        directory = os.path.join(os.getcwd(), serial_number, saving_directory)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Save the DataFrame to Excel within the serial number directory
        file_path = os.path.join(directory, file_name)
        df.to_excel(file_path, index=False)

        print(f"The DataFrame has been saved to the Excel file: {file_path}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
