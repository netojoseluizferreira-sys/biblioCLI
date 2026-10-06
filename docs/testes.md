# Testes Unitários — biblioCLI

Documentação da suíte de testes unitários do **biblioCLI**, desenvolvida com **pytest**.

---

## 1. Visão Geral

A suíte cobre todas as camadas do sistema:
- **Domínio (`models`)**: `Livro`, `Prateleira`, `Biblioteca`
- **Persistência (`utils/persistencia.py`)**: escrita atômica, carregamento, erros de I/O, corrupção e schema
- **Utilitários de Entrada/Saída (`utils/funcoes.py`)**: parsing de comandos, validação de números, confirmações e formatação de texto
- **Interface de Linha de Comando (`main.py`)**: comandos `add`, `rm`, `list`, `shelves`, `search`, loop interativo e tratamento de encerramento seguro

---

## 2. Estrutura dos Arquivos de Teste

```
tests/
├── __init__.py
├── test_livro.py          # 20 testes: criação, validação, regex de ano, comparação e hash
├── test_prateleira.py     # 22 testes: prateleira por gênero, remoção de exemplares, busca parcial
├── test_biblioteca.py     # 17 testes: criação de prateleiras, delegação, remoção global e persistência
├── test_persistencia.py   #  9 testes: escrita atômica com .tmp, leitura de JSON e tratamento de falhas
├── test_funcoes.py        # 13 testes: funções puras de parsing e helpers de terminal
└── test_main.py           # 14 testes: handlers de comandos e ciclo de vida do loop principal
```

**Total:** 95 testes unitários automatizados com 99% de cobertura total do código.

---

## 3. Como Executar

### Instalar Dependências de Desenvolvimento
```bash
pip install -e ".[dev]"
```

### Executar Todos os Testes
```bash
pytest
# ou
python -m pytest
```

### Executar com Relatório de Cobertura
```bash
pytest --cov --cov-report=term-missing
# ou
python -m pytest --cov --cov-report=term-missing
```

### Executar Arquivo Específico
```bash
pytest tests/test_livro.py
```
