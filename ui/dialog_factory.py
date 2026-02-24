# -*- coding: utf-8 -*-
from ..eficiencia_energetica_dialog import EficEnergDialog
from ..eficiencia_energetica_dialog_zoomed import EficEnergDialogZoomed
from ..eficiencia_energetica_dialog_accessibility import EficEnergDialogAccessibility

def create_main_dialog(use_zoomed: bool):
    return EficEnergDialogZoomed() if use_zoomed else EficEnergDialog()

def create_accessibility_dialog():
    return EficEnergDialogAccessibility()
