# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import sys
import os.path
from argparse import ArgumentParser
from qgis.core import (
    QgsApplication,
    QgsMapLayerRegistry,
    QgsVectorLayer,
    QgsMapRenderer,
    QgsCoordinateReferenceSystem)
from PyQt4.QtCore import (
    QSize,
    QByteArray,
    QBuffer,
    QIODevice)
from PyQt4.QtGui import (
    QImage,
    QPainter,
    qRgb)

aparser = ArgumentParser()
aparser.add_argument('input')
aparser.add_argument('output')
aparser.add_argument('--dpi', type=int, default=96)
aparser.add_argument('--width', type=int, default=1000)
args = aparser.parse_args(sys.argv[1:])

QgsApplication.setPrefixPath('/usr', True)
QgsApplication.initQgis()

layer = QgsVectorLayer(args.input, 'layer', 'ogr')
extent = layer.extent()
print("Layer extent: %s" % extent.toString())

QgsMapLayerRegistry.instance().removeAllMapLayers()
QgsMapLayerRegistry.instance().addMapLayer(layer)

crs = QgsCoordinateReferenceSystem(4326)
layer.setCrs(crs)

render = QgsMapRenderer()
render.setLayerSet([layer.id()])

iwidth = args.width
iheight = int(iwidth * (extent.height() / extent.width()))

print("Image size: %dx%d" % (iwidth, iheight))

dpi = args.dpi

img = QImage(iwidth, iheight, QImage.Format_RGB32)
img.setDotsPerMeterX(dpi / 25.4 * 1000)
img.setDotsPerMeterY(dpi / 25.4 * 1000)
img.fill(qRgb(255, 255, 255))

dpi = img.logicalDpiX()
print("Image DPI: %d" % dpi)

render.setOutputSize(QSize(img.width(), img.height()), dpi)

render.setDestinationCrs(crs)
render.setProjectionsEnabled(True)
render.setMapUnits(crs.mapUnits())

render.setExtent(extent)
print("Scale: %f" % render.scale())

painter = QPainter(img)
painter.setRenderHint(QPainter.Antialiasing)
render.render(painter)
painter.end()

ba = QByteArray()
bf = QBuffer(ba)
bf.open(QIODevice.WriteOnly)
img.save(bf, 'PNG')
bf.close()

with open(args.output, 'wb') as fd:
    fd.write(ba)
