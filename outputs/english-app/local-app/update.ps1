param([string]$TargetDirectory,[switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
try {
    $sourceDirectory = [IO.Path]::GetFullPath($PSScriptRoot)
    if (!$TargetDirectory) {
        Add-Type -AssemblyName System.Windows.Forms
        $picker = New-Object System.Windows.Forms.FolderBrowserDialog
        $picker.Description = 'Chon thu muc app cu, noi co MO-APP.cmd, server.mjs va data.'
        $picker.ShowNewFolderButton = $false
        if ($picker.ShowDialog() -ne [System.Windows.Forms.DialogResult]::OK) { exit 0 }
        $TargetDirectory = $picker.SelectedPath
    }
    $targetDirectoryResolved = (Resolve-Path -LiteralPath $TargetDirectory).Path
    $targetServer = Join-Path $targetDirectoryResolved 'server.mjs'
    if (!(Test-Path -LiteralPath $targetServer -PathType Leaf) -or !(Test-Path -LiteralPath (Join-Path $targetDirectoryResolved 'MO-APP.cmd') -PathType Leaf)) { throw 'Thu muc nay khong phai app cu. Chon dung thu muc co MO-APP.cmd va server.mjs.' }
    if ((Get-Content -LiteralPath $targetServer -Raw) -notmatch 'english-garden') { throw 'Khong nhan ra app English Garden trong thu muc da chon.' }
    $matchingServers = @(Get-CimInstance Win32_Process -Filter "Name = 'node.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.IndexOf($targetServer,[StringComparison]::OrdinalIgnoreCase) -ge 0 })
    foreach ($runningServer in $matchingServers) { Stop-Process -Id $runningServer.ProcessId -ErrorAction Stop }
    Start-Sleep -Milliseconds 500
    $oldData = Join-Path $targetDirectoryResolved 'data'
    if (Test-Path -LiteralPath $oldData -PathType Container) {
        $backupDirectory = Join-Path $targetDirectoryResolved ('sao-luu-truoc-update-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
        Copy-Item -LiteralPath $oldData -Destination $backupDirectory -Recurse
        Write-Host "Da sao luu du lieu: $backupDirectory" -ForegroundColor Green
    }
    if ($sourceDirectory -ne $targetDirectoryResolved) {
        foreach ($fileName in @('server.mjs','start.ps1','MO-APP.cmd','MO-GIAO-TRINH-52-TUAN.cmd','README.txt','update.ps1','CAP-NHAT-V1.1.cmd')) {
            Copy-Item -LiteralPath (Join-Path $sourceDirectory $fileName) -Destination (Join-Path $targetDirectoryResolved $fileName) -Force
        }
        $destinationPublic = Join-Path $targetDirectoryResolved 'public'
        New-Item -ItemType Directory -Path $destinationPublic -Force | Out-Null
        foreach ($entry in Get-ChildItem -LiteralPath (Join-Path $sourceDirectory 'public')) { Copy-Item -LiteralPath $entry.FullName -Destination $destinationPublic -Recurse -Force }
    }
    Write-Host 'DA CAP NHAT V1.1: 52 TUAN TIENG ANH MY. Thu muc data duoc giu nguyen.' -ForegroundColor Green
    Write-Host 'Dong tab app cu. App se mo lai; nhan Ctrl+F5 neu van thay giao dien cu.'
    & (Join-Path $targetDirectoryResolved 'start.ps1') -NoBrowser:$NoBrowser
} catch {
    Write-Host "CHUA CAP NHAT XONG: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Du lieu trong data khong bi xoa. Hay giu lai ban sao luu neu da tao.'
    exit 1
}

