import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.sankey import Sankey
from matplotlib.figure import Figure
from matplotlib.sankey import Sankey
from collections import Counter
import seaborn as sns
import matplotlib.patches as mpatches
from scipy.signal import butter, filtfilt
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QWidget, QLabel
from PyQt5.QtCore import Qt

"""
    Heat Eye Tracking Plot: Displays eye movement data in a scatter plot, colored based on different movement types.
    Sankey Diagram: Visualizes transitions between different eye movement types.
    3D Eye Tracking Plot: Represents eye movement points in a 3D space.
    EEG Signal Visualization: Displays the temporal variations of EEG signals in a selected channel.
    Pupil and EEG Plot: Correlates EEG alpha wave activity with pupil diameter, issuing warnings if values exceed normal thresholds.

"""


class HeatEyeTrackingPlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)  

        self.layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def plot_heat_eye_tracking_data(self, df):
        print("Displaying Eye Tracking Scatter Plot")
        self.ax.clear()  
        
        category_mapping = {0: "Fixation", 1: "Saccade", 2: "Eye Not Found"}
        df["Eye movement category"] = df["Eye movement type index"].map(category_mapping)

        custom_palette = {
            "Fixation": "#2ca02c",      # Green
            "Saccade": "#d62728",       # Red
            "Eye Not Found": "#000000"  # Black
        }
        
        # Creating a scatter plot using Seaborn
        sns.scatterplot(data=df, x="Gaze point X", y="Gaze point Y", hue="Eye movement category", 
                        palette=custom_palette, ax=self.ax)
        
        # Axis labels and settings
        self.ax.set_xlabel("Gaze point X")
        self.ax.set_ylabel("Gaze point Y")
        self.ax.set_title("Eye movement types and focused points")

        self.canvas.draw()
        self.setVisible(True)



class SankeyDiagramWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)  # Initially not visible
        
        self.layout = QVBoxLayout(self)
        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

    def show_sankey_diagram(self, df):
        print("Displaying Sankey Diagram")
        self.create_sankey_diagram(df)
        self.setVisible(True)
    
    def create_sankey_diagram(self, df):
        self.ax.clear()
        
        # Creating transitions between eye movement types
        transitions = [(df["Eye movement type index"].iloc[i], df["Eye movement type index"].iloc[i+1]) 
                       for i in range(len(df)-1)]
        counts = Counter(transitions)
        
        unique_indexes = sorted(set(df["Eye movement type index"]))
        labels = {idx: f"Type {idx}" for idx in unique_indexes}  # Dynamic labels
        
        flows = []
        labels_list = []
        for (source, target), value in counts.items():
            if source in labels and target in labels:
                flows.append(value)
                labels_list.append(f"{labels[source]} → {labels[target]}")

        # Creating the Sankey diagram
        sankey = Sankey(ax=self.ax, unit=None)
        sankey.add(flows=flows, labels=labels_list, orientations=[0]*len(flows))
        sankey.finish()
        
        self.ax.set_title("Transitions between eye movement types")
        self.canvas.draw()


class EyeTrackingPlot3DWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("3D Eye Tracking Data")
        self.setGeometry(100, 100, 800, 600)

        # Initialize layout and Matplotlib
        self.layout = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

    def clear_figure(self):
        """Clears the previous figure"""
        self.figure.clear()

    def plot_eye_tracking_data_3d(self, eye_data):
        """Displays 3D eye movement points with appropriate colors and legend"""
        self.clear_figure()
        ax = self.figure.add_subplot(111, projection="3d")

        # Color palette for integer types
        custom_palette = {
            0: ("#2ca02c", "Fixation"),      # Green
            1: ("#d62728", "Saccade"),       # Red
            2: ("#000000", "Eye Not Found")  # Black
        }

        # 🔍 Print unique values for verification
        unique_types = eye_data["Eye movement type index"].unique()
        print("Unique eye movement types:", unique_types)

        # Assign colors and labels
        colors = eye_data["Eye movement type index"].map(lambda t: custom_palette.get(t, ("#808080", "Unknown"))[0])

        # If a type is missing from the palette, assign gray
        colors = colors.fillna("#808080")

        # Verification: Print the color mapping
        print("🎨 Color mapping:", colors.unique())

        # Display points
        ax.scatter(
            eye_data["Gaze point 3D X"],
            eye_data["Gaze point 3D Y"],
            eye_data["Gaze point 3D Z"],
            c=colors,
            s=5,
            alpha=0.5
        )

        # Set axes labels
        ax.set_title("Eye Movement Points (3D Space)")
        ax.set_xlabel("Gaze point 3D X")
        ax.set_ylabel("Gaze point 3D Y")
        ax.set_zlabel("Gaze point 3D Z")

        # 📌 **Add legend**
        legend_patches = [mpatches.Patch(color=color, label=label) for _, (color, label) in custom_palette.items()]
        ax.legend(handles=legend_patches, loc="upper right")

        # Update the canvas
        self.canvas.draw()


