""" Global Variable Declarations """

# ----------------------------------------------------------------------------   Imports
import wx                               # GUI controls
import os                               # system controls
from os.path import expanduser          # get user's home directory
import datetime                         # date and time handling functions
import sys
import cPickle


exec_dir = sys.path[0]    # folder containing the scripts for this program


# -------------------------------------------------- nicknames for general configuration parameters
global monitors, \
    webcams, \
    thumb_size, \
    thumb_fps, \
    cfg_path, \
    thumbPanels, \
    trackers

monitors = 1
webcams = 1
thumb_size = (320,240)
thumb_fps = 5
cfg_path = os.path.join(expanduser('~'), 'PySolo_Files')

thumbPanels = ['']                  # list of thumbnail panels used in scrolled window on configuration page
                                                 # element 0 identifies the type of list

trackers = []                       # list of trackers for acquiring data.  index does not match cfg_dict
                                                # since not all monitors are necessarily tracked

# -------------------------------------------------- nicknames for monitor configuration for **current** mon_ID
global mon_ID, \
    mon_name, \
    source_type, \
    source, \
    source_fps, \
    preview_size, \
    preview_fps, \
    issdmonitor, \
    start_datetime, \
    track, \
    track_type, \
    mask_file, \
    data_folder

mon_ID = 1   # always at least one monitor.  use it to initialize
mon_name = 'Monitor1'
source_type = 0
source = 'Webcam1'
source_fps = 0.5
preview_size = (480, 480)
preview_fps = 1
issdmonitor = False
start_datetime = wx.DateTime_Now()
track_type = 0
track = True
mask_file = 'None'
data_folder = os.path.join(expanduser('~'), 'PySolo_Files')

# -------------------------------------------------------------- nicknames for video Monitor and ROIs
global previewPanel, \
        ROIs, \
        showROIs

previewPanel = None
ROIs = []
showROIs = False


# --------------------------------------------------------------------- cfg_dict contains all configuration settings
global cfg_dict

cfg_dict = [{                                               # create the default config dictionary
        'monitors'      : monitors,                        # element 0 is the options dictionary
        'webcams'       : webcams,                        # number of webcams available, not necessarily in use
        'thumb_size'    : thumb_size,
        'thumb_fps'     : thumb_fps,
        'cfg_path'      : cfg_path
        },
        {                                       # all additional elements are the monitor dictionaries (1-indexed)
        'mon_name'      : mon_name,                 # include one default monitor of a camera in default config
        'source_type'   : source_type,
        'source'        : source,
        'source_fps'    : source_fps,
        'preview_size'  : preview_size,
        'preview_fps'   : preview_fps,
        'issdmonitor'   : issdmonitor,
        'start_datetime': start_datetime,
        'track'         : track,
        'track_type'    : track_type,
        'mask_file'     : mask_file,
        'data_folder'   : data_folder
        }]


# ---------------------------------------------------------------- functions needed by multiple classes

def correctType(r, key):
    """
    changes string r into appropriate type (int, datetime, tuple, etc.)
    """

    if key == 'start_datetime':  # order of conditional test is important! do this first!
        if type(r) == type(wx.DateTime.Now()):
            pass
        elif type(r) == type(''):  # string -> datetime value
            try:
                r = string2wxdatetime(r)
            except:
                r = wx.DateTime.Now()
        elif type(r) == type(datetime.datetime.now()):
            try:
                r = pydatetime2wxdatetime(r)
            except:
                r = wx.DateTime.Now()
        else:
            r = wx.DateTime.Now()
            print('$$$$$$ could not interpret start_datetime value')
            return r

        return r

    if r == 'None' or r is None:  # None type
        r = None
        return r

    # look for string characteristics to figure out what type they should be
    if r == 'True' or r == 'False':  # boolean
        if r == 'False':
            r = False
        elif r == 'True':
            r = True

        return r

    try:
        int(r) == int(0)  # int
        return int(r)
    except Exception:
        pass

    try:
        float(r) == float(1.1)  # float
        return float(r)
    except Exception:
        pass

    if ',' in r:  # tuple of two integers
        if not '(' in r:
            r = '(' + r + ')'
        r = tuple(r[1:-1].split(','))
        r = (int(r[0]), int(r[1]))

        return r

    return r  # all else has failed:  return as string

def loadROIs(mask_file):
    if mask_file is None:
        return False  # there is no mask file

    if os.path.isfile(mask_file):  # if mask file is there, try to load ROIs
        try:
            cf = open(mask_file, 'r')  # read mask file
            ROItuples = cPickle.load(cf)  # list of 4 tuple sets describing rectangles on the image
            cf.close()
        except:
            print('Mask failed to load')
            return False

    ROIs = []
    for roi in ROItuples:  # complete each rectangle by adding first coordinate to end of list
        roiList = []  # clear for each rectangle
        for coordinate in roi:  # add each coordinate to the list for the rectangle
            roiList.append(coordinate)
        roiList.append(roi[0])
        ROIs.append(roiList)  # add the rectangle lists to the list of ROIs

    if not ROIs:
        showROIs = False

    return ROIs

def pydatetime2wxdatetime(pydt):  # ---------------------- convert python datetime.datetime to wx.datetime
    dt_iso = pydt.isoformat()
    wxdt = wx.DateTime()
    wxdt.ParseISOCombined(dt_iso, sep='T')
    return wxdt

def string2wxdatetime(strdt):  # ---------------------------------------- convert string to wx.datetime
    wxdt = wx.DateTime()
    wxdt.ParseDateTime(strdt)
    return wxdt

def wxdatetime2string(datetime):
    strdt = datetime.FormatISOTime()
    return strdt