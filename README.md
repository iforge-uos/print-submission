# PrintSubmissionApp
*Version Control for 3d print queue app development*

App to submit and order the 3d printing queue, this was created in 2018 to replace a paper spreadsheet and streamline the whole affair. 

**As copied from the old sign-in app:**

The app: It's written in Python using QT for GUI stuff and Google Sheets for a backend. This keeps data accessible in an easy spreadsheet format for any data analysis people might want to do about the userbase.

**To build:**

You'll need Python 3 and will need to get some dependencies from pip. These are modules used to access the Google Sheets API, create QT GUIs and authenticate etc.  

To run, make sure you have all the prerequisites. Use the requirements file and your IDE to achieve this. 
When up to date and ready run main.py.

*Features:*

  Automatic formatting of print queue  
  Google drive upload    
  GUI  
  Tells user position in queue after print upload  
  Only allows supported printers  
  Passive agressive when print is over 10 hours   
  Checks for valid emails and full names  
  Interfaces with kiosk system
  
*Quirks:*

  Does not adhere to PEP 8
  Registration involves copying from LDAP 


*Issues:*

  Poor compatibility for non 1080p devices     


*Planned features:*

  ETA of print time, eg your print will be ready within X time      
  I would like the same logging system as the login app implemented when a rep signs a print off, tried but failed to implement   
  
*Contributors:*

Alistair Mitchell - Initial creation of program (2018) and writer of base code to achieve all functionality up to 2021 with majority still valid in 2022.  
Sam Rhodes - Minor visual changes (2020)  
Harry Merckel & Dom Rugg-Gunn - Contribution of better coding practice and rewrite of some modules to use better techniques. Adjusted code to interface better with kiosk system (2022)  
Sam Piper & CT - Minor updates and changes as well as stewardship (2023)  
Eromu Ehwerhemepha - Present individual handling development  
