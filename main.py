import http.server
import os
import re
import socketserver
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser

PORT = 8000

# === CÓDIGO HTML/3D COMPLETO Y CORREGIDO PARA MARGARITA ===
HTML_CODE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Para Margarita ❤️</title>
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Playfair+Display:ital,wght@0,700;1,600&display=swap" rel="stylesheet">

  <style>
    * { box-sizing: border-box; }
    html, body {
      margin: 0; padding: 0; height: 100%;
      background: #000; overflow: hidden;
      font-family: 'JetBrains Mono', monospace;
    }
    #bg-canvas {
      position: fixed; inset: 0;
      width: 100vw; height: 100vh;
      display: block; z-index: 0; cursor: grab;
    }
    #bg-canvas:active { cursor: grabbing; }

    #flash-screen {
      position: fixed; inset: 0;
      background: #ffffff;
      opacity: 0;
      pointer-events: none;
      z-index: 15;
      transition: opacity 0.1s linear;
    }

    :root {
      --start-ink: #f8f4ff; 
      --start-mist: #d8cbff;
      --start-panel: rgba(13, 7, 28, 0.88); 
      --start-stroke: rgba(255, 120, 199, 0.5);
    }

    #start-overlay {
      position: fixed; inset: 0; z-index: 20;
      display: flex; align-items: center; justify-content: center;
      background:
        radial-gradient(70% 55% at 15% 100%, rgba(255, 80, 170, 0.3), transparent 68%),
        radial-gradient(60% 45% at 90% 10%, rgba(90, 120, 255, 0.3), transparent 70%),
        radial-gradient(120% 100% at 50% 50%, rgba(20, 8, 45, 0.95), rgba(2, 1, 8, 0.99));
      backdrop-filter: blur(12px);
      transition: opacity 1.2s ease, visibility 1.2s ease;
    }

    #start-overlay.hidden { 
      opacity: 0; 
      visibility: hidden; 
      pointer-events: none; 
    }

    #start-card {
      position: relative; z-index: 2; text-align: center;
      color: var(--start-ink); width: min(92vw, 480px);
      padding: 40px 30px;
      border: 1px solid var(--start-stroke); border-radius: 30px;
      background: var(--start-panel);
      box-shadow: 0 0 50px rgba(255, 120, 199, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
      animation: cardFloat 4s ease-in-out infinite;
    }

    @keyframes cardFloat {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-10px); }
    }

    .title {
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 2.8rem;
      margin: 0 0 10px 0;
      color: #fff;
      text-shadow: 0 0 25px rgba(255, 120, 199, 0.9);
      letter-spacing: 2px;
    }

    .cover-img {
      width: 150px; height: 150px;
      border-radius: 50%;
      object-fit: cover;
      margin: 15px auto;
      border: 3px solid #ff78c7;
      box-shadow: 0 0 25px rgba(255, 120, 199, 0.6);
    }

    .subtitle {
      font-size: 0.85rem;
      letter-spacing: 3px;
      color: var(--start-mist);
      margin: 18px 0 25px 0;
      font-weight: 600;
    }

    .start-btn {
      background: linear-gradient(135deg, rgba(255, 80, 180, 0.9), rgba(130, 50, 220, 0.95));
      border: 1px solid rgba(255, 255, 255, 0.6);
      color: #ffffff;
      padding: 14px 45px;
      font-size: 1.05rem;
      font-weight: 600;
      letter-spacing: 2px;
      border-radius: 30px;
      cursor: pointer;
      box-shadow: 0 0 25px rgba(255, 100, 180, 0.6);
      transition: all 0.3s ease;
    }

    .start-btn:hover {
      transform: scale(1.08);
      box-shadow: 0 0 35px rgba(255, 120, 200, 1);
    }

    #music-btn {
      position: fixed; top: 20px; right: 20px; z-index: 10;
      width: 48px; height: 48px; border-radius: 50%;
      background: rgba(20, 10, 35, 0.8);
      border: 1px solid rgba(255,120,199,0.5);
      color: white; font-size: 20px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer; backdrop-filter: blur(5px);
    }

    #focus-hint {
      position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%);
      z-index: 10; background: rgba(20, 10, 35, 0.85);
      border: 1px solid rgba(255, 120, 199, 0.6);
      color: #fff; padding: 10px 22px; border-radius: 25px;
      font-size: 0.85rem; letter-spacing: 1px; pointer-events: none;
      opacity: 0; transition: opacity 0.4s ease;
      box-shadow: 0 0 20px rgba(255, 120, 199, 0.4);
    }
    #focus-hint.visible { opacity: 1; }
  </style>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>

  <canvas id="bg-canvas"></canvas>
  <div id="flash-screen"></div>

  <button id="music-btn" title="Activar/Desactivar Música">🎵</button>
  <div id="focus-hint">🔍 Tocá en el espacio para alejar</div>

  <div id="start-overlay">
    <div id="start-card">
      <h1 class="title">PARA MARGARITA</h1>
      <img class="cover-img" src="imagen4.jpg" alt="Portada" onerror="this.src='https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExOHY5M2lyODZmdTRrbzFnZWp0YmhpaWZvbGkybnQyZjdrZjFmeHQ5OCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9cw/MDJ9IbxxvDUQM/giphy.gif'">
      <div class="subtitle">UN VIAJE POR NUESTRO UNIVERSO ❤️</div>
      <button class="start-btn" id="start-btn">INICIAR VIAJE 🚀</button>
    </div>
  </div>

  <audio id="bg-music" loop src="musica.mp3" preload="auto"></audio>

  <script>
    // --- 1. CONFIGURACIÓN THREE.JS ---
    const canvas = document.getElementById('bg-canvas');
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x020108, 0.0005);

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2500);
    const targetCamPos = new THREE.Vector3(0, 25, 55);
    camera.position.set(0, 0, 500);

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enabled = false;

    // --- TEXTURA DE ESTRELLAS NÍTIDAS ---
    function createSharpStarTexture() {
      const c = document.createElement('canvas');
      c.width = 64; c.height = 64;
      const ctx = c.getContext('2d');
      
      const grad = ctx.createRadialGradient(32,32,0, 32,32,32);
      grad.addColorStop(0, 'rgba(255,255,255,1)');
      grad.addColorStop(0.2, 'rgba(255,255,255,0.95)');
      grad.addColorStop(0.5, 'rgba(230,240,255,0.5)');
      grad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 64, 64);

      // Destello central
      ctx.strokeStyle = 'rgba(255,255,255,0.85)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(32, 10); ctx.lineTo(32, 54);
      ctx.moveTo(10, 32); ctx.lineTo(54, 32);
      ctx.stroke();

      return new THREE.CanvasTexture(c);
    }
    const starTex = createSharpStarTexture();

    // --- ESTRELLAS LEJANAS (10,000 ESTRELLAS NÍTIDAS Y BRILLANTES) ---
    const farStarsCount = 10000;
    const farStarsGeo = new THREE.BufferGeometry();
    const farStarsPos = new Float32Array(farStarsCount * 3);
    const farStarsColors = new Float32Array(farStarsCount * 3);

    const starColorsList = [
      new THREE.Color(0xffffff), // Blanco impoluto
      new THREE.Color(0xffd1dc), // Rosa bebé
      new THREE.Color(0xadd8e6), // Azul estelar
      new THREE.Color(0xffdfa9), // Dorado estelar
      new THREE.Color(0xe6e6fa)  // Lavanda
    ];

    for(let i = 0; i < farStarsCount; i++) {
      let u = Math.random();
      let v = Math.random();
      let theta = u * 2.0 * Math.PI;
      let phi = Math.acos(2.0 * v - 1.0);
      let r = 200 + Math.random() * 850;

      farStarsPos[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
      farStarsPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      farStarsPos[i * 3 + 2] = r * Math.cos(phi);

      let col = starColorsList[Math.floor(Math.random() * starColorsList.length)];
      farStarsColors[i * 3]     = col.r;
      farStarsColors[i * 3 + 1] = col.g;
      farStarsColors[i * 3 + 2] = col.b;
    }
    farStarsGeo.setAttribute('position', new THREE.BufferAttribute(farStarsPos, 3));
    farStarsGeo.setAttribute('color', new THREE.BufferAttribute(farStarsColors, 3));

    const farStarsMat = new THREE.PointsMaterial({
      size: 3.2,                 // Tamaño más grande y nítido
      sizeAttenuation: false,   // Mantienen nitidez independientemente de la distancia
      map: starTex,
      transparent: true,
      opacity: 1.0,
      vertexColors: true,
      blending: THREE.AdditiveBlending,
      fog: false                // La niebla no las oscurece
    });
    const farStarsMesh = new THREE.Points(farStarsGeo, farStarsMat);
    scene.add(farStarsMesh);

    // --- GRUPO DEL UNIVERSO (GALAXIA, CORAZÓN, FOTOS Y FRASES) ---
    const universeGroup = new THREE.Group();
    scene.add(universeGroup);
    universeGroup.scale.set(0.0001, 0.0001, 0.0001);

    // --- EFECTO HIPERESPACIO / VELOCIDAD DE LA LUZ ---
    const warpCount = 1200;
    const warpGeo = new THREE.BufferGeometry();
    const warpPos = new Float32Array(warpCount * 6);
    for (let i = 0; i < warpCount; i++) {
      let x = (Math.random() - 0.5) * 450;
      let y = (Math.random() - 0.5) * 450;
      let z = Math.random() * 1000 - 500;
      let len = 35 + Math.random() * 55;
      
      warpPos[i * 6]     = x; warpPos[i * 6 + 1] = y; warpPos[i * 6 + 2] = z;
      warpPos[i * 6 + 3] = x; warpPos[i * 6 + 4] = y; warpPos[i * 6 + 5] = z - len;
    }
    warpGeo.setAttribute('position', new THREE.BufferAttribute(warpPos, 3));
    const warpMat = new THREE.LineBasicMaterial({ color: 0xffb5ee, transparent: true, opacity: 0.9 });
    const warpLines = new THREE.LineSegments(warpGeo, warpMat);
    scene.add(warpLines);
    warpLines.visible = false;

    // --- 2. GALAXIA DE PARTÍCULAS ---
    const galaxyCount = 35000;
    const galaxyGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(galaxyCount * 3);
    const colors = new Float32Array(galaxyCount * 3);

    const colorInside = new THREE.Color(0xffcb74);
    const colorMiddle = new THREE.Color(0xff2a9d);
    const colorOutside = new THREE.Color(0x38b6ff);

    for (let i = 0; i < galaxyCount; i++) {
      const i3 = i * 3;
      const r = Math.pow(Math.random(), 2) * 45;
      const spinAngle = r * 0.35;
      const branchAngle = ((i % 4) / 4) * Math.PI * 2;

      const randomX = (Math.random() - 0.5) * (r * 0.18 + 0.4);
      const randomY = (Math.random() - 0.5) * (r * 0.12 + 0.2);
      const randomZ = (Math.random() - 0.5) * (r * 0.18 + 0.4);

      positions[i3]     = Math.cos(branchAngle + spinAngle) * r + randomX;
      positions[i3 + 1] = randomY;
      positions[i3 + 2] = Math.sin(branchAngle + spinAngle) * r + randomZ;

      let mixedColor = colorInside.clone();
      if (r < 15) {
        mixedColor.lerp(colorMiddle, r / 15);
      } else {
        mixedColor = colorMiddle.clone().lerp(colorOutside, (r - 15) / 27);
      }

      colors[i3]     = mixedColor.r;
      colors[i3 + 1] = mixedColor.g;
      colors[i3 + 2] = mixedColor.b;
    }

    galaxyGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    galaxyGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const galaxyMat = new THREE.PointsMaterial({
      size: 0.38, sizeAttenuation: true, depthWrite: false,
      blending: THREE.AdditiveBlending, vertexColors: true, map: starTex, transparent: true
    });
    const galaxyMesh = new THREE.Points(galaxyGeo, galaxyMat);
    universeGroup.add(galaxyMesh);

    // --- 3. AGUJERO NEGRO CENTRAL ---
    const holeGeo = new THREE.SphereGeometry(2.6, 32, 32);
    const blackHole = new THREE.Mesh(holeGeo, new THREE.MeshBasicMaterial({ color: 0x000000 }));
    universeGroup.add(blackHole);

    const ringGeo = new THREE.RingGeometry(2.7, 4.5, 64);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xffdb8b, side: THREE.DoubleSide, transparent: true, opacity: 0.85, blending: THREE.AdditiveBlending });
    const ringMesh = new THREE.Mesh(ringGeo, ringMat);
    ringMesh.rotation.x = Math.PI / 2;
    universeGroup.add(ringMesh);

    // --- 4. CORAZÓN EN 3D ---
    const heartCount = 4500;
    const heartGeo = new THREE.BufferGeometry();
    const heartPos = new Float32Array(heartCount * 3);
    const heartColors = new Float32Array(heartCount * 3);
    const pink1 = new THREE.Color(0xff1493), pink2 = new THREE.Color(0xffb6c1);

    for (let i = 0; i < heartCount; i++) {
      const i3 = i * 3;
      const t = Math.random() * Math.PI * 2;
      const u = Math.random();

      let hx = 16 * Math.pow(Math.sin(t), 3);
      let hy = 13 * Math.cos(t) - 5 * Math.cos(2*t) - 2 * Math.cos(3*t) - Math.cos(4*t);

      const scale = 0.45 * Math.sqrt(u);
      hx *= scale; hy *= scale;
      let hz = (Math.random() - 0.5) * 3 * Math.sqrt(u);

      heartPos[i3]     = hx;
      heartPos[i3 + 1] = hy + 8;
      heartPos[i3 + 2] = hz;

      const c = pink1.clone().lerp(pink2, Math.random());
      heartColors[i3] = c.r; heartColors[i3 + 1] = c.g; heartColors[i3 + 2] = c.b;
    }

    heartGeo.setAttribute('position', new THREE.BufferAttribute(heartPos, 3));
    heartGeo.setAttribute('color', new THREE.BufferAttribute(heartColors, 3));

    const heartMat = new THREE.PointsMaterial({
      size: 0.4, sizeAttenuation: true, depthWrite: false,
      blending: THREE.AdditiveBlending, vertexColors: true, map: starTex, transparent: true
    });
    const heartMesh = new THREE.Points(heartGeo, heartMat);
    universeGroup.add(heartMesh);

    // --- 5. FRASES Y FOTOS EN ÓRBITA ---
    const orbitingObjects = [];

    function createTextSprite(text) {
      const c = document.createElement('canvas');
      c.width = 1024; c.height = 180;
      const ctx = c.getContext('2d');

      ctx.fillStyle = 'rgba(15, 8, 30, 0.88)';
      if (ctx.roundRect) ctx.roundRect(10, 10, 1004, 160, 30);
      else ctx.fillRect(10, 10, 1004, 160);
      ctx.fill();

      ctx.strokeStyle = 'rgba(255, 120, 199, 0.9)';
      ctx.lineWidth = 5; ctx.stroke();

      ctx.font = 'bold 42px "Segoe UI", sans-serif';
      ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      ctx.fillStyle = '#ffffff';
      ctx.shadowColor = '#ff78c7'; ctx.shadowBlur = 18;
      ctx.fillText(text, 512, 90);

      const tex = new THREE.CanvasTexture(c);
      const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.scale.set(18, 3.1, 1);
      return sprite;
    }

    const phrases = [
      "Perdóname, no quise lastimarte.",
      "Lo siento mucho, Margarita.",
      "Perdóname por mis errores.",
      "Discúlpame, te amo con todo mi corazón.",
      "No quería hacerte daño, mi vida.",
      "Perdóname, eres lo más importante para mí.",
      "Lo siento, mi preciosa Margarita.",
      "Perdóname, quiero hacerte muy feliz."
    ];

    phrases.forEach((txt, idx) => {
      const sprite = createTextSprite(txt);
      const radius = 19 + (idx % 4) * 6;
      const angle = (idx / phrases.length) * Math.PI * 2;
      const speed = 0.002;
      const height = (idx % 2 === 0 ? 3.5 : -3.5);

      universeGroup.add(sprite);
      orbitingObjects.push({ mesh: sprite, radius, angle, speed, height, isImage: false });
    });

    const textureLoader = new THREE.TextureLoader();
    const photoFiles = ['imagen1.jpg', 'imagen2.jpg', 'imagen3.jpg', 'imagen4.jpg', 'imagen5.jpg'];

    photoFiles.forEach((file, idx) => {
      textureLoader.load(file, (texture) => {
        const geo = new THREE.PlaneGeometry(6.2, 6.2);
        const mat = new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide });
        const mesh = new THREE.Mesh(geo, mat);

        const frameGeo = new THREE.PlaneGeometry(6.6, 6.6);
        const frameMat = new THREE.MeshBasicMaterial({ color: 0xff78c7, side: THREE.DoubleSide });
        const frameMesh = new THREE.Mesh(frameGeo, frameMat);
        frameMesh.position.z = -0.05;
        mesh.add(frameMesh);

        const radius = 17 + idx * 5;
        const angle = (idx / photoFiles.length) * Math.PI * 2 + Math.PI / 5;
        const speed = 0.0025;
        const height = (idx % 2 === 0 ? -4 : 4);

        universeGroup.add(mesh);
        orbitingObjects.push({ mesh, radius, angle, speed, height, isImage: true });
      });
    });

    // --- 6. ACERCAMIENTO INTERACTIVO (RAYCASTER AL TOCAR FOTOS O FRASES) ---
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();
    let focusObject = null;
    const focusHint = document.getElementById('focus-hint');

    window.addEventListener('pointerdown', (e) => {
      // Ignorar clics en botones de la pantalla
      if (e.target.closest('#start-overlay') || e.target.closest('#music-btn')) return;

      mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
      mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);

      const targets = orbitingObjects.map(obj => obj.mesh);
      const intersects = raycaster.intersectObjects(targets, true);

      if (intersects.length > 0) {
        let hit = intersects[0].object;
        while (hit.parent && hit.parent !== universeGroup) {
          hit = hit.parent;
        }
        focusObject = hit;
        focusHint.classList.add('visible');
      } else {
        // Clic en el espacio vacío -> regresa la cámara
        focusObject = null;
        focusHint.classList.remove('visible');
      }
    });

    // --- 7. ANIMACIÓN Y TITILEO ---
    let isTraveling = false;
    let travelProgress = 0;
    const flashScreen = document.getElementById('flash-screen');

    function animate() {
      requestAnimationFrame(animate);

      // Rotación y parpadeo de estrellas
      farStarsMesh.rotation.y += 0.0004;
      farStarsMesh.rotation.x += 0.0002;
      farStarsMat.opacity = 0.8 + Math.sin(Date.now() * 0.003) * 0.2;

      if (isTraveling) {
        travelProgress += 0.007;

        if (travelProgress < 0.7) {
          warpLines.visible = true;
          warpLines.rotation.z += 0.08;

          const posArr = warpGeo.attributes.position.array;
          for (let i = 0; i < warpCount; i++) {
            posArr[i * 6 + 2] += 35;
            posArr[i * 6 + 5] += 35;
            if (posArr[i * 6 + 2] > 500) {
              posArr[i * 6 + 2] -= 1000;
              posArr[i * 6 + 5] -= 1000;
            }
          }
          warpGeo.attributes.position.needsUpdate = true;

          camera.fov = THREE.MathUtils.lerp(60, 115, travelProgress / 0.7);
          camera.updateProjectionMatrix();

        } else if (travelProgress < 0.85) {
          let flashP = (travelProgress - 0.7) / 0.15;
          flashScreen.style.opacity = flashP;

        } else if (travelProgress < 1.0) {
          warpLines.visible = false;
          camera.fov = 60;
          camera.position.copy(targetCamPos);
          camera.lookAt(0, 0, 0);
          camera.updateProjectionMatrix();

          let createP = (travelProgress - 0.85) / 0.15;
          let scaleVal = Math.sin(createP * Math.PI / 2);
          universeGroup.scale.set(scaleVal, scaleVal, scaleVal);

          flashScreen.style.opacity = 1 - createP;

        } else {
          isTraveling = false;
          universeGroup.scale.set(1, 1, 1);
          flashScreen.style.opacity = 0;
          controls.enabled = true;
        }

        galaxyMesh.rotation.y += 0.02;

      } else {
        galaxyMesh.rotation.y += 0.0012;
      }

      heartMesh.rotation.y += 0.003;
      const time = Date.now() * 0.002;
      heartMesh.position.y = Math.sin(time) * 0.5;

      orbitingObjects.forEach(obj => {
        obj.angle += obj.speed;
        obj.mesh.position.x = Math.cos(obj.angle) * obj.radius;
        obj.mesh.position.z = Math.sin(obj.angle) * obj.radius;
        obj.mesh.position.y = obj.height + Math.sin(time + obj.radius) * 1.2;

        if (obj.isImage) {
          obj.mesh.lookAt(camera.position);
        }
      });

      // MANEJO DE ACERCAMIENTO SUAVE
      if (focusObject && !isTraveling) {
        const worldPos = new THREE.Vector3();
        focusObject.getWorldPosition(worldPos);

        const offsetDir = camera.position.clone().sub(worldPos).normalize().multiplyScalar(13);
        const goalCamPos = worldPos.clone().add(offsetDir);

        camera.position.lerp(goalCamPos, 0.06);
        controls.target.lerp(worldPos, 0.06);
      } else if (!isTraveling && controls.enabled) {
        controls.target.lerp(new THREE.Vector3(0, 0, 0), 0.05);
      }

      if (controls.enabled) controls.update();
      renderer.render(scene, camera);
    }
    animate();

    // --- 8. EVENTOS DE AUDIO Y NAVEGACIÓN ---
    const startOverlay = document.getElementById('start-overlay');
    const startBtn = document.getElementById('start-btn');
    const musicBtn = document.getElementById('music-btn');
    const bgMusic = document.getElementById('bg-music');

    startBtn.addEventListener('click', () => {
      startOverlay.classList.add('hidden');
      
      // La música empieza exactamente al tocar INICIAR VIAJE
      bgMusic.currentTime = 0;
      bgMusic.play().then(() => {
        musicBtn.textContent = '🎵';
      }).catch(e => {
        console.log('Error de reproducción de audio:', e);
      });

      isTraveling = true;
    });

    musicBtn.addEventListener('click', () => {
      if (bgMusic.paused) {
        bgMusic.play();
        musicBtn.textContent = '🎵';
      } else {
        bgMusic.pause();
        musicBtn.textContent = '🔇';
      }
    });

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  </script>
</body>
</html>
"""

# 1. Crear el archivo HTML
with open("index.html", "w", encoding="utf-8") as f:
  f.write(HTML_CODE)


# 2. Servidor Local Multihilo
class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
  daemon_threads = True
  allow_reuse_address = True


def start_local_server():
  handler = http.server.SimpleHTTPRequestHandler
  with ThreadedHTTPServer(("", PORT), handler) as httpd:
    httpd.serve_forever()


server_thread = threading.Thread(target=start_local_server, daemon=True)
server_thread.start()

print("\n" + "=" * 65)
print("🚀 Servidor local iniciado.")
print("🌐 Generando enlace público para Margarita...")
print("=" * 65 + "\n")

webbrowser.open(f"http://localhost:{PORT}")


# 3. Ruta de cloudflared
def get_cloudflared_path():
  exe_name = "cloudflared.exe" if sys.platform == "win32" else "cloudflared"
  if os.path.exists(exe_name):
    return os.path.abspath(exe_name)
  return None


# 4. Iniciar túnel seguro y extraer URL pública
def start_public_tunnel():
  cf_bin = get_cloudflared_path()

  if cf_bin and os.path.exists(cf_bin):
    cmd = [cf_bin, "tunnel", "--url", f"http://localhost:{PORT}"]
  else:
    cmd = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "UserKnownHostsFile=/dev/null",
        "-R",
        f"80:localhost:{PORT}",
        "nokey@localhost.run",
    ]

  try:
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

    for line in iter(process.stdout.readline, ""):
      match = re.search(
          r"https://[a-zA-Z0-9-]+\.(trycloudflare\.com|lhr\.life|lhrtunnel\.link|pinggy\.link|serveo\.net)",
          line,
      )
      if match:
        public_url = match.group(0)

        if sys.platform == "win32":
          try:
            subprocess.run(
                ["powershell", "-Command", f'Set-Clipboard -Value "{public_url}"'],
                capture_output=True,
            )
            clip_msg = " (¡Copiado a tu portapapeles! 📋)"
          except:
            clip_msg = ""
        else:
          clip_msg = ""

        print("\n" + "✨" * 32)
        print(" ❤️  ¡AQUÍ TIENES TU ENLACE PÚBLICO PARA MARGARITA! ")
        print(f" 👉  {public_url}{clip_msg}")
        print("✨" * 32)
        print("\n📱 Copia esa dirección y envíasela por WhatsApp.")
        print("⚠️  IMPORTANTE: Deja la terminal abierta mientras ella navega.")
        print("-" * 65 + "\n")
        break

  except Exception as err:
    print("Error al iniciar el túnel público:", err)


tunnel_thread = threading.Thread(target=start_public_tunnel, daemon=True)
tunnel_thread.start()

try:
  while True:
    time.sleep(1)
except KeyboardInterrupt:
  print("\nServidor cerrado correctamente.")