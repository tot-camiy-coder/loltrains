  <script setup>
  import { Ban, Search } from 'lucide-vue-next'

  defineProps({
    disabled: Boolean
  })

  defineEmits(['click'])
  </script>

  <template>
    <button
      @click="!disabled && $emit('click')"
      :class="[
        'group relative flex-1 min-w-[100px] max-h-10 min-h-10 border-2 font-bold py-2 px-4 rounded-lg ' +
        'transition duration-500 overflow-hidden',
        disabled
          ? 'cursor-not-allowed opacity-70 bg-white/5 text-white/50 border-white/10 hover:border-red-500/50 hover:text-red-400'
          : 'cursor-pointer bg-white text-black hover:bg-transparent hover:text-white border-white'
      ]"
    >
      <span v-if="disabled" class="relative flex items-center justify-center w-full h-full">
        <span class="absolute transition-all duration-500 group-hover:opacity-0 group-hover:translate-y-4">
          Найти
        </span>
        <Ban
          :size="24"
          class="absolute -rotate-90 scale-50 text-red-500 opacity-0
                transition-all duration-400 group-hover:opacity-100
                group-hover:rotate-0 group-hover:scale-100"
        />
      </span>

      <span
        v-else
        class="relative flex items-center justify-center w-full h-full -top-0.5
              translate-x-2 transition duration-700 group-hover:translate-x-0"
      >
        Найти
        <Search
          :size="16"
          class="inline-block -rotate-90 -translate-x-8 opacity-0
                transition duration-500 group-hover:opacity-100
                group-hover:translate-x-1 group-hover:rotate-12"
        />
      </span>
    </button>
  </template>