import shlex
import sys
from datetime import date
from pathlib import Path
from typing import Literal

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
    QRadioButton,
)

from maproulette_metrics import mainwindow


class Worker(QObject):
    done = Signal()

    def __init__(self, parent: QObject | None) -> None:
        super().__init__(parent)


class MainApp(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.userAddPushButton.clicked.connect(self.add_user)
        self.userRemovePushButton.clicked.connect(self.remove_user)
        self.outputLocationSaveButton.clicked.connect(self.output_file)

        self.runButton.clicked.connect(self.run)

    @property
    def users(self) -> list[str]:
        return self.userListWidget.users

    @property
    def start_date(self) -> date:
        return self.startDateEdit.date().toPython()

    @property
    def end_date(self) -> date:
        return self.startDateEdit.date().toPython()

    @property
    def metric_type(self) -> Literal["editor", "qc"]:
        checked_item = next(
            radio_button
            for radio_button in self.metricTypeGroup.findChildren(QRadioButton)
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
            dirname(self.outputLineEdit.text().strip() or Path.home() / "Documents"),
        )
        if output_file_name := QFileDialog.getSaveFileName(
            self, "Enter output file location", output_file_dir, filter=".xlsx"
        )[0]:
            # Since this is a prefix, the user shouldn't be adding their own extension
            output_file_name = Path(output_file_name)
            output_file_name = output_file_name.with_suffix(".xlsx")
            self.outputLineEdit.selectAll()
            self.outputLineEdit.insert(str(output_file_name))

    def add_user(self) -> None:
        self.userListWidget.add

    def remove_user(self) -> None:
        pass

    def run_checker(self) -> None:
        pass

    def run(self) -> None:
        self.work_thread = QThread(parent=self)
        self.worker = Worker()


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
