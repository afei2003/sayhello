from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex
from PySide6.QtWidgets import QMessageBox

class PnTableModel(QAbstractTableModel):
    def __init__(self, session, data=None):
        super().__init__()
        self.session = session
        self._data = data if data is not None else []
        self._headers = ["ID", "Part Number", "Note"]

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            if index.column() == 0:
                return str(row.id)
            elif index.column() == 1:
                return row.partnumber
            elif index.column() == 2:
                return row.note
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def get_pn_by_row(self, row):
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def load_data(self):
        from database import PN
        try:
            self.beginResetModel()
            self._data = self.session.query(PN).order_by(PN.id).all()
            self.endResetModel()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Could not load PN data: {e}")
            self._data = []

    def add_pn(self, pn):
        self.session.add(pn)
        try:
            self.session.commit()
            self.load_data() # Reload to get the new ID and correct order
            return True
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(None, "Database Error", f"Could not add PN: {e}")
            return False

    def edit_pn(self, row, partnumber, note):
        pn_to_edit = self._data[row]
        pn_to_edit.partnumber = partnumber
        pn_to_edit.note = note
        try:
            self.session.commit()
            self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))
            return True
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(None, "Database Error", f"Could not edit PN: {e}")
            return False

    def delete_pn(self, row):
        pn_to_delete = self._data[row]
        self.session.delete(pn_to_delete)
        try:
            self.session.commit()
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()
            return True
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(None, "Database Error", f"Could not delete PN: {e}")
            return False

class PinTableModel(QAbstractTableModel):
    def __init__(self, session):
        super().__init__()
        self.session = session
        self._data = []
        self._headers = ["ID", "Pin", "Name", "Base Pin", "Note"]
        self.pn_id = None

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            row = self._data[index.row()]
            if index.column() == 0:
                return str(row.id)
            elif index.column() == 1:
                return row.pin
            elif index.column() == 2:
                return row.name
            elif index.column() == 3:
                return row.base_pin
            elif index.column() == 4:
                return row.note
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return None

    def get_pin_by_row(self, row):
        if 0 <= row < len(self._data):
            return self._data[row]
        return None

    def load_data(self, pn_id):
        from database import Pin
        self.pn_id = pn_id
        try:
            self.beginResetModel()
            if self.pn_id is None:
                self._data = []
            else:
                self._data = self.session.query(Pin).filter(Pin.pn_id == self.pn_id).order_by(Pin.id).all()
            self.endResetModel()
        except Exception as e:
            QMessageBox.critical(None, "Database Error", f"Could not load Pin data: {e}")
            self._data = []

    def add_pin(self, pin):
        if self.pn_id is None:
            QMessageBox.warning(None, "No PN Selected", "Please select a Part Number before adding a pin.")
            return False

        pin.pn_id = self.pn_id
        self.session.add(pin)
        try:
            self.session.commit()
            self.load_data(self.pn_id) # Reload to get new ID and correct order
            return True
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(None, "Database Error", f"Could not add Pin: {e}")
            return False

    def delete_pin(self, row):
        pin_to_delete = self._data[row]
        self.session.delete(pin_to_delete)
        try:
            self.session.commit()
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()
            return True
        except Exception as e:
            self.session.rollback()
            QMessageBox.critical(None, "Database Error", f"Could not delete Pin: {e}")
            return False
