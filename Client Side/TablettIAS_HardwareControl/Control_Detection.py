from HardwareList import HardwareList


class Control_Detection:



    def __init__(self, dict_detection , invertvalue):
        self.dict_detection = dict_detection
        self.invertvalue = invertvalue

    def initialise_det(self):
        for x in self.dict_detection:
            HardwareList.initialise_pin(self.dict_detection.get(x))

    def get_magazines_in_Dispenser(self):
        dictMags = {"status" : {}}
        digtStatus = dictMags.get("status" , None)
        count_mags = 0
        count_mags_positioned = 0
        inposition = 0

        for weekday in self.dict_detection:
            count_mags = count_mags+1
            value = HardwareList.getValue(self.dict_detection.get(weekday)) ^ self.invertvalue
            digtStatus.update({weekday: value})
            if value == 1:
                count_mags_positioned = count_mags_positioned+1

        if count_mags_positioned == count_mags:
            inposition = 1

        dictMags.update({"inposition" : inposition})

        return dictMags
        

    def get_magazine_weekday(self , weekday_short):
        return HardwareList.getValue(self.dict_detection.get(weekday_short) ^ self.invertvalue)
