# -*- coding: utf-8 -*-
"""
Paletes de colors, símbols i rangs de classificació utilitzats per al plugin principal Eficiència Energètica.
"""

from qgis.PyQt.QtGui import QColor
from qgis.core import QgsRendererRange, QgsSymbol, QgsWkbTypes

# ----------------------------
# Paleta per defecte
# ----------------------------
colors = {
    "colorConsum": QColor(0, 0, 0),
    "colorEmissions": QColor(0, 0, 0),
    "colorA": QColor.fromCmykF(0.85, 0.15, 0.95, 0.30),
    "colorB": QColor.fromCmykF(0.80, 0.00, 1.00, 0.00),
    "colorC": QColor.fromCmykF(0.45, 0.00, 1.00, 0.00),
    "colorD": QColor.fromCmykF(0.10, 0.00, 0.95, 0.00),
    "colorE": QColor.fromCmykF(0.05, 0.30, 1.00, 0.00),
    "colorF": QColor.fromCmykF(0.10, 0.65, 1.00, 0.00),
    "colorG": QColor.fromCmykF(0.05, 0.95, 0.95, 0.00),
}

# Copia per a restaurar ràpidament
default_colors = dict(colors)

# ----------------------------
# Paletes per al daltonisme
# ----------------------------
colors_protanopia = {
    "colorConsum": QColor(0, 0, 0),
    "colorEmissions": QColor(0, 0, 0),
    "colorA": QColor("#000080"),  # Azul marino
    "colorB": QColor("#0066CC"),
    "colorC": QColor("#3399FF"),
    "colorD": QColor("#66CCFF"),
    "colorE": QColor("#FFFF00"),  # Amarillo
    "colorF": QColor("#B8860B"),
    "colorG": QColor("#8B4513"),
}

colors_deuteranopia = {
    "colorConsum": QColor(0, 0, 0),
    "colorEmissions": QColor(0, 0, 0),
    "colorA": QColor("#663399"),
    "colorB": QColor("#9966CC"),
    "colorC": QColor("#CC99FF"),
    "colorD": QColor("#E6CCFF"),
    "colorE": QColor("#FFCC00"),
    "colorF": QColor("#FF6600"),
    "colorG": QColor("#CC3300"),
}

colors_tritanopia = {
    "colorConsum": QColor(0, 0, 0),
    "colorEmissions": QColor(0, 0, 0),
    "colorA": QColor("#CC0033"),
    "colorB": QColor("#FF3366"),
    "colorC": QColor("#FF6699"),
    "colorD": QColor("#FF99CC"),
    "colorE": QColor("#00CC66"),
    "colorF": QColor("#66FF99"),
    "colorG": QColor("#009966"),
}

def get_daltonism_colors(daltonism_type: str):
    """
    Retorna la paleta de colors segons el tipus de daltonisme.
    """
    if daltonism_type == "Protanopia":
        return colors_protanopia
    if daltonism_type == "Deuteranopia":
        return colors_deuteranopia
    if daltonism_type == "Tritanopia":
        return colors_tritanopia
    return colors

# ----------------------------
# Símbols base (per als rangs)
# ----------------------------
symbols = {
    "symbolConsum": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
    "symbolEmissions": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
    "symbolA": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
    "symbolB": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
    "symbolC": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
    "symbolD": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
    "symbolE": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
    "symbolF": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
    "symbolG": QgsSymbol.defaultSymbol(QgsWkbTypes.GeometryType(QgsWkbTypes.LineString)),
}

# Rangs estàndard A..G
ranges_consum = {
    'rangeA': QgsRendererRange(0.0, 44.6, symbols['symbolA'], 'A'),
    'rangeB': QgsRendererRange(44.7, 72.3, symbols['symbolB'], 'B'),
    'rangeC': QgsRendererRange(72.4, 112.1, symbols['symbolC'], 'C'),
    'rangeD': QgsRendererRange(112.2, 172.3, symbols['symbolD'], 'D'),
    'rangeE': QgsRendererRange(172.4, 303.7, symbols['symbolE'], 'E'),
    'rangeF': QgsRendererRange(303.8, 382.6, symbols['symbolF'], 'F'),
    'rangeG': QgsRendererRange(382.7, 9999999, symbols['symbolG'], 'G')
}

ranges_emissions = {
    'rangeA': QgsRendererRange(0.0, 10.1, symbols['symbolA'], 'A'),
    'rangeB': QgsRendererRange(10.2, 16.3, symbols['symbolB'], 'B'),
    'rangeC': QgsRendererRange(16.4, 25.3, symbols['symbolC'], 'C'),
    'rangeD': QgsRendererRange(25.4, 38.9, symbols['symbolD'], 'D'),
    'rangeE': QgsRendererRange(39.0, 66.0, symbols['symbolE'], 'E'),
    'rangeF': QgsRendererRange(66.1, 79.2, symbols['symbolF'], 'F'),
    'rangeG': QgsRendererRange(79.3, 9999999, symbols['symbolG'], 'G')
}

# Rangs comparativa
rangescomparativa = {
    "Molt positiu": QgsRendererRange(50.0, 999999.9, symbols["symbolA"], "Molt positiu"),
    "Positiu": QgsRendererRange(0.2, 49.9, symbols["symbolC"], "Positiu"),
    "Sense canvis": QgsRendererRange(-0.1, 0.1, symbols["symbolD"], "Sense canvis"),
    "Negatiu": QgsRendererRange(-49.9, -0.2, symbols["symbolE"], "Negatiu"),
    "Molt negatiu": QgsRendererRange(-999999.9, -50.0, symbols["symbolG"], "Molt negatiu"),
}

# Rangs per a consum
rangesconsum = {
    "units": QgsRendererRange(-1.0, -0.1, symbols["symbolConsum"], "Consum KWh/m²"),
    **ranges_consum
}

# Rangs per a emissions
rangesemissions = {
    "units": QgsRendererRange(-1.0, -0.1, symbols["symbolEmissions"], "Emissions KgCO₂/m²"),
    **ranges_emissions
}