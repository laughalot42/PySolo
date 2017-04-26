#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       pvg_acquire.py
#
#       Copyright 2011 Giorgio Gilestro <giorgio@gilest.ro>
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.
#
#

__author__ = "Giorgio Gilestro <giorgio@gilest.ro>"
__version__ = "$Revision: 1.0 $"
__date__ = "$Date: 2011/08/16 21:57:19 $"
__copyright__ = "Copyright (c) 2011 Giorgio Gilestro"
__license__ = "Python"

#       Revisions by Caitlin Laughrey and Loretta E Laughrey in 2016.

import wx
import os
import cv2
import numpy as np
import copy
import pysolovideoGlobals as gbl
import configurator as cfg
import videoMonitor as VM
import math
from itertools import repeat  # generate tab-delimited zeroes to fill in extra columns
import winsound

# TODO: monitors are being tracked one at a time

class consolePanel(wx.TextCtrl):  # ------------------------------------------------ redirect sysout to scrolled textctrl
    def __init__(self, parent, size=(200, 200)):  # parent is the cfgPanel
        self.mon_ID = gbl.mon_ID  # keep track of which monitor this console is for
        style = wx.TE_MULTILINE | wx.TE_RICH | wx.TE_AUTO_SCROLL | wx.HSCROLL | wx.VSCROLL | wx.TE_READONLY
        wx.TextCtrl.__init__(self, parent, wx.ID_ANY, size=size, style=style, name=gbl.mon_name)

    def writemsg(self, message):
        self.AppendText(message + '\n')
        self.Parent.SetSizer(self.Parent.thumbGridSizer)
        self.Refresh()
        self.Layout()

