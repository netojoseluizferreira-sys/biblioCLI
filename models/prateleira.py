# models/prateleira.py
# Prateleira: agrupa livros de um mesmo gênero.
# Estrutura interna: dict[(id, titulo)] → list[Livro]
# A chave é o par (id, titulo); o valor é a lista de exemplares daquela edição.
from collections import defaultdict
from .livro import Livro


class Prateleira:
    def __init__(self, genero: str) -> None:
        self._genero = str(genero).strip().title()
        # defaultdict(list): se a chave não existir, cria uma lista vazia
        self._livros: dict[tuple[str, str], list[Livro]] = defaultdict(list)

    # ------------------------------------------------------------------
    # Propriedades
    # ------------------------------------------------------------------

    @property
    def genero(self) -> str:
        """Gênero da prateleira (normalizado)."""
        return self._genero

    # ------------------------------------------------------------------
    # Adição
    # ------------------------------------------------------------------

    def adicionar(self, livro: Livro) -> None:
        """Adiciona um exemplar à prateleira.
        Levanta ValueError se o gênero do livro for diferente."""
        if livro.genero != self._genero:
            raise ValueError(
                f"Livro {livro.titulo!r} é do gênero {livro.genero!r}, "
                f"não pertence à prateleira {self._genero!r}"
            )
        chave = (livro.id, livro.titulo)
        self._livros[chave].append(livro)

    # ------------------------------------------------------------------
    # Remoção
    # ------------------------------------------------------------------

    def remover_por_titulo(
        self, titulo: str, quantidade: int | None = None
    ) -> tuple[int, list[Livro]]:
        """Remove exemplares com o título informado (exato, case-insensitive).

        - Sem 'quantidade': remove TODOS os exemplares com esse título.
        - Com 'quantidade': remove até N exemplares (os primeiros).

        Retorna (quantidade_removida, lista_removida).
        """
        titulo_norm = str(titulo).strip().title()
        removidos: list[Livro] = []

        # list(...) para poder deletar chaves durante a iteração
        for chave, exemplares in list(self._livros.items()):
            id_livro, t = chave
            if t != titulo_norm:
                continue

            if quantidade is None:
                # Remove todos os exemplares dessa chave
                removidos.extend(exemplares)
                del self._livros[chave]
            else:
                faltam = quantidade - len(removidos)
                if faltam <= 0:
                    break
                pegar = min(faltam, len(exemplares))
                removidos.extend(exemplares[:pegar])
                del exemplares[:pegar]   # remove de fato da lista
                if not exemplares:
                    del self._livros[chave]

            # Se já atingiu a quantidade, para o loop externo
            if quantidade is not None and len(removidos) >= quantidade:
                break

        return (len(removidos), removidos)

    def remover_exemplar(self, livro: Livro) -> bool:
        """Remove um exemplar específico (comparação por __eq__).
        Retorna True se removeu, False se não encontrou."""
        chave = (livro.id, livro.titulo)
        if chave not in self._livros:
            return False
        if livro in self._livros[chave]:     # usa __eq__
            self._livros[chave].remove(livro)
            if not self._livros[chave]:
                del self._livros[chave]
            return True
        return False

    # ------------------------------------------------------------------
    # Busca
    # ------------------------------------------------------------------

    def buscar(self, termo, campo: str) -> list[Livro]:
        """Busca exemplares por campo específico.

        Campos aceitos: 'titulo', 'autor', 'ano', 'genero', 'id'.
        Busca PARCIAL (substring, case-insensitive). Para 'ano', aceita
        int ou string e normaliza para o formato do Livro.
        Retorna lista de exemplares (com duplicatas se houver).
        """
        campos_validos = {"titulo", "autor", "ano", "genero", "id"}
        if campo not in campos_validos:
            raise ValueError(f"Campo inválido: {campo!r}")

        # Normaliza o termo conforme o campo
        if campo == "ano":
            termo_norm = self._normalizar_ano(termo)
        else:
            termo_norm = str(termo).strip().title()

        termo_lower = termo_norm.lower()
        resultados: list[Livro] = []
        for exemplares in self._livros.values():
            for livro in exemplares:
                valor = str(getattr(livro, campo)).lower()
                if termo_lower in valor:      # busca parcial
                    resultados.append(livro)

        return resultados

    @staticmethod
    def _normalizar_ano(termo) -> str:
        """Normaliza o termo de busca de ano para o formato do Livro: 'N DC' ou 'N AC'."""
        # Aceita int (positivo/negativo) ou string
        if isinstance(termo, int):
            if termo == 0:
                raise ValueError("Ano 0 não existe")
            return f"{abs(termo)} {'AC' if termo < 0 else 'DC'}"

        # String: tenta parsear com a mesma regex do Livro
        match = Livro._REGEX_ANO.fullmatch(str(termo).strip())
        if match is None:
            raise ValueError(f"Formato de ano inválido: {termo!r}")
        numero = int(match.group(1))
        era = (match.group(2) or "DC").upper()
        if numero == 0:
            raise ValueError("Ano 0 não existe")
        return f"{numero} {era}"

    # ------------------------------------------------------------------
    # Listagem e iteração
    # ------------------------------------------------------------------

    def listar(self) -> list[Livro]:
        """Retorna todos os exemplares da prateleira."""
        return list(self)

    def __len__(self) -> int:
        """Total de exemplares (não de obras únicas)."""
        return sum(len(exemplares) for exemplares in self._livros.values())

    def __iter__(self):
        """Itera sobre todos os exemplares."""
        for exemplares in self._livros.values():
            yield from exemplares

    # ------------------------------------------------------------------
    # Representação
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return (
            f"Prateleira(genero={self._genero!r}, "
            f"exemplares={len(self)}, obras={len(self._livros)})"
        )

    def __str__(self) -> str:
        # Ajusta singular/plural
        palavra = "exemplar" if len(self) == 1 else "exemplares"
        return f"Prateleira de {self._genero} ({len(self)} {palavra})"

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serializa a prateleira para dicionário (JSON-friendly)."""
        return {
            "genero": self._genero,
            "livros": [livro.to_dict() for livro in self],
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Prateleira":
        """Reconstrói a prateleira a partir de um dicionário."""
        prateleira = cls(dados["genero"])
        for livro_dict in dados["livros"]:
            prateleira.adicionar(Livro.from_dict(livro_dict))
        return prateleira


# ----------------------------------------------------------------------
# Testes manuais (rodar da raiz do projeto com: python -m models.prateleira)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import io

    # Força UTF-8 no stdout do Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("=== Criação ===")
    p = Prateleira("fantasia")
    print(p)

    print("\n=== Adição ===")
    p.adicionar(Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"))
    p.adicionar(Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"))
    p.adicionar(Livro("2", "O Senhor dos Anéis", "J. R. R. Tolkien", 1954, "Fantasia"))
    print(p)
    print(f"Total de exemplares: {len(p)}")

    print("\n=== Gênero diferente deve dar erro ===")
    try:
        p.adicionar(Livro("3", "Duna", "Frank Herbert", 1965, "Ficção Científica"))
    except ValueError as e:
        print(f"Erro esperado: {e}")

    print("\n=== Busca parcial por autor ===")
    for l in p.buscar("tolkien", "autor"):
        print(f"  {l}")

    print("\n=== Busca parcial por título ===")
    for l in p.buscar("hobbit", "titulo"):
        print(f"  {l}")

    print("\n=== Busca por id ===")
    for l in p.buscar("1", "id"):
        print(f"  {l}")

    print("\n=== Busca por ano ===")
    for l in p.buscar(1954, "ano"):
        print(f"  {l}")

    print("\n=== Remover 1 exemplar do Hobbit ===")
    qtd, removidos = p.remover_por_titulo("O Hobbit", quantidade=1)
    print(f"Removidos: {qtd}")
    print(f"Total atual: {len(p)}")

    print("\n=== Remover todos do Hobbit ===")
    qtd, removidos = p.remover_por_titulo("O Hobbit")
    print(f"Removidos: {qtd}")
    print(f"Total atual: {len(p)}")

    print("\n=== Round-trip (dict → objeto) ===")
    d = p.to_dict()
    print(d)
    p2 = Prateleira.from_dict(d)
    print(p2)
    print(f"Mesmo tamanho: {len(p) == len(p2)}")