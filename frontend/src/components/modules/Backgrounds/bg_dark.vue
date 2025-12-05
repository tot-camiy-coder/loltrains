<template>
  <div class="bg-container bg-[#09090B]">
    <!-- Определение SVG фильтра (скрыто) -->
    <svg style="display: none;">
      <defs>
        <filter id="staticDistortion">
          <feTurbulence 
            type="fractalNoise" 
            baseFrequency="0.005" 
            numOctaves="2" 
            result="noise" 
          />
          <feDisplacementMap 
            in="SourceGraphic" 
            in2="noise" 
            scale="60" 
          />
        </filter>
      </defs>
    </svg>

    <!-- Слой 1: Статическая обертка, на которую наложен фильтр искажения -->
    <div class="distortion-glass">
      <!-- Слой 2: Сама сетка, которая двигается внутри -->
      <div class="moving-grid"></div>
    </div>
  </div>
</template>

<script setup>
// Логика не требуется
</script>

<style scoped>
.bg-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  z-index: -1;
}

.distortion-glass {
  position: absolute;
  width: 100%;
  height: 100%;
  filter: url(#staticDistortion);
}

.moving-grid {
  position: absolute;
  top: -10%;
  left: -10%;
  width: 120%;
  height: 120%;
  
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.014) 2px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.014) 2px, transparent 1px);
    
  background-size: 80px 80px;
  
  animation: move-diagonal 4s linear infinite;
  will-change: background-position;
}

/* ========== МОБИЛЬНЫЕ УСТРОЙСТВА - СТОП КАДР ========== */
@media (max-width: 768px) {
  .moving-grid {
    animation: none;
    will-change: auto; /* Убираем для экономии ресурсов */
  }
  
  /* Опционально: можно также убрать фильтр для лучшей производительности */
  .distortion-glass {
    filter: url(#staticDistortion);
    /* Или полностью отключить: filter: none; */
  }
}

/* Альтернатива: отключение для устройств с тач-экраном */
@media (hover: none) and (pointer: coarse) {
  .moving-grid {
    animation: none;
    will-change: auto;
  }
}

/* Отключение анимации при включенном режиме экономии энергии */
@media (prefers-reduced-motion: reduce) {
  .moving-grid {
    animation: none;
    will-change: auto;
  }
}

@keyframes move-diagonal {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 80px -80px;
  }
}
</style>