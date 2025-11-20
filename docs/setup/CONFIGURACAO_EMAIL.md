# 📧 Configuração de Email para SuperEzio

O SuperEzio pode acessar seus emails via IMAP. Configure as credenciais no `.env.local`.

---

## 🔧 CONFIGURAÇÃO

### 1. Adicionar variáveis no `.env.local`:

```env
# Email Configuration
EMAIL_USER=seu-email@gmail.com
EMAIL_PASSWORD=sua-senha-ou-app-password
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_TLS=true
```

---

## 📋 PROVEDORES COMUNS

### Gmail
```env
EMAIL_USER=seu-email@gmail.com
EMAIL_PASSWORD=sua-app-password  # ⚠️ Use App Password, não senha normal
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_TLS=true
```

**Como obter App Password do Gmail:**
1. Acesse: https://myaccount.google.com/apppasswords
2. Gere uma senha de app
3. Use essa senha (não sua senha normal)

### Outlook/Hotmail
```env
EMAIL_USER=seu-email@outlook.com
EMAIL_PASSWORD=sua-senha
EMAIL_HOST=outlook.office365.com
EMAIL_PORT=993
EMAIL_TLS=true
```

### Yahoo
```env
EMAIL_USER=seu-email@yahoo.com
EMAIL_PASSWORD=sua-app-password
EMAIL_HOST=imap.mail.yahoo.com
EMAIL_PORT=993
EMAIL_TLS=true
```

---

## 🎯 COMO USAR

Depois de configurar, você pode usar comandos como:

```
"ler emails"
"mostrar emails"
"últimos 5 emails"
"buscar email por assunto X"
"quantos emails não lidos"
```

---

## 🔒 SEGURANÇA

- ⚠️ **NUNCA** commite o `.env.local` no git
- Use **App Passwords** quando disponível (Gmail, Yahoo)
- O SuperEzio só **LÊ** emails, não envia ou modifica
- Emails são marcados como lidos automaticamente

---

## 🐛 TROUBLESHOOTING

**Erro: "Email não configurado"**
- Verifique se as variáveis estão no `.env.local`
- Reinicie o servidor após adicionar variáveis

**Erro: "Authentication failed"**
- Gmail: Use App Password, não senha normal
- Verifique se a senha está correta
- Verifique se "Acesso a apps menos seguros" está habilitado (não recomendado)

**Erro: "Connection timeout"**
- Verifique se o host e porta estão corretos
- Verifique firewall/antivírus

---

*Configurado em 2025-11-11*

