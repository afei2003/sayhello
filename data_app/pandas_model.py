from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
)
import pandas as pd

class PandasModel(QAbstractTableModel):
    """A model to interface a pandas DataFrame with a QTableView."""

    def __init__(self, dataframe: pd.DataFrame, parent=None):
        super().__init__(parent)
        self._df = dataframe

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows in the model."""
        return len(self._df)

    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns in the model."""
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        """Return data from the DataFrame."""
        if not index.isValid():
            return None
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return header data."""
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            if orientation == Qt.Vertical:
                return str(self._df.index[section])
        return None

    def setData(self, index, value, role=Qt.EditRole):
        """Set data in the DataFrame."""
        if role == Qt.EditRole:
            self._df.iloc[index.row(), index.column()] = value
            self.dataChanged.emit(index, index, [Qt.EditRole])
            return True
        return False

    def flags(self, index):
        """Return the flags for the item."""
        return super().flags(index) | Qt.ItemIsEditable

    def get_dataframe(self):
        """Return the underlying DataFrame."""
        return self._df

    def addRow(self):
        """Add a new, empty row to the model."""
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        new_row = {col: "" for col in self._df.columns}
        new_row_df = pd.DataFrame([new_row])
        self._df = pd.concat([self._df, new_row_df], ignore_index=True)
        self.endInsertRows()
        return True

    def deleteRow(self, row):
        """Delete a row from the model."""
        if 0 <= row < self.rowCount():
            self.beginRemoveRows(QModelIndex(), row, row)
            self._df = self._df.drop(self._df.index[row]).reset_index(drop=True)
            self.endRemoveRows()
            return True
        return False
