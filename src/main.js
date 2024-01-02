import { createApp } from 'vue'
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import { Loader } from "@googlemaps/js-api-loader"
const loader = new Loader({
  apiKey: "AIzaSyCzX_AfviqCmFLFZQaaY5yRrTh75_fnlyY",
  version: "weekly",
});

loader.load().then(() => {
  map = new google.maps.Map(document.getElementById("map"), {
    center: { lat: 40.749364, lng: -73.999159 },
    zoom: 10,
  });
});
// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyA8IGYQt4DWzVbYbMortyx99Ro8eysuME8",
  authDomain: "hope-5da45.firebaseapp.com",
  projectId: "hope-5da45",
  storageBucket: "hope-5da45.appspot.com",
  messagingSenderId: "546691709874",
  appId: "1:546691709874:web:6f4927be50ef76932882ab",
  measurementId: "G-M6PE93M59S"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
// import VueGeolocation from 'vue-browser-geolocation'
// import * as VueGoogleMaps from "vue2-google-maps" // Import package
// Vue.config.productionTip = false
// Vue.use(VueGoogleMaps, {
//   load: {
//     key: "AIzaSyCzX_AfviqCmFLFZQaaY5yRrTh75_fnlyY",
//     libraries: "places"
//   }
// });
// new Vue({
//   render: h => h(App),
// }).$mount('#app')

// Vue.use(VueGeolocation)

// new Vue({
//   render: h => h(App),
// }).$mount('#app')
createApp(App).use(router).mount('#app')
