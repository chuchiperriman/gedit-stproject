from gi.repository import GObject, Gtk, Gedit
from panel import Panel
from project import ProjectJsonFile

UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="ProjectMenu" action="ProjectMenu">
      <placeholder name="ProjectsOps_1">
        <menuitem action='CreateAction' />
        <menuitem action="OpenAction"/>
        <separator/>
        <menuitem action="AddFolderAction"/>
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
            ('AddFolderAction', Gtk.STOCK_OPEN, "Add folder", 
                None, "Add forlder to the current project", 
                self.on_addfolder_action_activate),
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
        
    def on_open_action_activate(self, action, data=None):
        dialog = Gtk.FileChooserDialog("Please choose a project file", self.window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            res = self.load_project(ProjectJsonFile(dialog.get_filename()))
            #TODO If False, the project file is not valid
            self._panel.activate_item(self._side_widget)
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()
        
        
    def on_addfolder_action_activate(self, action, data=None):
        self._side_widget.add_folder_action()
        self._panel.activate_item(self._side_widget)
        
