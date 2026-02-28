#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Reverts Windows AI disablement. Why though?
.DESCRIPTION
    Re-enables Microsoft's AI features. You sure about this?
.PARAMETER All
    Enable everything. Embrace the surveillance.
.PARAMETER Copilot
    Enable Windows Copilot
.PARAMETER Recall
    Enable Windows Recall
.PARAMETER Edge
    Enable Copilot in Edge
.PARAMETER Paint
    Enable AI in Paint
.PARAMETER Notepad
    Enable Rewrite in Notepad
.PARAMETER Typing
    Enable typing data harvesting
.PARAMETER Office
    Enable Office AI training
.PARAMETER Voice
    Enable voice AI features
#>

[CmdletBinding()]
param(
    [switch]$All,
    [switch]$Copilot,
    [switch]$Recall,
    [switch]$Edge,
    [switch]$Paint,
    [switch]$Notepad,
    [switch]$Typing,
    [switch]$Office,
    [switch]$Voice
)

$ErrorActionPreference = "SilentlyContinue"

function Write-Status {
    param([string]$msg, [switch]$error, [switch]$success, [switch]$warn)
    if ($error) { Write-Host "  [!] $msg" -ForegroundColor Red }
    elseif ($success) { Write-Host "  [~] $msg" -ForegroundColor Yellow }
    elseif ($warn) { Write-Host "  [?] $msg" -ForegroundColor Cyan }
    else { Write-Host "  [-] $msg" -ForegroundColor Gray }
}

function Enable-Copilot {
    Write-Host "`n  RE-ENABLING COPILOT" -ForegroundColor Yellow
    Write-Host "  ====================" -ForegroundColor Yellow
    
    foreach ($hive in @('HKLM', 'HKCU')) {
        Reg.exe delete "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v 'TurnOffWindowsCopilot' /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Microsoft\Windows\Shell\Copilot\BingChat" /v 'IsUserEligible' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Microsoft\Windows\Shell\Copilot" /v 'IsCopilotAvailable' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe delete "$hive\SOFTWARE\Microsoft\Windows\Shell\Copilot" /v 'CopilotDisabledReason' /f 2>$null
    }
    Write-Status "Copilot policy reverted" -success
    
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone\Microsoft.Copilot_8wekyb3d8bbwe' /v 'Value' /t REG_SZ /d 'Prompt' /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' /v 'ShowCopilotButton' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsCopilot' /v 'AllowCopilotRuntime' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband\AuxilliaryPins' /v 'CopilotPWAPin' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Copilot UI restored" -success
    
    Reg.exe delete 'HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications\Microsoft.Copilot_8wekyb3d8bbwe' /v 'DisabledByUser' /f 2>$null
    Reg.exe delete 'HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications\Microsoft.Copilot_8wekyb3d8bbwe' /v 'Disabled' /f 2>$null
    Write-Status "Copilot background access restored" -success
    
    Reg.exe delete 'HKCU\SOFTWARE\Policies\Microsoft\Windows\Explorer' /v 'DisableSearchBoxSuggestions' /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' /v 'TaskbarCompanion' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\Shell\BrandedKey' /v 'BrandedKeyChoiceType' /t REG_SZ /d 'App' /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\Shell\BrandedKey' /v 'AppAumid' /t REG_SZ /d 'Microsoft.Copilot_8wekyb3d8bbwe!App' /f 2>$null
    Write-Status "Copilot search integration restored" -success
    
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Notifications\Settings' /v 'AutoOpenCopilotLargeScreens' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\generativeAI' /v 'Value' /t REG_SZ /d 'Allow' /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\systemAIModels' /v 'Value' /t REG_SZ /d 'Allow' /f 2>$null
    Reg.exe delete 'HKLM\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy' /v 'LetAppsAccessGenerativeAI' /f 2>$null
    Reg.exe delete 'HKLM\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy' /v 'LetAppsAccessSystemAIModels' /f 2>$null
    Write-Status "Generative AI access restored" -success
    
    # Remove velocity overrides
    $nudgeIds = @('1546588812', '203105932', '2381287564', '3189581453', '3552646797', '3389499533', '4027803789', '450471565')
    foreach ($id in $nudgeIds) {
        Reg.exe delete "HKLM\SYSTEM\ControlSet001\Control\FeatureManagement\Overrides\8\$id" /f 2>$null
    }
    Write-Status "Copilot feature flags restored" -success
    
    Write-Host "  Copilot is back. Happy now?" -ForegroundColor DarkGray
}

