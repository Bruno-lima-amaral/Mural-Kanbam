
from abc import ABC, abstractmethod
import uuid
from servidor.composite import Card
from servidor.state import TodoState


class CardFactory(ABC):
    @abstractmethod
    def create_card(self, title: str, description: str,
                    priority: str = "media") -> Card:
        pass

    def _generate_id(self) -> str:
        return str(uuid.uuid4())[:8]
class TaskCardFactory(CardFactory):

    def create_card(self, title: str, description: str,
                    priority: str = "media") -> Card:
        return Card(
            card_id=self._generate_id(),
            title=title,
            description=description,
            card_type="tarefa",
            color="#4A90D9",   # Azul
            priority=priority,
            state=TodoState()
        )


class BugCardFactory(CardFactory):
    def create_card(self, title: str, description: str,
                    priority: str = "media") -> Card:
        return Card(
            card_id=self._generate_id(),
            title=title,
            description=description,
            card_type="bug",
            color="#E74C3C",   # Vermelho
            priority=priority,
            state=TodoState()
        )


class ImprovementCardFactory(CardFactory):
    def create_card(self, title: str, description: str,
                    priority: str = "media") -> Card:
        return Card(
            card_id=self._generate_id(),
            title=title,
            description=description,
            card_type="melhoria",
            color="#2ECC71",   
            priority=priority,
            state=TodoState()
        )
FACTORIES = {
    "tarefa": TaskCardFactory(),
    "bug": BugCardFactory(),
    "melhoria": ImprovementCardFactory(),
}


def get_card_factory(card_type: str) -> CardFactory:
    factory = FACTORIES.get(card_type)
    if factory is None:
        raise ValueError(
            f"Tipo de cartão desconhecido: '{card_type}'. "
            f"Tipos válidos: {list(FACTORIES.keys())}"
        )
    return factory
