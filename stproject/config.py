import xdg
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
            with open(_config_file, 'rb') as fp:
                _config = json.load(fp)
        except:
            pass
    
def save_last_project(path):
    global _config, _config_file
    _load()
        
    _config['last_open'] = path
    with open(_config_file, 'wb') as fp:
        json.dump(_config, fp, indent=4)
            
def get_last_project():
    _load()
        
    if 'last_open' in _config:
        return _config['last_open']
        
    return None
    
