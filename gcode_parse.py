import re  # for searching
import datetime  # for time formatting


def run(fileName, short):
    parameters = {"name": None,
                  "email": None,
                  "filename": None,
                  "time_taken": None,
                  "filament_used": {},
                  "project_type": None,
                  "date_added": None,
                  "rep_check": None,
                  "status": None,
                  "printer_type": None,
                  "path": None,
                  "order": ["name",
                            "email",
                            "filename",
                            "time_taken",
                            "filament_used",
                            "project_type",
                            "date_added",
                            "rep_check",
                            "status",
                            "printer_type",
                            "path"]
                  }

    date = datetime.datetime.now()

    parameters["date_added"] = str(date.strftime("%d/%m/%Y %H:%M:%S"))

    # times in hh:mm:ss
    # lengths in metres
    # volumes in cm^3
    # dates in dd/mm/yyyy

    parameters["path"] = fileName
    parameters["filename"] = short
    increment = 0
    with open(fileName, "r", encoding="utf8") as myfile:  # open file that was handed to function
        for line in myfile:
            increment += 1
        print(increment)

    with open(fileName, "r", encoding="utf8") as myfile:  # open file that was handed to function
        for line in myfile:  # Read gcode line by line checking for things
            if parameters["printer_type"] and parameters["time_taken"] and len(parameters["filament_used"]) == 3:
                break

            if not parameters["printer_type"]:
                if re.search("iForge Ultimaker", line):  # this whole section could be cleaner
                    # if parameters["printer_type"]=="printer_type" and re.search("UltiG",line) : #this whole section could be cleaner
                    print("Ultimaker")
                    parameters["printer_type"] = "Ultimaker"

                elif re.search("iForge Prusa", line):
                    parameters["printer_type"] = "Prusa"
                    print("Prusa Identified")

                # Generic catch to see if the print is a non iForge but still prusa print
                elif re.search("Prusa", line):
                    parameters["printer_type"] = "Exotic_Prusa"
                    print("Prusa Identified")

                # Bodge to catch the iForge PETG profile, this will be done slightly better in future hopefully
                elif re.search("iForge Prusa PETG", line):
                    parameters["printer_type"] = "Exotic_Prusa"
                    print("Prusa Identified")

            if not parameters["time_taken"] and re.search("(normal mode)", line):

                times = {'d': 0, 'h': 0, 'm': 0, 's': 0}
                for elem in times.keys():
                    pattern = f"\d+(?={elem}\s)"
                    tmp = re.findall(pattern, line)
                    if tmp:
                        times[elem] = int(tmp[0])

                # time = f"{times['d'] * 24 + times['h']:02d}:{times['m']:02d}:{times['s']:02d}"  # Formatting to ensure two digits in minutes and seconds

                # format time_taken in seconds
                time = times['s'] + times['m'] * 60 + times['h'] * 3600 + times['d'] * 86400

                parameters["time_taken"] = time

            if len(parameters["filament_used"]) != 3 and re.search("(?<=; filament used \[)\w+(?=\])", line):
                # some regex optimisation :)

                # get mm/cm3/g string from line
                key = re.findall("(?<=; filament used \[)\w+(?=\])", line)[0]
                # get value from line
                parameters["filament_used"][key] = float(re.findall("(?<=\s=\s)\d+\.*\d*", line)[0])

                # if re.search("mm", line):
                #     print(12)
                #     search = list(map(float, re.findall('[-+]?\d*\.\d+|\d+', line)))
                #     print(search)
                #     length = round(search[0] / 1000, 2)
                #     print(length)
                #     parameters["filament_used"] = length
                #     volume = round(length * 3.1415 * (1.75 / 2) ** 2, 2)
                #     print(volume)

    parameters["status"] = "Uploading"
    error = False

    if not (parameters["printer_type"] and parameters["time_taken"] and len(parameters["filament_used"]) == 3):
        print("Malformed Gcode, please reslice. parameters:")
        print(parameters)
        parameters["printer_type"] = "non_iforge"
        error = True
    print(parameters["printer_type"])
    return parameters, error
