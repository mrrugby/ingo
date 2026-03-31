import { createApp } from "vue";
import { registerSW } from "virtual:pwa-register";

import App from "./App.vue";
import router from "./router";
import "./assets/main.css";
import { useAuthStore } from "./stores/auth";

registerSW({ immediate: true });

const app = createApp(App);
app.use(router);
app.mount("#app");

const auth = useAuthStore();
auth.initialize();

