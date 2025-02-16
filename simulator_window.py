import pandas as pd
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QComboBox, QVBoxLayout, QHBoxLayout, QWidget, QLabel, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QSlider, QScrollArea, QPushButton)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from Visualization import HeatEyeTrackingPlotWidget, SankeyDiagramWidget, EyeTrackingPlot3DWindow, EEGPupilAnalyzer, EEGSignalVisualizationbWidget
from data_manager import DataManager


"""
    The main window contains multiple tabs, including:

        An image of the simulator.
        A table displaying tasks.
        A file selection interface where the user can choose an EEG file.
        Based on the selected EEG file, it loads EEG and eye-tracking data, then updates various visualizations accordingly 
            (e.g., EEG signal, eye tracking plot, 3D plot, Sankey diagram).
            
        It also displays performance data in a separate table related to the selected file.

"""


class SimulatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()

        # Set up the main window
        self.setWindowTitle('DaVinci Simulator - Tamás Bányász')
        self.setGeometry(100, 100, 1024, 768)

        # Create tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Image Tab ---
        self.image_tab = QWidget()
        image_layout = QVBoxLayout(self.image_tab)

        self.image_label = QLabel()
        pixmap = QPixmap(r'C:\Users\T\Desktop\Figure1.png')
        pixmap = pixmap.scaled(1024, 768, Qt.KeepAspectRatio)  # Adjust image size
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        image_layout.addWidget(self.image_label)
        self.tabs.addTab(self.image_tab, "Simulator Image")

        # --- Tasks Table Tab ---
        self.table_tab = QWidget()
        table_layout = QVBoxLayout(self.table_tab)

        self.table_widget = QTableWidget()
        # Load CSV data into the table widget
        self.data_manager.insert_tasks_csv_data_into_tasks_table(pd, QTableWidgetItem, Qt, QtWidgets, 
                                                                 self.table_widget, r'C:\Users\T\Desktop\tomi_valai\Table1.csv')
        table_layout.addWidget(self.table_widget)

        self.tabs.addTab(self.table_tab, "Tasks Table")

        # --- File Selection Tab ---
        self.file_tab = QWidget()
        file_layout = QHBoxLayout(self.file_tab)  # Using horizontal layout

        # Left column layout
        left_layout = QVBoxLayout()  # Separate layout for the left column
        left_layout.setAlignment(Qt.AlignTop)
        left_layout.setSpacing(2)

        # "Choose file" label
        self.label = QLabel("Choose file:")
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(self.label)

        # Create ComboBox for file selection
        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.on_combobox_changed)
        self.combo_box.setFixedWidth(300)
        self.combo_box.setStyleSheet("font-size: 16px;")
        left_layout.addWidget(self.combo_box)
        
        self.channel_label = QLabel("Select Channel:")
        self.channel_label.setVisible(False)
        self.channel_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(self.channel_label)
        
        self.channel_box = QComboBox()
        self.channel_box.setVisible(False)
        self.channel_box.setFixedWidth(300)
        self.channel_box.setStyleSheet("font-size: 16px;")
        left_layout.addWidget(self.channel_box)

        # Right column layout
        right_layout = QVBoxLayout()  # New layout for the right column
        right_layout.setAlignment(Qt.AlignTop)

        # Scroll area for time slider and visualization widgets
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        # 3D Eye Plots Button
        self.button_3d = QPushButton("Show 3D Eye plots")
        self.button_3d.setVisible(False)
        self.button_3d.clicked.connect(self.on_button_3d_click)  # Connect button event
        left_layout.addWidget(self.button_3d)
        
        # Label for second slider
        self.slider_label_2 = QLabel("")
        self.slider_label_2.setVisible(False)
        self.slider_label_2.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(self.slider_label_2)
        
        # Second slider (for choosing visualization type)
        self.slider_2 = QSlider(Qt.Horizontal)
        self.slider_2.setFixedWidth(100)
        self.slider_2.setMinimum(0)
        self.slider_2.setMaximum(2)
        self.slider_2.setValue(0)
        left_layout.addWidget(self.slider_2)
        
        # Performance table
        self.performance_table = QTableWidget()
        self.performance_table.setVisible(False)
        left_layout.addWidget(self.performance_table)
        
        # Add visualization widgets to the scroll layout
        self.eeg_vis_widget = EEGSignalVisualizationbWidget()
        self.scroll_layout.addWidget(self.eeg_vis_widget)
        
        self.eeg_and_pupil_analyzer_widget = EEGPupilAnalyzer()
        self.scroll_layout.addWidget(self.eeg_and_pupil_analyzer_widget)
        
        self.heat_eye_tracking_widget = HeatEyeTrackingPlotWidget()
        self.scroll_layout.addWidget(self.heat_eye_tracking_widget)
        
        self.shankey = SankeyDiagramWidget()
        self.scroll_layout.addWidget(self.shankey)
        
        self.eye_tracking_3d_window = EyeTrackingPlot3DWindow()
        
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)
        
        # Main time slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setTickInterval(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        right_layout.addWidget(self.slider)
        
        right_layout.addWidget(self.scroll_area)
        
        # Add both left and right layouts to the file selection layout
        file_layout.addLayout(left_layout)
        file_layout.addLayout(right_layout)

        self.tabs.addTab(self.file_tab, "Choose File")
 
        self.setLayout(left_layout)

        self.update_combobox()

        self.raw = None
        self.eye_data = None
        
    def update_combobox(self):
        self.data_manager.fill_choose_file_combobox_with_filenames(self.combo_box)

    def on_combobox_changed(self):
        selected_filename = self.combo_box.currentText()
        
        if not selected_filename:
            self.eeg_vis_widget.clear_figure()
            self.eeg_and_pupil_analyzer_widget.clear_figure()
            self.raw = None
            self.eye_data = None
            
            self.slider.setVisible(False)
            self.slider_2.setVisible(False)
            self.shankey.setVisible(False)
            self.eeg_and_pupil_analyzer_widget.setVisible(False)
            self.heat_eye_tracking_widget.setVisible(False)
            self.channel_label.setVisible(False)
            self.slider_label_2.setVisible(False)
            self.channel_box.setVisible(False)
            self.button_3d.setVisible(False)
            self.performance_table.setVisible(False)
            
            print("EEG and Eye data cleared from memory.")
            return
        
        if selected_filename:
            self.performance_table.setVisible(True)
            self.slider.setVisible(True)
            self.slider_2.setVisible(True)
            self.button_3d.setVisible(True)
            self.channel_label.setVisible(True)
            self.slider_label_2.setVisible(True)
            self.channel_box.setVisible(True)
            self.eeg_vis_widget.setVisible(True)
            
            self.raw = self.data_manager.load_eeg_data(selected_filename)
            
            self.channel_box.clear()
            self.channel_box.addItems(self.raw.ch_names)

            total_duration = int(self.raw.n_times / self.raw.info['sfreq'])
            self.slider.setMinimum(0)
            self.slider.setMaximum(total_duration - 1)
            
            self.eye_data = self.data_manager.load_eye_data(selected_filename, pd)

            self.slider.valueChanged.connect(self.visualize_data)
            self.slider_2.valueChanged.connect(self.choose_visualization_by_slider)
            self.channel_box.currentIndexChanged.connect(self.visualize_data)

            self.display_selected_data()
            self.choose_visualization_by_slider()
            self.visualize_data()
        
    def visualize_data(self):
        if self.raw:
            selected_time = self.slider.value()
            selected_channel = self.channel_box.currentText()
            if selected_channel:
                sfreq = self.raw.info['sfreq']
                time = np.arange(self.raw.n_times) / sfreq
                data, _ = self.raw[:, :]

                channel_idx = self.raw.ch_names.index(selected_channel)
                start_idx = int(selected_time * sfreq)
                end_idx = int(start_idx + 10 * sfreq)  # 10-second window

                self.eeg_vis_widget.plot_eeg_signal(data[channel_idx, start_idx:end_idx],
                                                    time[start_idx:end_idx],
                                                    selected_channel)
                
    def choose_visualization_by_slider(self):
        slider_value = self.slider_2.value()
        if slider_value == 0:
            print(self.slider_2.value())
            self.slider_label_2.setText("Eye Tracking Plot:")
            self.heat_eye_tracking_widget.setVisible(False)
            self.eeg_and_pupil_analyzer_widget.setVisible(True)  # Show eye tracking plot
            self.eeg_and_pupil_analyzer_widget.show_pupil_eeg_plot(pd, np, self.raw, self.eye_data)  # Update plot
        
        elif slider_value == 1:
            print(self.slider_2.value())
            self.slider_label_2.setText("Heat Eye Tracking Plot:")
            self.shankey.setVisible(False)
            self.eeg_and_pupil_analyzer_widget.setVisible(False)
            self.heat_eye_tracking_widget.setVisible(True)
            self.heat_eye_tracking_widget.plot_heat_eye_tracking_data(self.eye_data)
        elif slider_value == 2:
            self.slider_label_2.setText("Sankey Diagram:")
            self.heat_eye_tracking_widget.setVisible(False)
            self.shankey.setVisible(True)
            self.shankey.show_sankey_diagram(self.eye_data)

    def on_button_3d_click(self):
        self.eye_tracking_3d_window.plot_eye_tracking_data_3d(self.eye_data)
        self.eye_tracking_3d_window.show()
        
    def display_selected_data(self):
        """Display data for the file selected in the combo_box in a vertical table."""
        selected_file = self.combo_box.currentText()  # The file name chosen by the user (e.g., '1_2_3')
        
        if not selected_file:
            return

        self.data_manager.insert_performance_data_into_table(pd, selected_file, QtWidgets, QTableWidgetItem, self.performance_table)
                