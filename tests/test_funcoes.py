# tests/test_funcoes.py
from utils.funcoes import (
    pedir_input,
    pedir_int,
    confirmar,
    imprimir_secao,
    imprimir_lista_livros,
    mostrar_ajuda,
    parse_comando,
)
from models.livro import Livro


class TestParseComando:
    def test_comando_simples(self):
        cmd, args = parse_comando("list")
        assert cmd == "list"
        assert args == []

    def test_comando_com_argumentos(self):
        cmd, args = parse_comando("add Duna 1965")
        assert cmd == "add"
        assert args == ["Duna", "1965"]

    def test_comando_com_espacos_extras_e_maiusculas(self):
        cmd, args = parse_comando("   SEARCH   autor   tolkien   ")
        assert cmd == "search"
        assert args == ["autor", "tolkien"]

    def test_linha_vazia(self):
        cmd, args = parse_comando("")
        assert cmd == ""
        assert args == []

        cmd2, args2 = parse_comando("     ")
        assert cmd2 == ""
        assert args2 == []


class TestPedirInputEConfirmar:
    def test_pedir_input(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "   resposta teste   ")
        assert pedir_input("Digite algo: ") == "resposta teste"

    def test_confirmar_sim(self, monkeypatch):
        for resposta in ["s", "sim", "SIM", "Sim", "yes", "só"]:
            monkeypatch.setattr("builtins.input", lambda prompt, r=resposta: r)
            if resposta == "yes":
                # 'yes' doesn't start with 's'
                assert confirmar("Deseja continuar?") is False
            else:
                assert confirmar("Deseja continuar?") is True

    def test_confirmar_nao(self, monkeypatch):
        for resposta in ["n", "nao", "não", "no", "anything"]:
            monkeypatch.setattr("builtins.input", lambda prompt, r=resposta: r)
            assert confirmar("Deseja continuar?") is False


class TestPedirInt:
    def test_pedir_int_direto(self, monkeypatch):
        monkeypatch.setattr("builtins.input", lambda prompt: "42")
        assert pedir_int("Digite um número: ") == 42

    def test_pedir_int_com_retry_invalido_e_minimo_maximo(self, monkeypatch, capsys):
        entradas = iter(["abc", "-5", "150", "50"])
        monkeypatch.setattr("builtins.input", lambda prompt: next(entradas))

        resultado = pedir_int("Digite:", minimo=0, maximo=100)
        assert resultado == 50

        saida = capsys.readouterr().out
        assert "Por favor, insira um número inteiro válido." in saida
        assert "O valor deve ser maior ou igual a 0." in saida
        assert "O valor deve ser menor ou igual a 100." in saida


class TestFuncoesImpressao:
    def test_imprimir_secao(self, capsys):
        imprimir_secao("Minha Seção")
        saida = capsys.readouterr().out
        assert "Minha Seção" in saida
        assert "=" * 50 in saida

    def test_imprimir_lista_livros_vazia(self, capsys):
        imprimir_lista_livros([])
        saida = capsys.readouterr().out
        assert "(nenhum livro)" in saida

    def test_imprimir_lista_livros_com_itens(self, capsys):
        livros = [
            Livro("1", "Duna", "Frank Herbert", 1965, "Ficção"),
            Livro("2", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"),
        ]
        imprimir_lista_livros(livros)
        saida = capsys.readouterr().out
        assert "ID: 1 | Título: Duna | Autor: Frank Herbert | Ano: 1965 DC" in saida
        assert "ID: 2 | Título: O Hobbit | Autor: J. R. R. Tolkien | Ano: 1937 DC" in saida

    def test_mostrar_ajuda(self, capsys):
        comandos = {"add": "Adiciona", "list": "Lista"}
        mostrar_ajuda(comandos)
        saida = capsys.readouterr().out
        assert "Comandos disponíveis:" in saida
        assert "add" in saida
        assert "Adiciona" in saida
