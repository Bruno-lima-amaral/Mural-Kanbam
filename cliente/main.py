
import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QListWidgetItem,
    QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
from PyQt5 import uic

from cliente.api_client import ApiClient, ApiError

UI_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_WINDOW_UI = os.path.join(UI_DIR, "kanban_window.ui")
CARD_DIALOG_UI = os.path.join(UI_DIR, "card_dialog.ui")


class CardDialog(QDialog):
    def __init__(self, parent=None, card_data=None):
        super().__init__(parent)
        uic.loadUi(CARD_DIALOG_UI, self)

        self.card_data = card_data

        if card_data:
            self.setWindowTitle("Editar Cartao")
            self.inputTitle.setText(card_data.get("title", ""))
            self.inputDescription.setPlainText(card_data.get("description", ""))
            type_map = {"tarefa": "Tarefa", "bug": "Bug", "melhoria": "Melhoria"}
            type_text = type_map.get(card_data.get("card_type", "tarefa"), "Tarefa")
            type_index = self.comboType.findText(type_text)
            if type_index >= 0:
                self.comboType.setCurrentIndex(type_index)
            self.comboType.setEnabled(False)
            priority_map = {"baixa": "Baixa", "media": "Media", "alta": "Alta"}
            priority_text = priority_map.get(
                card_data.get("priority", "media"), "Media"
            )
            priority_index = self.comboPriority.findText(priority_text)
            if priority_index >= 0:
                self.comboPriority.setCurrentIndex(priority_index)
        else:
            self.setWindowTitle("Novo Cartao")
        self.buttonBox.accepted.connect(self.validate_and_accept)
        self.buttonBox.rejected.connect(self.reject)

    def validate_and_accept(self):
        title = self.inputTitle.text().strip()
        description = self.inputDescription.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "Validacao", "O titulo e obrigatorio.")
            self.inputTitle.setFocus()
            return
        if not description:
            QMessageBox.warning(self, "Validacao", "A descricao e obrigatoria.")
            self.inputDescription.setFocus()
            return

        self.accept()

    def get_data(self) -> dict:
        type_map = {"Tarefa": "tarefa", "Bug": "bug", "Melhoria": "melhoria"}
        priority_map = {"Baixa": "baixa", "Media": "media", "Alta": "alta"}

        return {
            "title": self.inputTitle.text().strip(),
            "description": self.inputDescription.toPlainText().strip(),
            "card_type": type_map.get(self.comboType.currentText(), "tarefa"),
            "priority": priority_map.get(
                self.comboPriority.currentText(), "media"
            ),
        }


