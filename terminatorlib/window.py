#!/usr/bin/python
# Terminator by Chris Jones <cmsj@tenshu.net>
# GPL v2 only
"""window.py - class for the main Terminator window"""

import pygtk
pygtk.require('2.0')
import gobject
import gtk

from util import dbg, err

from container import Container

try:
    import deskbar.core.keybinder as bindkey
except ImportError:
    err('Unable to find python bindings for deskbar, "hide_window" is not' \
            'available.')

class Window(Container, gtk.Window):
    """Class implementing a top-level Terminator window"""

    title = None
    isfullscreen = None
    ismaximised = None
    hidebound = None
    hidefunc = None

    def __init__(self, configobject):
        """Class initialiser"""
        Container.__init__(self, configobject)
        gtk.Window.__init__(self)
        gobject.type_register(Window)
        self.register_signals(Window)

        self.set_property('allow-shrink', True)
        self.register_callbacks()
        self.apply_config()

    def register_callbacks(self):
        """Connect the GTK+ signals we care about"""
        self.connect('key-press-event', self.on_key_press)
        self.connect('delete_event', self.on_delete_event)
        self.connect('destroy', self.on_destroy_event)
        self.connect('window-state-event', self.on_window_state_changed)

        # Attempt to grab a global hotkey for hiding the window.
        # If we fail, we'll never hide the window, iconifying instead.
        try:
            self.hidebound = bindkey.tomboy_keybinder_bind(
                self.config['keybindings']['hide_window'],
                self.on_hide_window)
        except NameError:
            pass

        if not self.hidebound:
            dbg('Unable to bind hide_window key, another instance has it.')
            self.hidefunc = self.iconify
        else:
            self.hidefunc = self.hide

    def apply_config(self):
        """Apply various configuration options"""
        self.set_fullscreen(self.config['fullscreen'])
        self.set_maximised(self.config['maximised'])
        self.set_borderless(self.config['borderless'])
        self.set_real_transparency(self.config['enable_real_transparency'])
        if self.hidebound:
            self.set_hidden(self.config['hidden'])
        else:
            self.set_iconified(self.config['hidden'])

    def on_key_press(self, window, event):
        """Handle a keyboard event"""
        pass

    def on_delete_event(self, window, event, data=None):
        """Handle a window close request"""
        pass

    def on_destroy_event(self, widget, data=None):
        """Handle window descruction"""
        pass

    def on_hide_window(self, data):
        """Handle a request to hide/show the window"""
        pass

    def on_window_state_changed(self, window, event):
        """Handle the state of the window changing"""
        self.isfullscreen = bool(event.new_window_state & 
                                 gtk.gdk.WINDOW_STATE_FULLSCREEN)
        self.ismaximised = bool(event.new_window_state &
                                 gtk.gdk.WINDOW_STATE_MAXIMIZED)
        dbg('window state changed: fullscreen %s, maximised %s' %
            (self.isfullscreen, self.ismaximised))

        return(False)

    def set_maximised(self, value):
        """Set the maximised state of the window from the supplied value"""
        if value == True:
            self.maximize()
        else:
            self.unmaximize()

    def set_fullscreen(self, value):
        """Set the fullscreen state of the window from the supplied value"""
        if value == True:
            self.fullscreen()
        else:
            self.unfullscreen()

    def set_borderless(self, value):
        """Set the state of the window border from the supplied value"""
        self.set_decorated (not value)

    def set_hidden(self, value):
        """Set the visibility of the window from the supplied value"""
        pass

    def set_iconified(self, value):
        """Set the minimised state of the window from the value"""
        pass

    def set_real_transparency(self, value):
        """Enable RGBA if supported on the current screen"""
        screen = self.get_screen()
        if value:
            colormap = screen.get_rgba_colormap()
        else:
            colormap = screen.get_rgb_colormap()

        if colormap:
            self.set_colormap(colormap)

# Temporary config object until that code is refactored
CONFIG = {'fullscreen':False, 
          'maximised':False, 
          'borderless':False, 
          'enable_real_transparency':True, 
          'hidden':False,
          'keybindings':{'hide_window': '<Super>a',
                        }
         }

WINDOW = Window(CONFIG)
WINDOW.show_all()
gtk.main()

# vim: set expandtab ts=4 sw=4:
