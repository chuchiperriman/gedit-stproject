import json

class Project (object):

    def __init__(self):
        self.folders = []
        
    def get_folders(self):
        return self.folders

class ProjectJsonFile (Project):

    def __init__(self, path):
        
        self.folders = []
        with open(path, 'rb') as fp:
            self._data = json.load(fp)
        
        self._path = path
        
        for f in self._data['folders']:
            self.folders.append(f['path'])

    def add_folder(self, path):
        self._data['folders'].append({
            'path': path
        })
        self.save()
        
    def save(self):
        with open(self._path, 'wb') as fp:
            json.dump(self._data, fp, indent=4)
        