class trackedMonitor(wx.Panel):                                    # TODO: why does this need to be a panel?  does it matter?
    def __init__(self, parent, mon_ID):
        self.mon_ID = gbl.mon_ID = mon_ID       # make sure the settings for this monitor are in the nicknames
        cfg.mon_dict_to_nicknames()
        self.mon_name = gbl.mon_name
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, name=self.mon_name)

        # -------------------------------------------------------------------------------------------- source settings
        self.parent = parent
        self.loop = False                       # never loop tracking
        self.keepPlaying = False                # don't start yet
        self.source = gbl.source
        self.source_type = gbl.source_type
        self.devnum = 0                         # only one camera is currently supported
        self.fps = gbl.source_fps
        self.mmsize = gbl.source_mmsize
        self.start_datetime = gbl.start_datetime
        self.mask_file = gbl.mask_file
        self.data_folder = gbl.data_folder
        self.outputprefix = os.path.join(self.data_folder, self.mon_name)     # path to folder where output will be saved
        self.console = consolePanel(parent, size=gbl.thumb_size)                         # the output console


        # ---------------------------------------- use the sourcetype to create the correct type of object for capture
        if self.source_type == 0:
            self.captureMovie = VM.realCam(self.mon_ID, 1, devnum=0)
        elif self.source_type == 1:
            self.captureMovie = VM.virtualCamMovie(self.mon_ID, 1, self.source, loop=False)
        elif self.source_type == 2:
            self.captureMovie = VM.virtualCamFrames(self.mon_ID, 1, self.source, loop=False)

        (self.cols, self.rows) = self.size = self.captureMovie.initialSize
        self.distscale = (float(self.mmsize[0])/float(self.size[0]), float(self.mmsize[1])/float(self.size[1]))
        self.areascale = self.distscale[0] * self.distscale[1]

        self.ROIs = gbl.loadROIsfromMaskFile(self.mask_file)  # -----------------------------------------------------ROIs

    def startTrack(self, show_raw_diff=False, drawPath=True):  # ---------------------------------------- begin tracking
        """
        Each frame is compared against the moving average
        take an opencv frame as input and return an array of distances moved per minute for each ROI
        """

        gbl.statbar.SetStatusText('Tracking started: ' + self.mon_name)

        self.parent.trackedConsoles[self.mon_ID].writemsg('Start tracking monitor %d.' % self.mon_ID)
        self.parent.trackedConsoles[self.mon_ID].SetFocus()

        fly_coords = self.getCoordsArray()                       # finds coordinates of flies in each ROI in each frame

        # ----------------------------------------------------------------------------------------------------------------------------- debug
        try: os.remove('fly_coords.csv')
        except: pass
        open('fly_coords.csv', 'w').write('\n'.join('%d %d' % (mytuple[0][0], mytuple[0][1]) for mytuple in fly_coords))
        # ------------------------------------------------------------------------------------------------------------------------------------


        distByMinute = self.calcDistances(fly_coords)            # calculates distance each fly travelled in each minute
        outputArrays = self.colSplit32(distByMinute)             # splits data into 32 ROI groups

        self.outputprefix = self.checkFilenames(len(outputArrays))      # prevents overwriting of files

        for batch in range(0, len(outputArrays)):                  # output the files
            outputfile = self.outputprefix + str(batch + 1) + '.txt'  # create a filename for saving

            f_out = open(outputfile, 'a')                                       # TODO: if output fails, notify user
            for rownum in range(0, len(outputArrays[batch])):
                f_out.write(outputArrays[batch][rownum])       # save "part" to the file in tab delimited format
                self.parent.trackedConsoles[self.mon_ID].writemsg(outputArrays[batch][rownum])
                self.parent.trackedConsoles[self.mon_ID].SetFocus()
            f_out.close()

            outputfile = os.path.split(self.outputprefix)[1]

        if outputfile == '':
            gbl.statbar.SetStatusText('Cancelled.')
        else:
            gbl.statbar.SetStatusText('Done. Output file names start with:  ' + outputfile)

        self.parent.trackedConsoles[self.mon_ID].writemsg('Acquisition of Monitor %d is finished.' % self.mon_ID)
        self.parent.trackedConsoles[self.mon_ID].SetFocus()

    def getCoordsArray(self):
        self.parent.trackedConsoles[self.mon_ID].writemsg('collecting coordinates for monitor %d' % self.mon_ID)
        self.parent.trackedConsoles[self.mon_ID].SetFocus()
        keepgoing = True
        fly_coords = []                                 # table of coordinates of flies in each ROI for each frame
        self.frameCount = 0

        # ---------------------------------------------------- process first frame, which can't be compared to anything.
        frame = self.captureMovie.getImage()
        previousFrame_fly_coords = self.getFrameFlyCoords(frame, [(0,0)]*len(self.ROIs))    # there are no previous coordinates

        # ------------------------------------------------ make 2D array of fly coordinates for every ROI in every frame
        while keepgoing:                     # goes through WHOLE video
            # each of the 3 video input classes has a "getImage" function.
            # CaptureMovie is either webcam, video, or a folder
            frame = self.captureMovie.getImage()                # get image
            self.frameCount = self.frameCount + 1
            if frame is not None:
                fly_coords.append(self.getFrameFlyCoords(frame, previousFrame_fly_coords)) # append coordinates for every ROI in this frame
            else:
                keepgoing = False
            previousFrame_fly_coords = fly_coords[-1]

        return fly_coords

    def getFrameFlyCoords(self, grey_image, previousCoords):             # returns an array of fly coordinates for one frame

        fliesInFrame = []
        for flyNum in range(0, len(self.ROIs)):                               # locate the fly in each ROI
            ROI = self.ROIs[flyNum]
            ROIimg = grey_image[ROI[0][1]:ROI[2][1],ROI[0][0]:ROI[2][0]]    # make a mini-image of the ROI

            # prepare the ROI for object recognition.  By doing the preparation inside the ROI instead of over the
            # whole image, contrast issues are reduced.
            bw_image = self.prepImage(ROIimg)                               # convert image to binary b&w
            fliesInFrame.append(self.getFlyCoords(bw_image, previousCoords[flyNum]))   # determines coordinates of center of fly in ROI

        return fliesInFrame

    def prepImage(self, frame):
        # ----------blurs edges
        frame = cv2.GaussianBlur(frame, (3, 3), 0)  # height & width of kernel must be odd and positive
        grey_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # remove color & collapse to 2D array

        # -------------------------------------------------------------------------------------------------------------------------------debug
        self.origROIimg = grey_image                    # for use in getFlyCoords

        retvalue, bw_image = self.adptThreshold(grey_image)
