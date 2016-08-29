import Tkinter as tk
import tkFont

import keynames as kn

class QueueTrackView(tk.Frame):
    """ The view for a single track in the queue. """

    def __init__(self, parent, viewModel):
        """ Constructor """
        tk.Frame.__init__(self, parent)

        self.__viewModel = viewModel
        self.__defaultBackground = self.cget('background')

        self.grid_columnconfigure(1, weight=1)
        self.bind('<Button-1>', self.cb_selectEntry)
        label = tk.Label(self, text="%d." % viewModel[kn.index], width=3, anchor=tk.E)
        label.bind('<Button-1>', self.cb_selectEntry)
        label.grid(row=0, column=0, sticky=tk.E)
        label = tk.Label(self, text=viewModel[kn.title], anchor=tk.W)
        label.bind('<Button-1>', self.cb_selectEntry)
        label.configure(font=self.__createBoldFont(label['font']))
        label.grid(row=0, column=1, columnspan=2, sticky=tk.E+tk.W)
        label = tk.Label(self, text=viewModel[kn.artist], anchor=tk.W)
        label.bind('<Button-1>', self.cb_selectEntry)
        label.grid(row=1, column=1, sticky=tk.E+tk.W)
        if viewModel['duration']:
            label = tk.Label(self, text="(%s)" % viewModel[kn.duration], anchor=tk.W)
            label.bind('<Button-1>', self.cb_selectEntry)
            label.grid(row=1, column=2, sticky=tk.E+tk.W)
        self.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        self.__showSelectionState(viewModel[kn.selected])
        self.__viewModel.addListener(self.__onPropertyChanged)
    
    def destroy(self):
        """ Destroy the view and detach the event handler. """
        self.__viewModel.removeListener(self.__onPropertyChanged)
        tk.Frame.destroy()

    def __onPropertyChanged(self, propertyName, viewModel):
        """ Update the view after changes in the view model. """
        if propertyName == kn.selected:
            self.__showSelectionState(viewModel[propertyName])

    def __createBoldFont(self, font):
        """ Create a bold font from the specified font. """
        font = tkFont.Font(font=font)
        font.configure(weight='bold', size=10)
        return font

    def __showSelectionState(self, state):
        """ Set the selection state of this view. """
        color = self.__defaultBackground
        if state:
            color = 'darkgray'
        self.configure(background=color)
        for control in self.winfo_children():
            control.configure(background=color)
    
    def cb_selectEntry(self, evt):
        """ Handle the click event on this view. """
        self.__viewModel.selectAndPlay()
