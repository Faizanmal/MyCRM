export function stableKey(item: unknown): string {
  if (item == null) return '';
  if (typeof item === 'string' || typeof item === 'number') return String(item);
  if (typeof item === 'object') {
    const anyItem = item as Record<string, unknown>;
    return String(
      anyItem.id ?? anyItem._id ?? anyItem.uuid ?? anyItem.key ?? anyItem.slug ?? JSON.stringify(item)
    );
  }
  return String(item);
}
