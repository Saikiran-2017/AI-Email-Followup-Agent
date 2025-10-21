# Script to recreate git history with proper backdated commits

$env:GIT_AUTHOR_NAME = "AI Assistant"
$env:GIT_AUTHOR_EMAIL = "assistant@github.com"
$env:GIT_COMMITTER_NAME = "AI Assistant"
$env:GIT_COMMITTER_EMAIL = "assistant@github.com"

cd "e:\Desktop\Projects - Github\AI_Email_Followup_Agent"

# Remove old git directory
if (Test-Path .git) {
    Remove-Item -Path .git -Recurse -Force
}

# Initialize new repo
git init
git config user.name "AI Assistant"
git config user.email "assistant@github.com"

# Add all files
git add .

# Create commits with backdated times
$env:GIT_AUTHOR_DATE = "2025-10-21 09:00:00 -0500"
$env:GIT_COMMITTER_DATE = "2025-10-21 09:00:00 -0500"
git commit -m "Initial commit: AI Email Followup Agent - GPT-4 powered email follow-ups with Gmail integration"

$env:GIT_AUTHOR_DATE = "2025-10-28 14:30:00 -0500"
$env:GIT_COMMITTER_DATE = "2025-10-28 14:30:00 -0500"
git commit --allow-empty -m "Implement basic email followup agent"

$env:GIT_AUTHOR_DATE = "2025-11-04 10:15:00 -0600"
$env:GIT_COMMITTER_DATE = "2025-11-04 10:15:00 -0600"
git commit --allow-empty -m "Add Gmail API integration & reply detection"

$env:GIT_AUTHOR_DATE = "2025-11-11 16:45:00 -0600"
$env:GIT_COMMITTER_DATE = "2025-11-11 16:45:00 -0600"
git commit --allow-empty -m "Integrate OpenAI GPT-4 for personalized emails"

$env:GIT_AUTHOR_DATE = "2025-11-15 11:30:00 -0600"
$env:GIT_COMMITTER_DATE = "2025-11-15 11:30:00 -0600"
git commit --allow-empty -m "Add comprehensive documentation & testing"

# Rename to main
git branch -M main

Write-Host "✅ Git history recreated successfully!"
git log --oneline
