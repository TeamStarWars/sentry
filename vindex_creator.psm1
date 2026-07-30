# Vindex Creator Panel â€” Module PowerShell
# Import: Import-Module .\Vindex_creator.psm1
# Utilisation: See-PhareMachines, Start-PharePanel, Stop-PharePanel

$Script:VindexDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Start-PharePanel {
    <#
    .SYNOPSIS
        Demarre le panel createur web
    .PARAMETER Port
        Port du panel (defaut: 9090)
    #>
    param([int]$Port = 9090)
    $result = & py "$Script:VindexDir\main.py" creator $Port 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] $result"
        Write-Host "[i] Ouvrez http://127.0.0.1:$Port dans votre navigateur"
    } else {
        Write-Error $result
    }
}

function Stop-PharePanel {
    <#
    .SYNOPSIS
        Arrete le panel createur
    #>
    $result = & py "$Script:VindexDir\main.py" creator stop 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[-] $result"
    } else {
        Write-Error $result
    }
}

function Get-PhareStatus {
    <#
    .SYNOPSIS
        Affiche le statut du Phare et du panel createur
    #>
    $result = & py "$Script:VindexDir\main.py" phare status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[Phare] $result"
    }
    $panel = & py "$Script:VindexDir\main.py" creator status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[Panel] $panel"
    }
}

function See-PhareMachines {
    <#
    .SYNOPSIS
        Affiche toutes les machines connectees au Phare
    .DESCRIPTION
        Retourne un tableau PowerShell avec les machines, leurs modules actifs, alertes
    .EXAMPLE
        See-PhareMachines | Format-Table -AutoSize
        See-PhareMachines | Where-Object { $_.Alertes -gt 0 } | Format-Table
    #>
    $raw = & py -c "
import json, sys
from core import cloud_phare
try:
    clients = cloud_phare.CLIENTS
    if not clients:
        print(json.dumps([]))
    else:
        rows = []
        for cid, info in clients.items():
            mods = info.get('modules', {})
            actifs = [m for m, a in mods.items() if a]
            rows.append({
                'Machine': info.get('host', '?'),
                'IP': info.get('ip', '?'),
                'OS': info.get('os', '?'),
                'RAM%': info.get('ram_pct', '?'),
                'Modules': ', '.join(actifs) if actifs else '-',
                'Alertes': info.get('alerts_count', 0),
                'Vu': info.get('last_seen', '?')
            })
        print(json.dumps(rows, ensure_ascii=False))
except:
    print(json.dumps([]))
" 2>&1
    if ($LASTEXITCODE -eq 0 -and $raw) {
        $machines = $raw | ConvertFrom-Json
        if ($machines -and $machines.Count -gt 0) {
            return $machines
        }
    }
    Write-Host "[i] Aucune machine connectee. Lancez 'py main.py phare' d'abord."
}

function Start-PhareServer {
    <#
    .SYNOPSIS
        Demarre le serveur Phare
    .PARAMETER Port
        Port HTTP (defaut: 8089)
    .PARAMETER Bind
        Adresse de bind (defaut: 127.0.0.1, utiliser 0.0.0.0 pour le LAN)
    .PARAMETER Token
        Token d'authentification optionnel
    #>
    param(
        [int]$Port = 8089,
        [string]$Bind = "127.0.0.1",
        [string]$Token = $null
    )
    $argsList = @("$Script:VindexDir\main.py", "phare", $Port, $Bind)
    if ($Token) { $argsList += $Token }
    $result = & py $argsList 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] $result" -ForegroundColor Green
    } else {
        Write-Error $result
    }
}

function Connect-PhareClient {
    <#
    .SYNOPSIS
        Connecte cette machine en client a un Phare distant
    .PARAMETER Ip
        IP du serveur Phare
    .PARAMETER Port
        Port du serveur Phare (defaut: 8089)
    .PARAMETER Token
        Token d'authentification
    #>
    param(
        [string]$Ip,
        [int]$Port = 8089,
        [string]$Token = $null
    )
    if (-not $Ip) {
        Write-Error "Usage: Connect-PhareClient -Ip <ip_phare> [-Port 8089] [-Token '...']"
        return
    }
    $argsList = @("$Script:VindexDir\main.py", "phare-client", $Ip, $Port)
    if ($Token) { $argsList += $Token }
    $result = & py $argsList 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[+] $result" -ForegroundColor Green
    } else {
        Write-Error $result
    }
}

Export-ModuleMember -Function Start-PharePanel, Stop-PharePanel, Get-PhareStatus, See-PhareMachines, Start-PhareServer, Connect-PhareClient
