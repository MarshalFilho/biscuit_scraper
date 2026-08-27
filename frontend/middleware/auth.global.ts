export default defineNuxtRouteMiddleware(async (to) => {
  if (process.server) return

  const supabase = useSupabase()
  const { data: { session } } = await supabase.auth.getSession()

  if (!session && to.path !== '/login') {
    return navigateTo('/login')
  }

  if (session && to.path === '/login') {
    return navigateTo('/')
  }
})
