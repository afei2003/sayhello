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
