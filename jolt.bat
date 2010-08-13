@echo off
rem Windows Driver script for Jolt

setlocal
set JOLT=%~f0

%~dp0..\python "%~dp0jolt" %*
endlocal
