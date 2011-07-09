# Copyright 2009-2011 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the `CodeLink` class.

See its documentation for more information.
'''

import os.path

import wx

from garlicsim_wx.general_misc import wx_tools
from garlicsim_wx.widgets.general_misc.cute_hyperlink_ctrl \
                                                       import CuteHyperlinkCtrl


class CodeLink(CuteHyperlinkCtrl):
    
    def __init__(self, technical_details_bar):
        ''' '''
        self.technical_details_bar = technical_details_bar
        CuteHyperlinkCtrl.__init__(self, technical_details_bar)
        #self.ForegroundColour = wx_tools.colors.mix_wx_color(
            #0.333,
            #self.ForegroundColour,
            #self.BackgroundColour
        #)
        self.bind_event_handlers(CodeLink)
        
        
    def refresh(self):
        simpack_metadata = self.technical_details_bar.simpack_info_panel.\
                                      simpack_selection_dialog.simpack_metadata
        self.SetLabel('Show &code' if simpack_metadata is not None else '')
        
    def _on_hyperlink(self, event):
        simpack_metadata = self.technical_details_bar.simpack_info_panel.\
                                      simpack_selection_dialog.simpack_metadata
        assert simpack_metadata is not None
        folder_path = os.path.split(tasted_simpack.__file__)[0]
        os.system(folder_path)
        
        