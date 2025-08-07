import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)

from database import setup_database, load_data, save_data
from pandas_model import PandasModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Editor")
        self.setGeometry(100, 100, 600, 400)

        # Set up the database
        setup_database()

        # Load data and create the model
        self.df = load_data()
        self.model = PandasModel(self.df)

        # Create the table view
        self.table_view = QTableView()
        self.table_view.setModel(self.model)

        # Create the buttons
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)

        # Set up the button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_row_button)
        button_layout.addWidget(self.save_button)

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table_view)
        main_layout.addLayout(button_layout)

        # Set the central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def add_row(self):
        """Add a new row to the table."""
        self.model.addRow()

    def save_changes(self):
        """Save the changes from the model back to the database."""
        updated_df = self.model.get_dataframe()
        save_data(updated_df)
        print("Changes saved successfully.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # In a non-interactive environment, we can't show the window.
    # We will just check if it runs without errors and then exit.
    if app.platformName() == "offscreen":
        QTimer.singleShot(2000, app.quit)

    sys.exit(app.exec())
