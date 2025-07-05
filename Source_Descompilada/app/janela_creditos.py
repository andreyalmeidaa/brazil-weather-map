import os
from PyQt5.QtWidgets import (QDialog, QLabel, QVBoxLayout, QWidget, QSizePolicy,QGraphicsDropShadowEffect, QHBoxLayout, QScrollArea)
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect


class CardWidget(QWidget):
    def __init__(self, foto_pixmap, nome_texto, destaque=False):
        super().__init__()
        self.destaque = destaque
        self.initUI(foto_pixmap, nome_texto)
        self.anim = None

    def initUI(self, foto_pixmap, nome_texto):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        self.setStyleSheet("""
            background-color: white;
            border-radius: 15px;
        """)
        self.sombra = QGraphicsDropShadowEffect()
        self.sombra.setOffset(0, 4)
        self.sombra.setBlurRadius(20)
        self.sombra.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(self.sombra)


        self.label_foto = QLabel()
        self.label_foto.setPixmap(foto_pixmap)
        self.label_foto.setFixedSize(150, 150)
        self.label_foto.setAlignment(Qt.AlignCenter)
        self.label_foto.setStyleSheet("""
            border: 3px solid #ccc;
            border-radius: 15px;
            background-color: white;
        """)

        self.label_nome = QLabel(nome_texto)
        fonte = QFont("Segoe UI", 16 if self.destaque else 12)
        if self.destaque:
            self.label_nome.setStyleSheet("color: #1a73e8;")
        else:
            self.label_nome.setStyleSheet("color: #2c3e50;")
        self.label_nome.setFont(fonte)
        self.label_nome.setWordWrap(True)
        self.label_nome.setAlignment(Qt.AlignCenter)
        self.label_nome.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout.addWidget(self.label_foto)
        layout.addWidget(self.label_nome)

    def enterEvent(self, event):
        if self.anim is not None and self.anim.state() == QPropertyAnimation.Running:
            self.anim.stop()

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(200)
        rect = self.geometry()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(QRect(rect.x() - 10, rect.y() - 10, rect.width() + 20, rect.height() + 20))
        self.anim.start()

        self.sombra.setBlurRadius(40)
        self.sombra.setColor(QColor(26, 115, 232, 100)) 
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.anim is not None and self.anim.state() == QPropertyAnimation.Running:
            self.anim.stop()

        self.anim = QPropertyAnimation(self, b"geometry")
        self.anim.setDuration(200)
        rect = self.geometry()
        self.anim.setStartValue(rect)
        self.anim.setEndValue(QRect(rect.x() + 10, rect.y() + 10, rect.width() - 20, rect.height() - 20))
        self.anim.start()

        self.sombra.setBlurRadius(20)
        self.sombra.setColor(QColor(0, 0, 0, 30))
        super().leaveEvent(event)

def resource_path(relative_path):
    import sys, os
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)


class JanelaCreditos(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Créditos do Projeto")
        self.setFixedSize(800, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #f4f6f8;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #2c3e50;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        # Scroll Area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        conteudo = QWidget()
        layout_geral = QVBoxLayout(conteudo)
        layout_geral.setAlignment(Qt.AlignTop)
        layout_geral.setSpacing(30)

        caminho_base = resource_path("templates/fotos")

        integrantes = [
            {"nome": "Andrey Cavalcante de Almeida da Conceição Magalhäes", "foto": "andrey.png", "destaque": True},
            {"nome": "Daniel Leiner Cosenza", "foto": "daniel.png", "destaque": False},
            {"nome": "Bernardo Meucci Alves Pereira", "foto": "bernardo.png", "destaque": False},
            {"nome": "Murilo Kenzo Peña dos Santos", "foto": "murilo.png", "destaque": False},
            {"nome": "Sarah Raquel Aliendre de Figueireido", "foto": "sarah.png", "destaque": False},
        ]

        for integrante in integrantes:
            caminho_foto = os.path.join(caminho_base, integrante["foto"])
            pixmap = QPixmap(caminho_foto)

            if not pixmap.isNull():
                pixmap_resized = pixmap.scaled(150, 150, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            else:
                pixmap_resized = QPixmap(150, 150)
                pixmap_resized.fill(Qt.lightGray)

            card = CardWidget(pixmap_resized, integrante["nome"], destaque=integrante["destaque"])
            layout_geral.addWidget(card)

        scroll_area.setWidget(conteudo)

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.addWidget(scroll_area)
        self.setLayout(layout_principal)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    janela = JanelaCreditos()
    janela.show()
    sys.exit(app.exec_())
