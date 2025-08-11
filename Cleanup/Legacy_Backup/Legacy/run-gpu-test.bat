@echo off
echo Running Agent Exo-Suit GPU Test...
cd /d "C:\My Projects\Agent Exo-Suit"
call rag_env\Scripts\activate.bat
python rag\test_gpu_only.py
pause
