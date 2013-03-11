import os
from gi.repository import GObject, Gtk, Gedit, Gio, Gdk


POPUP_UI = """
  <popup name='PopupMenu'>
    <menuitem action='AddFolderAction' />
    <menuitem action='RemoveFolder' />
  </popup>
"""


class Panel (Gtk.ScrolledWindow):

    __gtype_name__ = 'StProjectPanel'

    def __init__(self, window):
        Gtk.ScrolledWindow.__init__(self)
        self.window = window
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self._store = Gtk.TreeStore(Gio.Icon, str, GObject.Object, Gio.FileType)
        
        self._build_ui()
        
    def load_project(self, project):
        
        #TODO Close current project
        self._store.clear()
        self._project = project
        
        for f in project.get_folders():
            self._append_dir(None, '', f)
            
        return True
        
    def add_folder(self, path):
        self._append_dir(None, '', path)
        
    def add_folder_action(self):
        dialog = Gtk.FileChooserDialog("Please choose a folder to add", self.window,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self._project.add_folder(dialog.get_filename())
            self.add_folder(dialog.get_filename())

        dialog.destroy()
        
        return response
        
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
    
    def _build_ui(self):
        self._tree = Gtk.TreeView(self._store)
        self._tree.set_headers_visible(False)
        
        column = Gtk.TreeViewColumn(None)
        
        renderer = Gtk.CellRendererPixbuf()
        column.pack_start(renderer, False)
        column.add_attribute(renderer, "gicon", 0)

        renderer = Gtk.CellRendererText()
        column.pack_start(renderer, True)
        column.add_attribute(renderer, "markup", 1)
        
        self._tree.append_column(column)
        
        self._tree.connect('row-activated', self._on_row_activated)
        
        self.add_with_viewport(self._tree)
        
        self._build_popup()
        
        self._tree.show()
        
    def _build_popup(self):
    
        action_group = Gtk.ActionGroup("StProjectPanelActions")
        
        action_group.add_actions([
            ("RemoveFolder", Gtk.STOCK_REMOVE, 'Remove folder from project', None, None,
             self.on_removefolder_action_activate),
            ('AddFolderAction', Gtk.STOCK_OPEN, "Add folder to project", 
                None, "Add forlder to the current project", 
                self.on_addfolder_action_activate),
        ])
    
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(POPUP_UI)
        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.window.add_accel_group(accelgroup)
        uimanager.insert_action_group(action_group)
        
        self.popup = uimanager.get_widget("/PopupMenu")

        self._tree.connect("button-press-event", self.on_button_press_event)
        
    def on_button_press_event(self, widget, event):
        # Check if right mouse button was preseed
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self.popup.popup(None, None, None, None, event.button, event.time)
            return True # event has been handled
            
    def on_removefolder_action_activate(self, action, data=None):
        selection = self._tree.get_selection()
        model, treeiter = selection.get_selected()
        if treeiter != None:
            info = model.get(treeiter, 2, 3)
            print info[0].get_path()
            self._project.remove_folder(info[0].get_path())
            model.remove(treeiter)
        
    def on_addfolder_action_activate(self, action, data=None):
        self.add_folder_action()
        
    def _on_row_activated(self, tree, path, column):
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
