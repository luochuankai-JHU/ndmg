import sys
import os
import xml.dom.minidom

import numpy as np

#
#  Makes a ton of assumptions about the XML data.  
#  Totally customize for MRCAP data.  Needs to be checked with 
#  anything that's not the original 109 data files on braingraph1
#
class ROIXML:
  """"Class to read the *.xml file and pull out important parameters"""

  def __init__(self,filename):

    print "Filename ", filename
    # Parse the XML document
    self._xmldoc = xml.dom.minidom.parse(filename)

  # There are three extents.  These are the dimensions.
  def getShape ( self ):

# RBTODO should probably assert on the assumptions.  Endianess what else?
     dims = self._xmldoc.getElementsByTagName ( 'Extents' )
     return [ int(dims[0].firstChild.nodeValue), int(dims[1].firstChild.nodeValue), int(dims[2].firstChild.nodeValue) ]



class ROIData:
  """Class to read ROI data derived from MRCAP.""" 

  # Get the dimension
  def __init__(self, filename, dim):

    self._filename = filename
    self._fileobj = open(self._filename, mode='rb')
    
    self.data = np.fromfile(self._fileobj, dtype='>i4', count=dim[0]*dim[1]*dim[2])
    self.data = np.reshape ( self.data, dim, order='F' )

    print self.data.shape

  # get the maximum value
  def maxval ( self ):
    """Returns the maximum ROI value.  Size of the graph."""
    return 200
    # RBTODO : get maximimum roi value
#    return max ( self.data[:,:,:] )

  # get the maximum value
  def get ( self, index ):
    """Returns the ROI associated with a voxel"""
    return self.data [ index[0], index[1], index[2] ]

