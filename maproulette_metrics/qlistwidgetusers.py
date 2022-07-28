import logging
from typing import Iterable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidget

logger = logging.getLogger(__name__)


class QListWidgetUsers(QListWidget):
    """
    QListWidget that enforces unique values and has methods for removing
    or clearing entries
    """

    def __init__(self, parent=None):
        super().__init__()

    def add_users_to_list(self, user: str | Iterable[str]) -> None:
        if isinstance(user, str):
            user = [user]

        for count, user in enumerate(user):
            if existing_item := next(
                iter(self.findItems(user, Qt.MatchExactly)),
                None,
            ):
                # Clear the prior selection on the first iteration only
                if count == 0:
                    self.selectionModel().clear()
                existing_item.setSelected(True)
                logger.warning("%s is already in the list.", user)
            else:
                self.addItem(user)
                logger.info("Adding to list: %s", user)

    def delete_user(self) -> None:
        """
        Clears selected list items with "Delete" button.
        Execute on `Delete` button signal.
        """
        try:
            # Remove selected items in user-selected Qlist
            for item in self.selectedItems():
                self.takeItem(self.row(item))
                logger.info("Deleted %s from processing list.", (item.text()))
        # Fails silently if nothing is selected
        except AttributeError:
            logger.exception()

    def clear_user(self) -> None:
        """
        Wipes all users listed on QList with "Clear" button.
        Execute on `Clear` button signal.
        """
        for row in (self.row(item) for item in self.findItems("*", Qt.MatchWildcard)):
            self.takeItem(row)
        logger.info("Cleared user list.")

    @property
    def users(self) -> set:
        return {item.text() for item in self.findItems("*", Qt.MatchWildcard)}
