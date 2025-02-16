import os
import mne

"""
    Loads EEG data from .edf files using the MNE library.
    Reads eye-tracking data from .csv files with predefined column names.
    Processes CSV files related to tasks and performance data, then displays them in tables (e.g., task list, performance data).
    
"""

class DataManager:
    def __init__(self):
        self.column_names_to_eye_df = [
            "Gaze point X", "Gaze point Y", "Gaze point 3D X", "Gaze point 3D Y", "Gaze point 3D Z",
            "Gaze direction left X", "Gaze direction left Y", "Gaze direction left Z",
            "Gaze direction right X", "Gaze direction right Y", "Gaze direction right Z",
            "Pupil position left X", "Pupil position left Y", "Pupil position left Z",
            "Pupil position right X", "Pupil position right Y", "Pupil position right Z",
            "Pupil diameter left", "Pupil diameter right", "Eye movement type index"
        ]

    def fill_choose_file_combobox_with_filenames(self, combo_box):
        eeg_files = [f for f in os.listdir(r'C:\Users\T\Desktop\tomi_valai\EEG') if f.endswith('.edf')]
        combo_box.addItem("")  # Empty value at the top of the list
        combo_box.addItems([f.replace('.edf', '') for f in eeg_files])

    def insert_tasks_csv_data_into_tasks_table(self, pd, QTableWidgetItem, Qt, QtWidgets, table_widget, file_path):
        df = pd.read_csv(file_path)  # Load CSV file
        df.fillna("", inplace=True)  # Remove NaN values

        df.columns = ["" if "Unnamed" in col else col for col in df.columns]

        table_widget.setRowCount(df.shape[0])
        table_widget.setColumnCount(df.shape[1])
        table_widget.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[row, col]))

                # Enable word wrapping for the second column (index 1)
                if col == 1:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignTop)  # Align left
                    item.setFlags(item.flags() | Qt.ItemIsEditable)  # Keep editability
                    item.setToolTip(item.text())  # Show full text in a tooltip

                table_widget.setItem(row, col, item)

        table_widget.verticalHeader().setVisible(False)  # Hide row indices
        table_widget.setAlternatingRowColors(True)  # Better appearance
        table_widget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        table_widget.resizeRowsToContents()  # Auto-adjust row height

    def insert_performance_data_into_table(self, pd, selected_file, QtWidgets, QTableWidgetItem, performance_table):
        perf_df = self.load_performance_csv(pd)

        perf_df["EEG File Name"] = perf_df["EEG File Name"].str.replace("'", "")
        perf_df["EEG File Name"] = perf_df["EEG File Name"].str.removesuffix(".edf")

        perf_df["Eye File Name"] = perf_df["Eye File Name"].str.replace("'", "")
        perf_df["Eye File Name"] = perf_df["Eye File Name"].str.removesuffix(".csv")
        selected_file = selected_file.strip().lower()

        matched_row = perf_df[perf_df["EEG File Name"] == selected_file]

        # Search based on the selected filename
        if matched_row.empty:  # No match found
            performance_table.clear()
            performance_table.setRowCount(1)
            performance_table.setColumnCount(1)
            performance_table.setItem(0, 0, QTableWidgetItem("No match found"))
            return

        row_data = matched_row.iloc[0]  # Select the first match

        # Update table and apply vertical formatting
        performance_table.clear()
        performance_table.setRowCount(len(row_data))
        performance_table.setColumnCount(2)  # Two columns: Attribute name + Value
        performance_table.verticalHeader().setVisible(False)

        performance_table.setHorizontalHeaderLabels(["Attribute", "Value"])

        # Insert data
        for row, (key, value) in enumerate(row_data.items()):
            performance_table.setItem(row, 0, QTableWidgetItem(str(key)))  # Attribute name
            performance_table.setItem(row, 1, QTableWidgetItem(str(value)))  # Value

        performance_table.resizeRowsToContents()
        performance_table.setMaximumWidth(300)
        performance_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        performance_table.horizontalHeader().setMaximumSectionSize(300)

    def load_eeg_data(self, selected_filename):
        eeg_file_path = os.path.join(r'C:\Users\T\Desktop\tomi_valai\EEG', selected_filename + '.edf')
        raw = mne.io.read_raw_edf(eeg_file_path, preload=True)

        print(f"EEG file loaded: {eeg_file_path}")
        print(raw.info)

        return raw

    def load_eye_data(self, selected_filename, pd):
        eye_file_path = os.path.join(r'C:\Users\T\Desktop\tomi_valai\EYE', selected_filename + '.csv')
        eye_data = pd.read_csv(eye_file_path, header=None, names=self.column_names_to_eye_df)

        return eye_data

    def load_performance_csv(self, pd):
        performance_df = pd.read_csv(r'C:\Users\T\Desktop\tomi_valai\PerformanceScores.csv')
        print(performance_df)
        return performance_df