function Enable-Recall {
    Write-Host "`n  RE-ENABLING RECALL" -ForegroundColor Yellow
    Write-Host "  ===================" -ForegroundColor Yellow
    
    foreach ($hive in @('HKLM', 'HKCU')) {
        Reg.exe delete "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableAIDataAnalysis' /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'AllowRecallEnablement' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe delete "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableClickToDo' /f 2>$null
        Reg.exe delete "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'TurnOffSavingSnapshots' /f 2>$null
        Reg.exe delete "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableSettingsAgent' /f 2>$null
        Reg.exe delete "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableAgentConnectors' /f 2>$null
        Reg.exe delete "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableAgentWorkspaces' /f 2>$null
        Reg.exe delete "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableRemoteAgentConnectors' /f 2>$null
    }
    Write-Status "Recall policies restored" -success
    
    Reg.exe delete 'HKCU\Software\Microsoft\Windows\Shell\ClickToDo' /v 'DisableClickToDo' /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband\AuxilliaryPins' /v 'RecallPin' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\SettingSync\WindowsSettingHandlers' /v 'A9HomeContentEnabled' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Recall UI restored" -success
    
    $aiActionIds = @('1853569164', '4098520719', '929719951', '1646260367')
    foreach ($id in $aiActionIds) {
        Reg.exe delete "HKLM\SYSTEM\ControlSet001\Control\FeatureManagement\Overrides\8\$id" /f 2>$null
    }
    Write-Status "AI Actions restored" -success
    
    Write-Host "  Recall is watching again. Enjoy." -ForegroundColor DarkGray
}

function Enable-Edge {
    Write-Host "`n  RE-ENABLING COPILOT IN EDGE" -ForegroundColor Yellow
    Write-Host "  ============================" -ForegroundColor Yellow
    
    $edgePolicies = @(
        'CopilotCDPPageContext', 'CopilotPageContext', 'HubsSidebarEnabled',
        'EdgeEntraCopilotPageContext', 'Microsoft365CopilotChatIconEnabled',
        'EdgeHistoryAISearchEnabled', 'ComposeInlineEnabled', 'GenAILocalFoundationalModelSettings',
        'BuiltInAIAPIsEnabled', 'AIGenThemesEnabled', 'DevToolsGenAiSettings',
        'ShareBrowsingHistoryWithCopilotSearchAllowed'
    )
    foreach ($policy in $edgePolicies) {
        Reg.exe delete 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v $policy /f 2>$null
    }
    Write-Status "Edge Copilot policies removed" -success
    
    taskkill.exe /im msedge.exe /f 2>$null
    $config = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Local State"
    if (Test-Path $config) {
        try {
            $jsonContent = (Get-Content $config -Raw).Replace('""', '"_empty"') | ConvertFrom-Json -ErrorAction Stop
            if ($jsonContent.browser.enabled_labs_experiments) {
                $flags = @('edge-copilot-mode@2', 'edge-ntp-composer@2', 'edge-compose@2')
                $jsonContent.browser.enabled_labs_experiments = $jsonContent.browser.enabled_labs_experiments | Where-Object { $_ -notin $flags }
                $newContent = $jsonContent | ConvertTo-Json -Compress -Depth 10
                $newContent = $newContent.Replace('"_empty"', '""')
                Set-Content $config -Value $newContent -Encoding UTF8 -Force
                Write-Status "Edge flags restored" -success
            }
        }
        catch {
            Write-Status "Could not restore Edge flags" -warn
        }
    }
    
    Write-Host "  Edge AI is back." -ForegroundColor DarkGray
}

function Enable-Paint {
    Write-Host "`n  RE-ENABLING AI IN PAINT" -ForegroundColor Yellow
    Write-Host "  ========================" -ForegroundColor Yellow
    
    Reg.exe delete 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableImageCreator' /f 2>$null
    Reg.exe delete 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableCocreator' /f 2>$null
    Reg.exe delete 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableGenerativeFill' /f 2>$null
    Reg.exe delete 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableGenerativeErase' /f 2>$null
    Reg.exe delete 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableRemoveBackground' /f 2>$null
    Write-Status "Paint AI features restored" -success
    
    Write-Host "  Paint is AI-infested again." -ForegroundColor DarkGray
}

function Enable-NotepadAI {
    Write-Host "`n  RE-ENABLING AI IN NOTEPAD" -ForegroundColor Yellow
    Write-Host "  ==========================" -ForegroundColor Yellow
    
    Reg.exe delete 'HKLM\SOFTWARE\Policies\Microsoft\Notepad' /v 'DisableRewrite' /f 2>$null
    Write-Status "Notepad Rewrite policy removed" -success
    
    Write-Host "  Notepad AI is back." -ForegroundColor DarkGray
}

function Enable-InputHarvesting {
    Write-Host "`n  RE-ENABLING TYPING DATA HARVESTING" -ForegroundColor Yellow
    Write-Host "  ====================================" -ForegroundColor Yellow
    
    Reg.exe add 'HKCU\Software\Microsoft\input\Settings' /v 'InsightsEnabled' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe delete 'HKCU\Software\Microsoft\InputPersonalization' /v 'RestrictImplicitInkCollection' /f 2>$null
    Reg.exe delete 'HKCU\Software\Microsoft\InputPersonalization' /v 'RestrictImplicitTextCollection' /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\InputPersonalization\TrainedDataStore' /v 'HarvestContacts' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\CPSS\Store\InkingAndTypingPersonalization' /v 'Value' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Typing data harvesting restored" -success
    
    Write-Host "  Microsoft is watching you type again." -ForegroundColor DarkGray
}

