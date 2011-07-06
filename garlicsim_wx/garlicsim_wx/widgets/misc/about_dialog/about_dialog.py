# Copyright 2009-2011 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the `AboutDialog` class.

See its documentation for more info.
'''

import time
import webbrowser

import pkg_resources
import wx.html

from garlicsim_wx.general_misc import wx_tools
import garlicsim_wx.general_misc.cute_timer
from garlicsim_wx.widgets.general_misc.cute_dialog import CuteDialog
from garlicsim_wx.widgets.general_misc.cute_html_window import CuteHtmlWindow
from garlicsim_wx.widgets.general_misc.cute_window.bind_savvy_window import \
                                              name_parser as name_parser_module

import garlicsim_wx
from .bitmap_viewer import BitmapViewer

from . import images as __images_package
images_package = __images_package.__name__


class AboutDialog(CuteDialog):
    '''
    An About dialog for GarlicSim.
    
    The dialog explains what GarlicSim does and shows the license and version
    number.
    '''

    _BindSavvyWindowType__name_parser = name_parser_module.NameParser(
        (name_parser_module.LowerCase, name_parser_module.CamelCase),
        n_preceding_underscores_possibilities=(0, 2,)
    )
    
    def __init__(self, frame):
   
        CuteDialog.__init__(self, frame, title='About GarlicSim')
        
        self.ExtraStyle &= ~wx.FRAME_EX_CONTEXTHELP
        
        self.frame = frame

        v_sizer = wx.BoxSizer(wx.VERTICAL)
        

        self._original_image = wx.ImageFromStream(
            pkg_resources.resource_stream(
                images_package,
                'about.png'
            )
        )
        
        self.bitmap_viewer = BitmapViewer(self, size=(597, 231))
        v_sizer.Add(self.bitmap_viewer, 0)
        
        self.html_window = CuteHtmlWindow(
            self,
            size=(597, 290 if wx_tools.is_gtk else 250)
        )
        v_sizer.Add(self.html_window, 0)
        
        foreground_color_in_hex = wx_tools.colors.wx_color_to_html_color(
            wx_tools.colors.get_background_color()
        )
        background_color_in_hex = wx_tools.colors.wx_color_to_html_color(
            wx.Colour(0, 0, 0)
        )
        
        
        self.html_window.SetPage(
            '''
            <html>
              <head>
                <style type="text/css">
                  body {
                    font-size: 80%%;
                  }
                </style>
              </head>
              <body bgcolor="%s" color="%s">
                <div align="center"> <font size="1">
                  &copy; 2009-2011 Ram Rachum (a.k.a. cool-RR)
                  <br />            
                  This program is distributed under the LGPL2.1 license.
                  <br />
                </font></div>
                <div> 
                  GarlicSim is a platform for writing, running and
                  analyzing computer simulations. It is general enough to
                  handle any kind of simulation: Physics, game theory,
                  epidemic spread, electronics, etc.<br />
                  <font size="1"><br /></font>
                  <b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Version %s</b>
                  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Website:
                  <a href="http://garlicsim.org">http://garlicsim.org</a>
                </div>
                <div>
                  <font size="1"><br /></font>
                  I would like to thank the open source community for
                  making this program possible. This includes the
                  developers of Python, Psyco, wxPython, wxWidgets,
                  Mayavi, git, and so many others... And more thanks to
                  the many people who spent many hours helping me out
                  with various issues, on mailing lists such as
                  wxpython-users and on the StackOverflow website.
                </div>
              </body>
            </html>
            ''' % (
                    foreground_color_in_hex,
                    background_color_in_hex,
                    garlicsim_wx.__version__
                )
        )

        
        self.button_sizer = button_sizer = wx.StdDialogButtonSizer()
        self.OkButton = wx.Button(self, wx.ID_OK,
                                   "&Let's get back to simulating!")
        self.OkButton.SetDefault()
        button_sizer.SetAffirmativeButton(self.OkButton)
        button_sizer.AddButton(self.OkButton)
        button_sizer.Realize()
        button_sizer.SetMinSize((500, -1))
        v_sizer.Add(button_sizer, 0, wx.BOTTOM, border=10)
        
        self.SetSizerAndFit(v_sizer)
        self.Layout()
        
        self.Timer = garlicsim_wx.general_misc.cute_timer.CuteTimer(self)
        self.Timer.Start(40, oneShot=True)
        
        self._rotate_image_hue()
        
        self.bind_event_handers(AboutDialog)

        
    def OnOkButton(self, event):
        self.EndModal(wx.ID_OK)

        
    def OnTimer(self, event):
        self._rotate_image_hue()

        
    def _rotate_image_hue(self):
        '''Rotate the image's hue by a tiny bit.'''
        new_image = self._original_image.Copy()
        t = time.time()
        new_image.RotateHue((t / 50.) % 1)
        self.bitmap_viewer.set_bitmap(wx.BitmapFromImage(new_image))
        self.Timer.Start(40, oneShot=True)

        
    def ShowModal(self):
        wx.CallAfter(self.OkButton.SetFocus)
        CuteDialog.ShowModal(self)
        
        
    def EndModal(self, *args, **kwargs):
        self.Timer.Stop()
        wx.Dialog.EndModal(self, *args, **kwargs)

        