# -*- mode: python -*-
import os
import sys
import site

block_cipher = None


a = Analysis(['car_sim_etti\\utils\\car_sim_etti_cmd.py'],
    pathex=['..\\car_sim_etti\\car_sim_etti'],
    binaries=[],
    datas=[],
    hiddenimports=[
        'json',
        'numpy',
        'PyQt5',
        'pyqtgraph',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    Tree('car_sim_etti\\', prefix='car_sim_etti\\'),
    name='car_sim_etti',
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon='car_sim_etti.ico',
    # version='version.rc', # file is generated from car_sim_etti/version.py/update_version_details
)