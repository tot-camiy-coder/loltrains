<template>
  <canvas ref="canvasRef" class="trail-canvas"></canvas>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';

const canvasRef = ref(null);
let ctx = null;
let animationId = null;

// Настройки хвоста
const totalPoints = 10;
const trail = [];
let mouse = { x: 0, y: 0 };
let hue = 0;

// --- НОВЫЕ ПЕРЕМЕННЫЕ ---
let lastMoveTime = Date.now(); // Время последнего движения
let currentOpacity = 1; // Текущая прозрачность (от 0 до 1)
const idleTimeout = 400; // Время бездействия в мс (3 секунды)
// ------------------------

// Инициализация точек
for (let i = 0; i < totalPoints; i++) {
  trail.push({ x: 0, y: 0 });
}

const handleMouseMove = (e) => {
  mouse.x = e.clientX;
  mouse.y = e.clientY;
  // Обновляем время последнего движения
  lastMoveTime = Date.now();
};

const handleTouchMove = (e) => {
  if (e.touches.length > 0) {
    mouse.x = e.touches[0].clientX;
    mouse.y = e.touches[0].clientY;
    // Обновляем время последнего движения
    lastMoveTime = Date.now();
  }
};

const handleResize = () => {
  if (canvasRef.value) {
    canvasRef.value.width = window.innerWidth;
    canvasRef.value.height = window.innerHeight;
  }
};

const animate = () => {
  if (!ctx || !canvasRef.value) return;

  ctx.clearRect(0, 0, canvasRef.value.width, canvasRef.value.height);

  // --- ЛОГИКА ИСЧЕЗНОВЕНИЯ ---
  const timeSinceLastMove = Date.now() - lastMoveTime;

  if (timeSinceLastMove > idleTimeout) {
    // Если прошло больше 3 секунд, плавно уменьшаем прозрачность
    currentOpacity -= 0.02; // Скорость затухания
    if (currentOpacity < 0) currentOpacity = 0;
  } else {
    // Если мышь движется, быстро возвращаем прозрачность
    currentOpacity += 0.1;
    if (currentOpacity > 1) currentOpacity = 1;
  }

  // Применяем прозрачность ко всему, что будет нарисовано ниже
  ctx.globalAlpha = currentOpacity;
  // ---------------------------

  // Если полностью прозрачно, можно не рисовать и не считать физику для оптимизации,
  // но лучше считать физику, чтобы хвост "прилетел" к курсору даже будучи невидимым.
  
  // 1. Первая точка всегда на курсоре
  trail[0].x = mouse.x;
  trail[0].y = mouse.y;

  // 2. Остальные точки следуют за предыдущей
  const speed = 0.5; 
  for (let i = 1; i < trail.length; i++) {
    const prev = trail[i - 1];
    const curr = trail[i];
    
    curr.x += (prev.x - curr.x) * speed;
    curr.y += (prev.y - curr.y) * speed;
  }

  if (currentOpacity > 0) {
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    for (let i = 0; i < trail.length - 1; i++) {
      const point = trail[i];
      const nextPoint = trail[i + 1];

      ctx.beginPath();
      ctx.moveTo(point.x, point.y);
      ctx.lineTo(nextPoint.x, nextPoint.y);

      const segmentHue = hue + (i * 2); 
      ctx.strokeStyle = `hsl(${segmentHue}, 60%, 30%)`;

      const lineWidth = ((totalPoints - i) / totalPoints) * 5; 
      ctx.lineWidth = lineWidth;

      ctx.stroke();
    }
  }

  hue += 2;
  animationId = requestAnimationFrame(animate);
};

onMounted(() => {
  if (canvasRef.value) {
    ctx = canvasRef.value.getContext('2d');
    
    mouse.x = window.innerWidth / 2;
    mouse.y = window.innerHeight / 2;
    lastMoveTime = Date.now(); 
    
    trail.forEach(p => { p.x = mouse.x; p.y = mouse.y; });

    handleResize();
    
    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('touchmove', handleTouchMove);
    
    animate();
  }
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  window.removeEventListener('mousemove', handleMouseMove);
  window.removeEventListener('touchmove', handleTouchMove);
  cancelAnimationFrame(animationId);
});
</script>

<style scoped>
.trail-canvas {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
  pointer-events: none;
}
</style>