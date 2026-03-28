# Guide Vue.js pour developpeurs React

Ce guide explique le code du frontend de la carte electorale en mettant en parallele les concepts Vue.js avec leurs equivalents React.

## 1. Vue vs React — correspondances rapides

| Concept | React | Vue 3 (Composition API) |
|---------|-------|-------------------------|
| Composant | fonction + JSX | fichier `.vue` (SFC) |
| State local | `useState()` | `ref()` |
| State derive | `useMemo()` | `computed()` |
| Side effects | `useEffect()` | `watch()` / `watchEffect()` |
| Lifecycle mount | `useEffect(() => {}, [])` | `onMounted()` |
| Lifecycle unmount | `useEffect(() => cleanup, [])` | `onUnmounted()` |
| Props | `function Comp({ name })` | `defineProps<{ name: string }>()` |
| Events | `onClick={handler}` | `@click="handler"` |
| Conditional render | `{cond && <Comp />}` | `v-if="cond"` |
| List render | `{items.map(i => <Comp key={i.id} />)}` | `v-for="i in items" :key="i.id"` |
| Context / global state | `useContext()` | composables (fonctions partagees) |
| Routing | React Router | Vue Router |
| CSS | CSS Modules, styled-components | Tailwind, scoped CSS |

## 2. Anatomie d'un fichier `.vue` (SFC)

En React, un composant est une fonction JS/TS qui retourne du JSX. En Vue, un composant est un fichier `.vue` qui contient 3 blocs :

```vue
<!-- ElectionSelector.vue -->

<script setup lang="ts">
// Equivalent du corps de la fonction React
// Tout le code ici s'execute une seule fois au setup du composant
import { ref, watch } from "vue";

const count = ref(0);  // comme useState(0)
</script>

<template>
  <!-- Equivalent du return JSX -->
  <button @click="count++">{{ count }}</button>
</template>

<style scoped>
/* CSS scope au composant (optionnel, on utilise Tailwind ici) */
</style>
```

