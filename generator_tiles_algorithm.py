# -*- coding: utf-8 -*-

"""
/***************************************************************************
 GeneratorTiles
                                 A QGIS plugin
 To split and ecw file with specific grid turn it into mbtiles
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-03-08
        copyright            : (C) 2023 by Kholil Rahman
        email                : its@ahmadk.me
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Kholil Rahman'
__date__ = '2023-03-08'
__copyright__ = '(C) 2023 by Kholil Rahman'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QColor
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterRasterLayer, 
                       QgsCoordinateReferenceSystem, 
                       QgsCoordinateTransform, 
                       QgsRectangle)
from qgis import processing
from pathlib import Path

class GeneratorTilesAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    INPUT_GRID = 'INPUT_GRID'
    INPUT_ORTHO = 'INPUT_ORTHO'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_GRID,
                self.tr('Grid Layer'),
                [QgsProcessing.TypeMapLayer]
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT_ORTHO,
                self.tr('Orthophoto layer')
            )
        )
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                self.tr('Output Folder')
            )
        )

    def prepareAlgorithm(self, parameters, context, feedback):
        feedback.pushInfo('Preparing...')
        project = context.project()
        data = [i for i in project.mapLayers().values()]
        layer = data[0]
        layer.removeSelection()
        project.layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(False)
        return True

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        if feedback.isCanceled():
            return

        extent_orig = self.parameterAsExtent(parameters, self.INPUT_GRID, context)
        crs_orig = self.parameterAsCrs(parameters, self.INPUT_GRID, context)
        crs_target = self.parameterAsCrs(parameters, self.INPUT_ORTHO, context)

        transform = QgsCoordinateTransform(crs_orig, crs_target, context.project())

        extent = transform.transformBoundingBox(extent_orig)

        source = self.parameterAsSource(parameters, self.INPUT_GRID, context)
        count = source.featureCount()
        id = next(source.getFeatures()).attribute('id_zona')
        dest_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)

        _path = Path(dest_folder.split('_')[0]).joinpath("{}.mbtiles".format(id))

        feedback.pushInfo('({}) Executing {}...'.format(count, id))
        feedback.pushInfo(extent.toString())
        feedback.pushInfo("in folder : {}".format(dest_folder.split('_')[0]))
        feedback.pushInfo("output : {}".format(_path))

        output = processing.run(
            "qgis:tilesxyzmbtiles", 
            {
                'EXTENT':'{},{},{},{} [{}]'.format(
                    extent.xMinimum(), 
                    extent.xMaximum(), 
                    extent.yMinimum(), 
                    extent.yMaximum(),
                    ''
                ),
                'ZOOM_MIN':16,
                'ZOOM_MAX':21,
                'DPI':96,
                'BACKGROUND_COLOR':QColor(0, 0, 0, 0),
                'TILE_FORMAT':1,
                'QUALITY':75,
                'METATILESIZE':4,
                'OUTPUT_FILE': str(_path)
            }
        )

        if feedback.isCanceled():
            return

        return {self.OUTPUT_FOLDER: output['OUTPUT_FILE']}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Create MBTiles'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'PetaDasar'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return GeneratorTilesAlgorithm()
