@echo off
call .venv\Scripts\activate
python -c "from banana import Banana; Banana().run()"
pause