**Equivalent React :**
```tsx
function ElectionSelector() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

**Differences cles :**
- `<script setup>` s'execute une seule fois (pas a chaque render). Pas de re-execution du corps de la fonction comme en React.
- `ref(0)` retourne un objet `{ value: 0 }`. On accede a la valeur via `.value` dans le script, mais dans le template Vue le deballe automatiquement.
- Le template utilise une syntaxe propre (`v-if`, `v-for`, `@click`, `{{ }}`) au lieu de JSX.

## 3. Reactivite : `ref()` vs `useState()`

### React
```tsx
const [name, setName] = useState("Paris");
// Pour modifier : setName("Lyon")
// Provoque un re-render complet du composant
```

### Vue
```ts
const name = ref("Paris");
// Pour modifier : name.value = "Lyon"
// Vue detecte le changement et met a jour UNIQUEMENT les parties du DOM qui utilisent `name`
```

**Difference fondamentale :** React re-execute toute la fonction composant a chaque changement d'etat. Vue ne re-execute jamais le `<script setup>` — il utilise un systeme de tracking de dependances qui met a jour chirurgicalement le DOM.

C'est pour ca qu'on n'a pas besoin de `useCallback` ou `useMemo` pour eviter les re-renders en Vue — le probleme n'existe pas.

### Dans notre code

`site/src/composables/useAppState.ts` :
```ts
const elections = ref<Election[]>([]);
const highlightedCommune = ref<string | null>(null);
```

Ce sont des refs globales (declarees hors de la fonction). Tous les composants qui les importent partagent la meme instance — equivalent d'un Context React global.

## 4. `computed()` vs `useMemo()`

### React
```tsx
const fullName = useMemo(() => `${first} ${last}`, [first, last]);
// Il faut declarer les dependances manuellement
```

### Vue
```ts
const fullName = computed(() => `${first.value} ${last.value}`);
// Les dependances sont detectees AUTOMATIQUEMENT
// Si first ou last change, fullName se recalcule
```

### Dans notre code

`site/src/composables/useAppState.ts` :
```ts
const viewLevel = computed<ViewLevel>(() => {
  if (route.params.dept) return "communes";
  if (route.params.region) return "departements";
  if (route.params.territory) return "regions";
  return "territoires";
});
```

Ce computed derive le niveau de vue directement des parametres de route. Pas besoin de synchroniser manuellement un state — il se recalcule automatiquement quand la route change.

**Computed writable** (pas d'equivalent direct en React) :
```ts
const currentElectionId = computed({
  get: () => (route.query.election as string) || "",
  set: (id: string) => {
    router.replace({ query: { ...route.query, election: id } });
  },
});
```

Lire `currentElectionId.value` retourne le query param. Ecrire `currentElectionId.value = "2022_pres_t1"` declenche un `router.replace`. Le dropdown `v-model` peut s'y binder directement.

## 5. `watch()` vs `useEffect()`

### React
```tsx
useEffect(() => {
  fetchData(electionId);
}, [electionId]); // dependances manuelles
```

### Vue
```ts
watch(
  () => [route.params.territory, route.query.election],
  () => { fetchData(); },
  { immediate: true }  // equivalent de "executer au mount aussi"
);
```

### Dans notre code

`site/src/composables/useElectionData.ts` :
```ts
watch(
  () => [route.params.territory, route.params.region, route.params.dept, route.query.election],
  loadData,
  { immediate: true }
);
```

Ce watch surveille 4 valeurs de la route. Des que l'une change (navigation, changement d'election), `loadData` est appelee. `{ immediate: true }` fait qu'elle est aussi appelee au montage initial.

## 6. Composables vs Custom Hooks

Les composables Vue sont l'equivalent exact des custom hooks React. Meme convention de nommage (`use*`), meme principe.

### React
```tsx
function useElectionData() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  useEffect(() => { /* fetch */ }, [deps]);
  return { data, loading };
}
```

### Vue
```ts
export function useElectionData() {
  const data = ref([]);
  const loading = ref(false);
  watch(deps, () => { /* fetch */ });
  return { data, loading };
}
```

**Difference importante :** en React, chaque appel a `useElectionData()` cree un state independant. En Vue aussi par defaut, SAUF si les refs sont declarees en dehors de la fonction (module scope) — dans ce cas, c'est un singleton partage.

### Pattern singleton dans notre code

```ts
// Hors de la fonction = partage entre tous les composants
const data = ref<ParticipationRecord[]>([]);
const loading = ref(false);
let initialized = false;

export function useElectionData() {
  if (!initialized) {
    initialized = true;
    // Setup du watch une seule fois
    watch(...);
  }
  return { data, loading }; // meme refs pour tous
}
```

Equivalent React : un Context + Provider qui wrappe l'app.

## 7. Vue Router vs React Router

### Structure des routes

```ts
// site/src/router.ts
const routes = [
  { path: "/", name: "home", component: TerritorySelector },
  { path: "/:territory", name: "regions", component: MapView },
  { path: "/:territory/:region", name: "departements", component: MapView },
  { path: "/:territory/:region/:dept", name: "communes", component: MapView },
];
```

Equivalent React Router :
```tsx
<Routes>
  <Route path="/" element={<TerritorySelector />} />
  <Route path="/:territory" element={<MapView />} />
  <Route path="/:territory/:region" element={<MapView />} />
  <Route path="/:territory/:region/:dept" element={<MapView />} />
</Routes>
```

### Lire les params

| React Router | Vue Router |
|---|---|
| `useParams()` | `useRoute().params` |
| `useSearchParams()` | `useRoute().query` |
| `useNavigate()` | `useRouter().push()` |

### Navigation programmatique

```ts
// Vue Router
router.push({ name: "departements", params: { territory: "metropole", region: "84" }, query: { election: "2022_pres_t1" } });

// React Router equivalent
navigate(`/metropole/84?election=2022_pres_t1`);
```

### `<router-view>` vs `<Outlet>`

```vue
<!-- Vue : App.vue -->
<router-view />

