@echo off
:: Imposta la directory di lavoro
cd /d E:\CODE\FOREX_CRYPTO_V2

:: 1. Apri la prima finestra CMD e attiva l'ambiente venv, quindi esegui update_and_train_loop.py
start /min cmd /k "venv\Scripts\activate && python update_and_train_loop.py"

:: 2. Attendi che lo script update_and_train_loop.py termini
echo Attendo il completamento dello script update_and_train_loop.py...
timeout /t 30 > nul

:: 3. Apri una nuova finestra CMD, attiva venv e prepara il comando per main_loop.py
start /min cmd /k "venv\Scripts\activate && python src/main_loop.py"

:: 4. Attendi che lo script main_loop.py termini
echo Attendo il completamento dello script main_loop.py...
timeout /t 5 > nul

:: 4. Apri un'altra finestra CMD, attiva venv e prepara il comando per evaluate_predictions.py (senza eseguirlo)
start cmd /k "venv\Scripts\activate && cd /d E:\CODE\FOREX_CRYPTO_V2 && echo python evaluate_predictions.py"

:: 5. Apri un'altra finestra CMD, attiva venv e prepara il comando per main.py (senza eseguirlo)
start cmd /k "venv\Scripts\activate && cd /d E:\CODE\FOREX_CRYPTO_V2 && echo python src/main.py"

echo Tutte le finestre CMD sono state aperte.
pause
