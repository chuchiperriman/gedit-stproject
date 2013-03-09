import json, os
from gi.repository import GObject, Gtk, Gedit, Gio

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
        
    def append_dir(self, piter, pfolder, folder):
        ppath = os.path.join(pfolder,folder)
        piter = self._append_store(Gio.File.new_for_path(ppath), piter)
        
        #TODO sort the tree, not two loops here...
        flist = os.listdir(ppath)
        flist.sort()
        for sub in flist:
            path = os.path.join(ppath,sub)
            if os.path.isdir(path):
                self.append_dir(piter, ppath, sub)

        for sub in flist:
            path = os.path.join(ppath,sub)
            if os.path.isfile(path):
                self._append_store(Gio.File.new_for_path(path), piter)
            
    def do_activate(self):
        icon = Gtk.Image.new_from_stock(Gtk.STOCK_FILE, Gtk.IconSize.MENU)
        self._store = Gtk.TreeStore(Gio.Icon, str, GObject.Object, Gio.FileType)
        
        data = self.load_data()
        for f in data['folders']:
            self.append_dir(None, '', f['path'])
        
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
        panel = self.window.get_side_panel()
        panel.add_item(self._side_widget,
                       "ExampleSidePanel", "Project", icon)
        self._side_widget.show()
        tree.show()
        panel.activate_item(self._side_widget)

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
        
    def load_data(self):
        json_data=open('/home/chuchiperriman/tmp/proyecto.json')
        data = json.load(json_data)
        json_data.close()
        return data
