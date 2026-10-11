param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$appDirectory = $PSScriptRoot
$storageDirectory = Join-Path $appDirectory 'data'
$rootBytes = [Text.Encoding]::UTF8.GetBytes([IO.Path]::GetFullPath($appDirectory).ToLowerInvariant())
$hasher = [Security.Cryptography.SHA256]::Create()
try { $expectedRootId = ([BitConverter]::ToString($hasher.ComputeHash($rootBytes))).Replace('-','').ToLowerInvariant().Substring(0,16) } finally { $hasher.Dispose() }
New-Item -ItemType Directory -Force -Path $storageDirectory | Out-Null
function Test-GardenServer([int]$serverPort) {
    try {
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$serverPort/api/health" -TimeoutSec 1
        return ($health.app -eq 'english-garden' -and $health.ok -eq $true -and $health.rootId -eq $expectedRootId)
    } catch { return $false }
}
try {
    $nodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
    $nodeExecutable = if ($nodeCommand) { $nodeCommand.Source } else { Join-Path $env:ProgramFiles 'nodejs/node.exe' }
    if (!(Test-Path -LiteralPath $nodeExecutable)) { throw 'Can cai Node.js 22.13 tro len. Tai tai https://nodejs.org/' }
    $nodeVersionText = & $nodeExecutable --version
    $nodeVersion = [version]$nodeVersionText.Trim().TrimStart('v')
    if ($nodeVersion -lt [version]'22.13.0') { throw "Node.js $nodeVersion qua cu. Can Node.js 22.13 tro len." }
    $ports = @(4173,4183,4184,4190,4192)
    $serverPort = $null
    $existing = $false
    foreach ($candidate in $ports) {
        if (Test-GardenServer $candidate) { $serverPort=$candidate; $existing=$true; break }
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback,$candidate)
        try { $listener.Start(); $serverPort=$candidate } catch {} finally { $listener.Stop() }
        if ($null -ne $serverPort) { break }
    }
    if ($null -eq $serverPort) { throw 'Khong tim duoc cong trong. Hay dong cac cua so app cu roi thu lai.' }
    if (!$existing) {
        $previousPort = $env:PORT
        try {
            $env:PORT = [string]$serverPort
            $serverPath = Join-Path $appDirectory 'server.mjs'
            $nodeProcess = Start-Process -FilePath $nodeExecutable -ArgumentList @('--no-warnings', ('"' + $serverPath + '"')) -WorkingDirectory $appDirectory -WindowStyle Hidden -RedirectStandardOutput (Join-Path $storageDirectory 'server.log') -RedirectStandardError (Join-Path $storageDirectory 'error.log') -PassThru
        } finally { $env:PORT = $previousPort }
        $ready = $false
        for ($attempt=0; $attempt -lt 40; $attempt++) {
            if (Test-GardenServer $serverPort) { $ready=$true; break }
            $nodeProcess.Refresh()
            if ($nodeProcess.HasExited) { break }
            Start-Sleep -Milliseconds 250
        }
        if (!$ready) {
            $logPath=Join-Path $storageDirectory 'error.log'
            $detail=if(Test-Path -LiteralPath $logPath){Get-Content -LiteralPath $logPath -Raw}else{''}
            throw "Khong khoi dong duoc app. $detail"
        }
    }
    $appUrl="http://127.0.0.1:$serverPort/"
    Set-Content -LiteralPath (Join-Path $storageDirectory 'app-url.txt') -Value $appUrl -Encoding utf8
    Write-Host "APP DA SAN SANG: $appUrl" -ForegroundColor Green
    Write-Host "Du lieu duoc giu tai: $storageDirectory"
    if (!$NoBrowser) { Start-Process $appUrl }
    Write-Host 'Ban co the dong cua so nay. May chu app van chay nen.'
} catch {
    Write-Host "KHONG MO DUOC APP: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Sao chep dong loi nay de kiem tra. Du lieu cua ban khong bi xoa.'
    exit 1
}
