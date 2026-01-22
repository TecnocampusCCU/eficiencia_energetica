import os

from PyQt5 import uic
from PyQt5 import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'eficiencia_energetica_dialog_accessibility.ui'))

class EficEnergDialogAccessibility(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(EficEnergDialogAccessibility, self).__init__(parent)
        self.setupUi(self)
        # Estado inicial: combo habilitado solo si el check está activo
        try:
            self.comboDaltonisme.setEnabled(self.checkDaltonisme.isChecked())
            self.checkDaltonisme.stateChanged.connect(self._on_toggle_daltonisme)
        except Exception:
            pass
        # Wire botones aceptar/cancelar si existen en el UI
        for name in ("pushAcceptar", "buttonBox"):
            if hasattr(self, name):
                btn = getattr(self, name)
                # QDialogButtonBox puede manejar accept/reject automáticamente,
                # aquí nos aseguramos de conectar si es un QPushButton personalizado
                try:
                    btn.accepted.connect(self.accept)  # QDialogButtonBox
                    btn.rejected.connect(self.reject)
                except Exception:
                    try:
                        btn.clicked.connect(self.accept)  # QPushButton Aceptar
                    except Exception:
                        pass
        if hasattr(self, "pushCancelar"):
            try:
                self.pushCancelar.clicked.connect(self.reject)
            except Exception:
                pass

    def _on_toggle_daltonisme(self, state):
        self.comboDaltonisme.setEnabled(bool(state))