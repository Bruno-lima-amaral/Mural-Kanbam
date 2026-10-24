# 📋 Mural Kanban — Cliente Desktop Qt & Servidor Flask

Projeto desenvolvido para a disciplina de **Paradigmas de Programação** (CC5AN) — Prof. Alex Carneiro.

O sistema implementa um **Mural Kanban** distribuído em arquitetura **Cliente-Servidor**, utilizando uma interface gráfica desktop em **PyQt5** integrada a uma API REST em **Flask**, com conformidade rigorosa aos padrões de projeto (*GoF Design Patterns*) e regras de domínio sem persistência em banco de dados externo.

> 📄 **Documentação Oficial da AP2 (Microsoft Word):**
> A documentação técnica e formal completa do projeto exigida na AP2 está disponível no arquivo **[DOCUMENTACAO.docx](DOCUMENTACAO.docx)**. O documento contém capa institucional, diagramas de arquitetura e classes UML em alta resolução embutidos, especificação completa de requisitos funcionais e não-funcionais, regras de negócio, critérios de aceitação e matriz de rastreabilidade dos testes de qualidade.

---

## 🎯 Padrões de Projeto Implementados

Conforme os critérios de qualidade da disciplina, o sistema demonstra os três grupos de padrões com comportamento observável:

| Grupo | Padrão | Onde se aplica | Descrição |
|---|---|---|---|
| **Criacional** | **Factory Method** | `servidor/factory.py` | Instanciação polimórfica de cartões (`Tarefa`, `Bug`, `Melhoria`) com cores, prefixos e propriedades personalizadas para cada tipo. |
| **Estrutural** | **Composite** | `servidor/composite.py` | Tratamento uniforme de elementos (`Board`, `Column`, `Card`) através da interface abstrata `KanbanComponent`, viabilizando cálculos recursivos de contagem e busca hierárquica. |
| **Comportamental** | **State** | `servidor/state.py` | Encapsula o ciclo de vida do cartão (`A Fazer` $\rightarrow$ `Em Progresso` $\rightarrow$ `Concluído`). Bloqueia transições inválidas (ex: pular direto de *A Fazer* para *Concluído*) e impede a edição de cartões finalizados. |

Além dos padrões, a aplicação implementa **Controle de Concorrência Otimista** via versionamento numérico dos cartões, retornando `HTTP 409 Conflict` caso duas instâncias tentem salvar edições simultâneas sobre o mesmo estado.

---

## 📦 Dependências do Projeto

O projeto depende dos seguintes pacotes Python (listados em `requirements.txt`):

* **Python 3.10+** (testado e homologado no Python 3.13)
* **Flask** (`==3.1.3` ou `>=3.0.0`): Servidor web RESTful
* **PyQt5** (`==5.15.11` ou `>=5.15.0`): Interface gráfica desktop
* **requests** (`==2.34.2` ou `>=2.31.0`): Comunicação HTTP entre o cliente e o servidor

---

## 🚀 Como Baixar e Instalar

### 1. Clonar o repositório
```bash
git clone https://github.com/Bruno-lima-amaral/Mural-Kanbam.git
cd Mural-Kanbam
```

### 2. (Opcional, mas recomendado) Criar e ativar um ambiente virtual
* **Windows (PowerShell):**
  ```powershell
  py -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
* **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 3. Instalar as dependências
Execute o comando pip para baixar os pacotes necessários:
```bash
pip install -r requirements.txt
```
*(No Windows, caso o comando `pip` não esteja no seu PATH, use: `py -m pip install -r requirements.txt`)*

---

## 🖥️ Como Executar a Aplicação

O projeto é dividido em **dois processos independentes**. Siga a ordem abaixo:

### Passo 1: Iniciar o Servidor Flask
Em um terminal, execute:
```bash
py run_server.py
```
> O servidor iniciará em `http://localhost:5000`. Mantenha este terminal aberto.

