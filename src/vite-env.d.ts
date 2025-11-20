/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL?: string
  // Adicionar mais env vars aqui se precisar
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
