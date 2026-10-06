# tests/test_prateleira.py
import pytest
from models.livro import Livro
from models.prateleira import Prateleira


@pytest.fixture
def prateleira_fantasia():
    return Prateleira("fantasia")


@pytest.fixture
def livro_hobbit():
    return Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")


@pytest.fixture
def livro_senhor():
    return Livro("2", "O Senhor dos Anéis", "J. R. R. Tolkien", 1954, "Fantasia")


class TestPrateleiraCriacaoEAdicao:
    def test_criacao_normaliza_genero(self, prateleira_fantasia):
        assert prateleira_fantasia.genero == "Fantasia"
        assert len(prateleira_fantasia) == 0
        assert prateleira_fantasia.listar() == []

    def test_adicionar_livro_com_mesmo_genero(self, prateleira_fantasia, livro_hobbit):
        prateleira_fantasia.adicionar(livro_hobbit)
        assert len(prateleira_fantasia) == 1
        assert livro_hobbit in prateleira_fantasia.listar()

    def test_adicionar_multiplos_exemplares(self, prateleira_fantasia, livro_hobbit):
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_hobbit)
        assert len(prateleira_fantasia) == 2

    def test_adicionar_genero_divergente_levanta_erro(self, prateleira_fantasia):
        livro_ficcao = Livro("3", "Duna", "Frank Herbert", 1965, "Ficção Científica")
        with pytest.raises(ValueError, match="não pertence à prateleira"):
            prateleira_fantasia.adicionar(livro_ficcao)


class TestPrateleiraRemocao:
    def test_remover_por_titulo_todos(self, prateleira_fantasia, livro_hobbit, livro_senhor):
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_senhor)

        qtd, removidos = prateleira_fantasia.remover_por_titulo("o hobbit")
        assert qtd == 2
        assert len(removidos) == 2
        assert len(prateleira_fantasia) == 1
        assert prateleira_fantasia.listar() == [livro_senhor]

    def test_remover_por_titulo_com_quantidade_esvaziando_chave(self, prateleira_fantasia, livro_hobbit):
        prateleira_fantasia.adicionar(livro_hobbit)
        qtd, removidos = prateleira_fantasia.remover_por_titulo("O Hobbit", quantidade=1)
        assert qtd == 1
        assert len(removidos) == 1
        assert len(prateleira_fantasia) == 0

    def test_remover_por_titulo_com_quantidade_multiplas_obras(self, prateleira_fantasia):
        # Duas obras diferentes (IDs diferentes), mas com mesmo título
        l1 = Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")
        l2 = Livro("2", "O Hobbit", "Outro Autor", 1980, "Fantasia")
        prateleira_fantasia.adicionar(l1)
        prateleira_fantasia.adicionar(l2)

        qtd, removidos = prateleira_fantasia.remover_por_titulo("O Hobbit", quantidade=1)
        assert qtd == 1
        assert len(removidos) == 1
        assert len(prateleira_fantasia) == 1

    def test_remover_por_titulo_com_quantidade(self, prateleira_fantasia, livro_hobbit):
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_hobbit)

        qtd, removidos = prateleira_fantasia.remover_por_titulo("O Hobbit", quantidade=2)
        assert qtd == 2
        assert len(removidos) == 2
        assert len(prateleira_fantasia) == 1

    def test_remover_por_titulo_inexistente(self, prateleira_fantasia, livro_hobbit):
        prateleira_fantasia.adicionar(livro_hobbit)
        qtd, removidos = prateleira_fantasia.remover_por_titulo("Silmarillion")
        assert qtd == 0
        assert removidos == []
        assert len(prateleira_fantasia) == 1

    def test_remover_exemplar_especifico(self, prateleira_fantasia, livro_hobbit, livro_senhor):
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_senhor)

        sucesso = prateleira_fantasia.remover_exemplar(livro_hobbit)
        assert sucesso is True
        assert len(prateleira_fantasia) == 1
        assert livro_hobbit not in prateleira_fantasia.listar()

    def test_remover_exemplar_inexistente(self, prateleira_fantasia, livro_hobbit, livro_senhor):
        prateleira_fantasia.adicionar(livro_senhor)
        sucesso = prateleira_fantasia.remover_exemplar(livro_hobbit)
        assert sucesso is False
        assert len(prateleira_fantasia) == 1

    def test_remover_exemplar_chave_existe_mas_livro_nao(self, prateleira_fantasia, livro_hobbit):
        class LivroDiferente(Livro):
            def __eq__(self, other):
                return False

        livro_sub = LivroDiferente("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")
        prateleira_fantasia.adicionar(livro_hobbit)
        assert prateleira_fantasia.remover_exemplar(livro_sub) is False


