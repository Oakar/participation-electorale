/**
 * Retourne une couleur RGB en dégradé continu pour un ratio 0-1 :
 * - Rouge foncé (0%) → Blanc (50%) → Bleu foncé (100%)
 */
export function ratioColor(ratio: number): string {
  if (ratio == null || isNaN(ratio)) return "#ccc";
  const pct = ratio * 100;

  if (pct < 50) {
    // Rouge foncé (180,0,0) → Blanc (255,255,255)
    const t = pct / 50;
    const r = Math.round(180 + t * 75);
    const gb = Math.round(t * 255);
    return `rgb(${r},${gb},${gb})`;
  } else {
    // Blanc (255,255,255) → Bleu foncé (0,0,170)
    const t = Math.min((pct - 50) / 50, 1);
    const rg = Math.round(255 * (1 - t));
    const b = Math.round(255 - t * 85);
    return `rgb(${rg},${rg},${b})`;
  }
}
