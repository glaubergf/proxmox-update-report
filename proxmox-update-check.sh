#!/bin/bash
#
# ===================================================================================
# PROXMOX UPDATE REPORT
# ===================================================================================
# Arquivo..........: proxmox-update-check.sh
# Versão...........: 1.0.1
# Autor............: Glauber GF (mcnd2)
# Data.............: 30-05-2026
# Atualizado.......: 22-06-2026
#
# Objetivo:
#   - Detectar atualizações relevantes do Proxmox
#   - Detectar atualização de kernel
#   - Detectar necessidade de reboot
#   - Classificar criticidade
#   - Gerar relatório amigável para e-mail
#
# Compatibilidade:
#   - Proxmox VE 8.x / 9.x
# ===================================================================================

set -euo pipefail

SCRIPT_VERSION="1.0.1"

HOSTNAME=$(hostname -f)
DATE=$(date '+%d/%m/%Y %H:%M:%S')

TMP_FILE=$(mktemp)

cleanup() {
    rm -f "$TMP_FILE"
}

trap cleanup EXIT

# ------------------------------------------------------------------------------
# Pacotes atualizáveis
# ------------------------------------------------------------------------------

apt list --upgradable 2>/dev/null > "$TMP_FILE"

UPDATES=$(tail -n +2 "$TMP_FILE")

TOTAL_UPDATES=$(echo "$UPDATES" | grep -c . || true)

# ------------------------------------------------------------------------------
# Arquivo auxiliar para envio por e-mail
# ------------------------------------------------------------------------------

REPORT_DIR="/tmp/proxmox-update-report"

mkdir -p "$REPORT_DIR"

PACKAGE_LIST_FILE="${REPORT_DIR}/packages.txt"

echo "$UPDATES" > "$PACKAGE_LIST_FILE"

# ------------------------------------------------------------------------------
# Informações do sistema
# ------------------------------------------------------------------------------

PVE_VERSION=$(pveversion 2>/dev/null | cut -d/ -f2)
RUNNING_KERNEL=$(uname -r)

# ------------------------------------------------------------------------------
# Kernel disponível
# ------------------------------------------------------------------------------

AVAILABLE_KERNEL=$(awk '
/^proxmox-kernel-[0-9]+\.[0-9]+\// {
    print $2
}
' "$TMP_FILE" | sort -V | tail -1)

if [[ -n "$AVAILABLE_KERNEL" ]]; then
    AVAILABLE_KERNEL="${AVAILABLE_KERNEL}-pve"
fi

REBOOT_REQUIRED="NÃO"

if [[ -n "$AVAILABLE_KERNEL" ]]; then
    if [[ "$AVAILABLE_KERNEL" != "$RUNNING_KERNEL" ]]; then
        REBOOT_REQUIRED="SIM"
    fi
fi

# ------------------------------------------------------------------------------
# Categorias
# ------------------------------------------------------------------------------

HAS_PVE_CORE=0
HAS_KERNEL=0
HAS_QEMU=0

HAS_OPENSSH=0
HAS_OPENSSL=0
HAS_SYSTEMD=0
HAS_ZFS=0

grep -Eiq 'pve-manager|libpve-|proxmox-ve' <<< "$UPDATES" && HAS_PVE_CORE=1 || true
grep -Eiq 'proxmox-kernel|pve-kernel' <<< "$UPDATES" && HAS_KERNEL=1 || true
grep -Eiq 'qemu-server' <<< "$UPDATES" && HAS_QEMU=1 || true

grep -Eiq 'openssh' <<< "$UPDATES" && HAS_OPENSSH=1 || true
grep -Eiq 'openssl' <<< "$UPDATES" && HAS_OPENSSL=1 || true
grep -Eiq 'systemd' <<< "$UPDATES" && HAS_SYSTEMD=1 || true
grep -Eiq 'zfs' <<< "$UPDATES" && HAS_ZFS=1 || true

