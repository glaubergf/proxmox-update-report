#!/usr/bin/env python3
#
# ===================================================================================
# PROXMOX UPDATE REPORT
# ===================================================================================
# Arquivo..........: proxmox-update-notify.py
# Versão...........: 1.0.1
# Autor............: Glauber GF (mcnd2)
# Data.............: 30-05-2026
# Atualizado.......: 24-06-2026
#
# Objetivo:
#   - Executar o script proxmox-update-check.sh
#   - Enviar notificação por e-mail quando houver atualizações importantes ou críticas.
#
# Compatibilidade:
#   - Proxmox VE 8.x / 9.x
#   - Python 3.11+
#
# Dependências:
#   - Python padrão (smtplib, email)
#
# Arquivos:
#   - /root/proxmox-update-report/security/.env
#   - /root/proxmox-update-report/proxmox-update-check.sh
# ===================================================================================

import os
import sys
import socket
import smtplib
import fcntl
import subprocess

from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# -----------------------------------------------------------------------------
# Carrega variáveis do .env
# -----------------------------------------------------------------------------

ENV_FILE = "/root/proxmox-update-report/security/.env"

if Path(ENV_FILE).exists():
    with open(ENV_FILE, "r") as env:
        for line in env:
            line = line.strip()
            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            value = value.strip().strip('"').strip("'")
            os.environ[key.strip()] = value

# -----------------------------------------------------------------------------
# Configuração SMTP
# -----------------------------------------------------------------------------

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

FROM_ADDR = os.getenv("FROM_ADDR")
TO_ADDR = os.getenv("TO_ADDR")

# -----------------------------------------------------------------------------
# Log local
# -----------------------------------------------------------------------------

