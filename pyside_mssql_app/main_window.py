import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QPushButton,
    QHeaderView,
    QMessageBox,
    QDialog,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox
)
from PySide6.QtCore import Slot

from database import SessionLocal, PN, Pin
from models import PnTableModel, PinTableModel

class PnDialog(QDialog):
    def __init__(self, parent=None, pn=None):
        super().__init__(parent)
        self.setWindowTitle("Add/Edit PN")

        self.partnumber_edit = QLineEdit(pn.partnumber if pn else "")
        self.note_edit = QLineEdit(pn.note if pn else "")

        form_layout = QFormLayout()
        form_layout.addRow("Part Number:", self.partnumber_edit)
        form_layout.addRow("Note:", self.note_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def get_data(self):
        return {
            "partnumber": self.partnumber_edit.text(),
            "note": self.note_edit.text()
        }

class PinDialog(QDialog):
    def __init__(self, parent=None, pin=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Pin" if pin else "Add Pin")

        self.pin_edit = QLineEdit(pin.pin if pin else "")
        self.name_edit = QLineEdit(pin.name if pin else "")
        self.base_pin_edit = QLineEdit(pin.base_pin if pin else "")
        self.note_edit = QLineEdit(pin.note if pin else "")

        form_layout = QFormLayout()
        form_layout.addRow("Pin:", self.pin_edit)
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Base Pin:", self.base_pin_edit)
        form_layout.addRow("Note:", self.note_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def get_data(self):
        return {
            "pin": self.pin_edit.text(),
            "name": self.name_edit.text(),
            "base_pin": self.base_pin_edit.text(),
            "note": self.note_edit.text()
        }


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Part Number Management")
        self.setGeometry(100, 100, 1200, 600)

        # Database session
        self.session = SessionLocal()

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # --- PN Table Section ---
        pn_layout = QVBoxLayout()
        pn_widget = QWidget()
        pn_widget.setLayout(pn_layout)

        self.table_pn = QTableView()
        self.table_pn.setObjectName("QTableView_pn")
        self.table_pn.setAlternatingRowColors(True)
        self.table_pn.setSelectionBehavior(QTableView.SelectRows)
        self.table_pn.setSelectionMode(QTableView.SingleSelection)
        self.table_pn.horizontalHeader().setStretchLastSection(True)

        self.pn_model = PnTableModel(self.session)
        self.table_pn.setModel(self.pn_model)
        self.table_pn.selectionModel().selectionChanged.connect(self.pn_selection_changed)


        pn_button_layout = QHBoxLayout()
        self.btn_add_pn = QPushButton("Add PN")
        self.btn_edit_pn = QPushButton("Edit PN")
        self.btn_delete_pn = QPushButton("Delete PN")
        pn_button_layout.addWidget(self.btn_add_pn)
        pn_button_layout.addWidget(self.btn_edit_pn)
        pn_button_layout.addWidget(self.btn_delete_pn)
        pn_button_layout.addStretch()

        pn_layout.addWidget(self.table_pn)
        pn_layout.addLayout(pn_button_layout)


        # --- Pin Table Section ---
        pin_layout = QVBoxLayout()
        pin_widget = QWidget()
        pin_widget.setLayout(pin_layout)

        self.table_pin = QTableView()
        self.table_pin.setObjectName("QTableView_pin")
        self.table_pin.setAlternatingRowColors(True)
        self.table_pin.setSelectionBehavior(QTableView.SelectRows)
        self.table_pin.setSelectionMode(QTableView.SingleSelection)
        self.table_pin.horizontalHeader().setStretchLastSection(True)

        self.pin_model = PinTableModel(self.session)
        self.table_pin.setModel(self.pin_model)

        pin_button_layout = QHBoxLayout()
        self.btn_add_pin = QPushButton("Add Pin")
        self.btn_edit_pin = QPushButton("Edit Pin")
        self.btn_delete_pin = QPushButton("Delete Pin")
        pin_button_layout.addWidget(self.btn_add_pin)
        pin_button_layout.addWidget(self.btn_edit_pin)
        pin_button_layout.addWidget(self.btn_delete_pin)
        pin_button_layout.addStretch()

        pin_layout.addWidget(self.table_pin)
        pin_layout.addLayout(pin_button_layout)

        # Add to main layout
        main_layout.addWidget(pn_widget, 1)
        main_layout.addWidget(pin_widget, 2)

        # Load initial data
        self.pn_model.load_data()

        # Connect signals and slots
        self.btn_add_pn.clicked.connect(self.add_pn)
        self.btn_edit_pn.clicked.connect(self.edit_pn)
        self.btn_delete_pn.clicked.connect(self.delete_pn)
        self.btn_add_pin.clicked.connect(self.add_pin)
        self.btn_edit_pin.clicked.connect(self.edit_pin)
        self.btn_delete_pin.clicked.connect(self.delete_pin)

    def closeEvent(self, event):
        self.session.close()
        event.accept()

    @Slot()
    def pn_selection_changed(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes:
            self.pin_model.load_data(None) # Clear pin view if no selection
            return

        row = indexes[0].row()
        pn = self.pn_model.get_pn_by_row(row)
        if pn:
            self.pin_model.load_data(pn.id)

    @Slot()
    def add_pn(self):
        dialog = PnDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["partnumber"]:
                QMessageBox.warning(self, "Input Error", "Part number cannot be empty.")
                return
            new_pn = PN(partnumber=data["partnumber"], note=data["note"])
            self.pn_model.add_pn(new_pn)

    @Slot()
    def edit_pn(self):
        indexes = self.table_pn.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Selection Error", "Please select a PN to edit.")
            return

        row = indexes[0].row()
        pn_to_edit = self.pn_model.get_pn_by_row(row)

        dialog = PnDialog(self, pn=pn_to_edit)
        if dialog.exec():
            data = dialog.get_data()
            if not data["partnumber"]:
                QMessageBox.warning(self, "Input Error", "Part number cannot be empty.")
                return
            self.pn_model.edit_pn(row, data["partnumber"], data["note"])

    @Slot()
    def delete_pn(self):
        indexes = self.table_pn.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Selection Error", "Please select a PN to delete.")
            return

        row = indexes[0].row()
        pn_to_delete = self.pn_model.get_pn_by_row(row)

        reply = QMessageBox.question(self, 'Delete PN', f"Are you sure you want to delete {pn_to_delete.partnumber}?\nThis will also delete all associated pins.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            if self.pn_model.delete_pn(row):
                # Clear pin view as the parent PN is gone
                self.pin_model.load_data(None)


    @Slot()
    def add_pin(self):
        pn_indexes = self.table_pn.selectionModel().selectedRows()
        if not pn_indexes:
            QMessageBox.warning(self, "Selection Error", "Please select a PN to add a pin to.")
            return

        dialog = PinDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data["pin"]:
                QMessageBox.warning(self, "Input Error", "Pin cannot be empty.")
                return
            new_pin = Pin(**data)
            self.pin_model.add_pin(new_pin)

    @Slot()
    def edit_pin(self):
        indexes = self.table_pin.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Selection Error", "Please select a pin to edit.")
            return

        row = indexes[0].row()
        pin_to_edit = self.pin_model.get_pin_by_row(row)
        if not pin_to_edit:
            return # Should not happen if a row is selected

        dialog = PinDialog(self, pin=pin_to_edit)
        if dialog.exec():
            data = dialog.get_data()
            if not data["pin"]:
                QMessageBox.warning(self, "Input Error", "Pin cannot be empty.")
                return
            self.pin_model.edit_pin(row, data)

    @Slot()
    def delete_pin(self):
        indexes = self.table_pin.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "Selection Error", "Please select a pin to delete.")
            return

        row = indexes[0].row()
        pin_to_delete = self.pin_model.get_pin_by_row(row)

        reply = QMessageBox.question(self, 'Delete Pin', f"Are you sure you want to delete pin {pin_to_delete.pin}?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.pin_model.delete_pin(row)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Check if the database connection can be established
    try:
        session = SessionLocal()
        session.close()
    except Exception as e:
        QMessageBox.critical(None, "Database Connection Error",
                             f"Could not connect to the database.\n"
                             f"Please check the connection settings in 'database.py'.\n\n"
                             f"Error: {e}")
        sys.exit(1)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
