class ErrorHandler:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if ErrorHandler._instance is None: 
            ErrorHandler._instance = super().__new__(cls, *args, **kwargs) 
        return ErrorHandler._instance
    
    def __init__(self):
        pass

    def notify(self, msg="", critical=True):
        print("Notify: {}".format(msg))
        if critical: exit(1)