class KanbanWindow(QMainWindow):
    STATE_COLUMNS = ["todo", "in_progress", "done"]
    TYPE_ICONS = {
        "tarefa": "[T]",
        "bug": "[B]",
        "melhoria": "[M]",
    }
    PRIORITY_LABELS = {
        "baixa": "Baixa",
        "media": "Media",
        "alta": "ALTA",
    }

    def __init__(self):
        super().__init__()
        uic.loadUi(MAIN_WINDOW_UI, self)

        self.api = ApiClient()
        self.list_widgets = {
            "todo": self.listTodo,
            "in_progress": self.listInProgress,
            "done": self.listDone,
        }
        self.actionNewCard.triggered.connect(self.on_new_card)
        self.actionEditCard.triggered.connect(self.on_edit_card)
        self.actionDeleteCard.triggered.connect(self.on_delete_card)
        self.actionMoveRight.triggered.connect(self.on_move_right)
        self.actionMoveLeft.triggered.connect(self.on_move_left)
        self.actionRefresh.triggered.connect(self.refresh_board)
        for list_widget in self.list_widgets.values():
            list_widget.itemDoubleClicked.connect(self.on_edit_card)
            list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_board)
        self.refresh_timer.start(5000)
        self.statusBar().showMessage("Conectando ao servidor...")
        self.refresh_board()

    def get_selected_card_info(self):
        for state, list_widget in self.list_widgets.items():
            selected = list_widget.selectedItems()
            if selected:
                item = selected[0]
                card_id = item.data(Qt.UserRole)
                return card_id, state
        return None, None

    def on_selection_changed(self):
        sender = self.sender()
        for list_widget in self.list_widgets.values():
            if list_widget != sender and list_widget.selectedItems():
                list_widget.clearSelection()
    def on_new_card(self):
        dialog = CardDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.api.create_card(
                    title=data["title"],
                    description=data["description"],
                    card_type=data["card_type"],
                    priority=data["priority"],
                )
                self.statusBar().showMessage(
                    "Cartao criado com sucesso!", 3000
                )
                self.refresh_board()
            except ApiError as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao criar cartao:\n{e}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Erro de Conexao",
                    f"Nao foi possivel conectar ao servidor:\n{e}"
                )

    def on_edit_card(self):
        card_id, state = self.get_selected_card_info()
        if card_id is None:
            QMessageBox.information(
                self, "Aviso", "Selecione um cartao para editar."
            )
            return

        try:
            card_data = self.api.get_card(card_id)
        except ApiError as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao obter cartao:\n{e}"
            )
            return
        except Exception as e:
            QMessageBox.critical(self, "Erro de Conexao", str(e))
            return

        if not card_data.get("can_edit", True):
            QMessageBox.warning(
                self, "Aviso",
                "Cartoes concluidos nao podem ser editados.\n"
                "Mova o cartao de volta para edita-lo."
            )
            return

        dialog = CardDialog(self, card_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.api.update_card(
                    card_id=card_id,
                    title=data["title"],
                    description=data["description"],
                    priority=data["priority"],
                    version=card_data.get("version"),
                )
                self.statusBar().showMessage(
                    "Cartao atualizado com sucesso!", 3000
                )
                self.refresh_board()
            except ApiError as e:
                if e.status_code == 409:
                    QMessageBox.warning(
                        self, "Conflito de Edicao",
                        f"O cartao foi modificado por outra sessao.\n"
                        f"Atualize o mural e tente novamente.\n\n{e}"
                    )
                else:
                    QMessageBox.critical(
                        self, "Erro", f"Erro ao atualizar cartao:\n{e}"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Erro de Conexao", str(e))

    def on_delete_card(self):
        card_id, state = self.get_selected_card_info()
        if card_id is None:
            QMessageBox.information(
                self, "Aviso", "Selecione um cartao para excluir."
            )
            return

        reply = QMessageBox.question(
            self, "Confirmar Exclusao",
            "Tem certeza que deseja excluir este cartao?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.api.delete_card(card_id)
                self.statusBar().showMessage(
                    "Cartao excluido com sucesso!", 3000
                )
                self.refresh_board()
            except ApiError as e:
                QMessageBox.critical(
                    self, "Erro", f"Erro ao excluir cartao:\n{e}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erro de Conexao", str(e))

    def on_move_right(self):
        card_id, state = self.get_selected_card_info()
        if card_id is None:
            QMessageBox.information(
                self, "Aviso", "Selecione um cartao para mover."
            )
            return

        current_index = self.STATE_COLUMNS.index(state)
        if current_index >= len(self.STATE_COLUMNS) - 1:
            QMessageBox.warning(
                self, "Aviso", "O cartao ja esta na ultima coluna."
            )
            return

        target_state = self.STATE_COLUMNS[current_index + 1]
        self._move_card(card_id, target_state)

    def on_move_left(self):
        card_id, state = self.get_selected_card_info()
        if card_id is None:
            QMessageBox.information(
                self, "Aviso", "Selecione um cartao para mover."
            )
            return

        current_index = self.STATE_COLUMNS.index(state)
        if current_index <= 0:
            QMessageBox.warning(
                self, "Aviso", "O cartao ja esta na primeira coluna."
            )
            return

        target_state = self.STATE_COLUMNS[current_index - 1]
        self._move_card(card_id, target_state)

    def _move_card(self, card_id, target_state):
        try:
            self.api.move_card(card_id, target_state)
            self.statusBar().showMessage("Cartao movido com sucesso!", 3000)
            self.refresh_board()
        except ApiError as e:
            QMessageBox.warning(self, "Movimento Invalido", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erro de Conexao", str(e))
    def refresh_board(self):
        try:
            board_data = self.api.get_board()
            self._update_lists(board_data)
            total = board_data.get("total_cards", 0)
            self.statusBar().showMessage(
                f"Conectado - {total} cartao(oes) no mural", 5000
            )
        except Exception:
            self.statusBar().showMessage(
                "Sem conexao com o servidor", 5000
            )

    def _update_lists(self, board_data):
        selected_id, _ = self.get_selected_card_info()

        for column_data in board_data.get("columns", []):
            state_name = column_data.get("state_name")
            list_widget = self.list_widgets.get(state_name)
            if list_widget is None:
                continue

            list_widget.clear()
            count = column_data.get("count", 0)
            group_box = list_widget.parent()
            if group_box:
                column_labels = {
                    "todo": f"A Fazer ({count})",
                    "in_progress": f"Em Progresso ({count})",
                    "done": f"Concluido ({count})",
                }
                group_box.setTitle(column_labels.get(state_name, ""))

            for card_data in column_data.get("cards", []):
                self._add_card_to_list(list_widget, card_data)

                # Restaura a seleção anterior
                if card_data.get("id") == selected_id:
                    list_widget.setCurrentRow(list_widget.count() - 1)

    def _add_card_to_list(self, list_widget, card_data):
        card_id = card_data.get("id", "")
        title = card_data.get("title", "")
        card_type = card_data.get("card_type", "tarefa")
        priority = card_data.get("priority", "media")

        type_icon = self.TYPE_ICONS.get(card_type, "[T]")
        priority_label = self.PRIORITY_LABELS.get(priority, "Media")

        display_text = f"{type_icon} {title}  ({priority_label})"

        item = QListWidgetItem(display_text)
        item.setData(Qt.UserRole, card_id)
        color = card_data.get("color", "#FFFFFF")
        bg_color = QColor(color).lighter(180)
        bg_color.setAlpha(60)
        item.setBackground(bg_color)
        tooltip = (
            f"ID: {card_id}\n"
            f"Tipo: {card_type.capitalize()}\n"
            f"Prioridade: {priority.capitalize()}\n"
            f"Descricao: {card_data.get('description', '')}\n"
            f"Versao: {card_data.get('version', 1)}"
        )
        item.setToolTip(tooltip)

        # Fonte
        font = QFont("Segoe UI", 10)
        item.setFont(font)

        list_widget.addItem(item)

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = KanbanWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
