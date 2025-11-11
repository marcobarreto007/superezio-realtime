// Serviço de Email para SuperEzio
// Suporta IMAP (Gmail, Outlook, etc.) e Gmail API

import Imap from 'imap';
import { simpleParser } from 'mailparser';

// Configuração de email (do .env.local)
function getEmailConfig() {
  return {
    imap: {
      user: process.env.EMAIL_USER || '',
      password: process.env.EMAIL_PASSWORD || '',
      host: process.env.EMAIL_HOST || 'imap.gmail.com',
      port: parseInt(process.env.EMAIL_PORT || '993'),
      tls: process.env.EMAIL_TLS !== 'false',
      tlsOptions: { rejectUnauthorized: false },
    },
  };
}

// Ler emails recentes
export async function readEmails(limit = 10, folder = 'INBOX') {
  return new Promise((resolve, reject) => {
    const config = getEmailConfig();
    
    if (!config.imap.user || !config.imap.password) {
      return reject(new Error('Email não configurado. Configure EMAIL_USER e EMAIL_PASSWORD no .env.local'));
    }

    const imap = new Imap(config.imap);

    imap.once('ready', () => {
      imap.openBox(folder, false, (err, box) => {
        if (err) {
          imap.end();
          return reject(err);
        }

        // Buscar emails não lidos ou recentes
        imap.search(['UNSEEN', ['SINCE', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)]], (err, results) => {
          if (err) {
            imap.end();
            return reject(err);
          }

          if (!results || results.length === 0) {
            imap.end();
            return resolve([]);
          }

          // Pegar os últimos N emails
          const fetch = imap.fetch(results.slice(-limit), {
            bodies: '',
            struct: true,
          });

          const emails = [];

          fetch.on('message', (msg, seqno) => {
            const email = {
              seqno,
              subject: '',
              from: '',
              to: '',
              date: null,
              text: '',
              html: '',
              attachments: [],
            };

            msg.on('body', (stream, info) => {
              simpleParser(stream, (err, parsed) => {
                if (err) return;
                
                email.subject = parsed.subject || '';
                email.from = parsed.from?.text || '';
                email.to = parsed.to?.text || '';
                email.date = parsed.date || null;
                email.text = parsed.text || '';
                email.html = parsed.html || '';
                email.attachments = parsed.attachments || [];
              });
            });

            msg.once('attributes', (attrs) => {
              const uid = attrs.uid;
              imap.addFlags(uid, ['\\Seen'], (err) => {
                if (err) console.error('Error marking as read:', err);
              });
            });

            msg.once('end', () => {
              emails.push(email);
            });
          });

          fetch.once('error', (err) => {
            imap.end();
            reject(err);
          });

          fetch.once('end', () => {
            imap.end();
            resolve(emails);
          });
        });
      });
    });

    imap.once('error', (err) => {
      reject(err);
    });

    imap.connect();
  });
}

// Buscar emails por assunto ou remetente
export async function searchEmails(query, limit = 10) {
  return new Promise((resolve, reject) => {
    const config = getEmailConfig();
    
    if (!config.imap.user || !config.imap.password) {
      return reject(new Error('Email não configurado'));
    }

    const imap = new Imap(config.imap);

    imap.once('ready', () => {
      imap.openBox('INBOX', false, (err) => {
        if (err) {
          imap.end();
          return reject(err);
        }

        // Buscar por assunto ou remetente
        imap.search(['OR', ['SUBJECT', query], ['FROM', query]], (err, results) => {
          if (err) {
            imap.end();
            return reject(err);
          }

          if (!results || results.length === 0) {
            imap.end();
            return resolve([]);
          }

          const fetch = imap.fetch(results.slice(-limit), {
            bodies: '',
            struct: true,
          });

          const emails = [];

          fetch.on('message', (msg) => {
            const email = {
              subject: '',
              from: '',
              date: null,
              text: '',
            };

            msg.on('body', (stream) => {
              simpleParser(stream, (err, parsed) => {
                if (err) return;
                email.subject = parsed.subject || '';
                email.from = parsed.from?.text || '';
                email.date = parsed.date || null;
                email.text = parsed.text?.substring(0, 500) || '';
              });
            });

            msg.once('end', () => {
              emails.push(email);
            });
          });

          fetch.once('end', () => {
            imap.end();
            resolve(emails);
          });

          fetch.once('error', (err) => {
            imap.end();
            reject(err);
          });
        });
      });
    });

    imap.once('error', reject);
    imap.connect();
  });
}

// Contar emails não lidos
export async function getUnreadCount() {
  return new Promise((resolve, reject) => {
    const config = getEmailConfig();
    
    if (!config.imap.user || !config.imap.password) {
      return reject(new Error('Email não configurado'));
    }

    const imap = new Imap(config.imap);

    imap.once('ready', () => {
      imap.openBox('INBOX', false, (err, box) => {
        if (err) {
          imap.end();
          return reject(err);
        }

        imap.search(['UNSEEN'], (err, results) => {
          imap.end();
          if (err) return reject(err);
          resolve(results ? results.length : 0);
        });
      });
    });

    imap.once('error', reject);
    imap.connect();
  });
}

