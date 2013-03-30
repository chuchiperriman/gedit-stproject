import xdg
import xdg.BaseDirectory
import os
import json


_config_file = None
_config = None


def _load():
    global _config, _config_file
    if not _config:
        _config_file = xdg.BaseDirectory.xdg_cache_home
        _config_file = os.path.join(_config_file, 'stproject')
        if not os.path.exists(_config_file):
            os.makedirs(_config_file)
        _config_file = os.path.join(_config_file, 'preferences.json')
        try:
            with open(_config_file, 'r') as fp:
                _config = json.load(fp)
        except:
            _config = {}
            
        if not 'recent_projects' in _config:
            _config['recent_projects'] = []
    
def _add_recent_project(path):
    global _config, _config_file
        
    for p in _config['recent_projects']:
        if p == path:
            _config['recent_projects'].remove(p)
            
    _config['recent_projects'].insert(0, path)
    _config['recent_projects'] = _config['recent_projects'][-5:]
    
def save_last_project(path):
    global _config, _config_file
    _load()
        
    _config['last_open'] = path
    
    _add_recent_project(path)
    
    with open(_config_file, 'w') as fp:
        json.dump(_config, fp, indent=4)

def get_last_project():
    _load()
        
    if 'last_open' in _config:
        return _config['last_open']
        
    return None
    
