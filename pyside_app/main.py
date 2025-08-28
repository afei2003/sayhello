import sys
import configparser
from pathlib import Path
import pandas as pd

from PySide6.QtCore import QAbstractTableModel, Qt, QDate
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableView,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QMessageBox,
    QFileDialog,
    QLabel,
    QDateEdit,
)
from sqlalchemy import create_engine, text, bindparam
from sqlalchemy.exc import SQLAlchemyError


class PandasModel(QAbstractTableModel):
    """
    A model to interface a pandas DataFrame with QTableView.
    This class provides a QAbstractTableModel implementation that wraps a pandas DataFrame,
    allowing it to be displayed and manipulated in a QTableView.
    """

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        QAbstractTableModel.__init__(self, parent)
        self._dataframe = dataframe

    def rowCount(self, parent=None):
        """Returns the number of rows in the DataFrame."""
        return self._dataframe.shape[0]

    def columnCount(self, parent=None):
        """Returns the number of columns in the DataFrame."""
        return self._dataframe.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data at the given index."""
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._dataframe.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Returns the header data for the given section."""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._dataframe.columns[section]
        return None

    def get_dataframe(self):
        """Returns the underlying pandas DataFrame."""
        return self._dataframe


class MainWindow(QMainWindow):
    """
    The main window of the application.
    This class sets up the UI, handles database connections, and manages data operations.
    """
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowTitle("Order Data Viewer")
        self.setGeometry(100, 100, 1024, 768)

        # --- UI Elements ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Date selection layout
        date_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit = QDateEdit(calendarPopup=True)

        # Set default dates
        self.end_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setDate(QDate.currentDate().addDays(-1))

        date_layout.addWidget(QLabel("Start Date:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("End Date:"))
        date_layout.addWidget(self.end_date_edit)
        date_layout.addStretch()

        self.fetch_button = QPushButton("Fetch Data")
        self.export_button = QPushButton("Export to Excel")
        self.table_view = QTableView()

        # Add widgets to main layout
        main_layout.addLayout(date_layout)
        main_layout.addWidget(self.fetch_button)
        main_layout.addWidget(self.export_button)
        main_layout.addWidget(self.table_view)

        # --- Initial State ---
        self.export_button.setEnabled(False) # Disabled until data is loaded
        self.engine = None
        self.model = None

        # --- Connections ---
        self.fetch_button.clicked.connect(self.fetch_data)
        self.export_button.clicked.connect(self.export_to_excel)

        # --- Initialization ---
        self.setup_database_connection()


    def setup_database_connection(self):
        """
        Reads database credentials from config.ini and sets up the SQLAlchemy engine.
        """
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / "config.ini"

        if not config_path.exists():
            self.show_error_message(
                "Configuration file 'config.ini' not found. "
                "Please copy 'config.ini.example' to 'config.ini' and fill in your database credentials."
            )
            return

        try:
            config.read(config_path)
            db_config = config["database"]
            server = db_config["server"]
            database = db_config["database"]
            username = db_config["username"]
            password = db_config["password"]
            driver = db_config.get("driver", "ODBC Driver 17 for SQL Server")

            # Create the connection string for MSSQL with pyodbc
            connection_string = (
                f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}"
            )
            self.engine = create_engine(connection_string)

            # Test the connection to ensure it's valid
            with self.engine.connect() as connection:
                print("Database connection successful!")

        except (SQLAlchemyError, KeyError) as e:
            self.show_error_message(f"Database connection failed: {e}")
            self.engine = None
        except Exception as e:
            self.show_error_message(f"An unexpected error occurred during database setup: {e}")
            self.engine = None

    def fetch_data(self):
        """
        Fetches data from the database in two steps and populates the QTableView.
        """
        if not self.engine:
            self.show_error_message("Database connection is not available.")
            return

        try:
            with self.engine.connect() as connection:
                # Get dates from the UI
                start_date = self.start_date_edit.date().toPython()
                end_date = self.end_date_edit.date().toPython()

                # Format dates for the SQL query
                start_date_str = start_date.strftime('%Y-%m-%d 00:00:00')
                end_date_str = end_date.strftime('%Y-%m-%d 23:59:59') # Inclusive of the end date

                # Step 1: Get the list of order_ids from the invoices table
                order_id_query = text("""
                    select a.order_id from dbo.invoice_step_maps a
                    left join
                    dbo.invoices b on a.invoice_id = b.id
                    where b.paid_at >= :start_date and b.paid_at <= :end_date
                    group by a.order_id
                """)

                params = {'start_date': start_date_str, 'end_date': end_date_str}
                order_id_result = connection.execute(order_id_query, params)
                order_ids = [row[0] for row in order_id_result]

                if not order_ids:
                    self.show_error_message("No orders found for the given date range.")
                    self.export_button.setEnabled(False)
                    if self.model:
                        self.model._dataframe = pd.DataFrame() # Clear table
                        self.model.layoutChanged.emit()
                    return

                # Step 2: Fetch data from v_invoice_step using the retrieved order_ids
                data_query = text("""
                    select order_id, model, quantity, count_pass, count_neg, unit_price, client, created_at
                    from v_invoice_step
                    where order_id in :order_ids
                """).bindparams(bindparam('order_ids', expanding=True))

                df = pd.read_sql(data_query, connection, params={'order_ids': order_ids})

                if df.empty:
                    self.show_error_message("No data found in v_invoice_step for the retrieved order IDs.")
                    self.export_button.setEnabled(False)
                    if self.model:
                        self.model._dataframe = pd.DataFrame()
                        self.model.layoutChanged.emit()
                    return

                # Populate the QTableView with the fetched data
                self.model = PandasModel(df)
                self.table_view.setModel(self.model)
                self.export_button.setEnabled(True)
                print(f"Successfully fetched {len(df)} rows.")

        except SQLAlchemyError as e:
            self.show_error_message(f"Failed to fetch data: {e}")
        except Exception as e:
            self.show_error_message(f"An unexpected error occurred during data fetch: {e}")

    def export_to_excel(self):
        """
        Exports the data from the QTableView to an Excel file.
        """
        if not self.model:
            self.show_error_message("No data to export.")
            return

        df = self.model.get_dataframe()
        if df.empty:
            self.show_error_message("No data to export.")
            return

        # Open a file dialog to get the save path from the user
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Excel Files (*.xlsx);;All Files (*)",
            options=options,
        )

        if file_path:
            try:
                # Use pandas to_excel to save the DataFrame
                df.to_excel(file_path, index=False, engine='openpyxl')
                QMessageBox.information(self, "Success", f"Data successfully exported to {file_path}")
            except Exception as e:
                self.show_error_message(f"Failed to export data to Excel: {e}")

    def show_error_message(self, message):
        """
        Displays an error message in a pop-up dialog.
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.exec()


if __name__ == "__main__":
    # Application entry point
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
