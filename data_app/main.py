import sys
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QPushButton,
    QVBoxLayout,
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

        # Create the save button
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)

        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        layout.addWidget(self.save_button)

        # Set the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

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
