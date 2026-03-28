/**
 * Retourne une couleur RGB en dégradé continu :
 * - Rouge saturé (0%) → Blanc (50%) → Bleu saturé (100%)
 */
export function participationColor(exprimes: number, inscrits: number): string {
  if (inscrits === 0) return "#ccc";
  const pct = (exprimes / inscrits) * 100;

  if (pct < 50) {
    // Rouge → Blanc (0% → 50%)
    const t = pct / 50;
    const g = Math.round(t * 255);
    return `rgb(255,${g},${g})`;
  } else {
    // Blanc → Bleu (50% → 100%)
    const t = Math.min((pct - 50) / 50, 1);
    const rg = Math.round(255 * (1 - t));
    return `rgb(${rg},${rg},255)`;
  }
}
