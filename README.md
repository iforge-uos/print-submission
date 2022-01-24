# PrintSubmissionApp
*Version Control for 3d print queue app development*

App to submit and order the 3d printing queue, streamline the whole affair. To run, make sure you have all the prerequisites and then run mainapp.py

**As copied from the main app:**

The app: It's written in Python using QT for GUI stuff and Google Sheets for a backend. This keeps data accessible in an easy spreadsheet format for any data analysis people might want to do about the userbase.

**To build:**

You'll need Python 3 (I use 3.7 at the moment) and will need to get some dependencies from pip. These are modules used to access the Google Sheets API, create QT GUIs and authenticate etc..: PYQT5, Gspread, Oauth2client,cython and google-api-python-client  

use `pip3 install pyqt5 gspread oauth2client cython google-api-python-client ldap3` to install prerequisites   

*Features:*

  Automatic formatting of print queue  
  Google drive upload (Can now specify which folder!!!)    
  GUI  
  Tells user position in queue after print upload  
  Only allows supported printers  
  Passive agressive when print is over 10 hours  
  Features can be toggled in Config file  
  Checks for valid emails and full names  
  
*Quirks:*

  Badly written code


*Issues:*

  LDAP required even at beginner level  
  App size updates are broken  
  Colour scheme for rep box is wrong  
  Putting prints on wrong sheet  
  Suggests last few names of users and fills respective details  (broken)  


*Planned features:*

  ETA of print time, eg your print will be ready within X time      
  I would like the same logging system as the login app implemented when a rep signs a print off, tried but failed to implement  
  Interface with print running program (yet to be developed)  
