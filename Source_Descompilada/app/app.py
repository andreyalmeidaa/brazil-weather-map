# pip install requests
# pip install unidecode
# pip install PyQt5
# pip install svg.path
# pip install PyQtWebEngine
# pip install feedparser

import threading

# isso aqui é para evitar o  erro de threading bug do Python 3.13. 
# https://stackoverflow.com/questions/13193278/understand-python-threading-bug

def dummy_del_fix(self):
    try:
        pass
    except Exception:
        pass

if hasattr(threading, '_DummyThread'):
    threading._DummyThread.__del__ = dummy_del_fix

import sys
import os
import xml.etree.ElementTree as ET
from svg.path import parse_path, Move, Line, CubicBezier, QuadraticBezier
from PyQt5.QtWidgets import QApplication, QGraphicsView, QPushButton, QMessageBox, QGraphicsScene, QGraphicsTextItem, QGraphicsPathItem, QGraphicsDropShadowEffect, QVBoxLayout, QWidget, QLabel, QComboBox, QHBoxLayout, QFrame
from PyQt5.QtGui import QPainterPath, QPen, QBrush, QColor, QPainter, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from api_requests import buscar_cidades_estado, buscar_clima
from graficos import JanelaGrafico
from noticias import JanelaNoticias
from janela_creditos import JanelaCreditos

info_estado_label = None
combo_cidades = None
clima_label = None
textos_uf = []
th_clima = None
clima_atual = None


#como posso fazer para burlar o bug do threading de erro no python? 
# isso nao interfere em nada, porem retorna error. 

class ClimaThread(QThread): # muito obrigado GB  baitola <3
    resultado_clima = pyqtSignal(dict)

    def __init__(self, cidade, estado):
        super().__init__()
        self.cidade = cidade
        self.estado = estado

    def run(self):
        if self.isInterruptionRequested():
            return
        
        clima = buscar_clima(self.cidade, self.estado)
        
        if self.isInterruptionRequested():
            return
        
        self.resultado_clima.emit(clima if clima else {})

def atualizar_info_estado(estado, titulo_svg_estados):
    info_estado_label.setText(f"<b>Estado selecionado:</b> {titulo_svg_estados}")
    combo_cidades.clear()
    cidades = buscar_cidades_estado(estado.lower())
    if cidades:
        combo_cidades.addItems(cidades)
    else:
        combo_cidades.addItem("Nenhuma cidade disponível")

def atualizar_clima(cidade, estado):
    global th_clima

    if not cidade or cidade == "Nenhuma cidade disponível":
        clima_label.setText("Clima: selecione uma cidade válida.")
        return

    start_spinner()


    if th_clima and th_clima.isRunning():
        #th_clima.terminate()
        th_clima.requestInterruption()
        th_clima.wait()  # espera a thread encerrar de forma segura

    th_clima = ClimaThread(cidade, estado)
    th_clima.resultado_clima.connect(exibir_clima)
    th_clima.start()




def exibir_clima(clima):
    global clima_atual
    clima_atual = clima  # salva o clima para usar no gráfico

    stop_spinner()
    if clima:
        html = f"""
        <div style="
            background-color: #f0f8ff;
            border-radius: 10px;
            padding: 15px 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #333;
            max-width: 320px;
        ">
            <h3 style="color: #2e8b57; margin-top: 0;">🌤️ Condições do Clima</h3>
            <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
            <p>🌡️ <b>Temperatura:</b> {clima['temperatura']}°C</p>
            <p>📈 <b>Máxima:</b> {clima.get('temp_max', 'N/A')}°C</p>
            <p>📉 <b>Mínima:</b> {clima.get('temp_min', 'N/A')}°C</p>
            <p>☁️ <b>Condição:</b> {clima['descricao'].capitalize()}</p>
            <p>💧 <b>Umidade:</b> {clima['umidade']}%</p>
            <p>💨 <b>Vento:</b> {clima['vento']} m/s ({clima.get('vento_direcao', 'N/A')})</p>
            <p>🌅 <b>Nascer do sol:</b> {clima.get('nascer_sol', 'N/A')}</p>
        </div>
        """

        clima_label.setTextFormat(Qt.RichText)  
        clima_label.setText(html)
        clima_label.setWordWrap(True)  

    else:
        clima_label.setText("Erro ao carregar clima.")
        clima_atual = None

