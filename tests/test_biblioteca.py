# tests/test_biblioteca.py
import pytest
from models.livro import Livro
from models.prateleira import Prateleira
from models.biblioteca import Biblioteca


@pytest.fixture
def biblioteca_vazia():
    return Biblioteca()


@pytest.fixture
def biblioteca_povoada():
    b = Biblioteca()
    b.adicionar_livro(Livro("1", "O Senhor dos Anéis", "J. R. R. Tolkien", 1954, "Fantasia"))
    b.adicionar_livro(Livro("2", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"))
    b.adicionar_livro(Livro("3", "Duna", "Frank Herbert", 1965, "Ficção Científica"))
    b.adicionar_livro(Livro("3", "Duna", "Frank Herbert", 1965, "Ficção Científica"))
    return b


class TestBibliotecaPrateleiras:
    def test_criar_prateleira_com_sucesso(self, biblioteca_vazia):
        p = biblioteca_vazia.criar_prateleira("fantasia")
        assert isinstance(p, Prateleira)
        assert p.genero == "Fantasia"
        assert biblioteca_vazia.listar_prateleiras() == ["Fantasia"]

    def test_criar_prateleira_duplicada_levanta_erro(self, biblioteca_vazia):
        biblioteca_vazia.criar_prateleira("Fantasia")
        with pytest.raises(ValueError, match="já existe"):
            biblioteca_vazia.criar_prateleira("fantasia")

    def test_obter_prateleira_existente_e_inexistente(self, biblioteca_vazia):
        biblioteca_vazia.criar_prateleira("Fantasia")
        assert biblioteca_vazia.obter_prateleira("fantasia") is not None
        assert biblioteca_vazia.obter_prateleira("terror") is None

    def test_remover_prateleira_vazia_com_sucesso(self, biblioteca_vazia):
        biblioteca_vazia.criar_prateleira("Terror")
        removido = biblioteca_vazia.remover_prateleira("terror")
        assert removido is True
        assert biblioteca_vazia.listar_prateleiras() == []

    def test_remover_prateleira_inexistente(self, biblioteca_vazia):
        removido = biblioteca_vazia.remover_prateleira("Não Existe")
        assert removido is False

    def test_remover_prateleira_com_livros_levanta_erro(self, biblioteca_vazia):
        livro = Livro("1", "Drácula", "Bram Stoker", 1897, "Terror")
        biblioteca_vazia.adicionar_livro(livro)
        with pytest.raises(ValueError, match="não está vazia"):
            biblioteca_vazia.remover_prateleira("Terror")


class TestBibliotecaOperacoesLivros:
    def test_adicionar_livro_cria_prateleira_automaticamente(self, biblioteca_vazia):
        livro = Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica")
        biblioteca_vazia.adicionar_livro(livro)

        assert "Ficção Científica" in biblioteca_vazia.listar_prateleiras()
        assert len(biblioteca_vazia) == 1
        assert biblioteca_vazia.listar() == [livro]

    def test_remover_livro_todos_exemplares(self, biblioteca_povoada):
        qtd, removidos = biblioteca_povoada.remover_livro("Duna")
        assert qtd == 2
        assert len(removidos) == 2
        assert len(biblioteca_povoada.buscar("Duna", "titulo")) == 0

    def test_remover_livro_com_quantidade_limitada(self, biblioteca_povoada):
        qtd, removidos = biblioteca_povoada.remover_livro("Duna", quantidade=1)
        assert qtd == 1
        assert len(removidos) == 1
        assert len(biblioteca_povoada.buscar("Duna", "titulo")) == 1

    def test_remover_livro_com_quantidade_atingida_interrompe_iteracao(self):
        b = Biblioteca()
        b.adicionar_livro(Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica"))
        b.adicionar_livro(Livro("2", "Duna", "Frank Herbert", 1965, "Fantasia"))
        qtd, removidos = b.remover_livro("Duna", quantidade=1)
        assert qtd == 1
        assert len(removidos) == 1
        assert len(b) == 1

    def test_remover_livro_inexistente(self, biblioteca_povoada):
        qtd, removidos = biblioteca_povoada.remover_livro("Livro Inexistente")
        assert qtd == 0
        assert removidos == []

    def test_buscar_em_todas_as_prateleiras(self, biblioteca_povoada):
        resultados_autor = biblioteca_povoada.buscar("tolkien", "autor")
        assert len(resultados_autor) == 2

        resultados_titulo = biblioteca_povoada.buscar("duna", "titulo")
        assert len(resultados_titulo) == 2

        resultados_ano = biblioteca_povoada.buscar(1965, "ano")
        assert len(resultados_ano) == 2


class TestBibliotecaRepresentacaoEPersistencia:
    def test_str_biblioteca_vazia(self, biblioteca_vazia):
        assert str(biblioteca_vazia) == "Biblioteca vazia"

    def test_str_biblioteca_povoada(self, biblioteca_povoada):
        texto = str(biblioteca_povoada)
        assert "Biblioteca — 4 exemplares em 2 prateleiras:" in texto
        assert "- Fantasia: 2 exemplares" in texto
        assert "- Ficção Científica: 2 exemplares" in texto

    def test_repr(self, biblioteca_povoada):
        assert repr(biblioteca_povoada) == "Biblioteca(prateleiras=2, exemplares=4)"

    def test_to_dict_e_from_dict(self, biblioteca_povoada):
        dados = biblioteca_povoada.to_dict()
        assert dados["version"] == 1
        assert len(dados["prateleiras"]) == 2

        restaurada = Biblioteca.from_dict(dados)
        assert len(restaurada) == len(biblioteca_povoada)
        assert set(restaurada.listar_prateleiras()) == set(biblioteca_povoada.listar_prateleiras())

    def test_from_dict_versao_incompativel_levanta_erro(self):
        dados_invalidos = {"version": 999, "prateleiras": []}
        with pytest.raises(RuntimeError, match="Versão de schema incompatível"):
            Biblioteca.from_dict(dados_invalidos)
