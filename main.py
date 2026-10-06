# main.py
# CLI do biblioCLI.
# Loop de leitura de comandos; cada comando modifica a biblioteca em memória.
# Após cada operação que muda (add, rm), salva em disco.
# Ao sair (exit, Ctrl+C, Ctrl+D), salva de novo e encerra.

from models.livro import Livro
from models.biblioteca import Biblioteca
from utils.persistencia import carregar, salvar
from utils.funcoes import (
    pedir_input,
    pedir_int,
    imprimir_secao,
    imprimir_lista_livros,
    mostrar_ajuda,
    parse_comando,
)


# Comandos disponíveis: nome → descrição
COMANDOS = {
    "add":     "Adiciona um livro (interativo)",
    "rm":      "Remove exemplares por título (ex: rm Duna)",
    "list":    "Lista todos os livros (ou por gênero: list Fantasia)",
    "shelves": "Lista as prateleiras (só gêneros)",
    "search":  "Busca por campo (ex: search autor tolkien)",
    "help":    "Mostra esta ajuda",
    "exit":    "Salva e sai (também aceita 'quit')",
}


# ----------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------

def cmd_add(biblioteca: Biblioteca) -> None:
    """Comando 'add': pede dados interativamente e adiciona o livro."""
    imprimir_secao("Novo livro")
    id_livro = pedir_input("ID: ")
    titulo = pedir_input("Título: ")
    autor = pedir_input("Autor: ")
    # Ano como int: aceita -384 (AC) ou 1965 (DC)
    ano = pedir_int("Ano: ")
    genero = pedir_input("Gênero: ")

    try:
        livro = Livro(id_livro, titulo, autor, ano, genero)
    except ValueError as e:
        print(f"Erro ao criar livro: {e}")
        return

    biblioteca.adicionar_livro(livro)
    print(f"Livro {livro.titulo!r} adicionado.")


def cmd_rm(biblioteca: Biblioteca, args: list[str]) -> None:
    """Comando 'rm': remove exemplares por título (aceita títulos com espaço)."""
    if not args:
        print("Uso: rm <titulo>")
        return

    # Junta as palavras para permitir títulos com espaço
    titulo = " ".join(args)

    qtd, _ = biblioteca.remover_livro(titulo)
    if qtd == 0:
        print(f"Nenhum livro com título {titulo!r}.")
    else:
        palavra = "exemplar" if qtd == 1 else "exemplares"
        print(f"{qtd} {palavra} removido(s).")


def cmd_list(biblioteca: Biblioteca, args: list[str]) -> None:
    """Comando 'list': lista todos ou por gênero."""
    imprimir_secao("Lista de livros")

    if args:
        # Filtro por gênero
        genero_filtro = " ".join(args)
        prateleira = biblioteca.obter_prateleira(genero_filtro)
        if prateleira is None:
            print(f"Prateleira {genero_filtro!r} não existe.")
            return
        livros = prateleira.listar()
        print(f"Livros do gênero {prateleira.genero!r}:")
    else:
        livros = biblioteca.listar()
        print("Todos os livros:")

    imprimir_lista_livros(livros)


def cmd_shelves(biblioteca: Biblioteca) -> None:
    """Comando 'shelves': lista só os gêneros das prateleiras."""
    imprimir_secao("Prateleiras (gêneros disponíveis)")
    generos = biblioteca.listar_prateleiras()
    if not generos:
        print("(nenhuma prateleira)")
        return
    for genero in sorted(generos):
        print(f"- {genero}")


def cmd_search(biblioteca: Biblioteca, args: list[str]) -> None:
    """Comando 'search': busca por campo.

    Uso: search <campo> <valor>
    Aceita valores com espaço (ex: search titulo O Hobbit).
    """
    if len(args) < 2:
        print("Uso: search <campo> <valor>")
        print("Campos válidos: titulo|autor|ano|genero|id")
        return

    campo = args[0].lower()
    valor = " ".join(args[1:])

    campos_validos = {"titulo", "autor", "ano", "genero", "id"}
    if campo not in campos_validos:
        print(f"Campo inválido: {campo!r}")
        print("Use: titulo|autor|ano|genero|id")
        return

    # Ordem correta da assinatura: buscar(termo, campo)
    try:
        livros = biblioteca.buscar(valor, campo)
    except ValueError as e:
        print(f"Erro na busca: {e}")
        return

    imprimir_secao(f"Resultados para {campo} = {valor!r}")
    imprimir_lista_livros(livros)


# ----------------------------------------------------------------------
# Loop principal
# ----------------------------------------------------------------------

def main() -> None:
    """Carrega a biblioteca, entra no loop de comandos, salva e sai."""
    biblioteca = carregar()

    print("Bem-vindo ao biblioCLI! Use 'help' para ver comandos.")

    try:
        while True:
            linha = pedir_input(">>> ")
            if not linha:
                continue

            comando, args = parse_comando(linha)

            # --- Comandos que mudam dados: salvam após execução ---
            if comando == "add":
                cmd_add(biblioteca)
                salvar(biblioteca)

            elif comando == "rm":
                cmd_rm(biblioteca, args)
                salvar(biblioteca)

            # --- Comandos de leitura: não salvam ---
            elif comando == "list":
                cmd_list(biblioteca, args)

            elif comando == "shelves":
                cmd_shelves(biblioteca)

            elif comando == "search":
                cmd_search(biblioteca, args)

            elif comando == "help":
                mostrar_ajuda(COMANDOS)

            # --- Saída ---
            elif comando in ("exit", "quit"):
                print("Salvando e saindo. Até logo!")
                break

            else:
                print(f"Comando desconhecido: {comando!r}")
                print("Digite 'help' para listar os comandos.")

    except (KeyboardInterrupt, EOFError):
        print("\nInterrompido pelo usuário.")

    finally:
        # Salva ao sair (por segurança, mesmo já salvando a cada operação)
        try:
            salvar(biblioteca)
            print("Biblioteca salva.")
        except Exception as e:
            print(f"ERRO ao salvar: {e}")


if __name__ == "__main__":
    main()