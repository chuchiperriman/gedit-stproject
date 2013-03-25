import os
import json
from gi.repository import Gio

class Folder (object):

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.folders = []
        self.files = []
        self._load()
        
    def _load(self):
        flist = os.listdir(self.path)
        flist.sort()
        for sub in flist:
            spath = os.path.join(self.path,sub)
            if os.path.isdir(spath):
                self.folders.append(Folder(sub, spath))
            elif os.path.isfile(spath):
                self.files.append(spath)
                
    def get_name(self):
        return self.name
        
    def get_path(self):
        return self.path
    
    def get_files(self):
        return self.files
        
    def get_folders(self):
        return self.folders

class Project (object):

    def __init__(self):
        self.folders = []
        self.name = 'Project'
    
    def get_name(self):
        return self.name
        
    def add_folder(self, path):
        self.folders.append(path)
        
    def remove_folder(self, path):
        self.folders.remove(path)
        
    def get_folders(self):
        return self.folders
    
    def get_folder_icon(self, folder):
        return None

class ProjectJsonFile (Project):

    def __init__(self, path):
        self.folders = []
        
        if not os.path.exists(path):
            with open(path, 'wb') as fp:
                json.dump({}, fp, indent=4)
                
        with open(path, 'rb') as fp:
            self._data = json.load(fp)
        
        self._path = path
        
        if 'name' in self._data:
            self.name = self._data['name']
            
        if 'folders' not in self._data:
            self._data['folders'] = []
            
        for f in self._data['folders']:
            name = os.path.basename(f['path'])
            self.folders.append(Folder(name, f['path']))

    def add_folder(self, path):
        self._data['folders'].append({
            'path': path
        })
        name = os.path.basename(path)
        self.folders.append(Folder(name, path))
        self.save()
    
    def remove_folder(self, path):
        for f in self._data['folders']:
            if f['path'] == path:
                self._data['folders'].remove(f)
                break
        for f in self.folders:
            if f.path == path:
                self.folders.remove(f)
                break
        self.save()
        
    def get_folder_icon(self, folder):
        for f in self._data['folders']:
            if f['path'] == folder and 'icon' in f:
                return Gio.FileIcon.new(Gio.File.new_for_path(f['icon']))
        return None
        
    def save(self):
        return
        with open(self._path, 'wb') as fp:
            json.dump(self._data, fp, indent=4)
        
