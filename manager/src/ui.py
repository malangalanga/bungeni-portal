'''
Created on May 24, 2011

@author: Ashok
'''
from javax.swing import *
from java.awt import FlowLayout, BorderLayout
from java.awt import Color, Font

"""
This module has UI abstractions
"""

"""
Generic UI classes
"""

class Panel(JPanel):
    """
    Sets up a JPanel
    """

    def __init__(self, title = "panel title", layout = FlowLayout()):
        JPanel.__init__(self)
        self.setLayout(layout)
        self.title = title
    

    def __get_items_in_list__(self, list):
        """
        Generic api to return the items in a  JList
        """
        list_model = list.getModel()
        list_items = []
        idx_range = range(0, list_model.getSize())
        for idx in idx_range:
            list_items.append(list_model.getElementAt(idx))
        return list_items    
    


class TabPane:
    """
    Sets up a Tabbed Pane
    """

    def __init__(self):
        self.tab = JTabbedPane(JTabbedPane.TOP)

    def add_tab(self, panel = Panel()):
        self.tab.addTab( panel.title , panel)


class FormPanel(Panel):
    """
    Extended Panel class specifically for containing FieldPanel   
    """

    """
    This is an easy access list to all fieldPanels with the formPanel
    """
    fields = []
    
    def __init__(self, title, initial_field_count):
        Panel.__init__(self, title)
   
    def add_field_panel(self, field_panel):
        """
        Adds a field panel to the FormPanel,
        also adds the field panel to the fields
        list
        """
        self.fields.append(field_panel)
        self.add(field_panel, "grow, push")
        
    def add_field_panel_at_index(self, index, field_panel):
        self.fields.insert(index, field_panel)
        self.add( field_panel, index)
    
    def remove_field_panel(self, field_panel):

        self.fields.remove(field_panel)
        self.remove(field_panel)
        
    def remove_field_panels(self):
        """
        Removes the field panels for a form
        """
        
        if len(self.fields) > 0:
            for fld in self.fields:
                self.remove(fld)
            self.validate()
            self.fields = []
            
    def field_index(self, field):
        if field in self.fields:
            return self.fields.index(field)
        else:
            return -1
        
        
    def restore_original_order(self):
        orig_fields = sorted(self.fields, key=lambda field: field.order)
        self.remove_field_panels()
        for fld in orig_fields:
            self.add_field_panel(fld)
        self.validate()


    def order_changed(self):
        orig_order = range(0, len(self.fields))
        for ord in orig_order:
            if ord <> self.fields[ord].order:
                return True
        return False

class Frame:
    """
    Sets up a JFrame
    """
    
    def __init__(self, title , size = (400,300), layout = BorderLayout()):
        self.frame = JFrame(title)
        self.frame.setSize(size[0], size[1])
        self.frame.setLayout(layout)
        self.frame.setResizable(True)


    def add(self, a_comp, layout = None):
        """
        Add component to frame using the layout directive
        """
        
        if layout is None:
            self.frame.add(a_comp)
        else:
            self.frame.add(a_comp, layout)
        
    def show(self):
        self.frame.setDefaultCloseOperation(WindowConstants.EXIT_ON_CLOSE)
        self.frame.setVisible(True)



class MultiSelectList(JList):
    """
    Creates a multi select list
    """
    
    def __init__(self, data):
        JList.__init__(self, data)
        self.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION)
        self.ignore_selection_event = False

    def set_selected_values(self, list_data, should_scroll = False):
        if list_data is not None:
            for item in list_data:
                self.setSelectedValue(item, should_scroll)
    
    def get_selected_values(self):
        """
        Returns selected values from list
        """
        return [str(sel) for sel in self.getSelectedValues()]
    
    def set_assoc_list(self, assoc_list):
        self.assoc_list = assoc_list


class H1Label(JLabel):
    
    def __init__(self, text):
        JLabel.__init__(self, text)
        self.setFont(Font("Courier New", Font.BOLD, 15))

class BlackLabel(JLabel):
    
    def __init__(self, text):
        JLabel.__init__(self, text)
        self.setForeground(Color.BLACK)

class RedLabel(JLabel):
    
    def __init__(self, text):
        JLabel.__init__(self, text)
        self.setForeground(Color.RED)

class BlueLabel(JLabel):

    def __init__(self, text):
        JLabel.__init__(self, text)
        self.setForeground(Color.BLUE)

class GreenLabel(JLabel):

    def __init__(self, text):
        JLabel.__init__(self, text)
        self.setForeground(Color.GREEN.darker())


class TitledAction(AbstractAction):
    """
    Extension of AbstractAction - usually the Action.NAME is also used
    as the caption for the button.
    But we record the title in long_description and use the name just to identify
    the button action.
    """
    
    def __init__(self, name = "up", display_title = "up"):
        self.putValue(Action.NAME, name)
        self.putValue(Action.LONG_DESCRIPTION, display_title)
        
    def getValue(self, key):
        if key == Action.NAME:
            return AbstractAction.getValue(self,Action.LONG_DESCRIPTION)
        else:
            return AbstractAction.getValue(self, key)


            
from javax.swing.event import ListSelectionListener
class MultiSelectListListener(ListSelectionListener):
    """
    Helper class for listening to multiselect list change
    events. Never used directly, inherited and value_changed
    is overriden.
    """

    def __init__(self, outer_self):
        self.outer_self = outer_self

        
    def valueChanged(self, lsevt):
        """
        provided valueChanged handler, we handle it here,
        and provide a special override api value_changed
        """
        src_list = lsevt.getSource()
        if lsevt.getValueIsAdjusting() == False:
            self.value_changed(lsevt, src_list)
    
    
    def value_changed(self, lsevt, src_list):
        """
        A value was selected in the list
        Override this as desired
        """
        pass
    


