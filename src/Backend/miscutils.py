
class Misc:


    @staticmethod
    def cleanScreen():
        print("\n"*20)



    @staticmethod
    def getInt(message):
        while (True):
            i = input(message)
            try:
                num = int(i)
                return num
            except:
                Misc.cleanScreen()
                print("Not a number")
