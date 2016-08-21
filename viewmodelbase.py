class ViewModelBase(object):
    def __init__(self):
        self.__propertyChanged = []
        self.__data = {}

    def addListener(self, func):
        self.__propertyChanged.append(func)
    
    def removeListener(self, func):
        self.__propertyChanged.remove(func)

    def __getitem__(self, key):
        return self.__data[key]
    
    def __setitem__(self, key, value):
        if not key in self.__data or self.__data[key] != value:
            self.__data[key] = value
            self.__onPropertyChanged(key)

    def __onPropertyChanged(self, propertyName):
        for func in self.__propertyChanged:
            func(propertyName, self)
