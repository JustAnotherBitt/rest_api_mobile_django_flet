import flet as ft
import requests
from connect import get_livros
from urllib.parse import parse_qs, urlparse

def main(page: ft.Page):
    page.title = "Cadastro App"
    page.window.width = 400

    def home_page():
        # Declarando como variáveis globais
        global nome_input, streaming_select, cadastrar_btn, lista_livros

        nome_input = ft.TextField(label="Nome do Produto", text_align=ft.TextAlign.LEFT)
        streaming_select = ft.Dropdown(
            options=[
                ft.dropdown.Option("K", text="Kindle"),
                ft.dropdown.Option("F", text="Físico"),
            ],
            label="Selecione o streaming"
        )

        lista_livros = ft.ListView()

        def carregar_livros():
            lista_livros.controls.clear()
            for i in get_livros():
                lista_livros.controls.append(
                    ft.Container(
                        ft.Text(i['nome']),
                        bgcolor=ft.colors.BLACK12,
                        padding=15,
                        alignment=ft.alignment.center,
                        margin=3,
                        border_radius=10,
                        on_click=lambda e, livro_id=i['id']: page.go(f'/review?id={livro_id}')
                    )
                )
            page.update()  # Atualiza a página

        def cadastrar(e):  # Faz uma requisição de dados ao backend
            data = {
                'nome': nome_input.value,
                'streaming': streaming_select.value,
                'categorias': []  # TODO: desenvolver as categorias
            }
            response = requests.post('http://127.0.0.1:8000/api/livros/', json=data)
            if response.status_code == 201:  # Verifica se o livro foi criado com sucesso
                id_novo_livro = response.json().get("id")  # Obtém o ID do livro recém-adicionado
                page.go(f'/review?id={id_novo_livro}')  # Redireciona para a página de review
            carregar_livros()

        cadastrar_btn = ft.ElevatedButton("Cadastrar", on_click=cadastrar)

        carregar_livros()  # Carrega os livros ao iniciar a página

        page.views.append(
            ft.View(
                "/",
                controls=[
                    nome_input,
                    streaming_select,
                    cadastrar_btn,
                    lista_livros
                ]
            )
        )

    def review_page(livro_id):
        nota_input = ft.TextField(label="Nota (inteiro)", text_align=ft.TextAlign.LEFT, value=0, width=100)
        comentario_input = ft.TextField(label="Comentário", multiline=True, expand=True)

        def avaliar(e):
            data = {
                'nota': int(nota_input.value),
                'comentarios': comentario_input.value
            }

            try:
                response = requests.put(f'http://127.0.0.1:8000/api/livros/{livro_id}', json=data)
                if response.status_code == 200:
                    page.snack_bar = ft.SnackBar(ft.Text("Avaliação enviada com sucesso!"))
                    page.snack_bar.open = True
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("Erro ao enviar a avaliação."))
                    page.snack_bar.open = True
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"Erro de conexão: {ex}"))
                page.snack_bar.open = True
            page.update()

        avaliar_btn = ft.ElevatedButton("Avaliar", on_click=avaliar)
        voltar_btn = ft.ElevatedButton("Voltar", on_click=lambda _: page.go('/'))
        page.views.append(
            ft.View(
                "/review",
                controls=[
                    nota_input,
                    comentario_input,
                    avaliar_btn,
                    voltar_btn
                ]
            )
        )

    def avaliar(livro_id, nota, comentario):
        # Implementa a lógica para enviar a avaliação
        print(f"Livro ID: {livro_id}, Nota: {nota}, Comentário: {comentario}")

    def route_change(e):  # e = event
        page.views.clear()  # Limpa as visualizações antes de adicionar novas
        if page.route == '/':
            home_page()
        elif page.route.startswith('/review'):
            parsed_url = urlparse(page.route)
            query_params = parse_qs(parsed_url.query)
            livro_id = query_params.get('id', [None])[0]
            review_page(livro_id)

        page.update()  # Atualiza a página para refletir mudanças na rota

    page.on_route_change = route_change
    page.go('/')  # Navega para a rota inicial

ft.app(target=main)
