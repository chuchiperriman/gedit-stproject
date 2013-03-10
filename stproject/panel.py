import os
from gi.repository import GObject, Gtk, Gedit, Gio

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
        
        for f in project.get_folders():
            self._append_dir(None, '', f)
            
        return True
        
    def add_folder(self, path):
        self._append_dir(None, '', path)
        
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
        
        tree.connect('row-activated', self._on_row_activated)
        
        self.add_with_viewport(tree)
        
        tree.show()
        
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
