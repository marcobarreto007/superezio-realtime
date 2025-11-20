/**
 * Badge mostrando expert/LoRA ativo
 */
interface ExpertBadgeProps {
  expert?: string
  loraAdapter?: string
  mode?: string
}

export function ExpertBadge({ expert, loraAdapter, mode }: ExpertBadgeProps) {
  if (!expert && !loraAdapter && !mode) {
    return null
  }

  return (
    <div className="flex gap-2 items-center text-xs text-gray-400 mt-2">
      {expert && (
        <span className="px-2 py-1 bg-blue-900/30 text-blue-300 rounded">
          Expert: {expert}
        </span>
      )}
      {loraAdapter && (
        <span className="px-2 py-1 bg-purple-900/30 text-purple-300 rounded">
          LoRA: {loraAdapter}
        </span>
      )}
      {mode && (
        <span className="px-2 py-1 bg-green-900/30 text-green-300 rounded">
          Mode: {mode}
        </span>
      )}
    </div>
  )
}

