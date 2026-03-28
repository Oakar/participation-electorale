import { ref, watch, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import type { ParticipationRecord } from "../types";
import { staticDao } from "../services/staticDao";
import { useGeoLabels } from "./useGeoLabels";

const dao = staticDao;

const data = ref<ParticipationRecord[]>([]);
const loading = ref(false);
const error = ref<string | null>(null);
let initialized = false;
let controller: AbortController | null = null;
let loadData: () => Promise<void> = async () => {};

export function useElectionData() {
  if (!initialized) {
    initialized = true;

    const route = useRoute();
    const geo = useGeoLabels();

    loadData = async () => {
      const electionId = route.query.election as string;
      const territory = route.params.territory as string | undefined;
      const region = route.params.region as string | undefined;
      const dept = route.params.dept as string | undefined;

      controller?.abort();

      if (!electionId || !territory) {
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
          data.value = await dao.fetchCommunes(dept, electionId, signal);
        } else if (region) {
          data.value = await dao.fetchDepartements(region, electionId, signal);
        } else {
          data.value = await dao.fetchRegions(electionId, signal);
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

    // Watch the route directly — covers all navigation and election changes
    watch(
      () => [route.params.territory, route.params.region, route.params.dept, route.query.election],
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