def efeitoMouse(caminho, id_svg_UF_estados, titulo_svg_estados):
    item = QGraphicsPathItem(caminho)
    item.setAcceptHoverEvents(True)
    cor_normal = QColor(60, 179, 113)  
    cor_hover = QColor(46, 139, 87)   
    pinceis = {'normal': QBrush(cor_normal), 'hover': QBrush(cor_hover)}
    item.setBrush(pinceis['normal'])
    item.setPen(QPen(QColor(255, 255, 255), 2))
    item.setTransformOriginPoint(item.boundingRect().center())

    def hoverEnterEvent(event):
        item.setBrush(pinceis['hover'])
        item.setScale(1.1)
        item.setZValue(1)
        event.accept()

    def hoverLeaveEvent(event):
        item.setBrush(pinceis['normal'])
        item.setScale(1.0)
        item.setZValue(0)
        event.accept()

    def mousePressEvent(event):
        if event.button() == Qt.LeftButton:
            atualizar_info_estado(id_svg_UF_estados, titulo_svg_estados)
        event.accept()

    item.hoverEnterEvent = hoverEnterEvent
    item.hoverLeaveEvent = hoverLeaveEvent
    item.mousePressEvent = mousePressEvent

    return item

def adicionar_texto_uf(caminho_qp, id_svg_UF_estados, cena_local):
    centro = caminho_qp.boundingRect().center()
    texto = QGraphicsTextItem(id_svg_UF_estados)
    fonte = QFont("Segoe UI", 10, QFont.Bold)
    texto.setDefaultTextColor(QColor(0, 0, 0))
    texto.setPos(centro.x() - texto.boundingRect().width() / 2, centro.y() - texto.boundingRect().height() / 2)
    texto.setAcceptedMouseButtons(Qt.NoButton)
    texto.setZValue(10)  
    texto.setVisible(True)  
    cena_local.addItem(texto)
    return texto

def toggle_textos_uf():
    global textos_uf
    for texto in textos_uf:
        texto.setVisible(not texto.isVisible())

def carregar_svg(caminho_arquivo, cena_local):
    arquivo = ET.parse(caminho_arquivo)
    raiz = arquivo.getroot()
    namespaces = {"svg": "http://www.w3.org/2000/svg"}

    for elemento_caminho in raiz.findall(".//svg:path", namespaces):
        dados_caminho = elemento_caminho.attrib.get("d")
        id_svg_UF_estados = elemento_caminho.attrib.get("id", "desconhecido")
        titulo_svg_estados = elemento_caminho.attrib.get("title", "desconhecido")
        if not dados_caminho:
            continue

        caminho_svg = parse_path(dados_caminho)
        caminho_qp = QPainterPath()

        for segmento in caminho_svg:
            if isinstance(segmento, Move):
                caminho_qp.moveTo(segmento.end.real, segmento.end.imag)
            elif isinstance(segmento, Line):
                caminho_qp.lineTo(segmento.end.real, segmento.end.imag)
            elif isinstance(segmento, CubicBezier):
                caminho_qp.cubicTo(segmento.control1.real, segmento.control1.imag, segmento.control2.real, segmento.control2.imag, segmento.end.real, segmento.end.imag)
            elif isinstance(segmento, QuadraticBezier):
                caminho_qp.quadTo(segmento.control.real, segmento.control.imag, segmento.end.real, segmento.end.imag)

        item = efeitoMouse(caminho_qp, id_svg_UF_estados, titulo_svg_estados)
        cena_local.addItem(item)
        texto_uf = adicionar_texto_uf(caminho_qp, id_svg_UF_estados, cena_local)
        textos_uf.append(texto_uf)

def renderizarMapa(caminho_svg):
    global info_estado_label, combo_cidades

    app = QApplication(sys.argv)
    window = QWidget()
    main_layout = QHBoxLayout()

    visualizar = QGraphicsView()
    visualizar.setWindowTitle("Mapa - Data Storm")
    cena = QGraphicsScene(visualizar)
    cena.setBackgroundBrush(QBrush(QColor(255, 255, 255)))
    visualizar.setScene(cena)

    carregar_svg(caminho_svg, cena)
    visualizar.setRenderHint(QPainter.Antialiasing)
    visualizar.setSceneRect(cena.itemsBoundingRect())

    painel_info, info_estado_label, combo_cidades, clima_label = barra_lateral()
    combo_cidades.currentIndexChanged.connect(
        lambda: atualizar_clima(combo_cidades.currentText(), info_estado_label.text().split(":")[-1].strip())
    )

    botoes_topo_(main_layout, window)
    main_layout.addWidget(visualizar)
    main_layout.addWidget(painel_info)

    window.resize(1100, 700)
    window.setWindowTitle("DATA STORM")
    window.show()
    return app, window

