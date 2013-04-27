import os
import json
import fnmatch
from gi.repository import Gio

class Folder (object):

    def __init__(self, name, path, excludes = []):
        self.name = name
        self.path = path
        self.folders = []
        self.files = []
        self.excludes = excludes
        self._load()
        
    def _load(self):
        flist = os.listdir(self.path)
        flist.sort()
        for sub in flist:
            exclude = False
            for ex in self.excludes:
                if fnmatch.fnmatch(sub, ex):
                    exclude = True
            if not exclude:
                spath = os.path.join(self.path,sub)
                if os.path.isdir(spath):
                    self.folders.append(Folder(sub, spath, self.excludes))
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
        self.open_files = []
    
    def get_name(self):
        return self.name
        
    def get_path(self):
        return None
        
    def add_folder(self, path):
        self.folders.append(path)
        
    def remove_folder(self, path):
        self.folders.remove(path)
        
    def get_folders(self):
        return self.folders
    
    def get_folder_icon(self, folder):
        return None
        
    def get_open_files(self):
        """
        List of path files
        """
        return self.open_files
        
    def set_open_files(self, files):
        """
        List of path files
        """
        self.open_files = files
        
    def reload(self):
        pass

class ProjectJsonFile (Project):

    def __init__(self, path):
        self._path = path
        self.reload()

    def reload(self):
        self.folders = []
        if not os.path.exists(self._path):
            with open(self._path, 'w') as fp:
                json.dump({}, fp, indent=4)
                
        with open(self._path, 'r') as fp:
            self._data = json.load(fp)
        
        if 'name' in self._data:
            self.name = self._data['name']
            
        if 'folders' not in self._data:
            self._data['folders'] = []
            
        if 'open_files' not in self._data:
            self._data['open_files'] = []
        
        self.open_files = self._data['open_files']
        
        for f in self._data['folders']:
            name = os.path.basename(f['path'])
            excludes = []
            if 'folder_exclude_patterns' in f:
                excludes = f['folder_exclude_patterns']
            self.folders.append(Folder(name, f['path'], excludes))
            
    def get_path(self):
        return self._path
                
    def add_folder(self, path):
        self._data['folders'].append({
            'path': path
        })
        name = os.path.basename(path)
        folder = Folder(name, path)
        self.folders.append(folder)
        self.save()
        return folder
    
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
        
    def set_open_files(self, files):
        super(ProjectJsonFile, self).set_open_files(files)
        self._data['open_files'] = files
        self.save()
        
    def save(self):
        with open(self._path, 'w') as fp:
            json.dump(self._data, fp, indent=4)
        
