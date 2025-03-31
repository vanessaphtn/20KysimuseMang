import { createRouter, createWebHistory } from 'vue-router'
import CategoryPage from '@/pages/CategoryPage.vue';
import GamePage from '@/pages/GamePage.vue';


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
  { path: '/', 
  name: 'CategoryPage', 
  component: CategoryPage
  },

  { path: '/game/:category',
   name: 'GamePage',
  component: GamePage
   }
    
  ],

})

export default router