def barra_lateral():
    global info_estado_label, combo_cidades, clima_label

    painel_info = QFrame()
    painel_info.setFixedWidth(280)
    painel_info.setStyleSheet("""
        QFrame {
            background-color: #ffffff;
            border-left: 3px solid #4CAF50;
            padding: 20px;
            border-radius: 10px 0 0 10px;
        }
        QLabel#titulo {
            font-size: 18px;
            font-weight: 700;
            color: #333333;
            margin-bottom: 12px;
        }
        QLabel {
            font-size: 15px;
            color: #555555;
            margin-bottom: 8px;
        }
        QComboBox {
            padding: 8px 12px;
            font-size: 14px;
            border: 1.5px solid #4CAF50;
            border-radius: 8px;
            background-color: #f9f9f9;
            color: #333333;
            min-height: 32px;
            selection-background-color: #A5D6A7;
        }
        QComboBox:hover {
            border-color: #388E3C;
            background-color: #e8f5e9;
        }
        QComboBox:focus {
            border-color: #2E7D32;
            background-color: #c8e6c9;
        }
        QComboBox::drop-down {
            border: none;
            width: 25px;
            subcontrol-origin: padding;
            subcontrol-position: top right;
        }
        QComboBox::down-arrow {
            border: none;
            width: 0;
            height: 0;
            border-left: 6px solid transparent;
            border-right: 6px solid transparent;
            border-top: 8px solid #4CAF50;
            margin-right: 6px;
        }
        QComboBox QListView {
            border: 1.5px solid #4CAF50;
            border-radius: 8px;
            background-color: #fff;
            padding: 5px;
            outline: 0;
            selection-background-color: #A5D6A7;
            font-size: 14px;
        }
    """)

    sombra = QGraphicsDropShadowEffect()
    sombra.setBlurRadius(12)
    sombra.setXOffset(3)
    sombra.setYOffset(0)
    sombra.setColor(QColor(0, 0, 0, 50))
    painel_info.setGraphicsEffect(sombra)

    layout_info = QVBoxLayout()
    layout_info.setContentsMargins(0, 0, 0, 0)
    layout_info.setSpacing(10)

    info_estado_label = QLabel("Clique em um estado")
    info_estado_label.setObjectName("titulo")
    info_estado_label.setWordWrap(True)

    combo_cidades = QComboBox()

    clima_label = QLabel("Selecione um estado e uma cidade.")
    clima_label.setWordWrap(True)
    clima_label.setStyleSheet("color: #777777; font-size: 13px;")

    layout_info.addWidget(info_estado_label)
    layout_info.addWidget(QLabel("<b>Cidades:</b>"))
    layout_info.addWidget(combo_cidades)
    layout_info.addWidget(clima_label)
    layout_info.addStretch()
    painel_info.setLayout(layout_info)

    return painel_info, info_estado_label, combo_cidades, clima_label