### Passo 2: Iniciar a Interface Gráfica (Cliente)
Em um **segundo terminal** (com o servidor já rodando), execute:
```bash
py run_client.py
```
> A janela gráfica do Mural Kanban será exibida na tela.

---

## 🧪 Como Executar os Testes Automatizados

O repositório inclui a suíte de testes automatizados `test_kanban.py`, implementada com a biblioteca nativa `unittest`. Ela valida integralmente os 4 cenários exigidos no **Plano de Testes de Qualidade**:

* **T3.1 — Mover cartão entre colunas:** Criação e transição válida (*A Fazer* $\rightarrow$ *Em Progresso* $\rightarrow$ *Concluído*).
* **T3.2 — Validação de cartão incompleto:** Rejeição de requisições com títulos/descrições ausentes ou tipos inválidos (`HTTP 400`).
* **T3.3 — Sincronização e conflito de edição:** Verificação de controle de concorrência por versionamento (`HTTP 409 Conflict`).
* **T3.4 — State e Composite:** Bloqueio de saltos de estado proibidos, impedimento de edição em cartões finalizados (`HTTP 403 Forbidden`) e consistência da contagem hierárquica.

Para rodar todos os testes, execute:
```bash
py test_kanban.py
```
Resultado esperado:
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.025s

OK
```

---

## 📂 Estrutura de Arquivos

```text
Mural-Kanbam/
├── cliente/
│   ├── __init__.py
│   ├── api_client.py       # Encapsulamento das requisições HTTP REST
│   ├── card_dialog.ui      # Layout do formulário de cartão (Qt Designer)
│   ├── kanban_window.ui    # Layout da janela principal (Qt Designer)
│   └── main.py             # Controlador da interface gráfica PyQt5
├── servidor/
│   ├── __init__.py
│   ├── app.py              # Endpoints da API REST em Flask
│   ├── composite.py        # Padrão Composite (Board, Column, Card)
│   ├── factory.py          # Padrão Factory Method (Tipos de Cartão)
│   └── state.py            # Padrão State (Estados e Transições)
├── Orientacoes_AP2.txt     # Requisitos da atividade
├── PLANO_DE_TESTES_DE_QUALIDADE_AP2.txt  # Critérios de teste do projeto
├── docs_img/               # Imagens de diagramas em alta resolução
├── requirements.txt        # Dependências do projeto
├── run_client.py           # Ponto de entrada do cliente desktop
├── run_server.py           # Ponto de entrada do servidor Flask
├── test_kanban.py          # Bateria de testes automatizados (unittest)
├── .gitignore              # Arquivos ignorados pelo Git
├── DOCUMENTACAO.docx       # Documentação técnica formal em Word (.docx) com capa e diagramas
└── README.md               # Apresentação e guia rápido do projeto
```

---

## 📡 Endpoints da API REST

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/board` | Retorna a estrutura completa do mural e contagens. |
| `GET` | `/api/columns` | Lista as colunas e seus respectivos cartões. |
| `GET` | `/api/columns/<state_name>/cards` | Retorna os cartões de uma coluna específica. |
| `POST` | `/api/cards` | Cria um novo cartão via Factory Method. |
| `GET` | `/api/cards/<card_id>` | Detalhes de um cartão específico. |
| `PUT` | `/api/cards/<card_id>` | Atualiza título/descrição com validação de versão. |
| `DELETE` | `/api/cards/<card_id>` | Remove um cartão do mural. |
| `PUT` | `/api/cards/<card_id>/move` | Transiciona o estado do cartão via State Pattern. |
| `GET` | `/api/card-types` | Lista tipos de cartões disponíveis e suas cores. |

---

## 👥 Autoria
* **Alunos:** Bruno Lima Amaral RA:2403403  & Pedro Henrique Rodrigues RA: 2403467
* **Curso:** Ciência da Computação / Paradigmas de Programação (CC5AN)