<!-- React equivalent -->
<Outlet />
```

### `<router-link>` vs `<Link>`

```vue
<!-- Vue : BreadcrumbNav.vue -->
<router-link :to="{ name: 'regions', params: { territory: 'metropole' } }">
  France metropolitaine
</router-link>

<!-- React equivalent -->
<Link to="/metropole">France metropolitaine</Link>
```

## 8. Template syntax vs JSX

### Binding d'attributs

```vue
<!-- Vue -->
<div :class="isActive ? 'bg-blue-500' : 'bg-gray-500'">
<input :value="name" @input="name = $event.target.value">
<input v-model="name">  <!-- raccourci pour la ligne au dessus -->

<!-- React -->
<div className={isActive ? 'bg-blue-500' : 'bg-gray-500'}>
<input value={name} onChange={e => setName(e.target.value)}>
```

### Rendu conditionnel

```vue
<!-- Vue -->
<div v-if="loading">Chargement...</div>
<div v-else-if="error">Erreur</div>
<div v-else>{{ data }}</div>

<!-- React -->
{loading ? <div>Chargement...</div> : error ? <div>Erreur</div> : <div>{data}</div>}
```

### Rendu de liste

```vue
<!-- Vue -->
<button v-for="region in data" :key="region.code_region" @click="select(region)">
  {{ region.libelle_region }}
</button>

<!-- React -->
{data.map(region => (
  <button key={region.code_region} onClick={() => select(region)}>
    {region.libelle_region}
  </button>
))}
```

## 9. Architecture de l'application

```
src/
├── main.ts                    # Point d'entree (createApp + router)
├── router.ts                  # Definition des 4 routes
├── App.vue                    # Layout global (header + router-view)
├── types.ts                   # Interfaces TypeScript
├── territories.ts             # Donnees statiques des 9 territoires
│
├── composables/               # "Custom hooks" Vue
│   ├── useAppState.ts         # State global (elections, navigation)
│   ├── useElectionData.ts     # Fetch reactif des donnees electorales
│   └── useGeoLabels.ts        # Cache code → nom pour breadcrumb
│
├── services/                  # Couche d'acces aux donnees
│   ├── dao.ts                 # Interface (contrat)
│   └── staticDao.ts           # Implementation (fetch JSON statiques)
│
├── components/
│   ├── TerritorySelector.vue  # Page d'accueil (grille de territoires)
│   ├── TerritoryOutline.vue   # SVG du contour d'un territoire
│   ├── MapView.vue            # Layout sidebar + carte
│   ├── TerritorySidebar.vue   # Navigation contextuelle (TOC)
│   ├── ElectionMap.vue        # Carte Leaflet interactive
│   ├── ElectionSelector.vue   # Dropdowns type/annee d'election
│   ├── BreadcrumbNav.vue      # Fil d'Ariane
│   └── MapLegend.vue          # Legende couleurs participation
│
└── utils/
    └── colors.ts              # Fonction rouge → blanc → bleu
```

### Flux de donnees

```
URL (route params + query)
    │
    ├─→ useAppState()      derive viewLevel, selectedTerritory, etc.
    │     │
    │     ├─→ BreadcrumbNav     affiche le fil d'Ariane
    │     ├─→ TerritorySidebar  affiche la liste contextuelle
    │     └─→ ElectionSelector  sync l'election avec ?election=
    │
    └─→ useElectionData()  watch la route, fetch les donnees
          │
          ├─→ TerritorySidebar  affiche les regions/depts/communes
          └─→ ElectionMap       dessine le GeoJSON avec les couleurs
