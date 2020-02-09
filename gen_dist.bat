@echo off
color d
cls

cd /d %~dp0


venv\py360x64\Scripts\python.exe -m PyInstaller car_sim_etti.spec --clean


pause