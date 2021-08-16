Add-Type -AssemblyName System.IO.Compression.FileSystem

$scriptPath = split-path -parent $MyInvocation.MyCommand.Definition
$winpythonVersion = [IO.File]::ReadAllText("${scriptPath}\winpython_version.txt")
$pythonVersion = [IO.File]::ReadAllText("${scriptPath}\python_version.txt")
$panoptosyncUrl = "https://gitlab.com/Microeinstein/panopto-sync/-/archive/master/panopto-sync-master.zip"


function Unzip {
    # Unzips files
    # Credits: https://stackoverflow.com/questions/27768303/how-to-unzip-a-file-in-powershell
    param([string]$zipfile, [string]$outpath)

    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipfile, $outpath)

    if ($boold -eq 1) {
        echo "[DEBUG] Extracted $zipfile into $outpath"
    }
}


echo "Running the script in this folder: ${scriptPath}..."

echo "Downloading WinPython ${winpythonVersion}, which contains python version ${pythonVersion}"
Invoke-WebRequest -uri "https://github.com/winpython/winpython/releases/download/${winpythonVersion}/Winpython64-${pythonVersion}dot.exe" -Method "GET"  -Outfile "$scriptPath\winpyhon.exe"

echo "Extracting WinPython..."
& "$scriptPath\winpyhon.exe" -y

$wpFolderName = -join("WPy64-", $pythonVersion -Replace '\.')
echo "The extracted folder should have this name: ${wpFolderName}"

ls

echo "Renaming it to PanoptoSync"
Rename-Item "$scriptPath\$wpFolderName" "PanoptoSync"

echo "Downloading PanoptoSync"
Invoke-WebRequest -uri "$panoptosyncUrl" -Method "GET"  -Outfile "$scriptPath\PanoptoSync\panoptosync.zip"

echo "Extracting PanoptoSync zip file"
Unzip "$scriptPath\PanoptoSync\panoptosync.zip" "$scriptPath\PanoptoSync\."

echo "Removing zip file"
Remove-Item "$scriptPath\PanoptoSync\panoptosync.zip"

echo "Renaming the extracted folder"
Rename-Item "$scriptPath\PanoptoSync\panopto-sync-master" "panopto-sync"

echo "Installing pip dependencies"
& "$scriptPath\PanoptoSync\scripts\python.bat" -m pip install -r "$scriptPath\PanoptoSync\panopto-sync\requirements.txt"

echo "Removing the notebooks folder"
Remove-Item "$scriptPath\PanoptoSync\notebooks" -Recurse

echo "Removing the scripts folder"
Remove-Item "$scriptPath\PanoptoSync\scripts" -Recurse

echo "Removing the t folder"
Remove-Item "$scriptPath\PanoptoSync\t" -Recurse

echo "Removing all the executable files"
Remove-Item "$scriptPath\PanoptoSync\*.exe"

echo "Writing the execute script batch file"

'@echo off' | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII

"REM Remember User's current path" | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII -Append
'set OLDPATH="%cd%"' | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII -Append

'REM Go inside the panopto-sync folder' | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII -Append
'cd "%~dp0panopto-sync"' | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII -Append

'REM Execute panoptoSync using python' | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII -Append

$pythonFolderName = -join("python-", $pythonVersion -Replace '0', "amd64")  
$pythonCommand = "`"%~dp0${pythonFolderName}\python.exe`" panoptoSync.py %*"
"$pythonCommand" | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII -Append

"REM Go back to the User's original directory" | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII -Append
'cd "%OLDPATH%"' | Out-File -FilePath "$scriptPath\PanoptoSync\panoptoSync.bat" -Encoding ASCII -Append

& "C:\Program Files\7-Zip\7z.exe" -sfx a PanoptoSync.exe "$scriptPath\PanoptoSync"