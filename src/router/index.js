import { createRouter, createWebHistory } from 'vue-router'
import About from '../views/About.vue'
import First from '../views/First.vue'
import LoginGender from "../views/LoginGender.vue"
import Children from '../views/Children.vue'
import Age from '../views/Age.vue'
import Language from '../views/Language.vue'
import Home from '../views/Home.vue'
import Mapping from '../views/Mapping.vue'
import Volenteering from '../views/Volenteering.vue'
import Shelters from '../views/Shelters.vue'
import Soupkitchens from '../views/Soupkitchens.vue'
import Link_nyc from '../views/Link_nyc.vue'
import Hotlines from '../views/Hotlines.vue'
import Personal_info from '../views/Personal_info.vue'
import Help from '../views/Help.vue'
import Feedback from '../views/Feedback.vue'
// import MapMarker from './components/MapMarker.vue'
// import MapInfoWindow from './components/MapInfoWindow.vue'
const routes = [
  {
    path: '/',
    name: 'First',
    component: First
  },
  {
    path: '/logingender',
    name: 'LoginGender',
    component: LoginGender
  },
  {
    path: '/age',
    name: 'Age',
    component: Age
  },
  {
    path: '/children',
    name: 'Children',
    component: Children
  },
  {
    path: '/language',
    name: 'Language',
    component: Language
  },
  {
    path: '/home',
    name: 'Home',
    component: Home
  },
  {
    path: '/mapping',
    name: 'Mapping',
    component: Mapping
  },
  {
    path: '/volenteering',
    name: 'Volenteering',
    component: Volenteering
  },
  {
    path: '/shelters',
    name: 'Shelters',
    component: Shelters
  },
  {
    path: '/soupkitchens',
    name: 'Soupkitchens',
    component: Soupkitchens
  },
  {
    path: '/Link_nyc',
    name: 'Link_nyc',
    component: Link_nyc
  },
  {
    path: '/hotlines',
    name: 'Hotlines',
    component: Hotlines
  },
  {
    path: '/personal_info',
    name: 'Personal_info',
    component: Personal_info
  },
  {
    path: '/help',
    name: 'Help',
    component: Help
  },
  {
    path: '/feedback',
    name: 'Feedback',
    component: Feedback
  },
  
  {
    path: '/about',
    name: 'About',
    component: About
  }
  /*
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: function () {
      return import(/* webpackChunkName: "about"  '../views/About.vue')
    }
  }*/
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
