Param(
  [string]$Owner = "",
  [Parameter(Mandatory=$true)][string]$Repo,
  [string]$Branch = "main",
  [switch]$Private
)

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "未检测到 git，请先安装 Git 再运行此脚本。"
  exit 1
}

if (-not $Env:GITHUB_TOKEN) {
  Write-Error "未检测到环境变量 GITHUB_TOKEN，请设置后重试。"
  Write-Host "例如（PowerShell）：`$Env:GITHUB_TOKEN = 'ghp_xxx...xxx'" -ForegroundColor Yellow
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
  Write-Host "使用账户：$login，目标所有者：$Owner" -ForegroundColor Cyan
} catch {
  Write-Warning "无法获取当前用户信息：$($_.Exception.Message)。继续尝试推送，但可能创建仓库失败。"
}

# 如果仓库不存在，尝试创建它
function Create-GithubRepo {
  param([string]$owner, [string]$repoName, [bool]$isPrivate)
  $bodyObj = @{ name = $repoName; private = $isPrivate }
  try {
    if ($login -and $owner -and $owner -eq $login) {
      Write-Host "尝试在用户账户下创建仓库：$repoName" -ForegroundColor Cyan
      $resp = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/user/repos" -Method POST -Body ($bodyObj | ConvertTo-Json)
    } else {
      Write-Host "尝试在组织 $owner 下创建仓库：$repoName" -ForegroundColor Cyan
      $resp = Invoke-RestMethod -Headers $headers -Uri "https://api.github.com/orgs/$owner/repos" -Method POST -Body ($bodyObj | ConvertTo-Json)
    }
    Write-Host "仓库创建成功：https://github.com/$owner/$repoName" -ForegroundColor Green
  } catch {
    $msg = $_.Exception.Message
    if ($msg -match "already exists") {
      Write-Host "仓库已存在：$owner/$repoName，继续推送。" -ForegroundColor Yellow
    } else {
      Write-Warning "创建仓库失败：$msg（可能是权限或网络问题），继续尝试推送。"
    }
  }
}

Create-GithubRepo -owner $Owner -repoName $Repo -isPrivate ([bool]$Private)

Write-Host "初始化本地git仓库并创建提交记录..." -ForegroundColor Cyan
git init

# 配置本地提交身份（如未设置）
$cfgUser = git config user.name 2>$null
if (-not $cfgUser -or $cfgUser.Trim() -eq "") {
  git config user.name "hk-tool-web"
  git config user.email "hk-tool-web@local.invalid"
}

git add .
git commit -m "chore: initial upload" 2>$null
git branch -M $Branch

Write-Host "配置远程并推送：$Owner/$Repo ($Branch)" -ForegroundColor Cyan
$remote = "https://$login:$($Env:GITHUB_TOKEN)@github.com/$Owner/$Repo.git"
git remote remove origin 2>$null
git remote add origin $remote
git push -u origin $Branch

Write-Host "推送完成。仓库地址：https://github.com/$Owner/$Repo" -ForegroundColor Green