```

La route est la **source de verite unique**. Tout le reste en derive. C'est l'equivalent d'un pattern "URL as state" en React.

### Navigation

Quand l'utilisateur clique sur une region (dans la carte ou la sidebar) :
1. `selectRegion("84", "Auvergne-Rhone-Alpes")` est appele
2. `router.push({ name: "departements", params: { territory: "metropole", region: "84" } })`
3. L'URL change → `/metropole/84?election=2022_pres_t1`
4. `useElectionData` detecte le changement de route et fetch `departements/84/2022_pres_t1.json`
5. `data` se met a jour → la carte et la sidebar se re-rendent

## 10. Pieges courants pour un dev React

### 1. `.value` dans le script, pas dans le template
```ts
// Script
const name = ref("Paris");
console.log(name.value); // "Paris"

// Template — Vue deballe automatiquement
<span>{{ name }}</span>  <!-- affiche "Paris", pas besoin de name.value -->
```

### 2. `ref()` vs `shallowRef()`
`ref()` rend l'objet entier reactif (deep). `shallowRef()` ne reagit qu'au remplacement de `.value`, pas aux mutations internes. Dans notre code, l'instance Leaflet est en `shallowRef` car on ne veut pas que Vue observe ses proprietes internes.

### 3. Les composants ne se re-executent pas
En React, le "render" re-execute tout le corps de la fonction. En Vue, `<script setup>` s'execute UNE SEULE FOIS. Les mises a jour du DOM sont gerees par le systeme de reactivite, pas par une re-execution.

Consequence : pas besoin de `useCallback`, `useMemo`, ou `React.memo` pour optimiser.

### 4. `v-if` detruit le composant
```vue
<ElectionMap v-if="showMap" />
```
Quand `showMap` passe de `true` a `false`, le composant est **detruit** (unmount). Quand il repasse a `true`, un **nouveau** composant est cree (mount). En React, le comportement est le meme avec du conditional rendering, mais c'est plus explicite en Vue car `v-if` est un attribut.

### 5. Singleton vs instances multiples
En React, chaque appel a un hook cree un state independant. En Vue, si les refs sont au module scope (hors de `export function`), elles sont partagees. C'est un pattern puissant mais il faut en etre conscient.

## 11. Gestion d'etat — de useState a Pinia

### Correspondance React ↔ Vue

| Besoin | React | Vue 3 |
|---|---|---|
| State local simple | `useState` | `ref()` |
| State local complexe | `useReducer` | `reactive()` + fonctions |
| State global simple | Context + `useState` | Composable singleton |
| State global structure | Redux / Zustand | **Pinia** |

### Niveau 1 : `ref()` — equivalent de `useState`

```ts
// Vue
const count = ref(0);
count.value++;

// React
const [count, setCount] = useState(0);
setCount(c => c + 1);
```

Suffisant pour le state local d'un composant.

### Niveau 2 : `reactive()` — equivalent de `useReducer`

Quand le state est un objet complexe, `reactive()` rend toutes ses proprietes reactives. Pas besoin d'un reducer avec des actions — on mute directement l'objet.

```ts
// Vue
const form = reactive({
  name: "",
  email: "",
  errors: {} as Record<string, string>,
});
form.name = "Jean";  // mutation directe, Vue detecte le changement

// React avec useReducer
const [form, dispatch] = useReducer(reducer, { name: "", email: "", errors: {} });
dispatch({ type: "SET_NAME", payload: "Jean" });
```

Vue n'a pas besoin du pattern action/reducer car son systeme de reactivite detecte les mutations. C'est a la fois plus simple et plus direct.

### Niveau 3 : Composable singleton — equivalent de Context

C'est ce qu'on utilise dans notre app. Les refs sont declarees au module scope (hors de la fonction) et partagees par tous les composants qui appellent le composable.

```ts
// composables/useAppState.ts

// Module scope = partage (equivalent d'un Context React)
const elections = ref<Election[]>([]);
const highlightedCommune = ref<string | null>(null);

export function useAppState() {
  // Chaque composant qui appelle useAppState() recoit les MEMES refs
  return { elections, highlightedCommune };
}
```

**Equivalent React :**
```tsx
const ElectionContext = createContext(null);

