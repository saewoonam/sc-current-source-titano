# Repo for pyportal titano code that will be used for controlling 8 channel current source
##  Code in the qt_py folder works... Other code is still in development
* This code has been written for the Adafruit QT PY board.   But, it will also work on the titano.
* It uses a different DAC.   Code for the 8 channel DAC needs to be added
##  Description of folders:
-  adafruit-circuitpython-bundle-6.x-mpy-20201126:  has circuit python 6 libraries that correspond to uf2 file
- titano_cpy_v5:  files from titano board that worked with v5 of circuit python
- titano_cpy_v6:  files from titano board that worked wtih v6 of circuit python

## Things to do
* write instructions on how to install code on to bare titano
* Add python code to set current by talking to DAC chip... Difficulty level:  easy
*  write to DAC.txt file on SD card everytime DAC values are changed... Difficulty level: medium
*  Add on/off button for all channels of the current source... Difficulty level: hard

## screenshot
![titano_screenshot](https://github.com/saewoonam/sc-current-source-titano/blob/main/screenshot_titano.png?raw=true)
## useful links:
*  (circuitpython firmware)[https://circuitpython.org/board/pyportal_titano/]
*  (adafruit libraries for circuit python v6) [https://circuitpython.org/libraries]
