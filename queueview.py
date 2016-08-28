import Tkinter as tk
import logging, traceback
from verticalscrolledframe import VerticalScrolledFrame
from queuetrackview import QueueTrackView

class QueueView(VerticalScrolledFrame):
    def __init__(self, parent):
        VerticalScrolledFrame.__init__(self, parent)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.__viewModel = None
        self.__speaker = None
        self.__tracks = []

    def attachViewModel(self, viewModel, speaker):
        self.__viewModel = viewModel
        self.__speaker = speaker
        self.__viewModel.addListener(self.__onPropertyChanged)
        self.__showQueue(self.__viewModel['entries'])

    def detachViewModel(self):
        if self.__viewModel:
            self.__viewModel.removeListener(self.__onPropertyChanged)
        self.__viewModel = None
        self.__speaker = None

    def __onPropertyChanged(self, propertyName, viewModel):
        if propertyName == 'entries':
            self.__showQueue(viewModel[propertyName])

    def __showQueue(self, queue):
        self.__clear()

        logging.debug('Inserting items (%d) to listbox', len(queue))
        for item in queue:
            trackView = QueueTrackView(self.interior, item)
            self.__tracks.append(trackView)

#        index = self.__speaker.getCurrentTrackIndex()
#        if index >= 0:
#            self._queuebox.selection_clear(0, tk.END)
#            self._queuebox.selection_anchor(index)
#            self._queuebox.selection_set(index)

    def __clear(self):
        logging.debug('Deleting old items')
        for track in self.__tracks:
            track.destroy()

    def _playSelectedQueueItem(self, evt):
        try:
            track_index = self.__getSelectedQueueItem()

            if track_index is None:
                logging.warning('Could not get track')
                return
            
            self.__speaker.play_from_queue(track_index)
        except:
            logging.error('Could not play queue item')
            logging.error(traceback.format_exc())

    def __getSelectedQueueItem(self):
#        selection = self._queuebox.curselection()
#        if not selection:
            return None

#        return int(selection[0])
