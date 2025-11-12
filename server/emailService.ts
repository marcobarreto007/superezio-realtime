// Serviço de Email para SuperEzio
// Suporta IMAP (Gmail, Outlook, etc.)

import Imap from 'imap';
import { simpleParser, ParsedMail, Attachment } from 'mailparser';

// Tipagem para a configuração do IMAP
interface ImapConfig {
  user: string;
  password: string;
  host: string;
  port: number;
  tls: boolean;
  tlsOptions: { rejectUnauthorized: boolean };
}

// Tipagem para o objeto de email que retornamos
export interface Email {
  seqno: number;
  subject: string;
  from: string;
  to: string;
  date: Date | null;
  text: string;
  html: string | boolean;
  attachments: Attachment[];
}

// Configuração de email (do .env)
function getEmailConfig(): { imap: ImapConfig } {
  // Carregar variáveis de ambiente de forma segura
  // Em um app real, usar um pacote como dotenv para carregar de um arquivo .env
  return {
    imap: {
      user: process.env.EMAIL_USER || '',
      password: process.env.EMAIL_PASSWORD || '',
      host: process.env.EMAIL_HOST || 'imap.gmail.com',
      port: parseInt(process.env.EMAIL_PORT || '993', 10),
      tls: process.env.EMAIL_TLS !== 'false',
      tlsOptions: { rejectUnauthorized: false },
    },
  };
}

// Função genérica para conectar e abrir a caixa de email
function connectAndOpenBox(folder: string, imap: Imap): Promise<void> {
  return new Promise((resolve, reject) => {
    imap.once('ready', () => {
      imap.openBox(folder, false, (err: Error | null) => {
        if (err) return reject(err);
        resolve();
      });
    });
    imap.once('error', reject);
    imap.connect();
  });
}

// Ler emails recentes
export async function readEmails(limit: number = 10, folder: string = 'INBOX'): Promise<Email[]> {
  const config = getEmailConfig();
  if (!config.imap.user || !config.imap.password) {
    throw new Error('Email não configurado. Configure EMAIL_USER e EMAIL_PASSWORD.');
  }

  const imap = new Imap(config.imap);

  return new Promise<Email[]>(async (resolve, reject) => {
    try {
      await connectAndOpenBox(folder, imap);
      
      // Buscar emails não lidos ou dos últimos 7 dias
      imap.search(['UNSEEN', ['SINCE', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)]], (err: Error | null, results: number[] | undefined) => {
        if (err) {
          imap.end();
          return reject(err);
        }
        if (!results || results.length === 0) {
          imap.end();
          return resolve([]);
        }

        const emails: Email[] = [];
        const fetch = imap.fetch(results.slice(-limit), { bodies: '' });

        fetch.on('message', (msg, seqno) => {
          msg.on('body', (stream) => {
            simpleParser(stream, (err: Error | null, parsed: ParsedMail) => {
              if (err) return;
              emails.push({
                seqno,
                subject: parsed.subject || '',
                from: parsed.from?.text || '',
                to: parsed.to?.text || '',
                date: parsed.date || null,
                text: parsed.text || '',
                html: parsed.html || '',
                attachments: parsed.attachments || [],
              });
            });
          });
          msg.once('attributes', (attrs) => {
            imap.addFlags(attrs.uid, ['\\Seen'], (err: Error | null) => {
              if (err) console.error('Erro ao marcar email como lido:', err);
            });
          });
        });

        fetch.once('error', (err: Error) => {
          imap.end();
          reject(err);
        });

        fetch.once('end', () => {
          imap.end();
          resolve(emails.sort((a, b) => b.seqno - a.seqno)); // Ordenar por mais recente
        });
      });
    } catch (error) {
      imap.end();
      reject(error);
    }
  });
}

// Buscar emails por assunto ou remetente
export async function searchEmails(query: string, limit: number = 10): Promise<Partial<Email>[]> {
    const config = getEmailConfig();
    if (!config.imap.user || !config.imap.password) {
        throw new Error('Email não configurado.');
    }

    const imap = new Imap(config.imap);

    return new Promise<Partial<Email>[]>(async (resolve, reject) => {
        try {
            await connectAndOpenBox('INBOX', imap);

            imap.search(['OR', ['SUBJECT', query], ['FROM', query]], (err: Error | null, results: number[] | undefined) => {
                if (err) {
                    imap.end();
                    return reject(err);
                }
                if (!results || results.length === 0) {
                    imap.end();
                    return resolve([]);
                }

                const emails: Partial<Email>[] = [];
                const fetch = imap.fetch(results.slice(-limit), { bodies: '' });

                fetch.on('message', (msg, seqno) => {
                    msg.on('body', (stream) => {
                        simpleParser(stream, (err: Error | null, parsed: ParsedMail) => {
                            if (err) return;
                            emails.push({
                                seqno,
                                subject: parsed.subject || '',
                                from: parsed.from?.text || '',
                                date: parsed.date || null,
                                text: parsed.text?.substring(0, 500) || '', // Preview
                            });
                        });
                    });
                });

                fetch.once('error', (err: Error) => {
                    imap.end();
                    reject(err);
                });

                fetch.once('end', () => {
                    imap.end();
                    resolve(emails.sort((a, b) => (b.seqno || 0) - (a.seqno || 0)));
                });
            });
        } catch (error) {
            imap.end();
            reject(error);
        }
    });
}


// Contar emails não lidos
export async function getUnreadCount(): Promise<number> {
  const config = getEmailConfig();
  if (!config.imap.user || !config.imap.password) {
    throw new Error('Email não configurado.');
  }

  const imap = new Imap(config.imap);

  return new Promise<number>(async (resolve, reject) => {
    try {
      await connectAndOpenBox('INBOX', imap);
      imap.search(['UNSEEN'], (err: Error | null, results: number[] | undefined) => {
        imap.end();
        if (err) return reject(err);
        resolve(results ? results.length : 0);
      });
    } catch (error) {
      imap.end();
      reject(error);
    }
  });
}