class EEGPupilAnalyzer(QWidget):
    
    """
     EEG Alpha Wave Activity (8-12 Hz)
     
        What does it measure?
            The brain's electrical activity, but only the alpha waves (8-12 Hz)
            These are signals of a relaxed, awake resting state (e.g., meditation, relaxation)
        How does it measure?
            Applies a bandpass filter (Butterworth filter) to retain only the alpha-band signals
            Averages EEG channels and smooths the data
        What does it monitor and alert?
            Too low alpha activity → Excessive attention, stress, mental fatigue
            Too high alpha activity → Excessive relaxation, drowsiness, loss of concentration
            Strong fluctuation → Unstable attention state, switching between rest and concentration

    Correlations and Warnings
        
        This system links pupil and EEG signals, for example:

            If the pupil constricts and alpha waves decrease → Mental overload, stress
            If the pupil dilates and alpha waves increase → Drowsiness, loss of concentration
            If both are within the normal range → Stable attention state
    
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVisible(False)

        self.layout = QVBoxLayout(self)
        self.figure = Figure(figsize=(12, 6))
        self.ax1 = self.figure.add_subplot(211)  # Pupil diameter
        self.ax2 = self.figure.add_subplot(212)  # EEG Alpha waves
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        # Display warning text
        self.alert_label = QLabel("", self)
        self.alert_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.alert_label)

    def clear_figure(self):
        """Clears the plots before redrawing."""
        self.ax1.clear()
        self.ax2.clear()

    def bandpass_filter(self, fs, data, lowcut=8, highcut=12, order=4):
        """Butterworth bandpass filter for highlighting EEG alpha waves."""
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return filtfilt(b, a, data, axis=0)

    def show_pupil_eeg_plot(self, pd, np, raw, df_pupil):
        """Displays pupil and EEG data on a common time scale."""
        print("Displaying Pupil Diameter and EEG Alpha Waves Plot")
        df_eeg = raw.to_data_frame()
        print(df_eeg)
        if "time" not in df_eeg.columns:
            raise ValueError("The EEG data does not contain a 'time' column.")

        df_eeg.set_index("time", inplace=True)

        min_time = max(df_pupil.index.min(), df_eeg.index.min())
        max_time = min(df_pupil.index.max(), df_eeg.index.max())
        """
            We calculate the time window during which both the EEG and pupil data are available.
                The max(df_pupil.index.min(), df_eeg.index.min()) ensures that we take the first common time point.
                The min(df_pupil.index.max(), df_eeg.index.max()) determines the last common time point.

            In other words, we consider only the data that exists in both sources.
        
        """

        if pd.isna(min_time) or pd.isna(max_time):
            raise ValueError("No common time interval found between pupil and EEG data.")

        common_time = np.linspace(min_time, max_time, num=len(df_pupil))
        """
            It creates evenly spaced time points for the EEG and pupil data.
            The number of samples is adjusted to match the number of pupil data points.
            
            The EEG and pupil data may have been recorded at different sampling rates. 
            They need to be brought onto a common time scale to make them comparable.
        """

        df_pupil_interp = df_pupil.reindex(df_pupil.index.union(common_time)).interpolate(method="linear").loc[common_time]
        df_eeg_interp = df_eeg.reindex(df_eeg.index.union(common_time)).interpolate(method="linear").loc[common_time]
        """
            The new common time points are added to the original index.
            
                Interpolation is performed (interpolate(method="linear")) to obtain the corresponding values for these new time points.
                The data is then filtered to the new common time scale using loc[common_time].

                    If the EEG and pupil data were recorded at different time points, interpolation is used to estimate the intermediate values.
                    Linear interpolation assumes a smooth, even transition between two known points.
        
        """

        self.create_pupil_eeg_plot(df_pupil_interp, df_eeg_interp, raw.info['sfreq'])
        self.setVisible(True)

    def create_pupil_eeg_plot(self, df_pupil, df_eeg, freq):
        """Displays pupil diameter and EEG Alpha waves with filtered data."""
        self.clear_figure()
        alert_messages = []

        # **Pupil warning**
        if "Pupil diameter left" in df_pupil.columns and "Pupil diameter right" in df_pupil.columns:
            self.ax1.plot(df_pupil.index, df_pupil["Pupil diameter left"], label="Left pupil", color="blue")
            self.ax1.plot(df_pupil.index, df_pupil["Pupil diameter right"], label="Right pupil", color="red")

            # **Warning if pupil diameter is too small or large**
            pupil_min, pupil_max = 2.0, 6.5  
            if df_pupil["Pupil diameter left"].min() < pupil_min or df_pupil["Pupil diameter right"].min() < pupil_min:
                self.ax1.axhline(y=pupil_min, color='red', linestyle='--', label="Too small pupil")
                alert_messages.append("⚠️ Pupil too small!")

            if df_pupil["Pupil diameter left"].max() > pupil_max or df_pupil["Pupil diameter right"].max() > pupil_max:
                self.ax1.axhline(y=pupil_max, color='orange', linestyle='--', label="Too large pupil")
                alert_messages.append("⚠️ Pupil too dilated!")

        self.ax1.set_ylabel("Pupil Diameter (mm)", fontsize=12, labelpad=10)
        self.ax1.set_title("Changes in Pupil Diameter Over Time", fontsize=14, pad=15)
        self.ax1.legend()
        self.ax1.grid()

        # **EEG Alpha Wave Filtering**
        eeg_alpha_filtered = df_eeg.apply(lambda col: self.bandpass_filter(freq, col, lowcut=8, highcut=12))
        """
            Apply a bandpass filter to every column (each channel) of the EEG data (df_eeg), allowing only frequencies between 8-12 Hz to pass through.
            This filters out the alpha waves (8-12 Hz) from the EEG signals.
        """
        eeg_alpha_mean = eeg_alpha_filtered.mean(axis=1)
        """
            Calculate the averaged alpha activity of all EEG channels over time (row-wise, meaning at each time point).
            The axis=1 parameter means averaging row-wise, so the final value is the average of all channels.
        
        """
        eeg_alpha_smooth = eeg_alpha_mean.rolling(window=50, min_periods=1).mean()
        """
            window=50 → The moving average is computed from 50 consecutive data points.
            
            Thus, at each time point, the new value is given by the average of the current value and the preceding 49 values.
        """

        self.ax2.plot(df_eeg.index, eeg_alpha_smooth, label="Filtered Alpha Activity", color="green")

        # **EEG Activity Warning**
        eeg_threshold_low, eeg_threshold_high = eeg_alpha_smooth.quantile(0.05), eeg_alpha_smooth.quantile(0.95)
        """
            0.05 quantile (5%) → Lower threshold: if the alpha activity is too low.
            0.95 quantile (95%) → Upper threshold: if the alpha activity is too high.
            
            These thresholds help determine when the EEG activity exceeds the normal range.
        
        """

        low_crossed = eeg_alpha_smooth.min() < eeg_threshold_low
        high_crossed = eeg_alpha_smooth.max() > eeg_threshold_high
        
        """
            It checks whether the alpha activity has exceeded the limits:

                # low_crossed → If the minimum value of the alpha activity is below the 5% threshold, then it is too low.
                # high_crossed → If the maximum value of the alpha activity is above the 95% threshold, then it is too high.
        """
        
        """
            The EEG alpha activity thresholds are determined based on the statistical distribution of the data.
            
            This means that the thresholds dynamically adjust according to the distribution of the recorded EEG data.
            So, the boundaries on the graph should not be set to zero but to the values determined by the quantiles.
        """

        if low_crossed and high_crossed:
            self.ax2.axhline(y=eeg_threshold_high, color='red', linestyle='--', label="EEG Activity Threshold")
            alert_messages.append("⚠️ EEG Alpha activity fluctuating strongly! Check your concentration or take a short break!")
        else:
            if low_crossed:
                self.ax2.axhline(y=eeg_threshold_low, color='red', linestyle='--', label="EEG Activity Threshold")
                alert_messages.append("⚠️ EEG Alpha activity too low!")

            if high_crossed:
                self.ax2.axhline(y=eeg_threshold_high, color='orange', linestyle='--', label="EEG Activity Threshold")
                alert_messages.append("⚠️ EEG Alpha activity too high!")

        self.ax2.set_xlabel("Time Index", fontsize=12, labelpad=10)
        self.ax2.set_ylabel("EEG Alpha Waves", fontsize=12, labelpad=10)
        self.ax2.set_title("Changes in EEG Alpha Waves Over Time", fontsize=14, pad=15)
        self.ax2.legend()
        self.ax2.grid()

        self.figure.subplots_adjust(hspace=0.4)

        if alert_messages:
            self.alert_label.setText("\n".join(alert_messages))
            self.alert_label.setStyleSheet("color: red; font-size: 14px; font-weight: bold;")
        else:
            self.alert_label.setText("")
            self.alert_label.setStyleSheet("")

        self.canvas.draw()


class EEGSignalVisualizationbWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def clear_figure(self):
        self.figure.clear()
        
    def plot_eeg_signal(self, data, time, channel_name):
        self.clear_figure() 
        
        ax = self.figure.add_subplot(111)
        ax.plot(time, data)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("EEG Signal (µV)")
        ax.set_title(f"EEG Signal Over Time - {channel_name}")
        ax.grid()
        
        self.canvas.draw()  
        