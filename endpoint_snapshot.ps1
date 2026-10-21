param(
    [Parameter(Mandatory=$true)][string]$ExpectedComputerName,
    [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
if ($env:COMPUTERNAME -ne $ExpectedComputerName) { throw 'Host identity differs from approved host' }
$record = [ordered]@{
    schema = 'endpoint-snapshot/v1'
    collected_at = [DateTime]::UtcNow.ToString('o')
    computer = $env:COMPUTERNAME
    identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
    observations = [ordered]@{}
    collection_errors = @()
}
$queries = [ordered]@{
    os = { Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber }
    services = { Get-CimInstance Win32_Service | Select-Object Name,StartMode,StartName,PathName,State }
    firewall = { Get-NetFirewallProfile | Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction }
    listeners = { Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess }
}
foreach ($queryName in $queries.Keys) {
    try { $record.observations[$queryName] = @(& $queries[$queryName]) }
    catch { $record.collection_errors += @{ query=$queryName; error=$_.Exception.Message } }
}
$json = $record | ConvertTo-Json -Depth 8
$absoluteOutput = [IO.Path]::GetFullPath($OutputPath)
$stream = [IO.File]::Open($absoluteOutput,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::None)
try {
    $writer = New-Object IO.StreamWriter($stream, (New-Object Text.UTF8Encoding($false)))
    try { $writer.WriteLine($json); $writer.Flush() } finally { $writer.Dispose() }
} finally { $stream.Dispose() }
if ($record.collection_errors.Count -gt 0) { Write-Warning 'Snapshot includes collection errors; inspect before drawing conclusions'; exit 1 }