function ElectionProvider({ children }) {
  const [elections, setElections] = useState([]);
  return (
    <ElectionContext.Provider value={{ elections, setElections }}>
      {children}
    </ElectionContext.Provider>
  );
}

function useAppState() {
  return useContext(ElectionContext);
}
```

Le composable Vue est plus concis : pas de Provider, pas de Context, pas de wrapping de l'arbre de composants.

**Limites du composable singleton :**
- Pas d'integration avec les Vue Devtools (on ne voit pas le state)
- Pas de structure formelle (state, getters, actions sont melanges)
- Pas de hot module replacement du state en dev

### Niveau 4 : Pinia — equivalent de Redux/Zustand

**Pinia** est le store officiel de Vue 3. Il remplace Vuex (l'ancien equivalent de Redux). Son API ressemble aux composables, ce qui le rend naturel a utiliser.

#### Comparaison Redux vs Pinia

**Redux :**
```ts
// store/electionSlice.ts
const electionSlice = createSlice({
  name: 'elections',
  initialState: { list: [], loading: false },
  reducers: {
    setElections(state, action) {
      state.list = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchElections.pending, (state) => {
      state.loading = true;
    });
    builder.addCase(fetchElections.fulfilled, (state, action) => {
      state.list = action.payload;
      state.loading = false;
    });
  },
});

// Dans un composant
const elections = useSelector(state => state.elections.list);
const dispatch = useDispatch();
dispatch(fetchElections());
```

**Pinia :**
```ts
// stores/elections.ts
export const useElectionStore = defineStore('elections', () => {
  // State
  const list = ref<Election[]>([]);
  const loading = ref(false);

  // Getters (equivalent des selectors Redux)
  const electionTypes = computed(() =>
    [...new Set(list.value.map(e => e.type))]
  );

  // Actions (equivalent des thunks/reducers)
  async function fetchElections() {
    loading.value = true;
    list.value = await staticDao.fetchElections();
    loading.value = false;
  }

  return { list, loading, electionTypes, fetchElections };
});

// Dans un composant
const store = useElectionStore();
store.fetchElections();
// store.list, store.electionTypes sont reactifs
```

#### Ce que Pinia apporte par rapport au composable singleton

| Fonctionnalite | Composable singleton | Pinia |
|---|---|---|
| State partage | oui | oui |
| Vue Devtools | non | **oui** (inspection, time-travel) |
| Hot Module Replacement | non | **oui** (state survit au rechargement) |
| Structure imposee | non | **oui** (state / getters / actions) |
| Plugins | non | **oui** (persistance, logging...) |
| SSR | manuel | **oui** (hydration automatique) |
| Complexite | minimale | faible |

#### Quand utiliser quoi ?

```
State local d'un composant
  → ref() / reactive()

State partage entre quelques composants proches
  → composable singleton (ce qu'on fait)

State global avec besoin de debug, structure, plugins
  → Pinia

State derive d'une source externe (URL, API)
  → computed() depuis la route (ce qu'on fait pour viewLevel, selectedRegion...)
```

#### Notre app : ou en est-on ?

On utilise le **niveau 3** (composable singleton) pour `useAppState` et `useElectionData`. C'est adapte a notre taille d'app. Si l'app grossissait (ajout de resultats par candidat, comparaisons, filtres avances...), migrer vers Pinia serait un bon refactoring. La migration est simple car l'API Pinia avec `defineStore(() => { ... })` ressemble exactement a un composable — il suffit de wrapper le code existant.

### Zustand vs Pinia

Si vous connaissez Zustand (alternative legere a Redux), Pinia en est l'equivalent Vue. Meme philosophie : API simple, pas de boilerplate, hooks/composables natifs.

```ts
// Zustand (React)
const useStore = create((set) => ({
  count: 0,
  increment: () => set((s) => ({ count: s.count + 1 })),
}));

// Pinia (Vue)
const useStore = defineStore('counter', () => {
  const count = ref(0);
  function increment() { count.value++; }
  return { count, increment };
});
```
