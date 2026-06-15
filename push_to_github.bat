@echo off
echo ========================================
echo Pushing to GitHub...
echo ========================================

cd /d "E:\claude_code_workspace\hacks\The Turing Test Hackathon 2026\AI-Trading-Strategy"

echo Adding files...
git add .

echo Committing...
git commit -m "Update: Manta - Macro-driven AI Trading Agent"

echo Pushing to GitHub...
git push -u origin main

echo ========================================
echo Done!
echo ========================================
pause
