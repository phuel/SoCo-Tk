import Tkinter as tk

class CurrentTrackViewModel(object):
    def __init__(self):
        self.PropertyChanged = None
        self.__data = {}
    
    def update(self, track):
        self["uri"] = self.__getTrackProperty(track, 'uri')
        self["title"] = self.__getTrackProperty(track, 'title')
        self["album"] = self.__getTrackProperty(track, 'album')
        self["artist"] = self.__getTrackProperty(track, 'artist')
        self["album_art"] = self.__getTrackProperty(track, 'album_art')
        self["duration"] = self.__getTrackProperty(track, 'duration')

    def updateFromEvent(self, entry):
        self["uri"] = entry.resources[0].uri
        self["title"] = entry.title
        self["album"] = entry.album
        self["artist"] = entry.creator
        self["album_art"] = entry.album_art_uri,
        self["duration"] = entry.resources[0].duration
        
    def __getitem__(self, key):
        return self.__data[key]
    
    def __setitem__(self, key, value):
        if not key in self.__data or self.__data[key] != value:
            self.__data[key] = value
            self.__onPropertyChanged(key)

    def __onPropertyChanged(self, propertyName):
        if self.PropertyChanged:
            self.PropertyChanged(propertyName)

    def __getTrackProperty(self, track, item):
        return track[item] if item in track else ""
    
class QueueTrackViewModel(object):
    labelQueue = '%(artist)s - %(title)s'
    
    def __init__(self, entry):
        self.Uri = entry.resources[0].uri
        self.Title = entry.title
        self.Album = entry.album,
        self.Artist = entry.creator
        self.AlbumArt = entry.album_art_uri,
        self.Duration = entry.resources[0].duration

    @property
    def display_name(self):
        text = self.labelQueue % { 'artist' : self.Artist, 'title' : self.Title }
        if self.Duration:
            text += " (%s)" % self.Duration
        return text
