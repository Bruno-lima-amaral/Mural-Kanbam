
"""
Para rodar:
    py test_kanban.py
"""
import unittest
from servidor.app import app, board
from servidor.composite import Board


class TestKanbanQualityPlan(unittest.TestCase):

    def setUp(self):
        global board
        self.app = app
        self.client = self.app.test_client()
        import servidor.app as app_module
        app_module.board = Board()

    def test_t3_1_mover_cartao_entre_colunas(self):
        resp = self.client.post('/api/cards', json={
            "title": "Implementar Login",
            "description": "Criar tela e validação",
            "card_type": "tarefa",
            "priority": "alta"
        })
        self.assertEqual(resp.status_code, 201)
        card_id = resp.get_json()['id']

        resp_move1 = self.client.put(f'/api/cards/{card_id}/move', json={
            "target_state": "in_progress"
        })
        self.assertEqual(resp_move1.status_code, 200)
        self.assertEqual(resp_move1.get_json()['state'], 'in_progress')

        resp_move2 = self.client.put(f'/api/cards/{card_id}/move', json={
            "target_state": "done"
        })
        self.assertEqual(resp_move2.status_code, 200)
        self.assertEqual(resp_move2.get_json()['state'], 'done')

        resp_board = self.client.get('/api/board')
        board_data = resp_board.get_json()
        done_column = next(c for c in board_data['columns'] if c['state_name'] == 'done')
        self.assertTrue(any(c['id'] == card_id for c in done_column['cards']))

    def test_t3_2_validar_cartao_incompleto(self):
        resp1 = self.client.post('/api/cards', json={
            "title": "",
            "description": "Descrição válida",
            "card_type": "bug",
            "priority": "alta"
        })
        self.assertEqual(resp1.status_code, 400)
        self.assertIn("título é obrigatório", resp1.get_json()['error'])

        resp2 = self.client.post('/api/cards', json={
            "title": "Título válido",
            "description": "",
            "card_type": "bug",
            "priority": "alta"
        })
        self.assertEqual(resp2.status_code, 400)
        self.assertIn("descrição é obrigatória", resp2.get_json()['error'])

        resp3 = self.client.post('/api/cards', json={
            "title": "Título válido",
            "description": "Descrição",
            "card_type": "tipo_inexistente",
            "priority": "alta"
        })
        self.assertEqual(resp3.status_code, 400)

        resp4 = self.client.post('/api/cards', json={
            "title": "Título válido",
            "description": "Descrição",
            "card_type": "tarefa",
            "priority": "urgente_demais"
        })
        self.assertEqual(resp4.status_code, 400)

    def test_t3_3_sincronizacao_e_conflito_de_edicao(self):
        resp = self.client.post('/api/cards', json={
            "title": "Refatorar Módulo",
            "description": "Código legado",
            "card_type": "melhoria",
            "priority": "media"
        })
        card_data = resp.get_json()
        card_id = card_data['id']
        self.assertEqual(card_data['version'], 1)
        resp_update1 = self.client.put(f'/api/cards/{card_id}', json={
            "title": "Refatorar Módulo - V2",
            "version": 1
        })
        self.assertEqual(resp_update1.status_code, 200)
        self.assertEqual(resp_update1.get_json()['version'], 2)
        resp_update_conflict = self.client.put(f'/api/cards/{card_id}', json={
            "title": "Tentativa Conflitante",
            "version": 1
        })
        self.assertEqual(resp_update_conflict.status_code, 409)
        self.assertIn("Conflito", resp_update_conflict.get_json()['error'])

    def test_t3_4_state_e_composite(self):
        resp = self.client.post('/api/cards', json={
            "title": "Correção de Bug",
            "description": "Erro 500 no login",
            "card_type": "bug",
            "priority": "alta"
        })
        card_id = resp.get_json()['id']
        resp_invalid_move = self.client.put(f'/api/cards/{card_id}/move', json={
            "target_state": "done"
        })
        self.assertEqual(resp_invalid_move.status_code, 400)
        self.assertIn("Transição", resp_invalid_move.get_json()['error'])
        self.client.put(f'/api/cards/{card_id}/move', json={"target_state": "in_progress"})
        self.client.put(f'/api/cards/{card_id}/move', json={"target_state": "done"})
        resp_edit_done = self.client.put(f'/api/cards/{card_id}', json={
            "title": "Tentando editar cartão concluído",
            "version": 1
        })
        self.assertEqual(resp_edit_done.status_code, 403)
        self.assertIn("não pode ser editado", resp_edit_done.get_json()['error'])
        resp_board = self.client.get('/api/board')
        board_info = resp_board.get_json()
        self.assertEqual(board_info['total_cards'], 1)
        done_col = next(c for c in board_info['columns'] if c['state_name'] == 'done')
        self.assertEqual(done_col['count'], 1)


if __name__ == '__main__':
    unittest.main()
