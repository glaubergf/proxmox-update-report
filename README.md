<!---
# ===================================================================================
Projeto..........: proxmox-update-report
Versão...........: 1.0.1
Autor............: Glauber GF (mcnd2)
Data.............: 30-05-2026
Atualizado.......: 24-06-2026
Descrição........: Script para monitoramento de atualizações do Proxmox VE e envio 
                   automático de notificações por e-mail.
# ===================================================================================
--->

# 📦 Proxmox Update Report

O **Proxmox Update Report** é um script para automatizar a verificação de atualizações em servidores Proxmox VE, fornecendo relatórios detalhados e notificações por e-mail com classificação de criticidade.

A solução analisa pacotes disponíveis para atualização, identifica componentes críticos da plataforma, verifica necessidade de reinicialização do host e gera relatórios consolidados para apoio às atividades de operação e manutenção da infraestrutura.

### ✨ Recursos

* Verificação automática de atualizações pendentes;
* Classificação por nível de criticidade;
* Detecção de atualização de Kernel e necessidade de reboot;
* Identificação de componentes estratégicos do Proxmox VE;
* Envio de notificações por e-mail;
* Anexo automático da lista de pacotes pendentes;
* Registro local de eventos e falhas;
* Controle de execução concorrente através de lock file;
* Compatibilidade com Proxmox VE 8.x e 9.x.

O projeto foi criado com foco em simplicidade, confiabilidade e facilidade de implantação, utilizando apenas Bash e Python padrão, sem dependências externas.

---

# 🚦 Níveis de Criticidade

| Status        | Descrição                                  |
| ------------- | ------------------------------------------ |
| 🟢 ATUALIZADO | Nenhuma atualização pendente               |
| 🟡 ATENÇÃO    | Atualizações comuns disponíveis            |
| 🟠 URGENTE    | Atualizações importantes identificadas     |
| 🔴 CRÍTICO    | Atualizações críticas ou reboot necessário |

---

# 📁 Estrutura

```text
proxmox-update-report/
├── CHANGELOG.md
├── proxmox-update-check.sh
├── proxmox-update-notify.py
├── README.md
└── security
    ├── .env
    └── note.txt
```

---

# ⚙️ Configuração

## Arquivo .env

Exemplo:

```env
SMTP_SERVER=smtp.mail.domain.com
SMTP_PORT=587

SMTP_USER=usuario@domain.com
SMTP_PASS=senha-do-app

FROM_ADDR=usuario@domain.com
TO_ADDR=destino@domain.com
```

Permissões recomendadas:

```bash
chmod 600 .env
```

---

# 🚀 Execução Manual

Validação do relatório:

* execução do script

```bash
./proxmox-update-check.sh
```

* saída

```bash
======================================================================
 PROXMOX UPDATE REPORT v1.0.0
======================================================================

🔴 CRÍTICO
Atualizações críticas requerem intervenção.

----------------------------------------------------------------------

Host................: pve.homelab.mcn
Versão PVE..........: 9.2.3
Kernel Atual........: 7.0.6-2-pve
Kernel Disponível...: 7.0.12-1-pve
Reboot Necessário...: SIM
Data................: 23/06/2026 04:00:01

Status..............: CRÍTICO
Total de Updates....: 17

🔴 COMPONENTES CRÍTICOS
  • Proxmox VE Core
  • Kernel Proxmox
  • QEMU Server

🟠 COMPONENTES IMPORTANTES
  • OpenSSL

Ação Recomendada....: Planejar atualização e reinicialização do host.

======================================================================
```

Envio de notificação:

```bash
python3 proxmox-update-notify.py
```

---

# ⏰ Agendamento

Exemplo para execução semanal via Cron:

```cron
0 3 * * 1 /usr/bin/apt-get update -qq
0 4 * * 1 /usr/bin/python3 /root/proxmox-update-report/proxmox-update-notify.py >> /var/log/proxmox-update-report.log 2>&1
```

Executa:

* Toda segunda-feira
* 03h00 da manhã - atualiza cache AT
* 04h00 da manhã - executa o script

---

# 📧 Notificações

O sistema envia:

* Relatório completo no corpo do e-mail
* Assunto com nível de criticidade
* Emoji correspondente ao status
* Quantidade de atualizações pendentes
* Anexo com lista de pacotes quando existirem atualizações

---

# 📝 Logs

Arquivo de log:

* /var/log/proxmox-update-notify.log

```text
[2026-06-22 04:00:12] ❌ ERRO SMTP: [Errno -3] Temporary failure in name resolution
[2026-06-23 04:00:02] ℹ️ Check executado: Host=pve.homelab.mcn Status=CRÍTICO Updates=17 
[2026-06-23 04:00:06] ✅ E-mail enviado com sucesso (Status=CRÍTICO, Updates=17)
```

* /var/log/proxmox-update-report.log 

```text
❌ ERRO ao enviar e-mail: [Errno -3] Temporary failure in name resolution
Anexo: packages-crítico-pve-homelab-mcn-20260623-040002.txt
Notificação enviada com sucesso.
```

---

# 🔒 Compatibilidade

| Plataforma     | Status |
| -------------- | ------ |
| Proxmox VE 8.x | ✅     |
| Proxmox VE 9.x | ✅     |

---

# 📑 Histórico de Alterações

Todas as mudanças importantes deste projeto são documentadas em:

- [CHANGELOG.md](CHANGELOG.md)

---

# 🤝 Contribuições

Contribuições são bem-vindas.

---

# 📜 Licença

Este projeto está licenciado sob os termos da:

**GNU General Public License v3**

https://www.gnu.org/licenses/gpl-3.0.html

---

# 🏛️ Aviso Legal

```text
Copyright (c) 2026 Glauber GF (mcnd2)

Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
sob os termos da GNU General Public License conforme publicada pela
Free Software Foundation, na versão 3 da Licença ou posterior.

Este programa é distribuído na esperança de ser útil,
mas SEM NENHUMA GARANTIA.

Veja a Licença Pública Geral GNU para mais detalhes.
```