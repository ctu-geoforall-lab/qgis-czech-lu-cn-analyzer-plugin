import tempfile
from pathlib import Path
from owslib.wps import WebProcessingService, monitorExecution
import os
from lxml import etree

URL = "https://rain1.fsv.cvut.cz/services/wps"
identifier = "soil-texture-hsg"

xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<wps:Execute service="WPS" version="1.0.0" xmlns:wps="http://www.opengis.net/wps/1.0.0" 
             xmlns:ows="http://www.opengis.net/ows/1.1" 
             xmlns:xlink="http://www.w3.org/1999/xlink" 
             xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <ows:Identifier>soil-texture-hsg</ows:Identifier>
  <wps:DataInputs>
    <wps:Input>
      <ows:Identifier>input</ows:Identifier>
      <wps:Data>
        <wps:ComplexData mimeType="text/xml">
          <ogr:FeatureCollection
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xsi:schemaLocation="http://ogr.maptools.org/ http://ogr.maptools.org/ogr.xsd"
            xmlns:ogr="http://ogr.maptools.org/"
            xmlns:gml="http://www.opengis.net/gml">
            <gml:boundedBy>
              <gml:Envelope>
                <gml:lowerCorner>-648275.875 -1061174.25 0</gml:lowerCorner>
                <gml:upperCorner>-648136.625 -1061071.125 0</gml:upperCorner>
              </gml:Envelope>
            </gml:boundedBy>
            <gml:featureMember>
              <ogr:SoilFeature fid="1">
                <ogr:geometryProperty>
                  <gml:Polygon srsName="EPSG:5514">
                    <gml:outerBoundaryIs>
                      <gml:LinearRing>
                        <gml:coordinates>
                          -648274.9874650223646313 -1061112.71474611340090632, 
                          -648275.84785364079289138 -1061151.64733109553344548, 
                          -648159.48029300349298865 -1061174.23253232822753489, 
                          -648136.67999461607541889 -1061071.20099527598358691, 
                          -648233.25861703045666218 -1061090.12954488047398627, 
                          -648274.9874650223646313 -1061112.71474611340090632
                        </gml:coordinates>
                      </gml:LinearRing>
                    </gml:outerBoundaryIs>
                  </gml:Polygon>
                </ogr:geometryProperty>
                <ogr:fid>1</ogr:fid>
                <ogr:idk>1</ogr:idk>
              </ogr:SoilFeature>
            </gml:featureMember>
          </ogr:FeatureCollection>
        </wps:ComplexData>
      </wps:Data>
    </wps:Input>
    <wps:Input>
      <ows:Identifier>layers</ows:Identifier>
      <wps:Data>
        <wps:LiteralData>hsg</wps:LiteralData>
      </wps:Data>
    </wps:Input>
  </wps:DataInputs>
</wps:Execute>"""

wps = WebProcessingService(URL)

# Log the request for debugging
with open('request_log.xml', 'wb') as log_file:
    log_file.write(xml.encode('utf-8'))

# Execute the request
execution = wps.execute(identifier, [], request=xml.encode('utf-8'))
monitorExecution(execution)

# Log the response for debugging
with open('response_log.xml', 'wb') as log_file:
    log_file.write(etree.tostring(execution.response, pretty_print=True))

# Check if the process succeeded
if execution.getStatus() != "ProcessSucceeded":
    raise Exception("WPS request failed: " + str(execution.errors))

# Download the output files
output_files = []
for output in execution.processOutputs:
    # output in desktop
    ofile = "/home/jehlijos/Desktop/test4.zip"
    execution.getOutput(ofile, output.identifier)
    output_files.append(ofile)