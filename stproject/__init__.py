import os
import xdg
import json
from gi.repository import GObject, Gtk, Gedit
from panel import Panel
from project import ProjectJsonFile

UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="ProjectMenu" action="ProjectMenu">
      <placeholder name="ProjectsOps_1">
        <menuitem action='CreateAction' />
        <menuitem action="OpenAction"/>
        <menuitem action="LastAction"/>
      </placeholder>
    </menu>
</menubar>
</ui>"""

class StProjectPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "StProjectPlugin"
    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)
    
    def do_activate(self):
        self._build_panel()
        self._build_menu()

    def do_deactivate(self):
        panel = self.window.get_side_panel()
        panel.remove_item(self._side_widget)

    def do_update_state(self):
        pass
        
    def load_project(self, project):
        self._side_widget.load_project(project)
        self._project = project
        
    def _build_panel(self):
        
        self._side_widget = Panel(self.window)
        
        self._panel = self.window.get_side_panel()
        icon = Gtk.Image.new_from_stock(Gtk.STOCK_FILE, Gtk.IconSize.MENU)
        self._panel.add_item(self._side_widget,
                       "StProjectPanel", "Project", icon)
        self._side_widget.show()
        self._panel.activate_item(self._side_widget)
    
    def _build_menu(self):
        manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup("StprojectActions")
        self._actions.add_actions([
            ('ProjectMenu', None, _('_Project'), None, None, None),
            ('CreateAction', Gtk.STOCK_NEW, "New project", 
                None, "Create a new project file", 
                self.on_create_action_activate),
            ('OpenAction', Gtk.STOCK_OPEN, "Open project", 
                None, "Open a project file", 
                self.on_open_action_activate),
            ('LastAction', Gtk.STOCK_OPEN, "Open last project", 
                None, "Open the las opened project", 
                self.on_last_action_activate),
        ])
        manager.insert_action_group(self._actions)
        self._ui_merge_id = manager.add_ui_from_string(UI_XML)
        
        # Moved the menu to a less surprising position.
        manager = self.window.get_ui_manager()
        menubar = manager.get_widget('/MenuBar')
        project_menu = manager.get_widget('/MenuBar/ProjectMenu')
        menubar.remove(project_menu)
        menubar.insert(project_menu, 5)
        self.do_update_state()
        manager.ensure_update()
        
    def on_create_action_activate(self, action, data=None):
        self._side_widget.create_project_action()
        self._panel.activate_item(self._side_widget)
        
    def on_open_action_activate(self, action, data=None):
        self._side_widget.open_project_action()
        self._panel.activate_item(self._side_widget)
        
    def on_last_action_activate(self, action, data=None):
        cache = xdg.BaseDirectory.xdg_cache_home
        cache = os.path.join(cache, 'stproject', 'preferences.json')
        pref = {}
        try:
            with open(cache, 'rb') as fp:
                pref = json.load(fp)
        except:
            pass
            
        if 'last_open' in pref:
            self.load_project(ProjectJsonFile(pref['last_open']))
        else:
            dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK, "No project to open")
            dialog.run()
            dialog.destroy()
            return
