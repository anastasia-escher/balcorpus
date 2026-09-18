<script lang="ts" setup>
import {ref} from 'vue'

const mobileNavOpen = ref(false)
const iconClass = ref('pi-moon')

const onThemeToggler = () => {
  document.documentElement.classList.toggle('p-dark')
  iconClass.value = iconClass.value === 'pi-moon' ? 'pi-sun' : 'pi-moon'
}

const links = [
  { path: '/', label: 'Home', icon: 'pi pi-home' },
]
</script>

<template>
  <div class="bg-blue-50 min-h-screen w-full">
    <section class="py-8 px-4 lg:px-10 bg-blue-800">
      <nav class="relative">
        <div class="flex justify-between items-center">
          <div class="lg:hidden">
            <button @click="mobileNavOpen = !mobileNavOpen" class="flex items-center p-3 rounded focus:outline-none">
              <i class="pi pi-bars text-white text-xl" />
            </button>
          </div>
          <!-- Desktop nav links -->
          <ul class="hidden lg:flex lg:space-x-10 items-center">
            <li v-for="link in links" :key="link.path">
              <NuxtLink class="text-white font-semibold hover:text-blue-50 flex items-center gap-1" :to="link.path">
                <i :class="link.icon" />
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
          <div class="hidden lg:flex items-center gap-4">
            <button @click="onThemeToggler" class="text-white p-2 rounded-full transition hover:bg-blue-700 focus:outline-none">
              <i :class="iconClass" />
            </button>
          </div>
        </div>
      </nav>
      <!-- Mobile nav overlay -->
      <transition name="fade">
        <div v-if="mobileNavOpen" class="fixed inset-0 z-40 bg-blue-800/90" @click="mobileNavOpen = false"></div>
      </transition>
      <transition name="slide">
        <nav v-if="mobileNavOpen" class="fixed top-0 left-0 bottom-0 w-5/6 max-w-sm z-50 bg-white border-r flex flex-col py-8 overflow-y-auto">
          <div class="flex items-center mb-12 px-6">
            <button @click="mobileNavOpen = false" class="ml-auto p-2">
              <i class="pi pi-times text-2xl text-blue-800" />
            </button>
          </div>
          <div>
            <ul>
              <li v-for="link in links" :key="link.path">
                <NuxtLink class="block pl-8 py-4 font-semibold text-blue-800 hover:bg-blue-50 rounded flex items-center gap-2"
                          :to="link.path" @click="mobileNavOpen = false">
                  <i :class="link.icon" />
                  {{ link.label }}
                </NuxtLink>
              </li>
            </ul>
          </div>
        </nav>
      </transition>
    </section>

    <article class="mt-8">
      <slot />
    </article>
  </div>
</template>

<style scoped>
.router-link-active {
  font-weight: bold;
  color: #42b983;
}
.icons {
  right: 3px;
  top: 3px;
}
.bg {
  background-color: #ffffffff;
}
/* Simple transition for overlay and mobile nav */
.fade-enter-active,
.fade-leave-active { transition: opacity .2s }
.fade-enter-from,
.fade-leave-to { opacity: 0 }
.slide-enter-active,
.slide-leave-active { transition: transform .25s cubic-bezier(.4,0,.2,1), opacity .25s }
.slide-enter-from,
.slide-leave-to { transform: translateX(-100%); opacity: 0 }
</style>
