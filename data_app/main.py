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
    QMessageBox,
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

        # Create the table view
        self.table_view = QTableView()

        # Load data and create the model
        self.load_and_set_model()

        # Create the buttons
        self.add_row_button = QPushButton("Add Row")
        self.add_row_button.clicked.connect(self.add_row)
        self.delete_row_button = QPushButton("Delete Row")
        self.delete_row_button.clicked.connect(self.delete_row)
        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.reload_button = QPushButton("Reload Data")
        self.reload_button.clicked.connect(self.reload_data)

        # Set up the button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_row_button)
        button_layout.addWidget(self.delete_row_button)
        button_layout.addStretch() # Add a spacer
        button_layout.addWidget(self.reload_button)
        button_layout.addWidget(self.save_button)

        # Set up the main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table_view)
        main_layout.addLayout(button_layout)

        # Set the central widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_and_set_model(self):
        """Loads data from the database and sets it as the model for the view."""
        self.df = load_data()
        self.model = PandasModel(self.df)
        self.table_view.setModel(self.model)

    def add_row(self):
        """Add a new row to the table."""
        self.model.addRow()

    def delete_row(self):
        """Delete the selected row from the table."""
        selected_row = self.table_view.currentIndex().row()
        if selected_row >= 0:
            self.model.deleteRow(selected_row)
        else:
            print("No row selected to delete.")

    def save_changes(self):
        """Save the changes from the model back to the database."""
        updated_df = self.model.get_dataframe()
        save_data(updated_df)
        print("Changes saved successfully.")
        # It's good practice to reload data from DB after saving to get new IDs
        print("Reloading data to get new IDs from database...")
        self.load_and_set_model()

    def reload_data(self):
        """Reloads the data from the database, discarding local changes."""
        print("Reloading data from database...")
        self.load_and_set_model()
        print("Data reloaded.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # In a non-interactive environment, we can't show the window.
    # We will just check if it runs without errors and then exit.
    if app.platformName() == "offscreen":
        QTimer.singleShot(2000, app.quit)

    sys.exit(app.exec())
