# biblioCLI

Sistema de gerenciamento de biblioteca via linha de comando.

Projeto integrador do **Bloco 1 — Orientação a Objetos** do 
[Diamond Forge](https://github.com/netojoseluizferreira-sys/diamond-forge).

## Sobre

Um CRUD de biblioteca que gerencia livros organizados por gênero em 
prateleiras. Aplica os conceitos de POO, dataclasses e persistência 
em JSON, consolidando o que foi aprendido no primeiro bloco do 
Diamond Forge.

## Contexto

**The Diamond Forge** é uma jornada de 60 exercícios de **Python Avançado**, 
projetada para transformar um programador que já domina a sintaxe em um 
**engenheiro de software que entende as profundezas da linguagem**. 

Não se trata de aprender a usar Python — trata-se de dominar os mecanismos 
internos que fazem do Python uma das linguagens mais poderosas do mundo.

Este projeto é o **primeiro integrador** da jornada, fechando o 
**Bloco 1 — Orientação a Objetos**.

## Funcionalidades

- Cadastrar livros com título, autor, ano e gênero
- Organizar livros automaticamente em prateleiras por gênero
- Listar livros (todos ou por gênero)
- Buscar por título ou autor
- Remover livros
- Persistência em JSON (carrega ao iniciar, salva ao sair)

## Estrutura

\`\`\`
biblioCLI/

├── docs/          # documentação de arquitetura e testes

├── data/          # arquivo JSON de dados

├── models/        # classes do domínio

├── tests/         # testes automatizados

├── main.py        # ponto de entrada

├── LICENSE

└── README.md
\`\`\`

## Como usar

\`\`\`bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Rodar o programa
python main.py

# Rodar os testes
pytest
\`\`\`

## Conceitos aplicados

- Classes e objetos
- Herança e composição
- Encapsulamento com `@property`
- Dataclasses para modelos de dados
- Métodos especiais (dunder methods)
- Persistência em JSON
- Testes automatizados

## Licença

MIT — veja [LICENSE](LICENSE).
