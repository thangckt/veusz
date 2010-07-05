#    Copyright (C) 2010 Jeremy S. Sanders
#    Email: Jeremy Sanders <jeremy@jeremysanders.net>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
##############################################################################

# $Id$

"""Data entry fields for plugins."""

import veusz.qtall as qt4
import veusz.utils as utils

class Field(object):
    """A class to represent an input field on the dialog or command line."""
    def __init__(self, name, descr=None, default=None):
        """name: name of field
        descr: description to show to user
        default: default value."""
        self.name = name
        if descr:
            self.descr = descr
        else:
            self.descr = name
        self.default = default

    def makeControl(self, doc=None):
        """Create a set of controls for field."""
        return None

    def getControlResults(self, cntrls):
        """Get result from created contrls."""
        return None

class FieldCheck(Field):
    """A check box on the dialog."""

    def makeControl(self, doc=None):
        l = qt4.QLabel(self.descr)
        c = qt4.QCheckBox()
        if self.default:
            c.setChecked(True)
        return (l, c)

    def getControlResults(self, cntrls):
        return cntrls[1].isChecked()

class FieldText(Field):
    """Text entry on the dialog."""

    def makeControl(self, doc=None):
        l = qt4.QLabel(self.descr)
        e = qt4.QLineEdit()
        if self.default:
            e.setText(self.default)
        return (l, e)

    def getControlResults(self, cntrls):
        return unicode( cntrls[1].text() )

class FieldFloat(Field):
    """Enter a floating point number."""

    def __init__(self, name, descr=None, default=None,
                 minval=-1e99, maxval=1e99):
        """name: name of field
        descr: description to show to user
        default: default value.
        minval and maxval: minimum and maximum values
        """
        Field.__init__(self, name, descr=descr, default=default)
        self.range = (minval, maxval)

    def makeControl(self, doc=None):
        l = qt4.QLabel(self.descr)
        e = qt4.QLineEdit()
        v = qt4.QDoubleValidator(e)
        v.setBottom(self.range[0])
        v.setTop(self.range[1])
        e.setValidator(v)
        if self.default is not None:
            e.setText( str(self.default) )
        return (l, e)

    def getControlResults(self, cntrls):
        try:
            return float( cntrls[1].text() )
        except:
            return None

class FieldInt(Field):
    """Enter an integer number."""

    def __init__(self, name, descr=None, default=None,
                 minval=-9999999, maxval=9999999):
        """name: name of field
        descr: description to show to user
        default: default value.
        minval and maxval: minimum and maximum integers
        """
        Field.__init__(self, name, descr=descr, default=default)
        self.range = (minval, maxval)

    def makeControl(self, doc=None):
        l = qt4.QLabel(self.descr)
        e = qt4.QSpinBox()
        e.setMinimum(self.range[0])
        e.setMaximum(self.range[1])
        if self.default is not None:
            e.setValue( self.default )
        return (l, e)

    def getControlResults(self, cntrls):
        try:
            return cntrls[1].value()
        except:
            return None

class FieldCombo(Field):
    """Drop-down combobox on dialog."""
    def __init__(self, name, descr=None, default=None, items=(),
                 editable=True):
        """name: name of field
        descr: description to show to user
        default: default value
        items: items in drop-down box
        editable: whether user can enter their own value."""
        Field.__init__(self, name, descr=descr, default=default)
        self.items = items
        self.editable = editable

    def makeControl(self, doc=None):
        l = qt4.QLabel(self.descr)
        c = qt4.QComboBox()
        c.addItems(self.items)
        c.setEditable(bool(self.editable))

        if self.default:
            if self.editable:
                c.setEditText(self.default)
            else:
                c.setCurrentIndex(c.findText(self.default))

        return (l, c)

    def getControlResults(self, cntrls):
        return unicode( cntrls[1].currentText() )

class WidgetCombo(qt4.QComboBox):
    """Combo box for selecting widgets."""

    def __init__(self, doc, widgettypes, default):
        """doc: Veusz document
        widgettypes: set of allowed widgettypes or empty for all
        default: default path."""

        qt4.QComboBox.__init__(self)
        self.doc = doc
        self.widgettypes = widgettypes
        self.default = default
        self.updateWidgets()
        self.connect(doc, qt4.SIGNAL("sigModified"), self.updateWidgets)

    def updateWidgets(self):
        """Update combo with new widgets."""

        self.paths = []    # veusz widget paths of items
        comboitems = []    # names of items (with tree spacing)

        def iterateWidgets(widget, level):
            """Walk tree recursively."""
            if not self.widgettypes or widget.typename in self.widgettypes:
                comboitems.append('  '*level + widget.name)
                self.paths.append(widget.path)
            for w in widget.children:
                iterateWidgets(w, level+1)

        iterateWidgets(self.doc.basewidget, 0)
        if self.count() == 0:
            # first time around add default to get it selected, yuck :-(
            try:
                idx = self.paths.index(self.default)
                self.addItem( comboitems[idx] )
            except ValueError:
                pass

        utils.populateCombo(self, comboitems)
    
    def getWidgetPath(self):
        """Get path of selected widget."""
        return self.paths[self.currentIndex()]

class FieldWidget(Field):
    """Drop-down combobox showing widget."""

    def __init__(self, name, descr=None, default='/', widgettypes=set()):
        """name: name of field
        descr: description to show to user
        default: default value."""
        Field.__init__(self, name, descr=descr, default=default)
        self.widgettypes = widgettypes

    def populateCombo(self, doc, combo):
        """Fill combo box with widgets."""

    def makeControl(self, doc=None):
        l = qt4.QLabel(self.descr)
        c = WidgetCombo(doc, self.widgettypes, self.default)
        return (l, c)

    def getControlResults(self, cntrls):
        return cntrls[1].getWidgetPath()
