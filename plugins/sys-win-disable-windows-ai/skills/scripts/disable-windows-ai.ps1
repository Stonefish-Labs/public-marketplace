#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Exterminates Windows AI features. All of them. Or just the ones you pick.
.DESCRIPTION
    Comprehensive script to disable Microsoft's AI infestation in Windows 11.
    Based on zoicware/RemoveWindowsAI - registry tweaks portion.
.PARAMETER All
    Disable everything. Nuclear option.
.PARAMETER Copilot
    Disable Windows Copilot (taskbar, system tray, search integration)
.PARAMETER Recall
    Disable Windows Recall (screenshot surveillance)
.PARAMETER Edge
    Disable Copilot and AI features in Microsoft Edge
.PARAMETER Paint
    Disable AI features in Paint (Image Creator, Cocreator, etc.)
.PARAMETER Notepad
    Disable Rewrite AI in Notepad
.PARAMETER Typing
    Disable typing data harvesting and Input Insights
.PARAMETER Office
    Disable Office AI training
.PARAMETER Voice
    Disable AI voice features
.EXAMPLE
    .\disable-windows-ai.ps1 -All
    .\disable-windows-ai.ps1 -Copilot -Edge -Recall
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
    elseif ($success) { Write-Host "  [X] $msg" -ForegroundColor Green }
    elseif ($warn) { Write-Host "  [~] $msg" -ForegroundColor Yellow }
    else { Write-Host "  [-] $msg" -ForegroundColor Cyan }
}

function Disable-Copilot {
    Write-Host "`n  KILLING COPILOT" -ForegroundColor Red
    Write-Host "  ================" -ForegroundColor Red
    
    # Delete telemetry and startup keys
    Reg.exe delete 'HKCU\Software\Microsoft\Windows\Shell\Copilot' /v 'CopilotLogonTelemetryTime' /f 2>$null
    Reg.exe delete 'HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\Microsoft.Copilot_8wekyb3d8bbwe\Copilot.StartupTaskId' /f 2>$null
    Reg.exe delete 'HKCU\Software\Microsoft\Copilot' /v 'WakeApp' /f 2>$null
    Reg.exe delete 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsAI\LastConfiguration' /f 2>$null
    
    # Set for both HKLM and HKCU
    foreach ($hive in @('HKLM', 'HKCU')) {
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot" /v 'TurnOffWindowsCopilot' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Microsoft\Windows\Shell\Copilot\BingChat" /v 'IsUserEligible' /t REG_DWORD /d 0 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Microsoft\Windows\Shell\Copilot" /v 'IsCopilotAvailable' /t REG_DWORD /d 0 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Microsoft\Windows\Shell\Copilot" /v 'CopilotDisabledReason' /t REG_SZ /d 'FeatureIsDisabled' /f 2>$null
    }
    Write-Status "Copilot policy disabled" -success
    
    # Deny microphone access
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone\Microsoft.Copilot_8wekyb3d8bbwe' /v 'Value' /t REG_SZ /d 'Deny' /f 2>$null
    Write-Status "Copilot microphone access denied" -success
    
    # Hide taskbar button
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' /v 'ShowCopilotButton' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Copilot taskbar button hidden" -success
    
    # Disable Copilot runtime
    Reg.exe add 'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsCopilot' /v 'AllowCopilotRuntime' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband\AuxilliaryPins' /v 'CopilotPWAPin' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Copilot runtime disabled" -success
    
    # Disable background access
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications\Microsoft.Copilot_8wekyb3d8bbwe' /v 'DisabledByUser' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications\Microsoft.Copilot_8wekyb3d8bbwe' /v 'Disabled' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Copilot background access disabled" -success
    
    # Disable search suggestions (Copilot in search)
    Reg.exe add 'HKCU\SOFTWARE\Policies\Microsoft\Windows\Explorer' /v 'DisableSearchBoxSuggestions' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Copilot in Windows Search disabled" -success
    
    # Disable Ask Copilot in taskbar search
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' /v 'TaskbarCompanion' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\Shell\BrandedKey' /v 'BrandedKeyChoiceType' /t REG_SZ /d 'Search' /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\Shell\BrandedKey' /v 'AppAumid' /t REG_SZ /d ' ' /f 2>$null
    Reg.exe add 'HKCU\SOFTWARE\Policies\Microsoft\Windows\CopilotKey' /v 'SetCopilotHardwareKey' /t REG_SZ /d ' ' /f 2>$null
    Write-Status "Copilot key and taskbar companion disabled" -success
    
    # Disable auto-open on large screens
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Notifications\Settings' /v 'AutoOpenCopilotLargeScreens' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Auto-open Copilot disabled" -success
    
    # Disable Copilot nudges (velocity IDs)
    $nudgeIds = @('1546588812', '203105932', '2381287564', '3189581453', '3552646797')
    foreach ($id in $nudgeIds) {
        Reg.exe add "HKLM\SYSTEM\ControlSet001\Control\FeatureManagement\Overrides\8\$id" /v 'EnabledState' /t REG_DWORD /d 1 /f 2>$null
    }
    Write-Status "Copilot nudges disabled" -success
    
    # Disable Copilot in taskbar/systray (velocity IDs)
    $taskbarIds = @('3389499533', '4027803789', '450471565')
    foreach ($id in $taskbarIds) {
        Reg.exe add "HKLM\SYSTEM\ControlSet001\Control\FeatureManagement\Overrides\8\$id" /v 'EnabledState' /t REG_DWORD /d 1 /f 2>$null
    }
    Write-Status "Copilot taskbar/systray integration disabled" -success
    
    # Hide Copilot ads in settings
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent' /v 'DisableConsumerAccountStateContent' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Copilot ads in Settings hidden" -success
    
    # Deny generative AI access
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\generativeAI' /v 'Value' /t REG_SZ /d 'Deny' /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\systemAIModels' /v 'Value' /t REG_SZ /d 'Deny' /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\systemAIModels' /v 'Value' /t REG_SZ /d 'Deny' /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy' /v 'LetAppsAccessGenerativeAI' /t REG_DWORD /d 2 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Windows\AppPrivacy' /v 'LetAppsAccessSystemAIModels' /t REG_DWORD /d 2 /f 2>$null
    Write-Status "Generative AI access denied" -success
    
    Write-Host "  Copilot terminated." -ForegroundColor Green
}

