from PyQt5.QtWidgets import QApplication
from simulator_window import SimulatorWindow 

"""
    
        Visual Studio Code Version:     1.97.1 (user setup)
        OS:                             Windows_NT x64 10.0.22631
        
        Source:                         https://physionet.org/content/eeg-eye-gaze-data/1.0.0/
    
    The system aims to provide an integrated platform for loading, processing, and visualizing EEG and eye-tracking data, enabling users to interactively 
    analyze the data, monitor cognitive states (such as relaxation, stress, and attention), and detect any deviations from normal patterns.
    
"""

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = SimulatorWindow()
    window.show()
    sys.exit(app.exec_())

