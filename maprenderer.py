# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import sys
from datetime import datetime

from argparse import ArgumentParser
from qgis.core import (
    QgsApplication,
    QgsMapLayerRegistry,
    QgsVectorLayer,
    QgsCoordinateReferenceSystem,
    QgsMapSettings, QgsMapRendererParallelJob, QgsMapRendererSequentialJob)
from PyQt4.QtCore import (
    QSize)
from PyQt4.QtGui import (
    QImage)


prefix = '/opt/qgis_stable'
parallel_rendering = False


aparser = ArgumentParser()
aparser.add_argument('input')
aparser.add_argument('output')
aparser.add_argument('--dpi', type=int, default=96)
aparser.add_argument('--width', type=int, default=1000)
args = aparser.parse_args(sys.argv[1:])

QgsApplication.setPrefixPath(prefix, True)
QgsApplication.setMaxThreads(4)
QgsApplication.initQgis()
app = QgsApplication([], False)


layer = QgsVectorLayer(args.input, 'layer', 'ogr')

QgsMapLayerRegistry.instance().removeAllMapLayers()
QgsMapLayerRegistry.instance().addMapLayer(layer)

crs = QgsCoordinateReferenceSystem(4326)
layer.setCrs(crs)


extent = layer.extent()
print("Layer extent: %s" % extent.toString())

iwidth = args.width
iheight = int(iwidth * (extent.height() / extent.width()))+1

print("Image size: %dx%d" % (iwidth, iheight))

sett = QgsMapSettings()
sett.setLayers([layer.id()])
sett.setFlag(QgsMapSettings.DrawLabeling)
sett.setFlag(QgsMapSettings.Antialiasing)

sett.setCrsTransformEnabled(True)
sett.setDestinationCrs(crs)
sett.setMapUnits(crs.mapUnits())
sett.setOutputSize(QSize(iwidth, iheight))
sett.setExtent(extent)

sett.setOutputImageFormat(QImage.Format_ARGB32)
sett.setOutputDpi(args.dpi)

print("Scale: %f" % sett.scale())

if parallel_rendering:
    job = QgsMapRendererParallelJob(sett)
else:
    job = QgsMapRendererSequentialJob(sett)

job.start()
job.waitForFinished()

img = job.renderedImage()
img.save(args.output)

app.exitQgis()
