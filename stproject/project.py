import os
import json

class Project (object):

    def __init__(self):
        self.folders = []
        
    def add_folder(self, path):
        self.folders.append(path)
        
    def remove_folder(self, path):
        self.folders.remove(path)
        
    def get_folders(self):
        return self.folders

class ProjectJsonFile (Project):

    def __init__(self, path):
        
        if not os.path.exists(path):
            with open(path, 'wb') as fp:
                json.dump({}, fp, indent=4)
                
        self.folders = []
        with open(path, 'rb') as fp:
            self._data = json.load(fp)
        
        self._path = path
        
        if 'folders' not in self._data:
            self._data['folders'] = []
            
        for f in self._data['folders']:
            self.folders.append(f['path'])

    def add_folder(self, path):
        self._data['folders'].append({
            'path': path
        })
        self.folders.append(path)
        self.save()
    
    def remove_folder(self, path):
        for f in self._data['folders']:
            if f['path'] == path:
                self._data['folders'].remove(f)
                break
        self.folders.remove(path)
        self.save()
        
    def save(self):
        with open(self._path, 'wb') as fp:
            json.dump(self._data, fp, indent=4)
        
