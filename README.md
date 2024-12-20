### blMenuKITSU
Baselight integration with Kitsu / Zou

### Installation

Copy blMenuKitsu.py file and blMenuKitsu.packages folder to Baselight scripts folder (i.e. /usr/fl/scripts).

### Packages and dependendencies

blMenuKitsu depends on [Gazu](https://github.com/cgwire/gazu) - python API for Kitsu / Zou:  

Gazu version should be up to date with Kitsu / Zou installed.  

At the moment of writing Gazu had additional packages that were not part of a standard Baselight python distribution:  
[Deprecated](https://pypi.org/project/Deprecated/#files)  
[SocketIO](https://pypi.org/project/python-socketio/#files)  
[EngineIO](https://pypi.org/project/python-engineio/#files)  
[Bidict](https://pypi.org/project/bidict/#files)  
[Warpt](https://pypi.org/project/wrapt/#files)  
  
Warpt package is binary and dependant on a platform and python version so it might need to be updated for newer Baselight versions.