export default defineNuxtRouteMiddleware((to) => {
  // Public dashboard mode - sem necessidade de login
  if (to.path === '/login') {
    return navigateTo('/')
  }
})

