"""
INiciar com: py run_server.py
"""
from servidor.app import app

if __name__ == '__main__':
    print("=" * 50)
    print("  SERVIDOR KANBAN - Flask")
    print("  Rodando em http://localhost:5000")
    print("  Pressione Ctrl+C para parar")
    print("=" * 50)
    app.run(debug=True, port=5000)
