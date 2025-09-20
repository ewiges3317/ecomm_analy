@echo off
setlocal ENABLEDELAYEDEXPANSION
title Delivery -> CSAT -> Repeat pipeline

REM Keep logs folder around (optional)
if not exist logs mkdir logs

echo [RUN] Delivery -> CSAT -> Repeat pipeline
cd /d "%~dp0\.."

echo [1/7] Profile inputs
python "scripts\profile_delivery_inputs.py" || goto :err

echo [2/7] Build journey table
python "scripts\build_journey.py" || goto :err

echo [3/7] KPIs + exec snapshot
python "scripts\kpi_delivery_csat.py" || goto :err

echo [4/7] $ impact simulator
python "scripts\simulate_impact_delivery.py" || goto :err

echo [5/7] Prioritize fixes (states/sellers)
python "scripts\prioritize_fixes.py" || goto :err

echo [6/7] One-pager + charts
python "scripts\make_exec_onepager.py" || goto :err
python "scripts\make_exec_charts.py" || goto :err

echo [7/7] CSV pack + PPTX deck
python "scripts\make_exec_csv_pack.py" || goto :err
python "scripts\make_exec_deck.py" || goto :err

echo(
echo ✅ DONE. Key outputs:
echo  - docs\EXEC_1P_Delivery_CSAT_Repeat.md
echo  - docs\impact_summary.txt
echo  - docs\prioritize_fixes_summary.txt
echo  - outputs\dashboards\*.png
echo  - outputs\reports\exec_csv_pack.zip
echo  - outputs\reports\Delivery_CSAT_Repeat_Executive.pptx
echo(
pause
exit /b 0

:err
echo(
echo ❌ Pipeline stopped with an error. Scroll up to see which step failed.
echo(
pause
exit /b 1
