from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QComboBox, QTableWidgetItem
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from functools import partial
from ui_main import Ui_MainWindow  # Interface do Qt Designer
from hrt_data import HrtData
from hrt_enum import hrt_enum
from hrt_bitenum import hrt_bitEnum
import sys

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, hrt_data: HrtData):
        super().__init__()
        self.setupUi(self)  # Configura a interface do Qt Designer
        self.hrt_data = hrt_data
        self.hrt_data.data_updated.connect(self.initUI)  # Conecta sinal de atualização
        self.initUI()
        self.tableWidget.cellChanged.connect(self.on_cell_changed)  # Detecta edições na tabela

    def initUI(self):
        """Configura a tabela com base nos dados carregados do Excel."""
        self.df = self.hrt_data.get_dataframe()
        rows, cols = self.df.shape
        self.tableWidget.blockSignals(True)  # Bloqueia sinais para evitar loops infinitos
        self.tableWidget.setRowCount(rows)
        self.tableWidget.setColumnCount(cols)
        self.tableWidget.setHorizontalHeaderLabels(self.df.columns)
        widget_row_types = self.df['TYPE']
        
        for row in range(rows): 
            if any(x in widget_row_types[row][:4] for x in ["PACK", "ASCI", "UNSI", "FLOA", "INTE", "INDE"]):  # "QLineEdit"
                row_type = 2
            elif any(x in widget_row_types[row][:4] for x in ["ENUM", "BIT_"]):  # "QComboBox"
                row_type = 1
            else:
                row_type = 0
              
            for col in range(cols): 
                data = self.hrt_data.get_variable_with_pos(row, col, machineValue=(col <= 2)) 
                cell_value = f"{data:.2f}" if isinstance(data, float) else str(data)

                if col > 2 and row_type == 2:
                    widget = QLineEdit()
                    widget.setStyleSheet("QLineEdit { background-color: white; }")
                    widget.setText(cell_value)
                    widget.editingFinished.connect(partial(self.on_edit_finished, widget, row, col))
                    self.tableWidget.setCellWidget(row, col, widget)

                elif col > 2 and row_type == 1:
                    widget = QComboBox()
                    if widget_row_types[row][:4] == "ENUM":
                        dados = list(hrt_enum[int(widget_row_types[row][4:])].values())
                    else:
                        dados = list(hrt_bitEnum[int(widget_row_types[row][8:])].values())
                    widget.addItems(dados)
                    widget.setCurrentText(cell_value)
                    widget.currentIndexChanged.connect(partial(self.on_combo_changed, widget, row, col))
                    self.tableWidget.setCellWidget(row, col, widget)
                
                else:
                    item = QTableWidgetItem(cell_value)
                    item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Não editável
                    item.setBackground(QColor("#D3D3D3"))  # Define fundo cinza claro
                    self.tableWidget.setItem(row, col, item)

        self.tableWidget.blockSignals(False)  # Libera sinais após a configuração da tabela
        self.tableWidget.viewport().update()  # Atualiza a interface

    def on_edit_finished(self, widget, row, col):
        """Atualiza os dados ao editar um QLineEdit."""
        value = widget.text()
        self.hrt_data.set_variable_with_pos(value, row, col, machineValue=(col <= 2))

    def on_combo_changed(self, widget, row, col, _):
        """Atualiza os dados ao mudar um QComboBox."""
        value = widget.currentText()
        self.hrt_data.set_variable_with_pos(value, row, col, machineValue=(col <= 2))

    def on_cell_changed(self, row, column):
        """Atualiza o Excel sempre que uma célula for editada na interface."""
        value = self.tableWidget.item(row, column).text()
        self.hrt_data.set_variable_with_pos(value, row, column, machineValue=(column <= 2))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    hrt_data = HrtData()
    window = MainWindow(hrt_data)
    window.show()
    sys.exit(app.exec())
