import subprocess
import cv2

cmd = "readlink -f /dev/CAMC"
process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

# output of form /dev/videoX
out = process.communicate()[0]

# parse for ints
nums = [int(x) for x in out if x.isdigit()]

cap = cv2.VideoCapture(nums[0])
