REM @ECHO off    
if [%1] == [] goto default
if /I %1 == tests goto tests
if /I %1 == install goto install
if /I %1 == shipit goto shipit
if /I %1 == clean goto clean

goto :eof ::can be ommited to run the `default` function similarly to makefiles

:default
echo DEFAULT
python36 setup.py sdist bdist_wheel  
REM python36 setup.py sdist bdist_wheel bdist_wininst bdist_msi 
goto :eof

:tests
echo TESTS
python36 -m pytest
python36-32 -m pytest
python27 -m pytest
python27-32 -m pytest
goto :eof

:install
echo INSTALL
python36 -m pip install --user --upgrade setuptools wheel
python36 -m pip install --user --upgrade twine
goto :eof

:shipit
echo UPLOAD TO PYPI
python36 -m twine upload dist/*
goto :eof

:clean
echo CLEAN
rd /s /q .pytest_cache
rd /s /q dist
rd /s /q build
rd /s /q "pymsfilereader.egg-info"
python36 -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
python36 -c "import pathlib; [p.rmdir()  for p in pathlib.Path('.').rglob('__pycache__')]"
python36 -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.meth')]"

goto :eof
