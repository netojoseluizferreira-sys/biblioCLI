# tests/test_livro.py
import pytest
from datetime import datetime
from models.livro import Livro


class TestLivroCriacaoEAtributos:
    def test_criacao_com_sucesso(self):
        livro = Livro("1", "o senhor dos anéis", "j. r. r. tolkien", 1954, "fantasia")
        assert livro.id == "1"
        assert livro.titulo == "O Senhor Dos Anéis"
        assert livro.autor == "J. R. R. Tolkien"
        assert livro.ano == "1954 DC"
        assert livro.genero == "Fantasia"

    def test_id_imutavel(self):
        livro = Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica")
        with pytest.raises(AttributeError):
            livro.id = "2"

    def test_id_vazio_ou_em_branco_levanta_erro(self):
        with pytest.raises(ValueError, match="ID não pode ser vazio"):
            Livro("", "Duna", "Frank Herbert", 1965, "Ficção Científica")

        with pytest.raises(ValueError, match="ID não pode ser vazio"):
            Livro("   ", "Duna", "Frank Herbert", 1965, "Ficção Científica")

    def test_id_com_espacos_eh_normalizado(self):
        livro = Livro("  42  ", "Duna", "Frank Herbert", 1965, "Ficção Científica")
        assert livro.id == "42"


class TestLivroValidacaoEModificacao:
    def test_titulo_setter_normalizacao_e_validacao(self):
        livro = Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica")
        livro.titulo = "messias de duna"
        assert livro.titulo == "Messias De Duna"

        with pytest.raises(ValueError, match="Título não pode ser vazio"):
            livro.titulo = ""
        with pytest.raises(ValueError, match="Título não pode ser vazio"):
            livro.titulo = "   "

    def test_autor_setter_normalizacao_e_validacao(self):
        livro = Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica")
        livro.autor = "brian herbert"
        assert livro.autor == "Brian Herbert"

        with pytest.raises(ValueError, match="Autor não pode ser vazio"):
            livro.autor = ""
        with pytest.raises(ValueError, match="Autor não pode ser vazio"):
            livro.autor = "   "

    def test_genero_setter_normalizacao_e_validacao(self):
        livro = Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica")
        livro.genero = "space opera"
        assert livro.genero == "Space Opera"

        with pytest.raises(ValueError, match="Gênero não pode ser vazio"):
            livro.genero = ""
        with pytest.raises(ValueError, match="Gênero não pode ser vazio"):
            livro.genero = "   "


class TestLivroAno:
    def test_ano_int_positivo(self):
        livro = Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica")
        assert livro.ano == "1965 DC"

    def test_ano_int_negativo_ac(self):
        livro = Livro("2", "A República", "Platão", -380, "Filosofia")
        assert livro.ano == "380 AC"

    def test_ano_zero_invalido(self):
        with pytest.raises(ValueError, match="Ano 0 não existe"):
            Livro("1", "Teste", "Autor", 0, "Gênero")

        with pytest.raises(ValueError, match="Ano 0 não existe"):
            Livro("1", "Teste", "Autor", "0", "Gênero")

        with pytest.raises(ValueError, match="Ano 0 não existe"):
            Livro("1", "Teste", "Autor", "0 DC", "Gênero")

    def test_ano_string_com_ou_sem_era(self):
        l1 = Livro("1", "Duna", "Frank Herbert", "1965", "Ficção Científica")
        assert l1.ano == "1965 DC"

        l2 = Livro("1", "Duna", "Frank Herbert", "1965 dc", "Ficção Científica")
        assert l2.ano == "1965 DC"

        l3 = Livro("2", "Poética", "Aristóteles", "335 AC", "Filosofia")
        assert l3.ano == "335 AC"

    def test_ano_formato_invalido(self):
        with pytest.raises(ValueError, match="Formato de ano inválido"):
            Livro("1", "Teste", "Autor", "ano 2000", "Gênero")

        with pytest.raises(ValueError, match="Formato de ano inválido"):
            Livro("1", "Teste", "Autor", "abc", "Gênero")

    def test_ano_dc_no_futuro_invalido(self):
        ano_futuro = datetime.now().year + 1
        with pytest.raises(ValueError, match="Ano não pode ser maior"):
            Livro("1", "Teste", "Autor", ano_futuro, "Gênero")

        with pytest.raises(ValueError, match="Ano não pode ser maior"):
            Livro("1", "Teste", "Autor", f"{ano_futuro} DC", "Gênero")

    def test_ano_ac_remoto_valido(self):
        livro = Livro("1", "Epopeia de Gilgamesh", "Desconhecido", "2100 AC", "Mitologia")
        assert livro.ano == "2100 AC"


class TestLivroComparacaoEHash:
    def test_mesma_obra(self):
        l1 = Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")
        l2 = Livro("1", "O Hobbit - Edição Especial", "J. R. R. Tolkien", 2001, "Fantasia")
        l3 = Livro("2", "O Senhor dos Anéis", "J. R. R. Tolkien", 1954, "Fantasia")

        assert l1.mesma_obra(l2) is True
        assert l1.mesma_obra(l3) is False
        assert l1.mesma_obra("1") is False

    def test_igualdade(self):
        l1 = Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")
        l2 = Livro("1", "O Hobbit", "Tolkien", 1999, "Fantasia")
        l3 = Livro("1", "O Hobbit Edição 2", "J. R. R. Tolkien", 1937, "Fantasia")

        assert l1 == l2
        assert l1 != l3
        assert (l1 == "não é livro") is False

    def test_hash_consistente(self):
        l1 = Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")
        l2 = Livro("1", "O Hobbit", "Tolkien", 1999, "Fantasia")
        l3 = Livro("2", "Duna", "Frank Herbert", 1965, "Ficção Científica")

        assert hash(l1) == hash(l2)
        conjunto = {l1, l2, l3}
        assert len(conjunto) == 2


class TestLivroRepresentacaoEPersistencia:
    def test_str(self):
        livro = Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")
        assert str(livro) == "O Hobbit — J. R. R. Tolkien (1937 DC) [Fantasia]"

    def test_repr(self):
        livro = Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")
        esperado = "Livro(id='1', titulo='O Hobbit', autor='J. R. R. Tolkien', ano='1937 DC', genero='Fantasia')"
        assert repr(livro) == esperado

    def test_to_dict_e_from_dict(self):
        livro = Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia")
        dados = livro.to_dict()

        assert dados == {
            "id": "1",
            "titulo": "O Hobbit",
            "autor": "J. R. R. Tolkien",
            "ano": "1937 DC",
            "genero": "Fantasia",
        }

        reconstruido = Livro.from_dict(dados)
        assert reconstruido == livro
        assert reconstruido.autor == livro.autor
        assert reconstruido.ano == livro.ano
        assert reconstruido.genero == livro.genero
