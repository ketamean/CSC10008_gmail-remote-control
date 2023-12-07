cd src
rmdir /s /q .\.venv
npm uninstall --save $(cat requirements/npm_requirements.txt)