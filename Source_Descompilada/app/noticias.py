import re
import feedparser
import mimetypes
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView


def is_formato_suportado(url):
    mime, _ = mimetypes.guess_type(url)
    return mime and mime.startswith("image/") and not mime.endswith("webp") and not mime.endswith("avif")


class JanelaNoticias(QDialog):
    def __init__(self, pai=None):
        super().__init__(pai)
        self.setWindowTitle("Notícias do G1")
        self.resize(980, 720)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Botão de fechar
        botao_container = QWidget()
        botao_layout = QHBoxLayout(botao_container)
        botao_layout.setContentsMargins(12, 12, 12, 12)
        botao_layout.setAlignment(Qt.AlignRight)

        botao_fechar = QPushButton("✖ Fechar")
        botao_fechar.setFixedHeight(30)
        botao_fechar.setStyleSheet("""
            QPushButton {
                background-color: rgba(211, 47, 47, 0.85);
                color: white;
                border: none;
                padding: 4px 12px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: rgba(165, 39, 39, 1);
            }
        """)
        botao_fechar.clicked.connect(self.close)
        botao_layout.addWidget(botao_fechar)
        layout.addWidget(botao_container)

        # WebEngine
        self.visualizador_web = QWebEngineView()
        layout.addWidget(self.visualizador_web, 1)

        self.carregar_noticias()

    def carregar_noticias(self):
        url_rss = "https://g1.globo.com/rss/g1/"
        feed = feedparser.parse(url_rss)

        if feed.bozo:
            self.visualizador_web.setHtml("""
                <h2 style='color: #b71c1c; font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; text-align:center; margin-top: 40px;'>
                    Erro ao carregar notícias do G1.
                </h2>
            """)
            return

        html = """
        <!DOCTYPE html>
        <html lang="pt-BR">
        <head>
            <meta charset="UTF-8" />
            <title>Notícias do G1</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
                body {
                    font-family: 'Roboto', Arial, sans-serif;
                    background-color: #fff;
                    margin: 0;
                    padding: 32px 48px;
                    color: #222;
                }
                article {
                    max-width: 820px;
                    margin: 0 auto 48px auto;
                    border-radius: 22px;
                    overflow: hidden;
                    background-color: #fff;
                }
                h2 {
                    font-weight: 700;
                    font-size: 2.4rem;
                    color: #d32f2f;
                    margin: 24px 32px 16px 32px;
                }
                a {
                    text-decoration: none;
                    color: inherit;
                }
                a:hover {
                    text-decoration: underline;
                }
                .imagem {
                    width: 100%;
                    overflow: hidden;
                    margin-bottom: 24px;
                }
                .imagem img {
                    width: 100%;
                    height: auto;
                    object-fit: cover;
                    border-radius: 0 0 22px 22px;
                    transition: transform 0.4s ease;
                    display: block;
                }
                article:hover .imagem img {
                    transform: scale(1.06);
                }
                p {
                    font-weight: 400;
                    font-size: 1.15rem;
                    color: #444;
                    line-height: 1.65;
                    margin: 0 32px 32px 32px;
                }
                @media (max-width: 720px) {
                    body {
                        padding: 24px 20px;
                    }
                    article {
                        margin-bottom: 36px;
                    }
                    h2 {
                        font-size: 1.9rem;
                        margin: 20px 24px 14px 24px;
                    }
                    p {
                        font-size: 1rem;
                        margin: 0 24px 28px 24px;
                    }
                }
            </style>
        </head>
        <body>
        """

        for entrada in feed.entries:
            titulo = entrada.title
            link = entrada.link
            resumo = entrada.get('summary', '')

            resumo_limpo = re.sub(r'<img[^>]*>', '', resumo).strip()

            url_imagem = ""

            if 'media_content' in entrada:
                media = entrada.media_content
                if isinstance(media, list) and media:
                    temp_url = media[0].get('url', '')
                    if is_formato_suportado(temp_url):
                        url_imagem = temp_url

            elif 'media_thumbnail' in entrada:
                media = entrada.media_thumbnail
                if isinstance(media, list) and media:
                    temp_url = media[0].get('url', '')
                    if is_formato_suportado(temp_url):
                        url_imagem = temp_url

            html += f"""
            <article>
                <h2><a href="{link}" target="_blank" rel="noopener noreferrer">{titulo}</a></h2>
                {"<div class='imagem'><a href='" + link + "' target='_blank' rel='noopener noreferrer'><img src='" + url_imagem + "' alt='" + titulo + "' loading='lazy'/></a></div>" if url_imagem else ""}
                <p>{resumo_limpo}</p>
            </article>
            """

        html += """
        </body>
        </html>
        """

        self.visualizador_web.setHtml(html)
