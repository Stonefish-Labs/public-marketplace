<#
.SYNOPSIS
    Checks the status of all Windows AI features.
.DESCRIPTION
    Reports which AI features are blocked vs enabled.
#>

function Test-RegValue {
    param(
        [string]$Path,
        [string]$Name,
        [object]$ExpectedValue,
        [switch]$ShouldNotExist
    )
    try {
        $value = Get-ItemProperty -Path $Path -Name $Name -ErrorAction Stop | Select-Object -ExpandProperty $Name
        if ($ShouldNotExist) {
            return $false  # exists but shouldn't
        }
        return $value -eq $ExpectedValue
    }
    catch {
        if ($ShouldNotExist) {
            return $true  # doesn't exist, which is what we want
        }
        return $false
    }
}

function Write-Check {
    param([string]$Name, [bool]$Blocked)
    if ($Blocked) {
        Write-Host "  [BLOCKED] " -ForegroundColor Green -NoNewline
        Write-Host $Name -ForegroundColor White
    }
    else {
        Write-Host "  [ENABLED] " -ForegroundColor Red -NoNewline
        Write-Host $Name -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host "     WINDOWS AI STATUS REPORT" -ForegroundColor Cyan
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host ""

# ===================================================================
Write-Host "  COPILOT" -ForegroundColor Yellow
Write-Host "  -------" -ForegroundColor Yellow

$copilotPolicy = (Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot' 'TurnOffWindowsCopilot' 1) -or 
                 (Test-RegValue 'HKCU:\SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot' 'TurnOffWindowsCopilot' 1)
Write-Check "Copilot Policy" $copilotPolicy

$copilotAvail = Test-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows\Shell\Copilot' 'IsCopilotAvailable' 0
Write-Check "Copilot Availability" $copilotAvail

$copilotButton = Test-RegValue 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced' 'ShowCopilotButton' 0
Write-Check "Taskbar Button" $copilotButton

$copilotRuntime = Test-RegValue 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\WindowsCopilot' 'AllowCopilotRuntime' 0
Write-Check "Copilot Runtime" $copilotRuntime

$searchSuggestions = Test-RegValue 'HKCU:\SOFTWARE\Policies\Microsoft\Windows\Explorer' 'DisableSearchBoxSuggestions' 1
Write-Check "Search Suggestions" $searchSuggestions

$genAI = Test-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\generativeAI' 'Value' 'Deny'
Write-Check "Generative AI Access" $genAI

Write-Host ""

# ===================================================================
Write-Host "  RECALL" -ForegroundColor Yellow
Write-Host "  ------" -ForegroundColor Yellow

$recallData = (Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' 'DisableAIDataAnalysis' 1) -or
              (Test-RegValue 'HKCU:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' 'DisableAIDataAnalysis' 1)
Write-Check "AI Data Analysis" $recallData

$recallEnable = Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' 'AllowRecallEnablement' 0
Write-Check "Recall Enablement" $recallEnable

$snapshots = (Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' 'TurnOffSavingSnapshots' 1) -or
             (Test-RegValue 'HKCU:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' 'TurnOffSavingSnapshots' 1)
Write-Check "Saving Snapshots" $snapshots

$clickToDo = (Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\WindowsAI' 'DisableClickToDo' 1) -or
             (Test-RegValue 'HKCU:\Software\Microsoft\Windows\Shell\ClickToDo' 'DisableClickToDo' 1)
Write-Check "Click-to-Do" $clickToDo

Write-Host ""

# ===================================================================
Write-Host "  EDGE" -ForegroundColor Yellow
Write-Host "  ----" -ForegroundColor Yellow

$edgeSidebar = Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' 'HubsSidebarEnabled' 0
Write-Check "Sidebar/Copilot" $edgeSidebar

$edgePageContext = Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' 'CopilotPageContext' 0
Write-Check "Page Context Sharing" $edgePageContext

$edgeCompose = Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' 'ComposeInlineEnabled' 0
Write-Check "AI Compose" $edgeCompose

$edgeHistory = Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' 'ShareBrowsingHistoryWithCopilotSearchAllowed' 0
Write-Check "History Sharing" $edgeHistory

$edgeBuiltIn = Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Edge' 'BuiltInAIAPIsEnabled' 0
Write-Check "Built-in AI APIs" $edgeBuiltIn

Write-Host ""

# ===================================================================
Write-Host "  PAINT" -ForegroundColor Yellow
Write-Host "  -----" -ForegroundColor Yellow

$paintCreator = Test-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' 'DisableImageCreator' 1
Write-Check "Image Creator" $paintCreator

$paintCocreator = Test-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' 'DisableCocreator' 1
Write-Check "Cocreator" $paintCocreator

$paintFill = Test-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' 'DisableGenerativeFill' 1
Write-Check "Generative Fill" $paintFill

$paintErase = Test-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Paint' 'DisableGenerativeErase' 1
Write-Check "Generative Erase" $paintErase

Write-Host ""

# ===================================================================
Write-Host "  NOTEPAD" -ForegroundColor Yellow
Write-Host "  -------" -ForegroundColor Yellow

$notepadRewrite = Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\Notepad' 'DisableRewrite' 1
Write-Check "Rewrite AI" $notepadRewrite

Write-Host ""

# ===================================================================
Write-Host "  INPUT / TYPING" -ForegroundColor Yellow
Write-Host "  --------------" -ForegroundColor Yellow

$inputInsights = Test-RegValue 'HKCU:\Software\Microsoft\input\Settings' 'InsightsEnabled' 0
Write-Check "Input Insights" $inputInsights

$inkCollection = Test-RegValue 'HKCU:\Software\Microsoft\InputPersonalization' 'RestrictImplicitInkCollection' 1
Write-Check "Ink Collection" $inkCollection

$textCollection = Test-RegValue 'HKCU:\Software\Microsoft\InputPersonalization' 'RestrictImplicitTextCollection' 1
Write-Check "Text Collection" $textCollection

Write-Host ""

# ===================================================================
Write-Host "  OFFICE" -ForegroundColor Yellow
Write-Host "  ------" -ForegroundColor Yellow

$officeTraining = Test-RegValue 'HKLM:\SOFTWARE\Policies\Microsoft\office\16.0\common\ai\training\general' 'disabletraining' 1
Write-Check "AI Training" $officeTraining

Write-Host ""

# ===================================================================
Write-Host "  VOICE" -ForegroundColor Yellow
Write-Host "  -----" -ForegroundColor Yellow

$voiceAgent = Test-RegValue 'HKCU:\Software\Microsoft\Speech_OneCore\Settings\VoiceActivation\UserPreferenceForAllApps' 'AgentActivationEnabled' 0
Write-Check "Voice Agent" $voiceAgent

$aiUsageData = Test-RegValue 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\Capabilities\systemAIModels' 'RecordUsageData' 0
Write-Check "AI Usage Recording" $aiUsageData

Write-Host ""
Write-Host "  ================================================" -ForegroundColor DarkGray
Write-Host "  [BLOCKED] = Good, AI is disabled" -ForegroundColor Green
Write-Host "  [ENABLED] = Bad, AI is active" -ForegroundColor Red
Write-Host "  ================================================" -ForegroundColor DarkGray
Write-Host ""
