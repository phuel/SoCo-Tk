import Tkinter as tk
import tkFont

class QueueTrackView(tk.Frame):
    def __init__(self, parent, viewModel):
        tk.Frame.__init__(self, parent)

        self.__viewModel = viewModel
        self.__defaultBackground = self.cget('background')

        self.grid_columnconfigure(1, weight=1)
        self.bind('<Button-1>', self.cb_selectEntry)
        label = tk.Label(self, text="%d." % viewModel['index'], width=3, anchor=tk.E)
        label.bind('<Button-1>', self.cb_selectEntry)
        label.grid(row=0, column=0, sticky=tk.E)
        label = tk.Label(self, text=viewModel['title'], anchor=tk.W)
        label.bind('<Button-1>', self.cb_selectEntry)
        label.configure(font=self.__createBoldFont(label['font']))
        label.grid(row=0, column=1, columnspan=2, sticky=tk.E+tk.W)
        label = tk.Label(self, text=viewModel['artist'], anchor=tk.W)
        label.bind('<Button-1>', self.cb_selectEntry)
        label.grid(row=1, column=1, sticky=tk.E+tk.W)
        if viewModel['duration']:
            label = tk.Label(self, text="(%s)" % viewModel['duration'], anchor=tk.W)
            label.bind('<Button-1>', self.cb_selectEntry)
            label.grid(row=1, column=2, sticky=tk.E+tk.W)
        self.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        self.__showSelectionState(viewModel['selected'])
        self.__viewModel.addListener(self.__onPropertyChanged)
    
    def destroy(self):
        self.__viewModel.removeListener(self.__onPropertyChanged)
        tk.Frame.destroy()

    def __onPropertyChanged(self, propertyName, viewModel):
        if propertyName == 'selected':
            self.__showSelectionState(viewModel[propertyName])

    def __createBoldFont(self, font):
        font = tkFont.Font(font=font)
        font.configure(weight='bold', size=10)
        return font

    def __showSelectionState(self, state):
        color = self.__defaultBackground
        if state:
            color = 'darkgray'
        self.configure(background=color)
        for control in self.winfo_children():
            control.configure(background=color)
    
    def cb_selectEntry(self, evt):
        self.__viewModel.selectAndPlay()
