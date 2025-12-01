<template>
  <div class="hidden md:block bg-container">
    <!-- Определение SVG фильтра (скрыто) -->
    <svg style="display: none;">
      <defs>
        <filter id="staticDistortion">
          <!-- baseFrequency: чем меньше число, тем шире "волны" искажения -->
          <feTurbulence 
            type="fractalNoise" 
            baseFrequency="0.005" 
            numOctaves="2" 
            result="noise" 
          />
          <!-- scale: сила искажения (30 - умеренно, 100 - сильно) -->
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

    <!-- Слой 3: Виньетка поверх всего (чтобы углы были темными) -->
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
  background-color: #050505; /* Черный фон */
  overflow: hidden;
  z-index: -1;
}

.distortion-glass {
  position: absolute;
  width: 100%;
  height: 100%;
  filter: url(#staticDistortion); /* Применяем фильтр сюда */
}

.moving-grid {
  position: absolute;
  top: -10%;
  left: -10%;
  width: 120%;
  height: 120%;
  
  background-image: 
    linear-gradient(rgba(255, 255, 255, 0.0075) 2px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.0075) 2px, transparent 1px);
    
  background-size: 80px 80px; /* Размер клетки */
  
  /* Анимация движения */
  animation: move-diagonal 4s linear infinite;
  will-change: background-position;
}

.vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: radial-gradient(
    circle at center, 
    transparent 20%, 
    rgba(0, 0, 0, 0.4) 60%, 
    #050505 100%
  );
}

/* 
  Движение по диагонали (Влево и Вниз).
  Чтобы цикл был идеальным, мы должны сдвинуть фон ровно на размер клетки (60px).
  Вниз = 60px
  Влево = -60px
*/
@keyframes move-diagonal {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 80px -80px;
  }
}
</style>