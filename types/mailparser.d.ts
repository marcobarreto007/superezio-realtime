declare module 'mailparser' {
  import { Readable } from 'stream';

  export interface AddressObject {
    value: Array<{ name: string; address: string }>;
    text: string;
  }

  export interface Attachment {
    filename?: string;
    contentType?: string;
    size?: number;
    content: Buffer | Readable;
  }

  export interface ParsedMail {
    subject?: string;
    from?: AddressObject;
    to?: AddressObject;
    date?: Date;
    text?: string;
    html?: string | boolean;
    attachments?: Attachment[];
  }

  export function simpleParser(
    stream: Readable | NodeJS.ReadableStream,
    callback: (err: Error | null, mail: ParsedMail) => void
  ): void;
}
