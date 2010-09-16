@echo off
rem Windows Driver script for Jolt

setlocal
set JOLT=%~f0

set PYTHON=%~dp0..\python.exe

if not exist "%PYTHON%" set PYTHON=c:\python26\python.exe

%PYTHON% "%~dp0jolt" %*

endlocal
