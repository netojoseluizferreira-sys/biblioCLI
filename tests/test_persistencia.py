# tests/test_persistencia.py
import json
from pathlib import Path
from unittest.mock import patch
import pytest

from models.livro import Livro
from models.biblioteca import Biblioteca
from utils.persistencia import salvar, carregar, CAMINHO_PADRAO


@pytest.fixture
def biblioteca_amostra():
    b = Biblioteca()
    b.adicionar_livro(Livro("1", "Duna", "Frank Herbert", 1965, "Ficção Científica"))
    b.adicionar_livro(Livro("2", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"))
    return b


class TestPersistencia:
    def test_caminho_padrao_definido(self):
        assert isinstance(CAMINHO_PADRAO, Path)
        assert CAMINHO_PADRAO.name == "library.json"

    def test_carregar_arquivo_inexistente_retorna_biblioteca_vazia(self, tmp_path):
        arquivo = tmp_path / "nao_existe.json"
        b = carregar(arquivo)
        assert isinstance(b, Biblioteca)
        assert len(b) == 0

    def test_salvar_cria_diretorios_e_arquivo_com_sucesso(self, tmp_path, biblioteca_amostra):
        arquivo = tmp_path / "subpasta" / "biblioteca.json"
        salvar(biblioteca_amostra, arquivo)

        assert arquivo.exists()
        conteudo = arquivo.read_text(encoding="utf-8")
        dados = json.loads(conteudo)
        assert dados["version"] == 1
        assert len(dados["prateleiras"]) == 2

    def test_salvar_e_carregar_roundtrip(self, tmp_path, biblioteca_amostra):
        arquivo = tmp_path / "test_lib.json"
        salvar(biblioteca_amostra, arquivo)

        carregada = carregar(arquivo)
        assert len(carregada) == len(biblioteca_amostra)
        assert len(carregada.buscar("Frank Herbert", "autor")) == 1
        assert len(carregada.buscar("Tolkien", "autor")) == 1

    def test_salvar_caracteres_acentuados(self, tmp_path):
        b = Biblioteca()
        b.adicionar_livro(Livro("1", "Memórias Póstumas de Brás Cubas", "Machado de Assis", 1881, "Ficção"))
        arquivo = tmp_path / "acentos.json"
        salvar(b, arquivo)

        conteudo = arquivo.read_text(encoding="utf-8")
        assert "Memórias Póstumas" in conteudo

        carregada = carregar(arquivo)
        livros = carregada.buscar("Brás Cubas", "titulo")
        assert len(livros) == 1

    def test_carregar_arquivo_corrompido_levanta_value_error(self, tmp_path):
        arquivo = tmp_path / "corrompido.json"
        arquivo.write_text("{ json invalido: sem fechar ", encoding="utf-8")

        with pytest.raises(ValueError, match="Arquivo de dados corrompido"):
            carregar(arquivo)

    def test_carregar_os_error_levanta_os_error(self, tmp_path):
        arquivo = tmp_path / "existente.json"
        arquivo.write_text("{}", encoding="utf-8")

        with patch("builtins.open", side_effect=OSError("Permissão negada")):
            with pytest.raises(OSError, match="Erro ao ler"):
                carregar(arquivo)

    def test_carregar_schema_incompativel_levanta_runtime_error(self, tmp_path):
        arquivo = tmp_path / "schema_antigo.json"
        arquivo.write_text(json.dumps({"version": 99, "prateleiras": []}), encoding="utf-8")

        with pytest.raises(RuntimeError, match="Versão de schema incompatível"):
            carregar(arquivo)

    def test_salvar_falha_na_escrita_limpa_temporario(self, tmp_path, biblioteca_amostra):
        arquivo = tmp_path / "arquivo_falha.json"

        with patch("json.dump", side_effect=IOError("Erro simulado de I/O")):
            with pytest.raises(RuntimeError, match="Erro ao salvar biblioteca"):
                salvar(biblioteca_amostra, arquivo)

        tmp_esperado = arquivo.with_name(arquivo.name + ".tmp")
        assert not tmp_esperado.exists()
        assert not arquivo.exists()