function Enable-OfficeAI {
    Write-Host "`n  RE-ENABLING OFFICE AI" -ForegroundColor Yellow
    Write-Host "  ======================" -ForegroundColor Yellow
    
    Reg.exe delete 'HKLM\SOFTWARE\Policies\Microsoft\office\16.0\common\ai\training\general' /v 'disabletraining' /f 2>$null
    Reg.exe delete 'HKLM\SOFTWARE\Policies\Microsoft\office\16.0\common\ai\training\specific\adaptivefloatie' /v 'disabletrainingofadaptivefloatie' /f 2>$null
    
    $contentPaths = @(
        'general', 'specific\alternativetext', 'specific\imagequestionandanswering',
        'specific\promptassistance', 'specific\rewrite', 'specific\summarization',
        'specific\summarizationwithreferences', 'specific\texttotable'
    )
    foreach ($path in $contentPaths) {
        Reg.exe delete "HKLM\SOFTWARE\Policies\Microsoft\office\16.0\common\ai\contentsafety\$path" /v 'disablecontentsafety' /f 2>$null
    }
    Write-Status "Office AI training restored" -success
    
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone\Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe' /v 'Value' /t REG_SZ /d 'Prompt' /f 2>$null
    Reg.exe delete 'HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications\Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe' /v 'DisabledByUser' /f 2>$null
    Reg.exe delete 'HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications\Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe' /v 'Disabled' /f 2>$null
    Reg.exe add 'HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe\WebViewHostStartupId' /v 'State' /t REG_DWORD /d 2 /f 2>$null
    Write-Status "Office Hub restored" -success
    
    Write-Host "  Office AI is training on your docs again." -ForegroundColor DarkGray
}

function Enable-VoiceAI {
    Write-Host "`n  RE-ENABLING VOICE AI" -ForegroundColor Yellow
    Write-Host "  =====================" -ForegroundColor Yellow
    
    Reg.exe add 'HKCU\Software\Microsoft\Speech_OneCore\Settings\VoiceActivation\UserPreferenceForAllApps' /v 'AgentActivationEnabled' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\Capabilities\systemAIModels' /v 'RecordUsageData' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Voice AI restored" -success
    
    Write-Host "  Voice AI is listening again." -ForegroundColor DarkGray
}

# Main
Write-Host "`n"
Write-Host "  ============================================" -ForegroundColor DarkYellow
Write-Host "     WINDOWS AI RESURRECTION (really?)" -ForegroundColor DarkYellow
Write-Host "  ============================================" -ForegroundColor DarkYellow
Write-Host "  Fine. Your funeral.`n" -ForegroundColor DarkGray

if (-not ($All -or $Copilot -or $Recall -or $Edge -or $Paint -or $Notepad -or $Typing -or $Office -or $Voice)) {
    Write-Host "  Usage: .\enable-windows-ai.ps1 [switches]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Switches:" -ForegroundColor Cyan
    Write-Host "    -All      Restore everything" -ForegroundColor White
    Write-Host "    -Copilot  Restore Windows Copilot" -ForegroundColor White
    Write-Host "    -Recall   Restore Recall surveillance" -ForegroundColor White
    Write-Host "    -Edge     Restore Copilot in Edge" -ForegroundColor White
    Write-Host "    -Paint    Restore AI in Paint" -ForegroundColor White
    Write-Host "    -Notepad  Restore Rewrite in Notepad" -ForegroundColor White
    Write-Host "    -Typing   Restore typing data harvesting" -ForegroundColor White
    Write-Host "    -Office   Restore Office AI training" -ForegroundColor White
    Write-Host "    -Voice    Restore voice AI features" -ForegroundColor White
    Write-Host ""
    exit
}

if ($All -or $Copilot) { Enable-Copilot }
if ($All -or $Recall) { Enable-Recall }
if ($All -or $Edge) { Enable-Edge }
if ($All -or $Paint) { Enable-Paint }
if ($All -or $Notepad) { Enable-NotepadAI }
if ($All -or $Typing) { Enable-InputHarvesting }
if ($All -or $Office) { Enable-OfficeAI }
if ($All -or $Voice) { Enable-VoiceAI }

Write-Host ""
Write-Host "  ============================================" -ForegroundColor DarkYellow
Write-Host "  Done. Microsofts AI has been restored." -ForegroundColor Yellow
Write-Host "  Restart Explorer or log out for full effect." -ForegroundColor DarkGray
Write-Host "  ============================================" -ForegroundColor DarkYellow
Write-Host ""
