import { ref, watch, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import type { ValeurTerritoire } from "../types";
import { apiDao } from "../services/apiDao";
import { useGeoLabels } from "./useGeoLabels";

const dao = apiDao;

const data = ref<ValeurTerritoire[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
let initialized = false;
let controller: AbortController | null = null;
let loadData: () => Promise<void> = async () => {};

export function useIndicateurData() {
  if (!initialized) {
    initialized = true;

    const route = useRoute();
    const geo = useGeoLabels();

    loadData = async () => {
      const indicateurId = route.query.indicateur as string;
      const territory = route.params.territory as string | undefined;
      const region = route.params.region as string | undefined;
      const dept = route.params.dept as string | undefined;

      controller?.abort();

      if (!indicateurId || !territory) {
        data.value = [];
        return;
      }

      controller = new AbortController();
      const { signal } = controller;

      loading.value = true;
      error.value = null;
      data.value = [];

      try {
        if (dept && region) {
          data.value = await dao.fetchCommunes(indicateurId, dept, signal);
        } else if (region) {
          data.value = await dao.fetchDepartements(indicateurId, region, signal);
        } else {
          data.value = await dao.fetchRegions(indicateurId, signal);
        }
        geo.storeFromRecords(data.value);
      } catch (e) {
        if (signal.aborted) return;
        error.value = e instanceof Error ? e.message : "Erreur de chargement";
        data.value = [];
      } finally {
        if (!signal.aborted) {
          loading.value = false;
        }
      }
    };

    // Watch the route directly — covers all navigation and indicateur changes
    watch(
      () => [route.params.territory, route.params.region, route.params.dept, route.query.indicateur],
      loadData,
      { immediate: true }
    );

    onUnmounted(() => {
      initialized = false;
      controller?.abort();
      controller = null;
    });
  }

  function retry() {
    loadData();
  }

  return { data, loading, error, retry };
}
