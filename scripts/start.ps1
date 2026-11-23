# One-command startup script for Windows PowerShell
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
python "$ProjectRoot\scripts\start_stack.py" $args
