class ViewModelBase(object):
    """ The base class for view models. """

    def __init__(self):
        """ Constructor. """
        self.__propertyChanged = []
        self.__data = {}

    def addListener(self, func):
        """ Add a handler for PropertyChanged events. """
        self.__propertyChanged.append(func)
    
    def removeListener(self, func):
        """ Remove a handler for PropertyChanged events. """
        self.__propertyChanged.remove(func)

    def __getitem__(self, key):
        """ Get a property value from this view model. """
        return self.__data[key]
    
    def __setitem__(self, key, value):
        """ Set a property value on this view model. """
        if not key in self.__data or self.__data[key] != value:
            self.__data[key] = value
            self.__onPropertyChanged(key)

    def __onPropertyChanged(self, propertyName):
        """ Call the PropertyChanged handlers. """
        for func in self.__propertyChanged:
            func(propertyName, self)
