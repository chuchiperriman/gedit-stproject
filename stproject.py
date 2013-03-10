import json
import os
from gi.repository import GObject, Gtk, Gedit, Gio

UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="ProjectMenu" action="ProjectMenu">
      <placeholder name="ProjectsOps_1">
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

    def _append_store(self, gfile, piter):
        info = gfile.query_info("standard::*",
                                Gio.FileQueryInfoFlags.NONE,
                                None)
        return self._store.append(piter, [info.get_icon(), 
                                          info.get_name(),
                                          gfile,
                                          info.get_file_type()])
        
    def _append_dir(self, piter, pfolder, folder):
        ppath = os.path.join(pfolder,folder)
        piter = self._append_store(Gio.File.new_for_path(ppath), piter)
        
        #TODO sort the tree, not two loops here...
        flist = os.listdir(ppath)
        flist.sort()
        for sub in flist:
            path = os.path.join(ppath,sub)
            if os.path.isdir(path):
                self._append_dir(piter, ppath, sub)

        for sub in flist:
            path = os.path.join(ppath,sub)
            if os.path.isfile(path):
                self._append_store(Gio.File.new_for_path(path), piter)
    
    def load_project(self, path):
        json_data=open(path)
        data = json.load(json_data)
        json_data.close()
        
        for f in data['folders']:
            self._append_dir(None, '', f['path'])
    
    def do_activate(self):
        self._store = Gtk.TreeStore(Gio.Icon, str, GObject.Object, Gio.FileType)
        
        self.load_project('/home/chuchiperriman/tmp/proyecto.json')
        self._build_panel()
        self._build_menu()

    def on_row_activated(self, tree, path, column):
        model = tree.get_model()
        i = model.get_iter(path)
        if model.iter_has_child(i):
            if tree.row_expanded(path):
                tree.collapse_row(path)
            else:
                tree.expand_row(path, False)
        else:
            info = model.get(i, 2, 3)
            if info[1] != Gio.FileType.DIRECTORY:
                Gedit.commands_load_location(self.window, 
                    info[0], None, -1, -1)
        
    def do_deactivate(self):
        panel = self.window.get_side_panel()
        panel.remove_item(self._side_widget)

    def do_update_state(self):
        pass
        
    def _build_panel(self):
        icon = Gtk.Image.new_from_stock(Gtk.STOCK_FILE, Gtk.IconSize.MENU)
        tree = Gtk.TreeView(self._store)
        tree.set_headers_visible(False)
        
        column = Gtk.TreeViewColumn(None)
        
        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, "gicon", 0)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "markup", 1)
        
        tree.append_column(column)
        
        tree.connect('row-activated', self.on_row_activated)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add_with_viewport(tree)
        
        self._side_widget = scroll
        self._panel = self.window.get_side_panel()
        self._panel.add_item(self._side_widget,
                       "ExampleSidePanel", "Project", icon)
        self._side_widget.show()
        tree.show()
        self._panel.activate_item(self._side_widget)
    
    def _build_menu(self):
        manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup("StprojectActions")
        self._actions.add_actions([
            ('ProjectMenu', None, _('_Project'), None, None, None),
            ('AddFolderAction', Gtk.STOCK_INFO, "Add folder", 
                None, "Open a project file", 
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
        
    def on_addfolder_action_activate(self, action, data=None):
        dialog = Gtk.FileChooserDialog("Please choose a folder to add", self.window,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._append_dir(None, '', dialog.get_filename())
            self._panel.activate_item(self._side_widget)
        elif response == Gtk.ResponseType.CANCEL:
            pass

        dialog.destroy()
        
