import os
from qgis.PyQt import uic
from qgis.PyQt import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'eficiencia_energetica_dialog_base_zoomed.ui'))

class EficEnergDialogZoomed(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(EficEnergDialogZoomed, self).__init__(parent)
        self.setupUi(self)