import datetime

from viewmodelbase import ViewModelBase 

class CurrentTrackViewModel(ViewModelBase):
    """ Viemodel for the current track. """
    
    def __init__(self):
        """ Constructor """
        ViewModelBase.__init__(self)
        self.__startPos = datetime.timedelta()
        self.__startTime = None
        self.__clear()

    def update(self, entry, baseUri):
        """ Update the view model content from an event. """
        if not entry:
            self.__clear()
            return
        self['uri'] = entry.resources[0].uri
        self['item_id'] = entry.item_id
        self['title'] = entry.title
        self['album'] = entry.album
        self['artist'] = entry.creator
        albumArt = entry.album_art_uri
        if not albumArt.startswith("http"):
            albumArt = baseUri + albumArt
        self['album_art'] = albumArt
        self['duration'] = self.__parseTime(entry.resources[0].duration)

    def start(self, position):
        """ Mark the start position for the playing track. """
        self.__startPos = self.__parseTime(position)
        self['position'] = self.__startPos
        self.__startTime = datetime.datetime.now()
    
    def updatePosition(self):
        """ Update the position for the playing track. """
        now = datetime.datetime.now()
        diff = now - self.__startTime
        self['position'] = self.__startPos + diff

    def __clear(self):
        """ Clear the content of the view model. """
        self['uri'] = ""
        self['title'] = ""
        self['album'] = ""
        self['artist'] = ""
        self['album_art'] = ""
        self['duration'] = ""
        self['position'] = 0

    def __parseTime(self, time):
        """ Parse a time stamp. """
        if not time:
            return datetime.timedelta()
        hour, minute, second = time.split(":")
        return datetime.timedelta(hours=int(hour), minutes=int(minute), seconds=int(second))
    
    def __getTrackProperty(self, track, item):
        """ Get a property fom a track or an empty string. """
        return track[item] if item in track else ""
    