# Changelog

Todas as alterações relevantes deste projeto serão documentadas neste arquivo.

O formato segue o padrão Keep a Changelog e Semantic Versioning.

---

## [1.0.1] - 2026-06-24

### Adicionado

* Variável para nome do arquivo em anexo sem acentuação

### Melhorado

* Padronização do nome dos anexos removendo caracteres acentuados.
* Maior compatibilidade dos anexos com clientes SMTP e leitores de e-mail.
* Nomenclatura dos anexos simplificada para uso em automações futuras.

---

## [1.0.0] - 2026-06-22

### Adicionado

* Log local em `/var/log/proxmox-update-notify.log`
* Registro de status da execução
* Registro de envio de e-mail
* Registro de falhas SMTP

### Melhorado

* Tratamento de exceções SMTP
* Estrutura de logging
* Identificação da quantidade de updates

### Corrigido

* Correção da indentação do bloco SMTP
* Correção do tratamento de exceções
* Correção do fluxo de saída do script

---

## [0.2.0] - 2026-05-31

### Adicionado

* Status ATUALIZADO
* Status ATENÇÃO
* Status URGENTE
* Status CRÍTICO
* Arquivo `.env`
* Lock file para evitar execuções simultâneas
* Integração SMTP
* Script Python para envio de notificações
* Anexo automático contendo lista de pacotes pendentes
* Nome dinâmico para anexos
* Emoji no assunto do e-mail
* Quantidade de updates no assunto

### Melhorado

* Segurança das credenciais
* Estrutura geral do projeto
* Classificação automática de criticidade
* Relatório mais amigável
* Detecção de reboot pendente
* Assunto do e-mail mais descritivo
* Identificação automática da criticidade

---

## [0.1.0] - 2026-05-30

### Inicial

* Verificação de atualizações do Proxmox VE
* Detecção de Kernel
* Relatório textual simples
* Envio básico de notificações por e-mail
