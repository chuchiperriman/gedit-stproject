from gi.repository import GObject, Gtk, Gedit
from .panel import Panel
from .project import ProjectJsonFile
from .config import config

UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="ProjectMenu" action="ProjectMenu">
      <placeholder name="ProjectsOps_1">
        <menuitem action='CreateAction' />
        <menuitem action="OpenAction"/>
        <menuitem action="LastAction"/>
      </placeholder>
      <placeholder name="RecentProjects">
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
        self.ui_manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup("StprojectActions")
        self._actions.add_actions([
            ('ProjectMenu', None, _('_Project'), None, None, None),
            ('CreateAction', None, "New project", 
                None, "Create a new project file", 
                self.on_create_action_activate),
            ('OpenAction', None, "Open project", 
                None, "Open a project file", 
                self.on_open_action_activate),
            ('LastAction', None, "Open last project", 
                None, "Open the las opened project", 
                self.on_last_action_activate),
        ])
        self.ui_manager.insert_action_group(self._actions)
        self._ui_merge_id = self.ui_manager.add_ui_from_string(UI_XML)
        
        # Moved the menu to a less surprising position.
        menubar = self.ui_manager.get_widget('/MenuBar')
        project_menu = self.ui_manager.get_widget('/MenuBar/ProjectMenu')
        menubar.remove(project_menu)
        menubar.insert(project_menu, 5)
        self.do_update_state()
        self.ui_manager.ensure_update()
        config.connect("saved", self.on_config_saved)
        
    def on_config_saved(self, data):
        #TODO Reorder the recent project (the last at top etc)
        for r in config.get_recent_projects():
            if not self._actions.get_action(r):
                self._actions.add_actions([(
                    r, None, r, 
                        None, "Open the project", 
                        self.on_recent_action_activate),])
            self.ui_manager.add_ui(self.ui_manager.new_merge_id(), 
                '/MenuBar/ProjectMenu/RecentProjects', r, 
                r, Gtk.UIManagerItemType.MENUITEM, False)
        
    def on_create_action_activate(self, action, data=None):
        self._side_widget.create_project_action()
        self._panel.activate_item(self._side_widget)
        
    def on_open_action_activate(self, action, data=None):
        self._side_widget.open_project_action()
        self._panel.activate_item(self._side_widget)
        
    def on_last_action_activate(self, action, data=None):
        path = config.get_last_project()
        if path:
            self.load_project(ProjectJsonFile(path))
            self._panel.activate_item(self._side_widget)
        else:
            dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.INFO,
                Gtk.ButtonsType.OK, "No project to open")
            dialog.run()
            dialog.destroy()
            
    def on_recent_action_activate(self, action, data=None):
        self.load_project(ProjectJsonFile(action.get_name()))
        self._panel.activate_item(self._side_widget)
        