class TestPrateleiraBusca:
    def test_buscar_campo_invalido_levanta_erro(self, prateleira_fantasia):
        with pytest.raises(ValueError, match="Campo inválido"):
            prateleira_fantasia.buscar("termo", "editora")

    def test_buscar_por_autor_parcial(self, prateleira_fantasia, livro_hobbit, livro_senhor):
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_senhor)

        encontrados = prateleira_fantasia.buscar("tolkien", "autor")
        assert len(encontrados) == 2

        encontrados_vazio = prateleira_fantasia.buscar("asimov", "autor")
        assert encontrados_vazio == []

    def test_buscar_por_titulo_parcial(self, prateleira_fantasia, livro_hobbit, livro_senhor):
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_senhor)

        encontrados = prateleira_fantasia.buscar("hobbit", "titulo")
        assert len(encontrados) == 1
        assert encontrados[0] == livro_hobbit

    def test_buscar_por_id(self, prateleira_fantasia, livro_hobbit, livro_senhor):
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_senhor)

        encontrados = prateleira_fantasia.buscar("1", "id")
        assert len(encontrados) == 1
        assert encontrados[0] == livro_hobbit

    def test_buscar_por_ano_int_e_string(self, prateleira_fantasia, livro_hobbit):
        prateleira_fantasia.adicionar(livro_hobbit)

        assert len(prateleira_fantasia.buscar(1937, "ano")) == 1
        assert len(prateleira_fantasia.buscar("1937", "ano")) == 1
        assert len(prateleira_fantasia.buscar("1937 dc", "ano")) == 1
        assert len(prateleira_fantasia.buscar(2000, "ano")) == 0

    def test_normalizar_ano_casos_borda(self):
        assert Prateleira._normalizar_ano(1954) == "1954 DC"
        assert Prateleira._normalizar_ano(-380) == "380 AC"
        assert Prateleira._normalizar_ano("380 ac") == "380 AC"
        assert Prateleira._normalizar_ano("1954 dc") == "1954 DC"

        with pytest.raises(ValueError, match="Ano 0 não existe"):
            Prateleira._normalizar_ano(0)

        with pytest.raises(ValueError, match="Ano 0 não existe"):
            Prateleira._normalizar_ano("0")

        with pytest.raises(ValueError, match="Formato de ano inválido"):
            Prateleira._normalizar_ano("invalido")


class TestPrateleiraRepresentacaoEPersistencia:
    def test_str_singular_e_plural(self, prateleira_fantasia, livro_hobbit):
        assert str(prateleira_fantasia) == "Prateleira de Fantasia (0 exemplares)"

        prateleira_fantasia.adicionar(livro_hobbit)
        assert str(prateleira_fantasia) == "Prateleira de Fantasia (1 exemplar)"

        prateleira_fantasia.adicionar(livro_hobbit)
        assert str(prateleira_fantasia) == "Prateleira de Fantasia (2 exemplares)"

    def test_repr(self, prateleira_fantasia, livro_hobbit):
        prateleira_fantasia.adicionar(livro_hobbit)
        assert repr(prateleira_fantasia) == "Prateleira(genero='Fantasia', exemplares=1, obras=1)"

    def test_to_dict_e_from_dict(self, prateleira_fantasia, livro_hobbit, livro_senhor):
        prateleira_fantasia.adicionar(livro_hobbit)
        prateleira_fantasia.adicionar(livro_senhor)

        dados = prateleira_fantasia.to_dict()
        assert dados["genero"] == "Fantasia"
        assert len(dados["livros"]) == 2

        reconstruida = Prateleira.from_dict(dados)
        assert reconstruida.genero == prateleira_fantasia.genero
        assert len(reconstruida) == 2
        assert len(reconstruida.buscar("hobbit", "titulo")) == 1
        assert len(reconstruida.buscar("senhor", "titulo")) == 1