function Disable-Recall {
    Write-Host "`n  KILLING RECALL" -ForegroundColor Red
    Write-Host "  ===============" -ForegroundColor Red
    
    foreach ($hive in @('HKLM', 'HKCU')) {
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableAIDataAnalysis' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'AllowRecallEnablement' /t REG_DWORD /d 0 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableClickToDo' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'TurnOffSavingSnapshots' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableSettingsAgent' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableAgentConnectors' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableAgentWorkspaces' /t REG_DWORD /d 1 /f 2>$null
        Reg.exe add "$hive\SOFTWARE\Policies\Microsoft\Windows\WindowsAI" /v 'DisableRemoteAgentConnectors' /t REG_DWORD /d 1 /f 2>$null
    }
    Write-Status "Recall policies disabled" -success
    
    # Disable Click-to-Do
    Reg.exe add 'HKCU\Software\Microsoft\Windows\Shell\ClickToDo' /v 'DisableClickToDo' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Click-to-Do disabled" -success
    
    # Hide Recall pin
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Taskband\AuxilliaryPins' /v 'RecallPin' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Recall taskbar pin hidden" -success
    
    # Disable recall homepage
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\SettingSync\WindowsSettingHandlers' /v 'A9HomeContentEnabled' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Recall customized homepage disabled" -success
    
    # Disable AI actions velocity IDs
    $aiActionIds = @('1853569164', '4098520719', '929719951')
    foreach ($id in $aiActionIds) {
        Reg.exe add "HKLM\SYSTEM\ControlSet001\Control\FeatureManagement\Overrides\8\$id" /v 'EnabledState' /t REG_DWORD /d 1 /f 2>$null
    }
    # Enable hiding AI actions when none available
    Reg.exe add 'HKLM\SYSTEM\ControlSet001\Control\FeatureManagement\Overrides\8\1646260367' /v 'EnabledState' /t REG_DWORD /d 2 /f 2>$null
    Write-Status "AI Actions disabled" -success
    
    Write-Host "  Recall neutralized." -ForegroundColor Green
}

