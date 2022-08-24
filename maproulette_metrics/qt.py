import shlex
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Literal

import requests.exceptions
from PySide6.QtCore import QObject, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFileDialog,
    QMainWindow,
    QProgressDialog,
    QRadioButton,
)

from . import get_metrics, mainwindow, set_api_key_gui
from .utils import dirname, get_api_key, set_api_key

try:
    import ptvsd

    ptvsd.enable_attach()
except ImportError:
    # logger.debug("PTVSD not imported")
    print("PTVSD not imported")
else:
    # logger.debug("VSCode debug library successful.")
    print("VSCode debug library successful.")


class Worker(QObject):
    done = Signal()

    def __init__(self, parent=None, host=None) -> None:
        super().__init__()
        self.host = host
        self.getter = get_metrics.MetricGetter()

    def run(self) -> None:
        # For debugging in VSCode only
        try:
            ptvsd.debug_this_thread()
        except (ModuleNotFoundError, NameError):
            print("Worker thread not exposed to VSCode")
        else:
            # logger.debug("Worker thread successfully exposed to debugger.")
            print("Worker thread successfully exposed to debugger.")
        try:
            df = self.getter.get_metrics(**self.host.opts)
        except requests.exceptions.Timeout:
            # Error dialog should go here
            pass
        else:
            get_metrics.write_excel(df, self.host.opts["output"])

        self.done.emit()


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


class MetricProgressDialog(QProgressDialog):
    def __init__(self, host):
        self.host = host
        super().__init__("", None, 0, self.host.worker.getter.max_iterations)

        self.setAutoClose(True)
        self.setAutoReset(False)
        self.setModal(True)
        self.setLabelText("Beginning analysis")
        self.setWindowFlags(Qt.Sheet | Qt.WindowModal)

    def start(self) -> None:
        for _ in range(20):
            if self.host.worker.getter.max_iterations > 0:
                self.setMaximum(self.host.worker.getter.max_iterations)
                break
            time.sleep(0.5)
        else:
            raise RuntimeError
        while (self.maximum() - self.value()) > 0:
            QApplication.processEvents()
            self.setValue(self.host.worker.getter.cur_iteration)
            self.setLabelText(
                f"Making request {self.host.worker.getter.page + 1} of "
                f"{self.host.worker.getter.page_count} for date {self.host.worker.getter.cur_date.strftime('%b %w')} "
                f"({self.value() + 1} of {self.maximum() + 1} total)"
            )
            time.sleep(0.5)
        self.setLabelText("Requests complete, putting it all together...")


class MainApp(QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.startDateEdit.setDate(date.today() - timedelta(weeks=4))
        self.endDateEdit.setDate(date.today())

        self.apikey = get_api_key()
        self.apikey_dialog = ApiKeyDialog()

        self.userAddPushButton.clicked.connect(self.add_user)
        self.userRemovePushButton.clicked.connect(self.remove_user)
        self.outputLocationSaveButton.clicked.connect(self.output_file)

        self.runButton.clicked.connect(self.run)

        self.run_checker()

    @property
    def users(self) -> list[str]:
        return self.userListWidget.users

    @property
    def start_date(self) -> date:
        return self.startDateEdit.date().toPython()

    @property
    def end_date(self) -> date:
        return self.endDateEdit.date().toPython()

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
            return Path(output_text).resolve()

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
            self.run_checker()

    def add_user(self) -> None:
        self.userListWidget.add_users_to_list(user_split(self.userAddLineEdit.text()))
        self.userAddLineEdit.clear()
        self.run_checker()

    def remove_user(self) -> None:
        self.userListWidget.delete_user()

    def run_checker(self) -> None:
        all_fields_filled = bool(any(self.users) and self.outputLineEdit.text().strip())
        self.runButton.setEnabled(all_fields_filled)

    def run(self) -> None:
        self.work_thread = QThread()
        self.worker = Worker(host=self)

        self.worker.moveToThread(self.work_thread)
        self.work_thread.started.connect(self.worker.run)
        self.work_thread.start()

        self.progbar = MetricProgressDialog(self)
        self.worker.done.connect(self.finished)

        self.progbar.show()
        self.progbar.start()

    def finished(self) -> None:
        self.progbar.reset()
        self.progbar.close()

        self.work_thread.quit()
        self.work_thread.wait()

        self.worker.deleteLater()


def user_split(raw_label: str) -> list[str]:
    """
    Splits comma- and/or space-separated values and returns sorted list
    """
    splitter = shlex.shlex(raw_label)
    # Count commas as a delimiter and don't include in the users
    splitter.whitespace += ","
    splitter.whitespace_split = True
    return sorted(splitter)


def main():
    app = QApplication(sys.argv)
    form = MainApp()
    form.show()
    app.exec()


if __name__ == "__main__":
    main()
