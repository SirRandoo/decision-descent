@echo off

REM Prompt setup
TITLE Decision Descent: Launcher

REM Variables
SET PYTHONLOCATION=
SET MODSLOCATION="%USERPROFILE%\Documents\My Games\Binding of Isaac Afterbirth+ Mods"

IF NOT DEFINED PYTHONLOCATION (
    REM Find Python
    REM Let's start with \Program Files\
    echo Searching for python.exe in "%ProgramFiles%"
    CD "%ProgramFiles%"

    FOR /D %%G IN ("Python*") do SET PYTHONLOCATION="%ProgramFiles%\%%G\python.exe"


    IF DEFINED PYTHONLOCATION (
        ECHO Found python.exe at "%PYTHONLOCATION%"
        GOTO init
    ) ELSE (
        ECHO Could not find python.exe in "%ProgramFiles%"
        ECHO Searching "%ProgramFiles(x86)%" for python.exe ...

        cd "%ProgramFiles(x86)%"

        FOR /D %%G in ("Python*") do SET PYTHONLOCATION="%ProgramFiles(x86)\%%G\python.exe"
    )


    IF DEFINED PYTHONLOCATION (
        ECHO Found python.exe at %PYTHONLOCATION%
        GOTO init
    ) ELSE (
        ECHO Could not find Python in "%ProgramFiles(x86)%"
        ECHO Searching "%LOCALAPPDATA%\Programs\Python"

        cd "%LOCALAPPDATA%"

        IF EXIST "Programs" (
            cd "Programs"

            IF EXIST "Python" (
                cd "Python"

                IF EXIST "Python36" (
                    SET PYTHONLOCATION="%LOCALAPPDATA%\Programs\Python\Python36\python.exe"
                ) ELSE (
                    FOR /D %%G in ("Python*") do SET PYTHONLOCATION="%LOCALAPPDATA%\Programs\Python\%%G\python.exe"

                    IF DEFINED PYTHONLOCATION (
                        ECHO Found python.exe at "%PYTHONLOCATION%"
                        GOTO init
                    ) ELSE (
                        ECHO Could not find a Python installation!
                        ECHO If you have installed Python, paste it after "SET PYTHONLOCATION="
                        ECHO If the file path contains spaces, include quotes around the file path.
                    )
                )
            ) ELSE (
                ECHO "%LOCALAPPDATA%\Programs\Python" does not exist!
            )
        ) ELSE (
            ECHO "%LOCALAPPDATA%\Programs" does not exist!
        )
    )
) ELSE (
    ECHO Using python.exe @ "%PYTHONLOCATION%"
    GOTO init
)

pause
GOTO:eof

:init
CD /d "%~dp0"

IF [%1]==[] (
    IF EXIST "Decision Descent.py" (
        ""%PYTHONLOCATION%"" "Decision Descent.py"
    ) ELSE (
        cd "client"
        ""%PYTHONLOCATION%"" "Decision Descent.py"
    )
) ELSE (
    IF "%1" == "setup" (
        ECHO Installing requirements...
        ""%PYTHONLOCATION%%"" -m pip install -r "client/requirements.txt"

        ECHO Please copy mod/ to "%MODSLOCATION%"
    )
)

pause
