# utils/persistencia.py
# Salva e carrega a biblioteca em JSON.
# Escrita atômica: grava em arquivo temporário e substitui de uma vez.
from pathlib import Path
import json
import os

from models.biblioteca import Biblioteca


# Caminho padrão: <raiz_projeto>/data/library.json
# Descoberto via __file__ para funcionar de qualquer diretório de execução.
RAIZ_PROJETO = Path(__file__).resolve().parent.parent
CAMINHO_PADRAO = RAIZ_PROJETO / "data" / "library.json"


def salvar(biblioteca: Biblioteca, caminho: Path = CAMINHO_PADRAO) -> None:
    """Salva a biblioteca em JSON de forma atômica.

    Cria a pasta pai se não existir. Escreve em arquivo temporário e
    substitui o original só depois que a escrita terminou com sucesso.
    Se algo falhar no meio, o arquivo original fica intacto.
    """
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    # Nome do temporário: library.json → library.json.tmp
    # (with_suffix não serve aqui porque só aceita um ponto)
    tmp = caminho.with_name(caminho.name + ".tmp")

    try:
        with open(tmp, "w", encoding="utf-8") as f:
            # ensure_ascii=False mantém acentos legíveis (não escapa pra \uXXXX)
            # indent=2 deixa o JSON formatado, fácil de ler
            json.dump(biblioteca.to_dict(), f, ensure_ascii=False, indent=2)
        os.replace(tmp, caminho)   # substituição atômica
    except Exception as e:
        # Limpa o temporário se algo deu errado antes do replace
        if tmp.exists():
            tmp.unlink()
        raise RuntimeError(f"Erro ao salvar biblioteca em {caminho}: {e}") from e


def carregar(caminho: Path = CAMINHO_PADRAO) -> Biblioteca:
    """Carrega a biblioteca do arquivo JSON.

    - Se o arquivo não existir, retorna uma Biblioteca vazia (primeira execução).
    - Se o arquivo estiver corrompido (JSON inválido), levanta ValueError.
    - Erros de schema (versão incompatível) sobem direto de Biblioteca.from_dict.
    """
    caminho = Path(caminho)

    # Primeira execução: ainda não tem arquivo
    if not caminho.exists():
        return Biblioteca()

    # Lê o JSON — erros específicos de parse e I/O
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Arquivo de dados corrompido: {caminho}") from e
    except OSError as e:
        raise OSError(f"Erro ao ler {caminho}: {e}") from e

    # Reconstrói — erros de schema sobem direto (RuntimeError)
    return Biblioteca.from_dict(dados)


# ----------------------------------------------------------------------
# Testes manuais
# Rodar da raiz do projeto com: python -m utils.persistencia
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import io
    from models.livro import Livro

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    caminho_teste = RAIZ_PROJETO / "data" / "library_teste.json"

    print("=== Carregar arquivo inexistente → vazia ===")
    b = carregar(caminho_teste)
    print(b)
    print()

    print("=== Adicionar livros e salvar ===")
    b.adicionar_livro(Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica"))
    b.adicionar_livro(Livro("2", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"))
    salvar(b, caminho_teste)
    print("Salvo com sucesso.")
    print()

    print("=== Carregar de volta ===")
    b2 = carregar(caminho_teste)
    print(b2)
    print(f"Mesmo tamanho: {len(b) == len(b2)}")
    print()

    print("=== Conteúdo do arquivo JSON ===")
    print(caminho_teste.read_text(encoding="utf-8"))
    print()

    print("=== Teste de arquivo corrompido ===")
    caminho_teste.write_text("{ isso não é json válido", encoding="utf-8")
    try:
        carregar(caminho_teste)
    except ValueError as e:
        print(f"Erro esperado: {e}")

    # Limpa
    caminho_teste.unlink()