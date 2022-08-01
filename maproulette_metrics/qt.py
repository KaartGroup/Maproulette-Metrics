import shlex
import sys
from datetime import date
from pathlib import Path
from typing import Literal

import keyring
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

from . import get_metrics, mainwindow, set_api_key_gui
from .utils import dirname


class Worker(QObject):
    done = Signal()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.host = parent

    def run(self) -> None:
        get_metrics.get_metrics()


class ApiKeyDialog(QDialog, set_api_key_gui.Ui_Dialog):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.apiKeyLineEdit.editingFinished.connect(self.run_checker)

    def run_checker(self) -> None:
        if self.apiKeyLineEdit.text().strip():
            self.buttonBox.setEnabled(False)
        else:
            self.buttonBox.setEnabled(True)

    def set_apikey(self) -> None:
        pass


class MainApp(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.apikey = keyring.get_password("maproulette", "")
        # if not self.apikey:
        # Prompt user to set apikey

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

    @property
    def opts(self) -> dict:
        return {
            "users": self.users,
            "start": self.start_date,
            "end": self.end_date,
            "metric_type": self.metric_type,
            "output": self.output_location,
            "apikey": self.apikey,
            "overwrite": True,
        }

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
        self.userListWidget.add_users_to_list(user_split(self.userAddLineEdit.text()))
        self.userAddLineEdit.clear()

    def remove_user(self) -> None:
        self.userListWidget.delete_user()

    def run_checker(self) -> None:
        all_fields_filled = bool(any(self.users) and self.outputLineEdit.strip())
        self.runButton.setEnabled(all_fields_filled)

    def run(self) -> None:
        self.work_thread = QThread(parent=self)
        self.worker = Worker()

        self.worker.moveToThread(self.work_thread)
        self.work_thread.started.connect(self.worker.run)
        self.work_thread.start()


def user_split(raw_label: str) -> list[str]:
    """
    Splits comma- and/or space-separated values and returns sorted list
    """
    splitter = shlex.shlex(raw_label)
    # Count commas as a delimiter and don't include in the users
    splitter.whitespace += ","
    splitter.whitespace_split = True
    return sorted(splitter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainApp()
    form.show()
    app.exec()
