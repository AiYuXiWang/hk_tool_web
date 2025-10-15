Param(
  [string]$Owner = "",
  [Parameter(Mandatory=$true)][string]$Repo,
  [string]$Branch = "main",
  [switch]$Private
)

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error 'Git not found. Please install Git and rerun.'
  exit 1
}

if (-not $Env:GITHUB_TOKEN) {
  Write-Error 'GITHUB_TOKEN not set. Please set it and retry.'
  Write-Host "Example (PowerShell): `$Env:GITHUB_TOKEN = 'ghp_xxx...xxx'" -ForegroundColor Yellow
  exit 1
}

$headers = @{ 
  Authorization = "Bearer $($Env:GITHUB_TOKEN)"; 
  Accept = "application/vnd.github+json" 
}

try {
  $user = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/user" -Method GET
  $login = $user.login
  if (-not $Owner -or $Owner.Trim() -eq "") { $Owner = $login }
  Write-Host ('Using account: ' + $login + '; target owner: ' + $Owner) -ForegroundColor Cyan
} catch {
  Write-Warning ('Failed to get current user info: ' + $_.Exception.Message + '; proceeding to push, repo creation may fail.')
}

# If the repository does not exist, attempt to create it
function Create-GithubRepo {
  param([string]$owner, [string]$repoName, [bool]$isPrivate)
  $bodyObj = @{ name = $repoName; private = $isPrivate }
  try {
    if ($login -and $owner -and $owner -eq $login) {
      Write-Host ('Trying to create repo under user: ' + $repoName) -ForegroundColor Cyan
      $resp = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/user/repos" -Method POST -Body ($bodyObj | ConvertTo-Json)
    } else {
      Write-Host ('Trying to create repo under org: ' + $owner + '; name: ' + $repoName) -ForegroundColor Cyan
      $resp = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/orgs/$owner/repos" -Method POST -Body ($bodyObj | ConvertTo-Json)
    }
    Write-Host ('Repository created: https://github.com/' + $owner + '/' + $repoName) -ForegroundColor Green
  } catch {
    $msg = $_.Exception.Message
    if ($msg -match "already exists") {
      Write-Host ('Repository exists: ' + $owner + '/' + $repoName + '; continue pushing.') -ForegroundColor Yellow
    } else {
      Write-Warning ('Failed to create repo: ' + $msg + ' (permission or network issue). Continuing to push.')
    }
  }
}

Create-GithubRepo -owner $Owner -repoName $Repo -isPrivate ([bool]$Private)

Write-Host 'Init local git repository and create initial commit...' -ForegroundColor Cyan
git init

# Configure local committer identity if not set
$cfgUser = git config user.name 2>$null
if (-not $cfgUser -or $cfgUser.Trim() -eq "") {
  git config user.name "hk-tool-web"
  git config user.email "hk-tool-web@local.invalid"
}

git add .
git commit -m "chore: initial upload" 2>$null
git branch -M $Branch

Write-Host ('Configure remote and push: ' + $Owner + '/' + $Repo + ' (' + $Branch + ')') -ForegroundColor Cyan
$remote = 'https://' + $login + ':' + $Env:GITHUB_TOKEN + '@github.com/' + $Owner + '/' + $Repo + '.git'
git remote remove origin 2>$null
git remote add origin $remote
git push -u origin $Branch

$repoUrl = 'https://github.com/' + $Owner + '/' + $Repo
Write-Host ('Push complete. Repo URL: ' + $repoUrl) -ForegroundColor Green