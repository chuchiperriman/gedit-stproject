import xdg
import xdg.BaseDirectory
import os
import json
from gi.repository import GObject

class StConfig(GObject.GObject):

    __gsignals__ = {
        'saved': (GObject.SIGNAL_RUN_FIRST, None, ())
    }
    
    def __init__(self):
        GObject.GObject.__init__(self)
        
        self._config_file = xdg.BaseDirectory.xdg_cache_home
        self._config_file = os.path.join(self._config_file, 'stproject')
        if not os.path.exists(self._config_file):
            os.makedirs(self._config_file)
        self._config_file = os.path.join(self._config_file, 'preferences.json')
        try:
            with open(self._config_file, 'r') as fp:
                self._config = json.load(fp)
        except:
            self._config = {}
            
        if not 'recent_projects' in self._config:
            self._config['recent_projects'] = []


    def _add_recent_project(self, path):
        for p in self._config['recent_projects']:
            if p == path:
                self._config['recent_projects'].remove(p)
                
        self._config['recent_projects'].insert(0, path)
        self._config['recent_projects'] = self._config['recent_projects'][-5:]
        
        self._save()
    
    def set_last_project(self, path):
        self._config['last_open'] = path
        
        self._add_recent_project(path)
        
        self._save()
        
    def get_last_project(self):
        if 'last_open' in self._config:
            return self._config['last_open']
            
        return None
        
    def get_recent_projects(self):
        return self._config['recent_projects']
        
    def _save(self):
        with open(self._config_file, 'w') as fp:
            json.dump(self._config, fp, indent=4)
        
        self.emit("saved")
    
config = StConfig()