function Disable-Edge {
    Write-Host "`n  KILLING COPILOT IN EDGE" -ForegroundColor Red
    Write-Host "  ========================" -ForegroundColor Red
    
    # Edge policies
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'CopilotCDPPageContext' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'CopilotPageContext' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'HubsSidebarEnabled' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'EdgeEntraCopilotPageContext' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'Microsoft365CopilotChatIconEnabled' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'EdgeHistoryAISearchEnabled' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'ComposeInlineEnabled' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'GenAILocalFoundationalModelSettings' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'BuiltInAIAPIsEnabled' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'AIGenThemesEnabled' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'DevToolsGenAiSettings' /t REG_DWORD /d 2 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Edge' /v 'ShareBrowsingHistoryWithCopilotSearchAllowed' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Edge Copilot policies disabled" -success
    
    # Try to set Edge flags
    taskkill.exe /im msedge.exe /f 2>$null
    $config = "$env:LOCALAPPDATA\Microsoft\Edge\User Data\Local State"
    if (Test-Path $config) {
        try {
            $jsonContent = (Get-Content $config -Raw).Replace('""', '"_empty"') | ConvertFrom-Json -ErrorAction Stop
            if ($null -eq ($jsonContent.browser | Get-Member -MemberType NoteProperty -Name enabled_labs_experiments -ErrorAction SilentlyContinue)) {
                $jsonContent.browser | Add-Member -MemberType NoteProperty -Name enabled_labs_experiments -Value @()
            }
            $flags = @('edge-copilot-mode@2', 'edge-ntp-composer@2', 'edge-compose@2')
            foreach ($flag in $flags) {
                if ($jsonContent.browser.enabled_labs_experiments -notcontains $flag) {
                    $jsonContent.browser.enabled_labs_experiments += $flag
                }
            }
            $newContent = $jsonContent | ConvertTo-Json -Compress -Depth 10
            $newContent = $newContent.Replace('"_empty"', '""')
            Set-Content $config -Value $newContent -Encoding UTF8 -Force
            Write-Status "Edge flags set to disable Copilot" -success
        }
        catch {
            Write-Status "Could not set Edge flags - set manually at edge://flags" -warn
        }
    }
    else {
        Write-Status "Edge config not found - open Edge once and run again" -warn
    }
    
    Write-Host "  Edge AI features disabled." -ForegroundColor Green
}

function Disable-Paint {
    Write-Host "`n  KILLING AI IN PAINT" -ForegroundColor Red
    Write-Host "  ====================" -ForegroundColor Red
    
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableImageCreator' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableCocreator' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableGenerativeFill' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableGenerativeErase' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' /v 'DisableRemoveBackground' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Paint AI features disabled" -success
    
    Write-Host "  Paint is clean." -ForegroundColor Green
}

function Disable-NotepadAI {
    Write-Host "`n  KILLING AI IN NOTEPAD" -ForegroundColor Red
    Write-Host "  ======================" -ForegroundColor Red
    
    # Policy method
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\Notepad' /v 'DisableRewrite' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Notepad Rewrite policy disabled" -success
    
    # Try settings.dat method
    $notepadAppData = "$env:LOCALAPPDATA\Packages\Microsoft.WindowsNotepad_8wekyb3d8bbwe\Settings"
    if (Test-Path "$notepadAppData\settings.dat") {
        try {
            # Load settings hive
            reg.exe load 'HKU\NotepadSettings' "$notepadAppData\settings.dat" 2>$null
            Reg.exe add 'HKU\NotepadSettings' /v 'RewriteEnabled' /t REG_DWORD /d 0 /f 2>$null
            [GC]::Collect()
            reg.exe unload 'HKU\NotepadSettings' 2>$null
            Write-Status "Notepad settings.dat updated" -success
        }
        catch {
            Write-Status "Could not update Notepad settings.dat" -warn
        }
    }
    
    Write-Host "  Notepad is clean." -ForegroundColor Green
}

function Disable-InputHarvesting {
    Write-Host "`n  KILLING TYPING DATA HARVESTING" -ForegroundColor Red
    Write-Host "  ================================" -ForegroundColor Red
    
    Reg.exe add 'HKCU\Software\Microsoft\input\Settings' /v 'InsightsEnabled' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Input Insights disabled" -success
    
    Reg.exe add 'HKCU\Software\Microsoft\InputPersonalization' /v 'RestrictImplicitInkCollection' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\InputPersonalization' /v 'RestrictImplicitTextCollection' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\InputPersonalization\TrainedDataStore' /v 'HarvestContacts' /t REG_DWORD /d 0 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\CPSS\Store\InkingAndTypingPersonalization' /v 'Value' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Typing data harvesting disabled" -success
    
    Write-Host "  Your typing is private." -ForegroundColor Green
}

