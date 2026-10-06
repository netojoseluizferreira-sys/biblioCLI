# tests/test_main.py
from unittest.mock import patch
from models.biblioteca import Biblioteca
from models.livro import Livro
from main import cmd_add, cmd_rm, cmd_list, cmd_shelves, cmd_search


class TestComandosCLI:
    def test_cmd_add_sucesso(self, capsys):
        b = Biblioteca()
        entradas = iter(["1", "Duna", "Frank Herbert", "1965", "Ficção Científica"])
        with patch("builtins.input", lambda prompt: next(entradas)):
            cmd_add(b)

        saida = capsys.readouterr().out
        assert "Livro 'Duna' adicionado." in saida
        assert len(b) == 1
        assert b.listar()[0].titulo == "Duna"

    def test_cmd_add_valor_invalido(self, capsys):
        b = Biblioteca()
        entradas = iter(["", "Duna", "Frank Herbert", "1965", "Ficção"])  # ID vazio
        with patch("builtins.input", lambda prompt: next(entradas)):
            cmd_add(b)

        saida = capsys.readouterr().out
        assert "Erro ao criar livro:" in saida
        assert len(b) == 0

    def test_cmd_rm_sem_args(self, capsys):
        b = Biblioteca()
        cmd_rm(b, [])
        saida = capsys.readouterr().out
        assert "Uso: rm <titulo>" in saida

    def test_cmd_rm_livro_inexistente(self, capsys):
        b = Biblioteca()
        cmd_rm(b, ["Livro", "Fantasma"])
        saida = capsys.readouterr().out
        assert "Nenhum livro com título 'Livro Fantasma'." in saida

    def test_cmd_rm_sucesso(self, capsys):
        b = Biblioteca()
        b.adicionar_livro(Livro("1", "Duna", "Frank Herbert", 1965, "Ficção"))
        cmd_rm(b, ["Duna"])
        saida = capsys.readouterr().out
        assert "1 exemplar removido(s)." in saida
        assert len(b) == 0

    def test_cmd_list_todos(self, capsys):
        b = Biblioteca()
        b.adicionar_livro(Livro("1", "Duna", "Frank Herbert", 1965, "Ficção"))
        cmd_list(b, [])
        saida = capsys.readouterr().out
        assert "Todos os livros:" in saida
        assert "Duna" in saida

    def test_cmd_list_genero_existente_e_inexistente(self, capsys):
        b = Biblioteca()
        b.adicionar_livro(Livro("1", "Duna", "Frank Herbert", 1965, "Ficção"))

        cmd_list(b, ["Ficção"])
        saida = capsys.readouterr().out
        assert "Livros do gênero 'Ficção':" in saida
        assert "Duna" in saida

        cmd_list(b, ["Fantasia"])
        saida_inexistente = capsys.readouterr().out
        assert "Prateleira 'Fantasia' não existe." in saida_inexistente

    def test_cmd_shelves_vazia_e_com_prateleiras(self, capsys):
        b = Biblioteca()
        cmd_shelves(b)
        assert "(nenhuma prateleira)" in capsys.readouterr().out

        b.adicionar_livro(Livro("1", "Duna", "Frank Herbert", 1965, "Ficção"))
        b.adicionar_livro(Livro("2", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"))
        cmd_shelves(b)
        saida = capsys.readouterr().out
        assert "- Fantasia" in saida
        assert "- Ficção" in saida

    def test_cmd_search_validacoes(self, capsys):
        b = Biblioteca()
        # Sem argumentos suficientes
        cmd_search(b, ["autor"])
        assert "Uso: search <campo> <valor>" in capsys.readouterr().out

        # Campo inválido
        cmd_search(b, ["editora", "intrinseca"])
        saida = capsys.readouterr().out
        assert "Campo inválido: 'editora'" in saida

    def test_cmd_search_ano_invalido(self, capsys):
        b = Biblioteca()
        b.criar_prateleira("Fantasia")
        cmd_search(b, ["ano", "ano-invalido"])
        assert "Erro na busca:" in capsys.readouterr().out

    def test_cmd_search_sucesso(self, capsys):
        b = Biblioteca()
        b.adicionar_livro(Livro("1", "O Hobbit", "J. R. R. Tolkien", 1937, "Fantasia"))
        cmd_search(b, ["autor", "tolkien"])
        saida = capsys.readouterr().out
        assert "Resultados para autor = 'tolkien'" in saida
        assert "O Hobbit" in saida


class TestMainLoop:
    def test_main_fluxo_basico(self, capsys):
        from main import main

        entradas = iter(["", "help", "comando_desconhecido", "list", "shelves", "exit"])
        with patch("main.carregar", return_value=Biblioteca()), \
             patch("main.salvar") as mock_salvar, \
             patch("builtins.input", lambda prompt: next(entradas)):
            main()

        saida = capsys.readouterr().out
        assert "Bem-vindo ao biblioCLI!" in saida
        assert "Comandos disponíveis:" in saida
        assert "Comando desconhecido: 'comando_desconhecido'" in saida
        assert "Salvando e saindo. Até logo!" in saida
        assert "Biblioteca salva." in saida
        assert mock_salvar.called

    def test_main_com_add_e_rm(self, capsys):
        from main import main

        entradas = iter([
            "add", "1", "Duna", "Frank Herbert", "1965", "Ficção",
            "search autor herbert",
            "rm Duna",
            "quit"
        ])
        with patch("main.carregar", return_value=Biblioteca()), \
             patch("main.salvar") as mock_salvar, \
             patch("builtins.input", lambda prompt: next(entradas)):
            main()

        saida = capsys.readouterr().out
        assert "Livro 'Duna' adicionado." in saida
        assert "Resultados para autor = 'herbert'" in saida
        assert "1 exemplar removido(s)." in saida
        assert mock_salvar.call_count >= 3

    def test_main_interrompido_por_teclado(self, capsys):
        from main import main

        with patch("main.carregar", return_value=Biblioteca()), \
             patch("main.salvar"), \
             patch("builtins.input", side_effect=KeyboardInterrupt):
            main()

        saida = capsys.readouterr().out
        assert "Interrompido pelo usuário." in saida
        assert "Biblioteca salva." in saida

    def test_main_erro_ao_salvar_no_finally(self, capsys):
        from main import main

        with patch("main.carregar", return_value=Biblioteca()), \
             patch("main.salvar", side_effect=Exception("Disco cheio")), \
             patch("builtins.input", return_value="exit"):
            main()

        saida = capsys.readouterr().out
        assert "ERRO ao salvar: Disco cheio" in saida
