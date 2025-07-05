from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QApplication, QLabel, QPushButton, QHBoxLayout,
    QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt, QPoint
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import numpy as np

class JanelaGrafico(QDialog):
    def __init__(self, parent=None, clima=None):
        super().__init__(parent)
        self.setWindowTitle("Gráfico do Clima")
        self.setMinimumSize(750, 620)

        self.setStyleSheet("""
            QDialog {
                background-color: #fdfdfd;
                border-radius: 14px;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #2c3e50;
            }
            QLabel {
                font-size: 14px;
                color: #2c3e50;
            }
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: 600;
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 130px;
            }
            QPushButton:hover {
                background-color: #1e8449;
            }
            QComboBox {
                padding: 6px 12px;
                border: 1.8px solid #bbb;
                border-radius: 8px;
                background-color: #fff;
                font-size: 15px;
                min-width: 130px;
            }
        """)


        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(25)

        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(['Barra', 'Pizza'])
        self.combo_tipo.currentIndexChanged.connect(self.atualizar_grafico)
        control_layout.addWidget(QLabel("Tipo de gráfico:"))
        control_layout.addWidget(self.combo_tipo)

        self.btn_salvar = QPushButton("Salvar Gráfico")
        self.btn_salvar.clicked.connect(self.salvar_grafico)
        control_layout.addWidget(self.btn_salvar)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        self.fig = Figure(figsize=(7, 5), tight_layout=True, facecolor='#fafafa')
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setStyleSheet("border-radius: 14px; background-color: white;")
        layout.addWidget(self.canvas)


        self.tooltip = QLabel("", self)
        self.tooltip.setStyleSheet("""
            background-color: #fff9db;
            border: 1.5px solid #f39c12;
            padding: 8px 12px;
            font-weight: 700;
            color: #b9770e;
            border-radius: 8px;
            font-size: 14px;
        """)
        self.tooltip.setWindowFlags(Qt.ToolTip)
        self.tooltip.hide()


        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.info_label.setStyleSheet("""
            font-size: 16px;
            padding: 20px 25px;
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 16px;
            color: #2c3e50;
            max-width: 400px;
            line-height: 1.6;
            font-weight: 600;
        """)
        layout.addWidget(self.info_label)

        # Dados do clima
        self.clima = clima or {
            'temperatura': 22,
            'nascer_sol': '06:15',
            'descricao': 'ensolarado',
            'umidade': 65,
            'vento': 5.3,
            'vento_direcao': 'NE',
            'temp_max': 28,
            'temp_min': 15,
        }

        self.x = np.array([0, 1, 2])
        self.labels = ['Mín', 'Atual', 'Máx']

        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("figure_leave_event", lambda event: self.tooltip.hide())

        self.atualizar_grafico()
        self.atualizar_info_label()

    def atualizar_grafico(self):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        temperaturas = [
            self.clima.get('temp_min', 0),
            self.clima.get('temperatura', 0),
            self.clima.get('temp_max', 0)
        ]

        tipo = self.combo_tipo.currentText()

        if tipo == 'Barra':
            cores = ['#3498db', '#f39c12', '#e74c3c']  # azul, amarelo, vermelho
            bars = self.ax.bar(self.x, temperaturas, color=cores, edgecolor='black', linewidth=0.9, zorder=3)
            
            max_height = max(temperaturas)
            padding = max_height * 0.15
            self.ax.set_ylim(0, max_height + padding)

            for rect, temp in zip(bars, temperaturas):
                height = rect.get_height()

                if height > max_height * 0.15:
                    self.ax.text(
                        rect.get_x() + rect.get_width() / 2, 
                        height - padding / 5,
                        f"{temp:.1f}°C",
                        ha='center', va='top', fontsize=13, fontweight='bold', color='white', zorder=4
                    )
                else:
                    self.ax.text(
                        rect.get_x() + rect.get_width() / 2, 
                        height + padding / 10,
                        f"{temp:.1f}°C",
                        ha='center', va='bottom', fontsize=13, fontweight='bold', color='#34495e', zorder=4
                    )

            self.ax.set_xticks(self.x)
            self.ax.set_xticklabels(self.labels, fontsize=13, fontweight='bold', color='#34495e')
            self.ax.set_ylabel("Temperatura (°C)", fontsize=14, fontweight='bold', color='#16a085')
            self.ax.set_title("Temperatura Mínima, Atual e Máxima (Barra)", fontsize=18, fontweight='bold', color='#16a085', pad=20)
            self.ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)
            self.ax.set_axisbelow(True)
            self.tooltip.show_tooltip = True

        elif tipo == 'Pizza':
            def func(pct):
                total = sum(temperaturas)
                val = pct * total / 100
                return f"{pct:.1f}%\n({val:.1f}°C)"

            cores = ['#3498db', '#f39c12', '#e74c3c']
            wedges, texts, autotexts = self.ax.pie(
                temperaturas, labels=self.labels, autopct=func, colors=cores, startangle=90,
                textprops={'fontsize': 14, 'fontweight': 'bold', 'color': '#2c3e50'}
            )
            for w in wedges:
                w.set_edgecolor('white')
                w.set_linewidth(3)
            self.ax.set_title("Distribuição de Temperaturas (Pizza)", fontsize=18, fontweight='bold', color='#16a085', pad=20)
            self.ax.axis('equal')
            self.tooltip.hide()
            self.tooltip.show_tooltip = False

        self.canvas.draw()

    def atualizar_info_label(self):
        c = self.clima
        html = f"""
        <div style="
            background-color: #a8edea;
            background-image: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 12px;
            padding: 12px 15px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #2c3e50;
            max-width: 320px;
            line-height: 1.3;
            font-weight: 600;
            font-size: 14px;
        ">
            <h3 style="color: #16a085; margin: 0 0 10px 0; font-size: 18px;">🌤️ Condições do Clima</h3>
            <p style="margin: 3px 0;">🌡️ Temperatura Atual: <b>{c['temperatura']}°C</b></p>
            <p style="margin: 3px 0;">📈 Máxima: <b>{c.get('temp_max', 'N/A')}°C</b></p>
            <p style="margin: 3px 0;">📉 Mínima: <b>{c.get('temp_min', 'N/A')}°C</b></p>
            <p style="margin: 3px 0;">☁️ Condição: <b>{c['descricao'].capitalize()}</b></p>
            <p style="margin: 3px 0;">💧 Umidade: <b>{c['umidade']}%</b></p>
            <p style="margin: 3px 0;">💨 Vento: <b>{c['vento']} m/s</b> ({c.get('vento_direcao', 'N/A')})</p>
            <p style="margin: 3px 0;">🌅 Nascer do sol: <b>{c.get('nascer_sol', 'N/A')}</b></p>
        </div>

        """
        self.info_label.setText(html)

    def salvar_grafico(self):
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Salvar Gráfico", "", "PNG (*.png);;JPEG (*.jpg *.jpeg);;Todos os Arquivos (*)"
        )
        if caminho:
            self.fig.savefig(caminho, dpi=300)

    def on_mouse_move(self, event):
        if not hasattr(self.tooltip, 'show_tooltip') or not self.tooltip.show_tooltip:
            self.tooltip.hide()
            return

        if event.inaxes != self.ax:
            self.tooltip.hide()
            return

        xdata, ydata = event.xdata, event.ydata
        tolerancia = (self.ax.get_ylim()[1]) * 0.05  # 5% da altura

        temperaturas = [
            self.clima.get('temp_min', 0),
            self.clima.get('temperatura', 0),
            self.clima.get('temp_max', 0)
        ]

        for i, temp in enumerate(temperaturas):
            if abs(self.x[i] - xdata) < 0.4 and abs(temp - ydata) < tolerancia:
                texto = f"{self.labels[i]}: {temp:.1f} °C"
                pos = self.mapFromGlobal(QPoint(int(event.guiEvent.globalX()), int(event.guiEvent.globalY())))
                self.tooltip.setText(texto)
                self.tooltip.adjustSize()
                self.tooltip.move(pos.x() + 15, pos.y() + 15)
                self.tooltip.show()
                return

        self.tooltip.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    clima_exemplo = {
        'temperatura': 22,
        'nascer_sol': '06:15',
        'descricao': 'ensolarado',
        'umidade': 65,
        'vento': 5.3,
        'vento_direcao': 'NE',
        'temp_max': 28,
        'temp_min': 15,
    }

    janela = JanelaGrafico(clima=clima_exemplo)
    janela.show()
    sys.exit(app.exec_())
