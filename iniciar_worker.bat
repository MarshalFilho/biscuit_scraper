@echo off
title MarketPulse AI - Worker Daemon Local
color 0A
echo =======================================================================
echo   📈 MarketPulse AI - Worker Daemon Local (Monitoramento & IA)
echo =======================================================================
echo.
echo   [*] Conectando ao Supabase e iniciando escuta de comandos...
echo   [*] Agendamento automatico configurado para todos os dias as 22:00
echo   [*] Disparos sob demanda via Dashboard Vercel serao executados na hora
echo.
echo =======================================================================

python backend/main.py --daemon

pause
