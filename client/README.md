# PRISME — Client Vue.js

Frontend de l'application PRISME. Carte interactive Leaflet avec navigation regions / departements / communes.

## Developpement

```bash
npm install
npm run dev        # http://localhost:3000/prisme/
```

Le proxy Vite redirige `/api` vers `http://localhost:8080` (backend Spring Boot).

## Build

```bash
npm run build      # Genere dist/
```

## Architecture

```
src/
  components/       # ElectionMap, IndicateurSelector, TerritorySidebar, MapLegend, ...
  composables/      # useAppState, useIndicateurData, useGeoLabels
  services/         # dao (interface), apiDao (implementation API REST)
  utils/            # colors (echelle de couleur par ratio)
  types.ts          # Categorie, Indicateur, ValeurTerritoire, Territory, ViewLevel
  territories.ts    # Definition des territoires (Metropole, DOM-TOM)
  router.ts         # Routes Vue Router
```
