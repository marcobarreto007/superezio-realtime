@echo off
REM Atualiza o PATH na sessão atual do CMD
set "PATH=%PATH%;C:\Users\marco\AppData\Local\Programs\Ollama"
echo PATH atualizado na sessao atual do CMD.
echo Testando ollama...
ollama --version

