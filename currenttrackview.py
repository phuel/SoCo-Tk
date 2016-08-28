import logging, traceback
import Tkinter as tk

from albumimageprovider import AlbumImageProvider
from progressmeter import Meter

try:
    from PIL import Image, ImageTk
except:
    logging.error('Could not import PIL')
    logging.error(traceback.format_exc())
    ImageTk = None
    Image = None

class CurrentTrackView(tk.Frame):

    def __init__(self, parent, settings):
        tk.Frame.__init__(self, parent)

        self.columnconfigure(1, weight = 1)

        self.__images = AlbumImageProvider(settings)

        self.empty_info = '-'
        self.__parent = parent
        self._labels = {}
        self.__image = None
        infoIndex = 0

        ###################################
        # Title
        ###################################
        label = tk.Label(self, text = 'Title:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels['title'] = tk.Label(self,
                                         anchor = 'w')
        
        self._labels['title'].grid(row = infoIndex,
                                   column = 1,
                                   padx = 5,
                                   pady = 5,
                                   sticky = 'we')
        infoIndex += 1

        ###################################
        # Artist
        ###################################
        label = tk.Label(self, text = 'Artist:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels['artist'] = tk.Label(self,
                                          anchor = 'w')
        
        self._labels['artist'].grid(row = infoIndex,
                                    column = 1,
                                    padx = 5,
                                    sticky = 'we')
        infoIndex += 1

        ###################################
        # Album
        ###################################
        label = tk.Label(self, text = 'Album:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels['album'] = tk.Label(self,
                                         anchor = 'w')
        
        self._labels['album'].grid(row = infoIndex,
                                   column = 1,
                                   padx = 5,
                                   pady = 5,
                                   sticky = 'we')
        infoIndex += 1

        ###################################
        # Album art
        ###################################
        self._album_art = tk.Label(self,
                                   image = tk.PhotoImage(),
                                   width = 150,
                                   height = 150)
        
        self._album_art.grid(row = infoIndex,
                             column = 0,
                             columnspan = 2,
                             padx = 5,
                             pady = 5)
        infoIndex += 1

        ###################################
        # Position
        ###################################
        label = tk.Label(self, text = 'Position:')
        label.grid(row = infoIndex,
                   column = 0,
                   sticky = 'w')
        
        self._labels['position'] = Meter(self, fillcolor='darkgray', bg='lightgray', relief="sunken", bd=1, height=14, text="")
        self._labels['position'].grid(row = infoIndex,
                                      column = 1,
                                      padx = 5,
                                      pady = 5,
                                      sticky = 'we')
 
    def clearImage(self):
        self.__showAlbumArt(None)
        
    def attachViewModel(self, viewModel):
        self.__viewModel = viewModel
        self.__viewModel.addListener(self.__onPropertyChanged)
    
    def detachViewModel(self):
        if self.__viewModel:
            self.__viewModel.removeListener(self.__onPropertyChanged)
            self.__viewModel = None
        for label in self.__labels:
            label.configure(text = self.empty_info)
        self.clearImage()

    def __onPropertyChanged(self, propertyName, viewModel):
        if propertyName == 'position':
            if viewModel['duration'] and viewModel['position']:
                showHours = viewModel['duration'].seconds > 3600
                position = self.__formatDuration(viewModel['position'], showHours) + " / " + self.__formatDuration(viewModel['duration'], showHours)
                self._labels[propertyName].set(value=viewModel['position'].total_seconds() / viewModel['duration'].total_seconds(), text=position)
            else:
                self._labels[propertyName].set(value=0, text="")
        elif propertyName in self._labels:
            value = viewModel[propertyName]
            self._labels[propertyName].configure(text=value)
        elif propertyName == 'album_art':
            image = self.__images.getImage(viewModel['uri'], viewModel['album_art'])
            self.__showAlbumArt(image)
    
    def __formatDuration(self, time, showHours):
        hours, remainder = divmod(time.seconds, 3600)
        minutes, seconds = divmod(remainder, 60) 
        if showHours:
            return "%d:%02d:%02d" % (hours, minutes, seconds)
        return "%d:%02d" % (minutes, seconds)

    def __showAlbumArt(self, image):
        if image is None:
            self._album_art.config(image = None)
            self.__image = None
            return

        widgetConfig = self._album_art.config()
        thumbSize = (int(widgetConfig['width'][4]),
                     int(widgetConfig['height'][4]))

        logging.debug('Resizing album art to: %s', thumbSize)
        image.thumbnail(thumbSize, Image.ANTIALIAS)
        self.__image = ImageTk.PhotoImage(image = image)
        self._album_art.configure(image = self.__image)