#        retvalue, bw_image = cv2.threshold(grey_image, 80, 255, cv2.THRESH_BINARY)  # convert to black & white          # TODO:  best threshold values?  was 20,255
                                                                                    # adaptive thresholds are terrible
        bw_image = cv2.morphologyEx(bw_image, cv2.MORPH_OPEN, (2, 2))  # remove noise (dilate and erode)
        bw_image = 255 - bw_image  # flies need to be white on black background for using cv2.contours to locate them.

        # -------------------------------------------------------------------------------------------------------------------------------debug
        self.origROIimg = grey_image                    # for use in getFlyCoords
#        gbl.debugimg(np.hstack((grey_image, bw_image)))

        # -------------------------------------------------------------------------------------------------------------------------------

        return bw_image

    def adptThreshold(self, img):
    # goal is to choose threshold value that produces three contours in the image                                           # TODO: could be more efficient by combining with finding coordinates
        for testValue in range(45, 150, 5):
            retvalue, bw_image = cv2.threshold(img, testValue, 255, cv2.THRESH_BINARY)  # convert to black & white          # TODO:  best threshold values?  was 20,255

            a = copy.deepcopy(bw_image)                       # find contours
            contours, hierarchy = cv2.findContours(a, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)  # find contours

            """ # --------------------------------------------------------------debug
            try:
                cv2.drawContours(a, contours, -1, (100, 0, 0), 1)
                rect0 = cv2.boundingRect(contours[0])
                rect1 = cv2.boundingRect(contours[1])
                rect2 = cv2.boundingRect(contours[2])
            except:
                pass

            pt1 = (rect0[0], rect0[1])
            pt2 = (rect0[0] + rect0[2], rect0[1] + rect0[3])
            cv2.rectangle(a, pt1, pt2, 150, 1)
            try:
                pt1 = (rect1[0], rect1[1])
                pt2 = (rect1[0] + rect1[2], rect1[1] + rect1[3])
                cv2.rectangle(a, pt1, pt2, 150, 1)
            except:
                pass
            try:
                pt1 = (rect2[0], rect2[1])
                pt2 = (rect2[0] + rect2[2], rect2[1] + rect2[3])
                cv2.rectangle(a, pt1, pt2, 150, 1)
            except:
                pass

            both = np.hstack((self.origROIimg, bw_image, a))

            gbl.debugimg(both, outprefix=str(testValue))

            """ # --------------------------------------------------------------------

            if len(contours) == 2:
                return retvalue, bw_image

        # if no setting produced 3 contours, use value of 75
        retvalue, bw_image = cv2.threshold(img, 75, 255, cv2.THRESH_BINARY)

        return retvalue, bw_image


    def getFlyCoords(self, ROIimg, previousCoords):  # returns coordinates of a single fly
        a = copy.deepcopy(ROIimg)
        contours, hierarchy = cv2.findContours(a, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)  # find contours

        """# --------------------------------------------------------------debug
        try:
            cv2.drawContours(a, contours, -1, (100, 0, 0), 1)
            rect0 = cv2.boundingRect(contours[0])
            rect1 = cv2.boundingRect(contours[1])
            rect2 = cv2.boundingRect(contours[2])
        except:
            pass

        pt1 = (rect0[0], rect0[1])
        pt2 = (rect0[0] + rect0[2], rect0[1] + rect0[3])
        cv2.rectangle(a, pt1, pt2, 150, 1)
        try:
            pt1 = (rect1[0], rect1[1])
            pt2 = (rect1[0] + rect1[2], rect1[1] + rect1[3])
            cv2.rectangle(a, pt1, pt2, 150, 1)
        except:
            pass
        try:
            pt1 = (rect2[0], rect2[1])
            pt2 = (rect2[0] + rect2[2], rect2[1] + rect2[3])
            cv2.rectangle(a, pt1, pt2, 150, 1)
        except:
            pass

        both = np.hstack((self.origROIimg, ROIimg, a))

        gbl.debugimg(both)

        """# --------------------------------------------------------------------

        # use the smallest region for the fly
        flyArea = []
        if len(contours) == 3:  # if there's a fly, there will be 3 contours: edge of frame, edge of cell, and fly
            for contour in contours:
                flyArea.append(cv2.contourArea(contour))  # find the area of each contour

            # smallest contour represents the fly
            val, flyidx = min((val, idx) for (idx, val) in enumerate(flyArea))
            # coordinates (x, y, w, h) of a rectangle around the outside of the contour
            fly_rect = cv2.boundingRect(contours[flyidx])

        else:
            return previousCoords  # no fly found. use coords from previous frame so motion = 0

        # use center of rectangle as center of fly.  # TODO: tracking will not account for turning in place
        return ((fly_rect[0] + fly_rect[2] / 2),  # x-coordinate
                (fly_rect[1] + fly_rect[3] / 2))  # y-coordinate

    def calcDistances(self, fly_coords):        # calculate distances travelled in mm
        # ------------------------------------------------------- in one minute increments, tabulate the distances moved
        # AFTER whole video is finished, do calculations

        self.parent.trackedConsoles[self.mon_ID].writemsg('Calculating distances for monitor %d' % self.mon_ID)
        self.parent.trackedConsoles[self.mon_ID].SetFocus()
        distByMinute = []  # this is the tracking data we're producing in pixels per minute
        self.previousFrame = fly_coords[0]
        for self.frameCount in range(0, len(fly_coords), int(60 * self.fps)):  # for each one minute interval
            subsetCoordinates = fly_coords[self.frameCount:(self.frameCount + int(60 * self.fps))]  # get distance value for each ROI
            distByMinute.append(self.getDistances(subsetCoordinates, self.frameCount))  # append to array of distance calculations

        return distByMinute

    def getDistances(self, coords, currentFrame):   # ------------------------- tabulates distance travelled by each fly
        totalDists = np.zeros(len(self.ROIs), dtype=int)     # tabulation of distances travelled in each ROI throughout video
        theseDists = np.zeros(len(self.ROIs))          # array of distances travelled between 2 frames for each ROI

        for thisFrame in coords:
            d_squareds = np.square(np.subtract(self.previousFrame, thisFrame))  # (x1-x2)^2, (y1-y2)^2 for each element
            d_squareds = d_squareds * self.distscale            # convert pixels to distance in mm

            for roiNum in range(0, len(d_squareds)):        # iterate through the ROIs, calculating distances
                flyDist = np.sqrt(d_squareds[roiNum][0] + d_squareds[roiNum][1])  # d = sqrt(x^2 + y^2)

                if flyDist >= 3:          # ignore distances that are this small: could be vibrations or rounding errors
                    theseDists[roiNum] = flyDist
                else:
                    theseDists[roiNum] = 0

            totalDists = totalDists + theseDists   # adds these distances to the running tab

            self.previousFrame = thisFrame                  # store for comparison with next frame
            currentFrame = currentFrame +1                  # keeps track of actual frame number in whole video

        return totalDists

    def colSplit32(self, array):                                                                                        # TODO: didn't fill 2nd file
        self.parent.trackedConsoles[self.mon_ID].writemsg('Splitting monitor %d' % self.mon_ID)                         # TODO: third file not needed
        self.parent.trackedConsoles[self.mon_ID].SetFocus()

        monitorDateTime = self.start_datetime
        oneMinute = wx.TimeSpan(0,1,0,0)
        rownum = 1

        # ----------------------------------------------------------- determine how many files are needed and prep array
        listofFilesContents = []
        moreFilesNeeded = int(math.ceil((len(array) - 10) / 32.0))      # number of additional files needed
        for num in range(0, 1 + moreFilesNeeded):
            listofFilesContents.append([])                            # create an empty list for each file to be created


        # all three files are being generated at the same time by adding 32 elements of the row to each file before going
        # to the next row.
        for rowdata in array:
            # ------------------------------------------------------------------------- create first 10 columns (prefix)
            if rownum <> 1:
                monitorDateTime = monitorDateTime.AddTS(oneMinute)            # get the date and time for this row of data

            prefix = str(rownum) + '\t' + monitorDateTime.Format('%d %b %y')           # column 0 is the row number, column 1 is the date
            prefix = prefix + '\t' + monitorDateTime.Format('%H:%M:%S')                # column 2 is the time
            prefix = prefix + '\t1\t1\t0\t0\t0\t0\t0'                               # next 7 columns are not used but DAMFileScan110X does not take 0000000 or 1111111

            # ------------------------------------ split row into 32 column listofFilesContents and write to the files with the prefix
            #                                           last 32 or fewer columns will be handled after this loop
            for batch in range(0, moreFilesNeeded):
                datastring = prefix                 # start the row with the prefix

                startcol = batch * 32         # calculate start and end columns for this file (rowdata is 0-indexed)
                endcol = startcol + 32

                for number in rowdata[startcol:endcol]:           # add the 32 data values to the row
                    datastring = datastring + '\t%d' % number

                listofFilesContents[batch].append(datastring + '\n')            # append the row to list "listofFilesContents[batch]" for this file

            # ------------------------------------------------------------------ handle last 32 or fewer columns of data
            datastring = prefix

            startcol = (moreFilesNeeded) * 32        # all but one file of data from rowdata has been added  (rowdata is 0-indexed)
            endcol = startcol + len(rowdata)         # include remaining data in this file

            for number in rowdata[startcol:endcol]:                 # add data to the string
                datastring = datastring + '\t%d' % number

            # ------------------------------------------------------- pad with zeros until 32 columns of data are added
            if len(rowdata) != moreFilesNeeded * 32:        # need to pad empty columns with zeroes
                morecols = (moreFilesNeeded+1) * 32 - len(rowdata)        # calculate how many zero columns are needed

                datastring = datastring + '\t' + '\t'.join(list(repeat('0', morecols))) + '\n'      # add the zeros

            listofFilesContents[moreFilesNeeded].append(datastring)  # ----  append data to last batch (0-indexed)

            rownum = rownum +1


        return listofFilesContents          # returns array containing list of all files with their contents

    def tryNewName(self):
        defaultDir = os.path.split(self.outputprefix)[0]
        wildcard = "File Prefix |*.txt|" \
                       "All files (*.*)|*.*"

        dlg = wx.FileDialog(self.parent,
                            message="Choose a different output prefix for Monitor %d ..." % self.mon_ID,
                            defaultDir=defaultDir, wildcard=wildcard, style=wx.SAVE)

        if dlg.ShowModal() == wx.ID_OK:  # show the file browser window
            self.outputprefix = dlg.GetPath()[0:-4]  # get the filepath & name from the save dialog, don't use extension
        else:
            self.outputprefix = ''

        dlg.Destroy()
        return self.outputprefix

    def checkFilenames(self, moreFilesNeeded):       # ----------------------------- gets valid output name and avoids overwriting
        goodname = False
        if not os.path.isdir(os.path.split(self.outputprefix)[0]):          # ------ directory must exist
            self.outputprefix = self.tryNewName()

        while not goodname:                                     # test to see if files will be overwritten
            goodname = True     # assume name is good until proven otherwise
            for batch in range(0, moreFilesNeeded):                             # ------ check for each output file
                outputfile = self.outputprefix + str(batch + 1) + '.txt'  # create a filename for saving

                if goodname  and  os.path.isfile(outputfile):
                    gbl.statbar.SetStatusText('Avoid overwrite: File -> ' + outputfile + ' <- already exists.')
                    winsound.Beep(600, 200)
                    goodname = False

            if not goodname:
                self.outputprefix = self.tryNewName()       # ask for a new prefix

        return self.outputprefix

# ------------------------------------------------------------------------------------------ Stand alone test code
#  insert other classes above and call them in mainFrame
#

class mainFrame(wx.Frame):

    def __init__(self, *args, **kwds):

        wx.Frame.__init__(self, None, id=wx.ID_ANY, size=(1000,200))



        print('done.')

if __name__ == "__main__":

    app = wx.App()
    wx.InitAllImageHandlers()


    frame_1 = mainFrame(None, 0, "")           # Create the main window.
    app.SetTopWindow(frame_1)                   # Makes this window the main window
    frame_1.Show()                              # Shows the main window

    app.MainLoop()                              # Begin user interactions.

#

