# models/biblioteca.py
# Biblioteca: agrupa prateleiras por gênero.
# Estrutura interna: dict[str, Prateleira] (chave: gênero normalizado).
# O id do livro identifica a OBRA; o ano identifica a EDIÇÃO.
from .livro import Livro
from .prateleira import Prateleira


class Biblioteca:
    # Versão do schema de persistência. Muda quando a estrutura do JSON mudar.
    _VERSAO_SCHEMA = 1

    def __init__(self) -> None:
        # Chave: gênero (str normalizado); valor: Prateleira
        self._prateleiras: dict[str, Prateleira] = {}

    # ------------------------------------------------------------------
    # Prateleiras
    # ------------------------------------------------------------------

    def criar_prateleira(self, genero: str) -> Prateleira:
        """Cria uma prateleira nova. Levanta ValueError se já existir."""
        genero_norm = str(genero).strip().title()
        if genero_norm in self._prateleiras:
            raise ValueError(f"Prateleira {genero_norm!r} já existe")
        prateleira = Prateleira(genero_norm)
        self._prateleiras[genero_norm] = prateleira
        return prateleira

    def remover_prateleira(self, genero: str) -> bool:
        """Remove uma prateleira. Só se estiver vazia.

        Retorna True se removeu, False se não existia.
        Levanta ValueError se a prateleira tiver livros.
        """
        genero_norm = str(genero).strip().title()
        if genero_norm not in self._prateleiras:
            return False
        prateleira = self._prateleiras[genero_norm]
        if len(prateleira) > 0:
            raise ValueError(
                f"Prateleira {genero_norm!r} não está vazia "
                f"({len(prateleira)} exemplares)"
            )
        del self._prateleiras[genero_norm]
        return True

    def listar_prateleiras(self) -> list[str]:
        """Retorna os gêneros das prateleiras existentes."""
        return list(self._prateleiras.keys())

    def obter_prateleira(self, genero: str) -> Prateleira | None:
        """Retorna a prateleira do gênero, ou None se não existir."""
        genero_norm = str(genero).strip().title()
        return self._prateleiras.get(genero_norm)

    # ------------------------------------------------------------------
    # Livros
    # ------------------------------------------------------------------

    def adicionar_livro(self, livro: Livro) -> None:
        """Adiciona um livro. Cria a prateleira do gênero se não existir."""
        genero_norm = livro.genero
        if genero_norm not in self._prateleiras:
            self.criar_prateleira(genero_norm)
        self._prateleiras[genero_norm].adicionar(livro)

    def remover_livro(
        self, titulo: str, quantidade: int | None = None
    ) -> tuple[int, list[Livro]]:
        """Remove exemplares pelo título em TODAS as prateleiras.

        - Sem 'quantidade': remove todos os exemplares com esse título.
        - Com 'quantidade': remove até N exemplares no total (todas as prateleiras).

        Retorna (quantidade_removida, lista_removida).
        """
        removidos_totais: list[Livro] = []

        for prateleira in self._prateleiras.values():
            # Calcula quanto ainda falta remover (ou None = todos)
            if quantidade is None:
                faltam = None
            else:
                faltam = quantidade - len(removidos_totais)
                if faltam <= 0:
                    break

            qtd, livros = prateleira.remover_por_titulo(titulo, faltam)
            removidos_totais.extend(livros)

        return (len(removidos_totais), removidos_totais)

    def buscar(self, termo, campo: str) -> list[Livro]:
        """Busca em todas as prateleiras (delega para Prateleira.buscar)."""
        resultados: list[Livro] = []
        for prateleira in self._prateleiras.values():
            resultados.extend(prateleira.buscar(termo, campo))
        return resultados

    def listar(self) -> list[Livro]:
        """Retorna todos os exemplares de todas as prateleiras."""
        return list(self)

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Total de exemplares (soma de todas as prateleiras)."""
        return sum(len(p) for p in self._prateleiras.values())

    def __iter__(self):
        """Itera sobre todos os exemplares, prateleira por prateleira."""
        for prateleira in self._prateleiras.values():
            yield from prateleira

    def __repr__(self) -> str:
        return (
            f"Biblioteca(prateleiras={len(self._prateleiras)}, "
            f"exemplares={len(self)})"
        )

    def __str__(self) -> str:
        if not self._prateleiras:
            return "Biblioteca vazia"

        # Ajusta singular/plural
        palavra_p = "prateleira" if len(self._prateleiras) == 1 else "prateleiras"
        palavra_l = "exemplar" if len(self) == 1 else "exemplares"

        linhas = [
            f"Biblioteca — {len(self)} {palavra_l} "
            f"em {len(self._prateleiras)} {palavra_p}:"
        ]
        for genero, prateleira in sorted(self._prateleiras.items()):
            qtd = len(prateleira)
            palavra = "exemplar" if qtd == 1 else "exemplares"
            linhas.append(f"  - {genero}: {qtd} {palavra}")

        return "\n".join(linhas)

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Serializa a biblioteca para dicionário (JSON-friendly).

        O campo 'version' permite migrar o schema no futuro.
        A lista de prateleiras é achatada (cada prateleira carrega seu
        próprio gênero), evitando redundância com uma chave de dict.
        """
        return {
            "version": self._VERSAO_SCHEMA,
            "prateleiras": [p.to_dict() for p in self._prateleiras.values()],
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Biblioteca":
        """Reconstrói a Biblioteca a partir de um dicionário.

        Levanta RuntimeError se a versão do schema não for compatível.
        """
        schema_v = dados.get("version")
        if schema_v != cls._VERSAO_SCHEMA:
            raise RuntimeError(
                f"Versão de schema incompatível: {schema_v!r} "
                f"(esperado: {cls._VERSAO_SCHEMA})"
            )

        biblioteca = cls()
        for p_dict in dados["prateleiras"]:
            prateleira = Prateleira.from_dict(p_dict)
            # Reconstroi o índice interno pelo gênero da prateleira
            biblioteca._prateleiras[prateleira.genero] = prateleira

        return biblioteca


# ----------------------------------------------------------------------
# Testes manuais
# Rodar da raiz do projeto com: python -m models.biblioteca
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import io

    # Força UTF-8 no stdout do Windows
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("=== Biblioteca vazia ===")
    b = Biblioteca()
    print(b)
    print()

    print("=== Adicionando livros (cria prateleiras automaticamente) ===")
    b.adicionar_livro(Livro("1", "O Senhor dos Anéis", "J. R. R. Tolkien", 1954, "Fantasia"))
    b.adicionar_livro(Livro("2", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"))
    b.adicionar_livro(Livro("3", "Duna", "Frank Herbert", 1965, "Ficção Científica"))
    b.adicionar_livro(Livro("3", "Duna", "Frank Herbert", 1965, "Ficção Científica"))
    print(b)
    print()

    print("=== Listar prateleiras ===")
    print(b.listar_prateleiras())
    print()

    print("=== Obter prateleira específica ===")
    fantasia = b.obter_prateleira("fantasia")
    print(fantasia)
    print()

    print("=== Busca por autor em todas as prateleiras ===")
    for l in b.buscar("tolkien", "autor"):
        print(f"  {l}")
    print()

    print("=== Busca por título em todas as prateleiras ===")
    for l in b.buscar("duna", "titulo"):
        print(f"  {l}")
    print()

    print("=== Remover 1 exemplar de 'Duna' (global) ===")
    qtd, removidos = b.remover_livro("Duna", quantidade=1)
    print(f"Removidos: {qtd}")
    print(b)
    print()

    print("=== Tentar remover prateleira com livros (deve dar erro) ===")
    try:
        b.remover_prateleira("Fantasia")
    except ValueError as e:
        print(f"Erro esperado: {e}")
    print()

    print("=== Criar prateleira que já existe (deve dar erro) ===")
    try:
        b.criar_prateleira("Fantasia")
    except ValueError as e:
        print(f"Erro esperado: {e}")
    print()

    print("=== Round-trip (dict → objeto) ===")
    d = b.to_dict()
    print(d)
    b2 = Biblioteca.from_dict(d)
    print(b2)
    print(f"Mesmo tamanho: {len(b) == len(b2)}")