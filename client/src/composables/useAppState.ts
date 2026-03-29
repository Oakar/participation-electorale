import { ref, computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import type { Categorie, Indicateur, ViewLevel, Territory } from "../types";
import { TERRITORIES } from "../territories";
import { useGeoLabels } from "./useGeoLabels";

const categories = ref<Categorie[]>([]);
const indicateurs = ref<Indicateur[]>([]);
const hoveredCode = ref<string | null>(null);
const isBackNavigation = ref(false);

export function useAppState() {
  const route = useRoute();
  const router = useRouter();
  const geo = useGeoLabels();

  // --- Derived from route params ---

  const viewLevel = computed<ViewLevel>(() => {
    if (route.params.dept) return "communes";
    if (route.params.region) return "departements";
    if (route.params.territory) return "regions";
    return "territoires";
  });

  const selectedTerritory = computed<Territory | null>(() =>
    TERRITORIES.find((t) => t.id === route.params.territory) ?? null
  );

  const selectedRegion = computed(() => {
    const code = route.params.region as string | undefined;
    if (!code) return null;
    return { code, libelle: geo.get(code) };
  });

  const selectedDepartement = computed(() => {
    const code = route.params.dept as string | undefined;
    if (!code) return null;
    return { code, libelle: geo.get(code) };
  });

  // --- Categorie (query param) ---

  const currentCategorieId = computed({
    get: () => (route.query.categorie as string) || "",
    set: (id: string) => {
      router.replace({ query: { ...route.query, categorie: id, indicateur: undefined } });
    },
  });

  // --- Indicateur (query param) ---

  const currentIndicateurId = computed({
    get: () => (route.query.indicateur as string) || "",
    set: (id: string) => {
      router.replace({ query: { ...route.query, indicateur: id } });
    },
  });

  const currentIndicateur = computed(() =>
    indicateurs.value.find((i) => i.id === currentIndicateurId.value) ?? null
  );

  // --- Breadcrumb ---

  const breadcrumb = computed(() => {
    const crumbs: { label: string; to: any }[] = [
      { label: "Territoires", to: { name: "home", query: route.query } },
    ];
    if (selectedTerritory.value) {
      crumbs.push({
        label: selectedTerritory.value.label,
        to: { name: "regions", params: { territory: route.params.territory }, query: route.query },
      });
    }
    if (selectedRegion.value) {
      crumbs.push({
        label: selectedRegion.value.libelle,
        to: { name: "departements", params: { territory: route.params.territory, region: route.params.region }, query: route.query },
      });
    }
    if (selectedDepartement.value) {
      crumbs.push({
        label: selectedDepartement.value.libelle,
        to: { name: "communes", params: route.params, query: route.query },
      });
    }
    return crumbs;
  });

  // --- Navigation ---

  function selectTerritory(territory: Territory) {
    hoveredCode.value = null;
    isBackNavigation.value = false;
    router.push({ name: "regions", params: { territory: territory.id }, query: route.query });
  }

  function selectRegion(code: string, libelle: string) {
    hoveredCode.value = null;
    geo.store(code, libelle);
    router.push({
      name: "departements",
      params: { territory: route.params.territory, region: code },
      query: route.query,
    });
  }

  function selectDepartement(code: string, libelle: string) {
    hoveredCode.value = null;
    geo.store(code, libelle);
    router.push({
      name: "communes",
      params: { territory: route.params.territory, region: route.params.region, dept: code },
      query: route.query,
    });
  }

  function navigateTo(level: ViewLevel) {
    hoveredCode.value = null;
    isBackNavigation.value = true;
    if (level === "territoires") {
      router.push({ name: "home", query: route.query });
    } else if (level === "regions") {
      router.push({ name: "regions", params: { territory: route.params.territory }, query: route.query });
    } else if (level === "departements") {
      router.push({
        name: "departements",
        params: { territory: route.params.territory, region: route.params.region },
        query: route.query,
      });
    }
  }

  function hoverFeature(code: string | null) {
    hoveredCode.value = code;
  }

  return {
    categories,
    indicateurs,
    currentCategorieId,
    currentIndicateurId,
    currentIndicateur,
    viewLevel,
    selectedTerritory,
    selectedRegion,
    selectedDepartement,
    hoveredCode,
    isBackNavigation,
    breadcrumb,
    navigateTo,
    selectTerritory,
    selectRegion,
    selectDepartement,
    hoverFeature,
  };
}
