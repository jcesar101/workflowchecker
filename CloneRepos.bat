@echo off
SETLOCAL EnableDelayedExpansion

IF "%1"=="" GOTO noArguments

REM Hosting platform URL
SET platform=https://github.com/

REM Get directory name and create it if does not exist
CALL :GetDir dirName
IF NOT EXIST "!dirName!\" MKDIR !dirName!
CD !dirName!

REM Get list of repos names and user or namespaces for each workflow
FOR /f  %%i IN (..\%1) DO (
 CALL :CountTokens "%%i",countToken
 FOR /l %%g IN (1,1,!countToken!) DO (  
  CALL :GetRepos %%g,"%%i",workflow,repo
  IF "%%g" EQU "1" (
   IF NOT EXIST "!workflow!\" MKDIR !workflow!
   CD !workflow!
  ) ELSE (
   FOR /f "tokens=2 delims=/" %%r IN ("!repo!") DO (
    MKDIR %%r
    CD %%r
    git clone %platform%!repo! .
    CD ..
   )
  )
 )
 CD ..
)
ENDLOCAL
EXIT /B %ERRORLEVEL%

REM No arguments message
:noArguments
ECHO "Usage: %~n0 <text file with list of repositories>
EXIT /B 1

REM Functions
:CountTokens
 SET tstr=%~1
 SET delim=,
 SET tcount=1
 :loop
 IF !tstr:~0^,1! EQU !delim! (
  SET /a tcount+=1
 )
 IF "!tstr:~1!" NEQ "" (
  SET tstr=!tstr:~1!
  GOTO :loop
 )
 SET %~2=%tcount%
 EXIT /B 0

:GetRepos
 FOR /f "tokens=%~1 delims=," %%x IN ("%~2") DO (
  IF "%~1" EQU "1" (
   SET "%~3=%%x"
  ) ELSE (
   SET "%~4=%%x"
  )
 )
 EXIT /B 0

:GetDir
 SET HOUR=%time:~0,2%
 SET dtStamp9=%date:~0,2%%date:~3,2%%date:~-2%_0%time:~1,1%%time:~3,2%
 SET dtStamp24=%date:~0,2%%date:~3,2%%date:~-2%_%time:~0,2%%time:~3,2%

 IF "%HOUR:~0,1%" == " " (SET dtStamp=%dtStamp9%) else (SET dtStamp=%dtStamp24%)

 SET "%~1=%dtStamp%"
EXIT /B 0