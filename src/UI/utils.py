import logging
from pathlib import Path

filepath = Path(__file__).parent.parent.parent / "logs" / "TUI.log"
print(filepath)

with open(filepath,"w+") as f:
    f.write("")

class CustomAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = self.extra or {}

        
        focusmanager = extra.get("focusmanager",None)
        if focusmanager != None:
            extra.setdefault("class_full_name",focusmanager) #type:ignore
            kwargs.setdefault("extra",extra)
            return '%s' % (msg), kwargs



        class_full_name = str(extra.get("class_full_name",""))
        extra.setdefault("class_full_name",class_full_name)#type:ignore

        

        kwargs.setdefault("extra",extra)
        return '%s' % (msg), kwargs


root_logger_name = "TUI"

def initialize_root_logger():
    root = logging.getLogger(root_logger_name)
    root.setLevel(logging.DEBUG)
    hand = logging.FileHandler(filepath)
    formatter = logging.Formatter(fmt="%(class_full_name)s::%(levelname)s %(message)s")
    hand.setFormatter(formatter)
    root.addHandler(hand)