def botoes_topo_(main_layout, window):
    layout_principal = QVBoxLayout()
    layout_botoes = QHBoxLayout()

    btn_toggle_textos = QPushButton("Ocultar UF")
    btn_toggle_textos.setFixedSize(100, 30)
    btn_toggle_textos.setStyleSheet("""
        QPushButton {
            background-color: red;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: darkred;
        }
    """)

    def toggle_textos():
        toggle_textos_uf()
        if btn_toggle_textos.text() == "Mostrar UF":
            btn_toggle_textos.setText("Ocultar UF")
        else:
            btn_toggle_textos.setText("Mostrar UF")

    btn_toggle_textos.clicked.connect(toggle_textos)

    # Botão 2 - Gerar Relatório
    btn_funcao2 = QPushButton("Gerar Relatório")
    btn_funcao2.setFixedSize(130, 30)
    btn_funcao2.setStyleSheet("""
        QPushButton {
            background-color: green;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: darkgreen;
        }
    """)

    def abrir_grafico():
        global clima_atual
        if clima_atual:
            dialog = JanelaGrafico(window, clima=clima_atual)
            dialog.exec_()
        else:
            exibir_mensagem("Erro", "Nenhum dado de clima disponível para gerar o gráfico.", tipo="erro")
    btn_funcao2.clicked.connect(abrir_grafico)

    btn_noticias = QPushButton("Notícias")
    btn_noticias.setFixedSize(100, 30)
    btn_noticias.setStyleSheet("""
        QPushButton {
            background-color: orange;
            color: white;
            font-weight: bold;
            border-radius: 5px;
            border: none;
        }
        QPushButton:hover {
            background-color: darkorange;
        }
    """)


    def abrir_noticias():
        janela = JanelaNoticias(window)
        janela.exec_()

    btn_noticias.clicked.connect(abrir_noticias)


    btn_creditos = QPushButton("Créditos")
    btn_creditos.setFixedSize(100, 30)
    btn_creditos.setStyleSheet("""
        QPushButton {
            background-color: #555;
            color: white;
            font-weight: bold;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #333;
        }
    """)

    def mostrar_creditos():
        janela = JanelaCreditos(window)
        janela.exec_()


    btn_creditos.clicked.connect(mostrar_creditos)
    
    layout_botoes.addWidget(btn_toggle_textos)
    layout_botoes.addWidget(btn_funcao2)
    layout_botoes.addWidget(btn_noticias)
    layout_botoes.addWidget(btn_creditos)
    layout_botoes.addStretch()

    layout_principal.addLayout(layout_botoes)
    layout_principal.addLayout(main_layout)
    window.setLayout(layout_principal)

spinner_timer = None
spinner_index = 0
spinner_frames = ['◐', '◓', '◑', '◒'] 


def start_spinner():
    global spinner_timer, spinner_index

    spinner_index = 0
   # clima_label.setText("Carregando clima...")

    spinner_timer = QTimer()
    spinner_timer.timeout.connect(update_spinner)
    spinner_timer.start(150)  

def update_spinner():
    global spinner_index, spinner_frames

    frame = spinner_frames[spinner_index]
    spinner_index = (spinner_index + 1) % len(spinner_frames)

    clima_label.setTextFormat(Qt.RichText)
    clima_label.setAlignment(Qt.AlignCenter)
    clima_label.setText(f"""
        <div style="font-size: 42px; font-weight: bold; color: #2c3e50;">
            {frame}
        </div>
        <div style="font-size: 16px; margin-top: 8px;">
            Carregando clima...
        </div>
    """)


def stop_spinner(): #finalizar a porcaria da bolinha que gira
    global spinner_timer
    if spinner_timer:
        spinner_timer.stop()
        spinner_timer = None


def exibir_mensagem(titulo: str, mensagem: str, tipo: str = "informacao"):
    msg = QMessageBox()
    
    if tipo == "erro":
        msg.setIcon(QMessageBox.Critical)
    elif tipo == "aviso":
        msg.setIcon(QMessageBox.Warning)
    else:
        msg.setIcon(QMessageBox.Information)
    
    msg.setWindowTitle(titulo)
    msg.setText(mensagem)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

# to enfrentando um bug do python que nao sei resolve bug no módulo threading

if __name__ == "__main__":
    diretorio_base = os.path.dirname(os.path.abspath(__file__)) 
    pasta_base = os.path.dirname(diretorio_base)               
    caminho_svg = os.path.join(pasta_base, "templates", "brazil.svg")  

    app, window = renderizarMapa(caminho_svg)


#aqui é pra quando o app for fechar, garantir q a thread do clima n
# fique rodando ainda, entao usa terminate() pra matar ela na hora e wait() pra esperar terminar,
# aí n dá erro estranho d thread no final.
    def finalizar_threads():
        global th_clima
        if th_clima:
            if th_clima.isRunning():
                th_clima.requestInterruption()
                #th_clima.terminate()  # Encerra imediatamente workaround para py 3.13
                th_clima.wait()
            th_clima = None  # para evitar coletar lixos


    app.aboutToQuit.connect(finalizar_threads)

    sys.exit(app.exec_())
