@echo off
setlocal

:: 获取当前日期（格式：YYYY-MM-DD）
for /f "tokens=1-3 delims=-/" %%a in ("%date%") do (
    set y=%%a
    set m=%%b
    set d=%%c
)

git add .
git commit -m "%y%-%m%-%d%"
git push

