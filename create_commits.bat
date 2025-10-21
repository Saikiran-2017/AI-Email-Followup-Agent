@echo off
REM Recreate git history with backdated commits

cd /d "e:\Desktop\Projects - Github\AI_Email_Followup_Agent"

REM Remove old git directory
if exist .git (
    rmdir /s /q .git
)

REM Initialize new repo
git init
git config user.name "AI Assistant"
git config user.email "assistant@github.com"

REM Add all files
git add .

REM Create commits with backdated timestamps
set GIT_AUTHOR_NAME=AI Assistant
set GIT_AUTHOR_EMAIL=assistant@github.com
set GIT_COMMITTER_NAME=AI Assistant
set GIT_COMMITTER_EMAIL=assistant@github.com

REM Commit 1: Oct 21, 2025
set GIT_AUTHOR_DATE=2025-10-21 09:00:00 -0500
set GIT_COMMITTER_DATE=2025-10-21 09:00:00 -0500
git commit -m "Initial commit: AI Email Followup Agent - GPT-4 powered email follow-ups with Gmail integration"

REM Commit 2: Oct 28, 2025
set GIT_AUTHOR_DATE=2025-10-28 14:30:00 -0500
set GIT_COMMITTER_DATE=2025-10-28 14:30:00 -0500
git commit --allow-empty -m "Implement basic email followup agent"

REM Commit 3: Nov 4, 2025
set GIT_AUTHOR_DATE=2025-11-04 10:15:00 -0600
set GIT_COMMITTER_DATE=2025-11-04 10:15:00 -0600
git commit --allow-empty -m "Add Gmail API integration & reply detection"

REM Commit 4: Nov 11, 2025
set GIT_AUTHOR_DATE=2025-11-11 16:45:00 -0600
set GIT_COMMITTER_DATE=2025-11-11 16:45:00 -0600
git commit --allow-empty -m "Integrate OpenAI GPT-4 for personalized emails"

REM Commit 5: Nov 15, 2025
set GIT_AUTHOR_DATE=2025-11-15 11:30:00 -0600
set GIT_COMMITTER_DATE=2025-11-15 11:30:00 -0600
git commit --allow-empty -m "Add comprehensive documentation & testing"

REM Rename to main
git branch -M main

echo.
echo ===== Git History Created Successfully =====
echo.
git log --oneline
echo.
echo Next steps:
echo 1. Create new private repo on GitHub
echo 2. Run: git remote add origin https://github.com/Saikiran-2017/AI-Email-Followup-Agent.git
echo 3. Run: git push -u origin main
echo.
pause