def write_log(message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    with open(LOG_FILE, "a") as log:
        log.write(
            f"[{timestamp}] {message}\n"
        )

# -----------------------------------------------------------------------------
# Valida configuração
# -----------------------------------------------------------------------------

required = [
SMTP_SERVER,
SMTP_PORT,
SMTP_USER,
SMTP_PASS,
FROM_ADDR,
TO_ADDR
]

if not all(required):
    write_log(
        "❌ Configuração SMTP inválida ou incompleta"
    )
    print(
        "❌ ERRO: Variáveis SMTP não configuradas corretamente "
        "em /root/proxmox-update-report/security/.env"
    )
    sys.exit(1)

# -----------------------------------------------------------------------------
# Configuração do script de check
# -----------------------------------------------------------------------------

CHECK_SCRIPT = "/root/proxmox-update-report/proxmox-update-check.sh"

PACKAGE_LIST_FILE = "/tmp/proxmox-update-report/packages.txt"

LOG_FILE = "/var/log/proxmox-update-notify.log"

# -----------------------------------------------------------------------------
# Arquivo de lock
# -----------------------------------------------------------------------------

LOCK_FILE = "/var/run/proxmox-update-notify.lock"

# -----------------------------------------------------------------------------
# Obtém lock para evitar execuções duplas
# -----------------------------------------------------------------------------

lock_fd = open(LOCK_FILE, "w")

try:
    fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
except BlockingIOError:
    write_log(
        "⚠️  Execução ignorada: processo já está em execução"
    )
    print(
        "⚠️  Outro processo já está executando."
    )
    sys.exit(0)

# -----------------------------------------------------------------------------
# Executa script de check
# -----------------------------------------------------------------------------

try:
    result = subprocess.run(
        [CHECK_SCRIPT],
        capture_output=True,
        text=True
    )
except Exception as err:
    write_log(
        f"❌ ERRO ao executar script de check: {err}"
    )
    print(
        f"❌ ERRO ao executar script de check: {err}"
    )
    sys.exit(2)

report = result.stdout.strip()

updates_count = 0

for line in report.splitlines():

    if "Total de Updates....:" in line:

        try:
            updates_count = int(
                line.split(":")[-1].strip()
            )
        except Exception:
            pass

# -----------------------------------------------------------------------------
# Define severidade
# -----------------------------------------------------------------------------

if "Status..............: CRÍTICO" in report:
    severity = "CRÍTICO"

elif "Status..............: URGENTE" in report:
    severity = "URGENTE"

elif "Status..............: ATENÇÃO" in report:
    severity = "ATENÇÃO"

else:
    severity = "ATUALIZADO"

# -----------------------------------------------------------------------------
# Informações do host
# -----------------------------------------------------------------------------

hostname = socket.getfqdn()

timestamp = datetime.now().strftime(
    "%Y%m%d-%H%M%S"
)

safe_hostname = hostname.replace(
    ".",
    "-"
)

severity_file = {
    "CRÍTICO": "critico",
    "URGENTE": "urgente",
    "ATENÇÃO": "atencao",
    "ATUALIZADO": "atualizado"
}.get(severity, "desconhecido")

attachment_name = (
    f"packages-{severity_file}-"
    f"{safe_hostname}-"
    f"{timestamp}.txt"
)

# -----------------------------------------------------------------------------
# Assunto
# -----------------------------------------------------------------------------

if severity == "CRÍTICO":
    emoji = "🔴"

elif severity == "URGENTE":
    emoji = "🟠"

elif severity == "ATENÇÃO":
    emoji = "🟡"

else:
    emoji = "🟢"

if severity == "ATUALIZADO":

    subject = (
        f"{emoji} Proxmox Update Report "
        f"({hostname}) - Sistema Atualizado"
    )

else:

    subject = (
        f"{emoji} Proxmox Update Report "
        f"({hostname}) - "
        f"{severity} - "
        f"{updates_count} updates pendentes"
    )

write_log(
    f"ℹ️  Check executado: "
    f"Host={hostname} "
    f"Status={severity} "
    f"Updates={updates_count} "
)

# -----------------------------------------------------------------------------
# Monta e-mail
# -----------------------------------------------------------------------------

msg = MIMEMultipart()

msg["From"] = FROM_ADDR
msg["To"] = TO_ADDR
msg["Subject"] = subject

msg.attach(MIMEText(report, "plain", "utf-8"))

# -----------------------------------------------------------------------------
# Anexo com lista de pacotes
# -----------------------------------------------------------------------------

if (
    severity != "ATUALIZADO"
    and os.path.exists(PACKAGE_LIST_FILE)
):

    with open(
        PACKAGE_LIST_FILE,
        "rb"
    ) as attachment:

        part = MIMEBase(
            "application",
            "octet-stream"
        )

        part.set_payload(
            attachment.read()
        )

    encoders.encode_base64(part)

    part.add_header(
        "Content-Disposition",
        "attachment",
        filename=attachment_name
    )

    print(f"Anexo: {attachment_name}")

    msg.attach(part)

elif severity != "ATUALIZADO":

    write_log(
        f"❌ Arquivo de anexo não encontrado: "
        f"{PACKAGE_LIST_FILE}"
    )

# -----------------------------------------------------------------------------
# Envia e-mail
# -----------------------------------------------------------------------------

try:

    server = smtplib.SMTP(
        SMTP_SERVER,
        SMTP_PORT,
        timeout=30
    )

    # server.set_debuglevel(1)

    server.ehlo()
    server.starttls()
    server.ehlo()

    server.login(
        SMTP_USER,
        SMTP_PASS
    )

    server.sendmail(
        FROM_ADDR,
        [TO_ADDR],
        msg.as_string()
    )

    server.quit()

    write_log(
        f"✅ E-mail enviado com sucesso "
        f"(Status={severity}, Updates={updates_count})"
    )

    print("Notificação enviada com sucesso.")

except Exception as err:

    write_log(
        f"❌ ERRO SMTP: {err}"
    )

    print(
        f"❌ ERRO ao enviar e-mail: {err}"
    )

    sys.exit(3)

sys.exit(0)