
# pyrefly: ignore[missing-import]
from flask import Flask, request, jsonify
from servidor.composite import Board, ConflictError
from servidor.factory import get_card_factory, FACTORIES
from servidor.state import InvalidTransitionError


app = Flask(__name__)
board = Board()


@app.route('/api/board', methods=['GET'])
def get_board():
    return jsonify(board.get_info()), 200


@app.route('/api/columns', methods=['GET'])
def get_columns():
    return jsonify([col.get_info() for col in board.columns]), 200


@app.route('/api/columns/<state_name>/cards', methods=['GET'])
def get_column_cards(state_name):
    column = board.get_column(state_name)
    if column is None:
        return jsonify({"error": f"Coluna '{state_name}' não encontrada."}), 404
    return jsonify(column.get_info()), 200

@app.route('/api/cards', methods=['POST'])
def create_card():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição vazio."}), 400

    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    card_type = data.get('card_type', '').strip()
    priority = data.get('priority', 'media').strip()

    if not title:
        return jsonify({"error": "O título é obrigatório."}), 400
    if not description:
        return jsonify({"error": "A descrição é obrigatória."}), 400
    if not card_type:
        return jsonify({"error": "O tipo do cartão é obrigatório."}), 400
    if priority not in ("baixa", "media", "alta"):
        return jsonify({
            "error": f"Prioridade inválida: '{priority}'. Use: baixa, media, alta."
        }), 400

    try:
        factory = get_card_factory(card_type)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    card = factory.create_card(title, description, priority)
    column = board.get_column("todo")
    column.add(card)
    return jsonify(card.get_info()), 201


@app.route('/api/cards/<card_id>', methods=['GET'])
def get_card(card_id):
    card = board.find_by_id(card_id)
    if card is None:
        return jsonify({"error": f"Cartão '{card_id}' não encontrado."}), 404
    return jsonify(card.get_info()), 200


@app.route('/api/cards/<card_id>', methods=['PUT'])
def update_card(card_id):
    card = board.find_by_id(card_id)
    if card is None:
        return jsonify({"error": f"Cartão '{card_id}' não encontrado."}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição vazio."}), 400

    title = data.get('title')
    description = data.get('description')
    priority = data.get('priority')
    expected_version = data.get('version')
    if title is not None and not title.strip():
        return jsonify({"error": "O título não pode ser vazio."}), 400
    if description is not None and not description.strip():
        return jsonify({"error": "A descrição não pode ser vazia."}), 400
    if priority is not None and priority not in ("baixa", "media", "alta"):
        return jsonify({"error": f"Prioridade inválida: '{priority}'."}), 400

    try:
        card.update(
            title=title.strip() if title else None,
            description=description.strip() if description else None,
            priority=priority,
            expected_version=expected_version
        )
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ConflictError as e:
        return jsonify({"error": str(e)}), 409

    return jsonify(card.get_info()), 200


@app.route('/api/cards/<card_id>', methods=['DELETE'])
def delete_card(card_id):
    column = board.find_card_column(card_id)
    if column is None:
        return jsonify({"error": f"Cartão '{card_id}' não encontrado."}), 404

    card = column.find_by_id(card_id)
    if not card.state.can_delete():
        return jsonify({
            "error": "Cartão não pode ser excluído neste estado."
        }), 403

    column.remove(card_id)
    return jsonify({
        "message": f"Cartão '{card_id}' excluído com sucesso."
    }), 200


@app.route('/api/cards/<card_id>/move', methods=['PUT'])
def move_card(card_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Corpo da requisição vazio."}), 400

    target_state = data.get('target_state', '').strip()
    if not target_state:
        return jsonify({
            "error": "O estado alvo (target_state) é obrigatório."
        }), 400
    source_column = board.find_card_column(card_id)
    if source_column is None:
        return jsonify({"error": f"Cartão '{card_id}' não encontrado."}), 404

    card = source_column.find_by_id(card_id)
    if card.state.get_name() == target_state:
        return jsonify({"error": "O cartão já está nesta coluna."}), 400
    try:
        card.move_to(target_state)
    except InvalidTransitionError as e:
        return jsonify({"error": str(e)}), 400
    source_column.remove(card_id)
    target_column = board.get_column(target_state)
    target_column.add(card)

    return jsonify(card.get_info()), 200
@app.route('/api/card-types', methods=['GET'])
def get_card_types():
    types_list = []
    for type_name, factory in FACTORIES.items():
        sample = factory.create_card("sample", "sample")
        types_list.append({
            "name": type_name,
            "color": sample.color,
        })
    return jsonify(types_list), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
