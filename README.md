# blMenuKITSU
Baselight integration with Kitsu / Zou

# Mac SSL issue

'''
pip uninstall urllib3
pip install 'urllib3<2.0'
'''

# PyInstaller
./appenv/bin/pyinstaller --onefile --windowed --add-data "resources/eye.png:resources/" -y blMenuKITSU.py