CRITICAL_COUNT=$((HAS_PVE_CORE + HAS_KERNEL + HAS_QEMU))
IMPORTANT_COUNT=$((HAS_OPENSSH + HAS_OPENSSL + HAS_SYSTEMD + HAS_ZFS))

# ------------------------------------------------------------------------------
# Criticidade
# ------------------------------------------------------------------------------

if (( TOTAL_UPDATES == 0 )); then

    STATUS="ATUALIZADO"
    EXIT_CODE=0

elif (( HAS_KERNEL == 1 || HAS_PVE_CORE == 1 )) || [[ "$REBOOT_REQUIRED" == "SIM" ]]; then

    STATUS="CRÍTICO"
    EXIT_CODE=3

elif (( IMPORTANT_COUNT > 0 )); then

    STATUS="URGENTE"
    EXIT_CODE=2

else

    STATUS="ATENÇÃO"
    EXIT_CODE=1

fi

# ------------------------------------------------------------------------------
# Cabeçalho
# ------------------------------------------------------------------------------

echo
echo "======================================================================"
echo " PROXMOX UPDATE REPORT v${SCRIPT_VERSION}"
echo "======================================================================"
echo

case "$STATUS" in

    ATUALIZADO)
        echo "🟢 SISTEMA ATUALIZADO"
        echo "Nenhuma atualização pendente."
        ;;

    ATENÇÃO)
        echo "🟡 ATENÇÃO"
        echo "Existem atualizações disponíveis."
        ;;

    URGENTE)
        echo "🟠 URGENTE"
        echo "Atualizações importantes foram identificadas."
        ;;

    CRÍTICO)
        echo "🔴 CRÍTICO"
        echo "Atualizações críticas requerem intervenção."
        ;;

esac

echo
echo "----------------------------------------------------------------------"
echo

echo "Host................: ${HOSTNAME}"
echo "Versão PVE..........: ${PVE_VERSION}"
echo "Kernel Atual........: ${RUNNING_KERNEL}"

if [[ -n "$AVAILABLE_KERNEL" ]]; then
    echo "Kernel Disponível...: ${AVAILABLE_KERNEL}"
fi

echo "Reboot Necessário...: ${REBOOT_REQUIRED}"
echo "Data................: ${DATE}"

echo
echo "Status..............: ${STATUS}"
echo "Total de Updates....: ${TOTAL_UPDATES}"
echo

# ------------------------------------------------------------------------------
# Componentes críticos
# ------------------------------------------------------------------------------

if (( CRITICAL_COUNT > 0 )); then

    echo "🔴 COMPONENTES CRÍTICOS"

    if (( HAS_PVE_CORE )); then
        echo "  • Proxmox VE Core"
    fi

    if (( HAS_KERNEL )); then
        echo "  • Kernel Proxmox"
    fi

    if (( HAS_QEMU )); then
        echo "  • QEMU Server"
    fi

    echo

fi

# ------------------------------------------------------------------------------
# Componentes importantes
# ------------------------------------------------------------------------------

if (( IMPORTANT_COUNT > 0 )); then

    echo "🟠 COMPONENTES IMPORTANTES"

    if (( HAS_OPENSSH )); then
        echo "  • OpenSSH"
    fi

    if (( HAS_OPENSSL )); then
        echo "  • OpenSSL"
    fi

    if (( HAS_SYSTEMD )); then
        echo "  • Systemd"
    fi

    if (( HAS_ZFS )); then
        echo "  • ZFS"
    fi

    echo

fi

# ------------------------------------------------------------------------------
# Ação recomendada
# ------------------------------------------------------------------------------

case "$STATUS" in

    ATUALIZADO)
        ACTION="Nenhuma ação necessária."
        ;;

    ATENÇÃO)
        ACTION="Planejar atualização em momento oportuno."
        ;;

    URGENTE)
        ACTION="Atualização recomendada o quanto antes."
        ;;

    CRÍTICO)
        ACTION="Planejar atualização e reinicialização do host."
        ;;

esac

echo "Ação Recomendada....: ${ACTION}"
echo
echo "======================================================================"

exit ${EXIT_CODE}