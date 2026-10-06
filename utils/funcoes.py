# utils/funcoes.py
# Funções utilitárias para a CLI.
# Sem dependência dos models — só helpers de input/output.
# As funções de input (pedir_input, pedir_int, confirmar) fazem loop até
# receberem um valor válido. As de output são puras e testáveis.


def pedir_input(mensagem: str) -> str:
    """Pede uma linha ao usuário e retorna com strip() (remove espaços nas pontas)."""
    return input(mensagem).strip()


def pedir_int(mensagem: str, minimo: int | None = None, maximo: int | None = None) -> int:
    """Pede um inteiro, repetindo enquanto o valor for inválido.

    Aceita faixa opcional [minimo, maximo]. Se o valor lido estiver fora
    ou não for inteiro, imprime mensagem e pede de novo.
    """
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Por favor, insira um número inteiro válido.")
            continue

        if minimo is not None and valor < minimo:
            print(f"O valor deve ser maior ou igual a {minimo}.")
            continue
        if maximo is not None and valor > maximo:
            print(f"O valor deve ser menor ou igual a {maximo}.")
            continue

        return valor


def confirmar(mensagem: str) -> bool:
    """Pergunta s/n e retorna True/False.

    Aceita 's', 'sim', 'y', 'yes' como True (qualquer coisa começando com 's').
    Qualquer outra resposta é False.
    """
    resposta = pedir_input(f"{mensagem} [s/n]: ").lower()
    return resposta.startswith("s")


def imprimir_secao(titulo: str) -> None:
    """Imprime um título centralizado entre linhas de '='."""
    print("\n" + "=" * 50)
    print(titulo.center(50))
    print("=" * 50)


def imprimir_lista_livros(livros: list) -> None:
    """Imprime uma lista de livros, um por linha.

    Cada linha tem ID, título, autor e ano. Se a lista estiver vazia,
    imprime uma mensagem informativa em vez de nada.
    """
    if not livros:
        print("(nenhum livro)")
        return

    for livro in livros:
        print(
            f"ID: {livro.id} | "
            f"Título: {livro.titulo} | "
            f"Autor: {livro.autor} | "
            f"Ano: {livro.ano}"
        )


def mostrar_ajuda(comandos: dict[str, str]) -> None:
    """Imprime a lista de comandos disponíveis.

    Recebe um dict {nome_do_comando: descrição}. Não depende de nada
    específico do biblioCLI — só formata.
    """
    print("\nComandos disponíveis:")
    for comando, descricao in comandos.items():
        print(f"  {comando:<20} {descricao}")
    print()


def parse_comando(linha: str) -> tuple[str, list[str]]:
    """Divide a linha em (comando, argumentos).

    O comando é sempre lowercase. Os argumentos mantêm o que o usuário
    digitou (mas sem espaços nas pontas).

    Exemplos:
        'add Duna 1965'  → ('add', ['Duna', '1965'])
        'list'           → ('list', [])
        '  ADD  X  '     → ('add', ['X'])
        ''               → ('', [])
    """
    partes = linha.strip().split()
    if not partes:
        return ("", [])
    return (partes[0].lower(), partes[1:])


# ----------------------------------------------------------------------
# Testes manuais
# Rodar da raiz do projeto com: python -m utils.funcoes
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    # Testes das funções puras
    print("=== parse_comando ===")
    print(parse_comando("add Duna 1965"))       # ('add', ['Duna', '1965'])
    print(parse_comando("list"))                 # ('list', [])
    print(parse_comando("  ADD  X  "))           # ('add', ['X'])
    print(parse_comando(""))                     # ('', [])
    print()

    print("=== imprimir_secao ===")
    imprimir_secao("Teste de Seção")

    print("=== imprimir_lista_livros (vazia) ===")
    imprimir_lista_livros([])

    print("\n=== imprimir_lista_livros (com itens fake) ===")
    # Objeto fake — só pra testar a formatação
    class _Fake:
        def __init__(self, id, titulo, autor, ano):
            self.id = id
            self.titulo = titulo
            self.autor = autor
            self.ano = ano

    imprimir_lista_livros([
        _Fake("1", "Duna", "Frank Herbert", "1965 DC"),
        _Fake("2", "O Hobbit", "J. R. R. Tolkien", "1937 DC"),
    ])

    print("\n=== mostrar_ajuda ===")
    mostrar_ajuda({
        "add": "Adiciona livro",
        "rm": "Remove livro",
        "list": "Lista todos",
        "exit": "Salva e sai",
    })