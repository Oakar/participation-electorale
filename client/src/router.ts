import { createRouter, createWebHashHistory } from "vue-router";
import TerritorySelector from "./components/TerritorySelector.vue";
import MapView from "./components/MapView.vue";

export const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: "/", name: "home", component: TerritorySelector },
    { path: "/:territory", name: "regions", component: MapView },
    { path: "/:territory/:region", name: "departements", component: MapView },
    { path: "/:territory/:region/:dept", name: "communes", component: MapView },
  ],
});
