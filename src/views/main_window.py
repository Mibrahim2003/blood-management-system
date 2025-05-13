from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTabWidget
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blood Donation System")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.label = QLabel("Welcome to the Blood Donation System")
        self.layout.addWidget(self.label)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        self.init_tabs()

    def init_tabs(self):
        # Placeholder for donor views
        donor_tab = QWidget()
        self.tab_widget.addTab(donor_tab, "Donors")
        donor_layout = QVBoxLayout()
        donor_tab.setLayout(donor_layout)
        donor_button = QPushButton("Manage Donors")
        donor_layout.addWidget(donor_button)

        # Placeholder for receiver views
        receiver_tab = QWidget()
        self.tab_widget.addTab(receiver_tab, "Receivers")
        receiver_layout = QVBoxLayout()
        receiver_tab.setLayout(receiver_layout)
        receiver_button = QPushButton("Manage Receivers")
        receiver_layout.addWidget(receiver_button)

        # Placeholder for blood unit views
        blood_unit_tab = QWidget()
        self.tab_widget.addTab(blood_unit_tab, "Blood Units")
        blood_unit_layout = QVBoxLayout()
        blood_unit_tab.setLayout(blood_unit_layout)
        blood_unit_button = QPushButton("Manage Blood Units")
        blood_unit_layout.addWidget(blood_unit_button)

        # Placeholder for blood request views
        blood_request_tab = QWidget()
        self.tab_widget.addTab(blood_request_tab, "Blood Requests")
        blood_request_layout = QVBoxLayout()
        blood_request_tab.setLayout(blood_request_layout)
        blood_request_button = QPushButton("Manage Blood Requests")
        blood_request_layout.addWidget(blood_request_button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())