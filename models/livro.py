# models/livro.py
# Classe que representa um livro (obra + edição).
# O id identifica a OBRA; o ano identifica a EDIÇÃO.
# Dois livros são iguais (==) se têm mesmo id E mesmo ano.
# Dois livros são "a mesma obra" se têm mesmo id.
import re
from datetime import datetime


class Livro:
    # Regex para parsear o ano: aceita "384", "384 AC", "384 DC" (case-insensitive).
    # O grupo 1 captura o número; o grupo 2 captura a era (opcional).
    _REGEX_ANO = re.compile(r"^(\d+)\s*(AC|DC)?$", re.IGNORECASE)

    def __init__(self, id: str, titulo: str, autor: str, ano, genero: str) -> None:
        # id é imutável — só aceita string não vazia
        if not id or not str(id).strip():
            raise ValueError("ID não pode ser vazio")
        self._id = str(id).strip()

        # Os demais passam pelos setters (validação + normalização)
        self.titulo = titulo
        self.autor = autor
        self.ano = ano
        self.genero = genero

    # ------------------------------------------------------------------
    # Getters e setters
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Retorna o id (identificador da obra). Imutável."""
        return self._id

    @property
    def titulo(self) -> str:
        return self._titulo

    @titulo.setter
    def titulo(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ValueError("Título não pode ser vazio")
        self._titulo = str(valor).strip().title()

    @property
    def autor(self) -> str:
        return self._autor

    @autor.setter
    def autor(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ValueError("Autor não pode ser vazio")
        self._autor = str(valor).strip().title()

    @property
    def ano(self) -> str:
        """Ano no formato 'N DC' ou 'N AC'."""
        return self._ano

    @ano.setter
    def ano(self, valor) -> None:
        # Aceita int positivo/negativo:
        #   positivo → "N DC"
        #   negativo → "N AC" (abs)
        if isinstance(valor, int):
            if valor == 0:
                raise ValueError("Ano 0 não existe")
            valor = f"{abs(valor)} {'AC' if valor < 0 else 'DC'}"

        # Parseia string via regex
        match = self._REGEX_ANO.fullmatch(str(valor).strip())
        if match is None:
            raise ValueError(f"Formato de ano inválido: {valor!r}")

        numero = int(match.group(1))
        era = (match.group(2) or "DC").upper()

        # Validações
        if numero == 0:
            raise ValueError("Ano 0 não existe")

        # Ano DC não pode estar no futuro
        if era == "DC" and numero > datetime.now().year:
            raise ValueError(
                f"Ano não pode ser maior que {datetime.now().year}"
            )

        self._ano = f"{numero} {era}"

    @property
    def genero(self) -> str:
        return self._genero

    @genero.setter
    def genero(self, valor: str) -> None:
        if not valor or not str(valor).strip():
            raise ValueError("Gênero não pode ser vazio")
        self._genero = str(valor).strip().title()

    # ------------------------------------------------------------------
    # Comparação e identidade
    # ------------------------------------------------------------------

    def mesma_obra(self, outro: object) -> bool:
        """Retorna True se outro é o mesmo livro (mesmo id), ignorando edição."""
        if not isinstance(outro, Livro):
            return False
        return self._id == outro._id

    def __eq__(self, other: object) -> bool:
        """Dois livros são iguais se têm mesmo id E mesmo ano (mesma edição)."""
        if not isinstance(other, Livro):
            return NotImplemented
        return self._id == other._id and self._ano == other._ano

    def __hash__(self) -> int:
        """Hash consistente com __eq__: id + ano."""
        return hash((self._id, self._ano))

    # ------------------------------------------------------------------
    # Representação
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Formato amigável para o usuário."""
        return f"{self._titulo} — {self._autor} ({self._ano}) [{self._genero}]"

    def __repr__(self) -> str:
        """Formato de debug; código Python válido que recria o objeto."""
        return (
            f"Livro(id={self._id!r}, titulo={self._titulo!r}, "
            f"autor={self._autor!r}, ano={self._ano!r}, genero={self._genero!r})"
        )

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Retorna dicionário para persistência."""
        return {
            "id": self._id,
            "titulo": self._titulo,
            "autor": self._autor,
            "ano": self._ano,
            "genero": self._genero,
        }

    @classmethod
    def from_dict(cls, dados: dict) -> "Livro":
        """Cria um Livro a partir de um dicionário."""
        return cls(**dados)


if __name__ == "__main__":
    # Testes
    import sys
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    l1 = Livro("1", "O Senhor dos Anéis", "J. R. R. Tolkien", 1954, "Fantasia")
    print(l1)
    print(l1.to_dict())
    l2 = Livro.from_dict(l1.to_dict())
    print(l2)
    print(l1 == l2)