mode con:cols=137 lines=38
@echo off
:loopStart
python %cd%\course2_0.py > temp.txt
cls
type temp.txt
timeout 2 >nul
goto loopStart