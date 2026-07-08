@echo off
title SRIE Engine - Deploy
cd /d "%~dp0"

echo ============================================
echo   SRIE ENGINE - DEPLOY A PRODUCCION
echo ============================================
echo.
echo  Servidor: 161.35.1.105
echo  Usuario:  root
echo.

set /p confirm="Confirmas el deploy? (s/n): "
if not "%confirm%"=="s" goto EOF

echo.
echo [1/5] Conectando al servidor...
ssh -o StrictHostKeyChecking=no root@161.35.1.105 "echo Conexion OK"

echo.
echo [2/5] Instalando dependencias del sistema...
ssh root@161.35.1.105 "apt-get update -qq && apt-get install -y python3-venv python3-pip -qq"

echo.
echo [3/5] Clonando repositorio...
ssh root@161.35.1.105 "cd /opt && mv stonelytics stonelytics-backup-$(date +%s) 2>/dev/null; git clone https://github.com/Daviddb007/SRIE_engie.git stonelytics"

echo.
echo [4/5] Instalando dependencias de Python...
ssh root@161.35.1.105 "cd /opt/stonelytics && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip -q && pip install -r requirements.txt -q && pip install gunicorn flask-login flask-mail flask-sqlalchemy flask-wtf flask-limiter python-dotenv requests email-validator psycopg2-binary -q"

echo.
echo [5/5] Configurando .env y reiniciando servidor...
ssh root@161.35.1.105 "cd /opt/stonelytics && cat > .env << 'ENVEOF'
FLASK_SECRET_KEY=dcd1f77aab0399e70e13a9883e23a4d9e900118912ec0277adb7df0ce802eda1
MAIL_SERVER=smtp.hostinger.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=daviddb@stonelytics.tech
MAIL_PASSWORD=%MAIL_PASSWORD%
CONTACT_EMAIL=daviddb@stonelytics.tech
WHATSAPP_NUMBER=573057708315
ADMIN_EMAIL=daviddb@stonelytics.tech
ADMIN_PASSWORD=StonelyticsAdmin2026!
DATABASE_URL=sqlite:///studio.db
OPENAI_API_KEY=%OPENAI_API_KEY%
ENVEOF"

echo.
echo  Deteniendo servidor anterior...
ssh root@161.35.1.105 "pkill -f gunicorn 2>/dev/null; sleep 1"

echo.
echo  Iniciando nuevo servidor...
ssh root@161.35.1.105 "cd /opt/stonelytics && source venv/bin/activate && nohup gunicorn --bind 0.0.0.0:10000 --workers 2 --timeout 120 app:app > /var/log/srie.log 2>&1 &"

echo.
echo  Verificando...
timeout /t 3
curl -s -o /dev/null -w "HTTP Status: %%{http_code}\n" http://161.35.1.105:10000/ 2>/dev/null || echo "Espera unos segundos y visita http://161.35.1.105:10000"

echo.
echo ============================================
echo   DEPLOY COMPLETADO
echo ============================================
echo.
echo  Admin:    http://161.35.1.105:10000/admin/login
echo  Studio:   http://161.35.1.105:10000/studio/
echo  Portal:   http://161.35.1.105:10000/portal/login
echo.
echo  Email:    daviddb@stonelytics.tech
echo  Password: StonelyticsAdmin2026!
echo.
echo  Backend:  /opt/stonelytics/
echo  Logs:     /var/log/srie.log
echo.

set /p mailpass="Ingresa MAIL_PASSWORD (deja vacio si no aplica): "
if not "%mailpass%"=="" (
    ssh root@161.35.1.105 "cd /opt/stonelytics && sed -i 's/MAIL_PASSWORD=/MAIL_PASSWORD=%mailpass%/' .env"
)

set /p openai="Ingresa OPENAI_API_KEY: "
if not "%openai%"=="" (
    ssh root@161.35.1.105 "cd /opt/stonelytics && sed -i 's|OPENAI_API_KEY=|OPENAI_API_KEY=%openai%|' .env"
)

echo.
echo  Reiniciando con credenciales...
ssh root@161.35.1.105 "cd /opt/stonelytics && pkill -f gunicorn 2>/dev/null; sleep 1; source venv/bin/activate; nohup gunicorn --bind 0.0.0.0:10000 --workers 2 --timeout 120 app:app > /var/log/srie.log 2>&1 &"
echo.
echo  Listo!

:EOF
pause
