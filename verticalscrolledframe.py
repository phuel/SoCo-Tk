# -*- coding: utf-8 -*-

from Tkinter import *

# Based on: http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
 
     * Use the 'interior' attribute to place widgets inside the scrollable frame
     * Construct and pack/place/grid normally
     * This frame only allows vertical scrolling
     
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            
 
        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=self.vscrollbar.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.ScrollTop()

        # create a frame inside the canvas which will be scrolled with it
        self.interior = Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior, anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        self.interior.bind('<Configure>', self.cb_configure_interior)
        self.canvas.bind('<Configure>', self.cb_configure_canvas)

    def ScrollTop(self):
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        
    def cb_configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())
        
    def cb_configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