function Disable-OfficeAI {
    Write-Host "`n  KILLING OFFICE AI" -ForegroundColor Red
    Write-Host "  ==================" -ForegroundColor Red
    
    # AI training
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\office\16.0\common\ai\training\general' /v 'disabletraining' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKLM\SOFTWARE\Policies\Microsoft\office\16.0\common\ai\training\specific\adaptivefloatie' /v 'disabletrainingofadaptivefloatie' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Office AI training disabled" -success
    
    # Content safety (prevents AI processing)
    $contentPaths = @(
        'general',
        'specific\alternativetext',
        'specific\imagequestionandanswering',
        'specific\promptassistance',
        'specific\rewrite',
        'specific\summarization',
        'specific\summarizationwithreferences',
        'specific\texttotable'
    )
    foreach ($path in $contentPaths) {
        Reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\office\16.0\common\ai\contentsafety\$path" /v 'disablecontentsafety' /t REG_DWORD /d 1 /f 2>$null
    }
    Write-Status "Office content AI processing disabled" -success
    
    # Office Hub
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone\Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe' /v 'Value' /t REG_SZ /d 'Deny' /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications\Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe' /v 'DisabledByUser' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications\Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe' /v 'Disabled' /t REG_DWORD /d 1 /f 2>$null
    Reg.exe add 'HKCU\Software\Classes\Local Settings\Software\Microsoft\Windows\CurrentVersion\AppModel\SystemAppData\Microsoft.MicrosoftOfficeHub_8wekyb3d8bbwe\WebViewHostStartupId' /v 'State' /t REG_DWORD /d 1 /f 2>$null
    Write-Status "Office Hub background access disabled" -success
    
    Write-Host "  Office AI silenced." -ForegroundColor Green
}

function Disable-VoiceAI {
    Write-Host "`n  KILLING VOICE AI" -ForegroundColor Red
    Write-Host "  =================" -ForegroundColor Red
    
    Reg.exe add 'HKCU\Software\Microsoft\Speech_OneCore\Settings\VoiceActivation\UserPreferenceForAllApps' /v 'AgentActivationEnabled' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "Voice activation agent disabled" -success
    
    Reg.exe add 'HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\Capabilities\systemAIModels' /v 'RecordUsageData' /t REG_DWORD /d 0 /f 2>$null
    Write-Status "AI model usage recording disabled" -success
    
    Write-Host "  Voice AI muted." -ForegroundColor Green
}

# Main execution
Write-Host "`n" 
Write-Host "  ============================================" -ForegroundColor DarkRed
Write-Host "     WINDOWS AI EXTERMINATION PROTOCOL" -ForegroundColor DarkRed
Write-Host "  ============================================" -ForegroundColor DarkRed
Write-Host "  Microsofts AI does not belong here." -ForegroundColor DarkGray
Write-Host ""

# If no switches specified, show help
if (-not ($All -or $Copilot -or $Recall -or $Edge -or $Paint -or $Notepad -or $Typing -or $Office -or $Voice)) {
    Write-Host "  Usage: .\disable-windows-ai.ps1 [switches]" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Switches:" -ForegroundColor Cyan
    Write-Host "    -All      Kill everything" -ForegroundColor White
    Write-Host "    -Copilot  Kill Windows Copilot" -ForegroundColor White
    Write-Host "    -Recall   Kill Recall surveillance" -ForegroundColor White
    Write-Host "    -Edge     Kill Copilot in Edge" -ForegroundColor White
    Write-Host "    -Paint    Kill AI in Paint" -ForegroundColor White
    Write-Host "    -Notepad  Kill Rewrite in Notepad" -ForegroundColor White
    Write-Host "    -Typing   Kill typing data harvesting" -ForegroundColor White
    Write-Host "    -Office   Kill Office AI training" -ForegroundColor White
    Write-Host "    -Voice    Kill voice AI features" -ForegroundColor White
    Write-Host ""
    Write-Host "  Example: .\disable-windows-ai.ps1 -Copilot -Edge -Recall" -ForegroundColor DarkGray
    Write-Host ""
    exit
}

# Execute based on switches
if ($All -or $Copilot) { Disable-Copilot }
if ($All -or $Recall) { Disable-Recall }
if ($All -or $Edge) { Disable-Edge }
if ($All -or $Paint) { Disable-Paint }
if ($All -or $Notepad) { Disable-NotepadAI }
if ($All -or $Typing) { Disable-InputHarvesting }
if ($All -or $Office) { Disable-OfficeAI }
if ($All -or $Voice) { Disable-VoiceAI }

Write-Host ""
Write-Host "  ============================================" -ForegroundColor DarkGreen
Write-Host "  Done. Microsofts AI has been dealt with." -ForegroundColor Green
Write-Host "  Restart Explorer or log out to complete." -ForegroundColor DarkGray
Write-Host "  ============================================" -ForegroundColor DarkGreen
Write-Host ""
