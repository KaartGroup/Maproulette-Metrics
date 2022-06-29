from datetime import date
from operator import itemgetter
from pathlib import Path
import sys

from PySide6.QtCore import QEvent, QObject, Qt, QThread, Signal
from PySide6.QtGui import QAction, QIcon, QKeyEvent, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCompleter,
    QDialog,
    QFileDialog,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressDialog,
    QPushButton,
)

import shlex

from maproulette_metrics import mainwindow


class MainApp(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

    @property
    def users(self) -> tuple[str]:
        return tuple(
            user.text() for user in self.userListWidget.findItems("*", Qt.MatchWildcard)
        )

    @property
    def start_date(self) -> date:
        return self.startDateEdit.date()

    @property
    def end_date(self) -> date:
        return self.startDateEdit.date()

    @property
    def metric_type(self) -> str:
        checked_item = next(
            radio_button
            for radio_button in self.metricTypeGroup.findChildren()
            if radio_button.isChecked()
        )
        item_table = {self.editingRadioButton: "editor", self.qcRadioButton: "qc"}
        return item_table[checked_item]

    @property
    def output_location(self) -> Path | None:
        if output_text := self.outputLineEdit.text():
            return Path(output_text.text()).resolve()

    def output_file(self) -> None:
        """
        Adds functionality to the Output File (…) button, opens the
        '/documents' system path for user to name an output file.
        """
        # If no previous location, default to Documents folder
        output_file_dir = str(
            dirname(self.outputFileNameBox.text().strip() or Path.home() / "Documents"),
        )
        if output_file_name := QFileDialog.getSaveFileName(
            self, "Enter output file location", output_file_dir
        )[0]:
            # Since this is a prefix, the user shouldn't be adding their own extension
            output_file_name = Path(output_file_name)
            output_file_name = output_file_name.with_suffix(".xlsx")
            self.outputFileNameBox.selectAll()
            self.outputFileNameBox.insert(str(output_file_name))


def dirname(the_path: str | Path) -> Path:
    """
    Return the URI of the nearest directory,
    which can be self if it is a directory
    or else the parent
    """
    the_path = Path(the_path)
    return the_path if the_path.is_dir() else the_path.parent


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainApp()
    form.show()
    app.exec()
