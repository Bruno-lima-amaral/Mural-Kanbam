
from abc import ABC, abstractmethod
from datetime import datetime
from servidor.state import CardState, TodoState, state_from_name


class KanbanComponent(ABC):


    @abstractmethod
    def get_info(self) -> dict:
        pass
    @abstractmethod
    def count(self) -> int:
        pass
    @abstractmethod
    def find_by_id(self, component_id: str):
        pass


class Card(KanbanComponent):
    def __init__(self, card_id: str, title: str, description: str,
                 card_type: str, color: str, priority: str = "media",
                 state: CardState = None):
        self.card_id = card_id
        self.title = title
        self.description = description
        self.card_type = card_type     
        self.color = color            
        self.priority = priority      
        self.state = state or TodoState()
        self.version = 1              
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def get_info(self) -> dict:
        return {
            "id": self.card_id,
            "title": self.title,
            "description": self.description,
            "card_type": self.card_type,
            "color": self.color,
            "priority": self.priority,
            "state": self.state.get_name(),
            "can_edit": self.state.can_edit(),
            "can_delete": self.state.can_delete(),
            "allowed_transitions": self.state.allowed_transitions(),
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def count(self) -> int:
        return 1

    def find_by_id(self, component_id: str):
        if self.card_id == component_id:
            return self
        return None

    def update(self, title: str = None, description: str = None,
               priority: str = None, expected_version: int = None):
        if not self.state.can_edit():
            raise PermissionError(
                f"Cartão no estado '{self.state.get_name()}' não pode ser editado."
            )
        if expected_version is not None and expected_version != self.version:
            raise ConflictError(
                f"Conflito de versão: esperado {expected_version}, "
                f"atual {self.version}. O cartão foi modificado por outra sessão."
            )
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if priority is not None:
            self.priority = priority
        self.version += 1
        self.updated_at = datetime.now().isoformat()

    def move_to(self, target_state_name: str):
        self.state = self.state.transition_to(target_state_name)
        self.version += 1
        self.updated_at = datetime.now().isoformat()


class Column(KanbanComponent):
    def __init__(self, name: str, state_name: str):
        self.name = name               
        self.state_name = state_name   
        self.children: list[KanbanComponent] = []

    def add(self, component: KanbanComponent):
        self.children.append(component)

    def remove(self, component_id: str) -> KanbanComponent:
        for i, child in enumerate(self.children):
            if hasattr(child, 'card_id') and child.card_id == component_id:
                return self.children.pop(i)
        return None

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "state_name": self.state_name,
            "cards": [child.get_info() for child in self.children],
            "count": self.count(),
        }

    def count(self) -> int:
        return sum(child.count() for child in self.children)

    def find_by_id(self, component_id: str):
        for child in self.children:
            result = child.find_by_id(component_id)
            if result is not None:
                return result
        return None


class Board(KanbanComponent):
    def __init__(self, name: str = "Mural Kanban"):
        self.name = name
        self.columns: list[Column] = [
            Column("A Fazer", "todo"),
            Column("Em Progresso", "in_progress"),
            Column("Concluído", "done"),
        ]

    def get_column(self, state_name: str) -> Column:
        for col in self.columns:
            if col.state_name == state_name:
                return col
        return None

    def find_card_column(self, card_id: str) -> Column:
        for col in self.columns:
            if col.find_by_id(card_id):
                return col
        return None

    def get_info(self) -> dict:
        return {
            "name": self.name,
            "columns": [col.get_info() for col in self.columns],
            "total_cards": self.count(),
        }

    def count(self) -> int:
        return sum(col.count() for col in self.columns)

    def find_by_id(self, component_id: str):
        for col in self.columns:
            result = col.find_by_id(component_id)
            if result is not None:
                return result
        return None


class ConflictError(Exception):
    pass
