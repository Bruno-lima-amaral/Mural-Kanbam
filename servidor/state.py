from abc import ABC, abstractmethod


class CardState(ABC):

    @abstractmethod
    def get_name(self) -> str:
        pass
    @abstractmethod
    def allowed_transitions(self) -> list:
        pass
    @abstractmethod
    def can_edit(self) -> bool:
        pass

    @abstractmethod
    def can_delete(self) -> bool:
        pass

    def transition_to(self, target_state_name: str) -> 'CardState':
        if target_state_name not in self.allowed_transitions():
            raise InvalidTransitionError(
                f"Transição de '{self.get_name()}' para '{target_state_name}' não é permitida. "
                f"Transições permitidas: {self.allowed_transitions()}"
            )
        return state_from_name(target_state_name)


class TodoState(CardState):
    def get_name(self) -> str:
        return "todo"

    def allowed_transitions(self) -> list:
        return ["in_progress"]

    def can_edit(self) -> bool:
        return True

    def can_delete(self) -> bool:
        return True


class InProgressState(CardState):
    def get_name(self) -> str:
        return "in_progress"

    def allowed_transitions(self) -> list:
        return ["todo", "done"]

    def can_edit(self) -> bool:
        return True

    def can_delete(self) -> bool:
        return True


class DoneState(CardState):
    def get_name(self) -> str:
        return "done"

    def allowed_transitions(self) -> list:
        return ["in_progress"]

    def can_edit(self) -> bool:
        return False

    def can_delete(self) -> bool:
        return True


class InvalidTransitionError(Exception):
    pass

STATE_MAP = {
    "todo": TodoState,
    "in_progress": InProgressState,
    "done": DoneState,
}
STATE_COLUMN_MAP = {
    "todo": "A Fazer",
    "in_progress": "Em Progresso",
    "done": "Concluído",
}
COLUMN_STATE_MAP = {v: k for k, v in STATE_COLUMN_MAP.items()}


def state_from_name(name: str) -> CardState:
    state_class = STATE_MAP.get(name)
    if state_class is None:
        raise ValueError(
            f"Estado desconhecido: '{name}'. "
            f"Estados válidos: {list(STATE_MAP.keys())}"
        )
    return state_class()
