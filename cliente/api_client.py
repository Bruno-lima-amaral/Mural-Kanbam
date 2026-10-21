
import requests


class ApiClient:

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def get_board(self) -> dict:
        response = requests.get(self._url("/api/board"))
        response.raise_for_status()
        return response.json()

    def get_columns(self) -> list:
        response = requests.get(self._url("/api/columns"))
        response.raise_for_status()
        return response.json()

    def get_column_cards(self, state_name: str) -> dict:
        response = requests.get(self._url(f"/api/columns/{state_name}/cards"))
        response.raise_for_status()
        return response.json()
    def create_card(self, title: str, description: str,
                    card_type: str, priority: str = "media") -> dict:
        data = {
            "title": title,
            "description": description,
            "card_type": card_type,
            "priority": priority,
        }
        response = requests.post(self._url("/api/cards"), json=data)
        if response.status_code == 201:
            return response.json()
        error = response.json().get("error", "Erro desconhecido")
        raise ApiError(error, response.status_code)

    def get_card(self, card_id: str) -> dict:
        response = requests.get(self._url(f"/api/cards/{card_id}"))
        if response.status_code == 200:
            return response.json()
        error = response.json().get("error", "Erro desconhecido")
        raise ApiError(error, response.status_code)

    def update_card(self, card_id: str, title: str = None,
                    description: str = None, priority: str = None,
                    version: int = None) -> dict:
        data = {}
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if priority is not None:
            data["priority"] = priority
        if version is not None:
            data["version"] = version

        response = requests.put(self._url(f"/api/cards/{card_id}"), json=data)
        if response.status_code == 200:
            return response.json()
        error = response.json().get("error", "Erro desconhecido")
        raise ApiError(error, response.status_code)

    def delete_card(self, card_id: str) -> dict:
        response = requests.delete(self._url(f"/api/cards/{card_id}"))
        if response.status_code == 200:
            return response.json()
        error = response.json().get("error", "Erro desconhecido")
        raise ApiError(error, response.status_code)

    def move_card(self, card_id: str, target_state: str) -> dict:
        data = {"target_state": target_state}
        response = requests.put(
            self._url(f"/api/cards/{card_id}/move"), json=data
        )
        if response.status_code == 200:
            return response.json()
        error = response.json().get("error", "Erro desconhecido")
        raise ApiError(error, response.status_code)
    def get_card_types(self) -> list:
        response = requests.get(self._url("/api/card-types"))
        response.raise_for_status()
        return response.json()

    def check_connection(self) -> bool:
        try:
            response = requests.get(self._url("/api/board"), timeout=3)
            return response.status_code == 200
        except requests.ConnectionError:
            return False


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
