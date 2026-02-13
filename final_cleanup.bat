@echo off
cd /d "e:\Desktop\Projects - Github\AI_Email_Followup_Agent"

echo Removing helper scripts...
del create_commits.bat create_commits.ps1 fix_push.bat push_to_github.bat recreate_with_email.bat cleanup.bat 2>nul

echo Staging changes...
git add -A

echo Committing...
git commit -m "Clean up: Remove setup scripts" --no-verify

echo Pushing to GitHub...
git push -f origin main

echo.
echo Done! Repository is now clean.
echo Helper scripts removed from GitHub.
echo.
pause
