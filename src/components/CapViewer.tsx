"use client";

import { ContactShadows, useGLTF } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { Suspense, useLayoutEffect, useMemo, useRef } from "react";
import * as THREE from "three";

const variantColors = [new THREE.Color("#292d35"), new THREE.Color("#e5dece"), new THREE.Color("#4d0d18")];
const embroideryColors = [new THREE.Color("#596575"), new THREE.Color("#11151d"), new THREE.Color("#f5e5c8")];

function ProductCap({ progress, revealProgress }: { progress: number; revealProgress: number }) {
  const { scene } = useGLTF("/models/baseball_cap.glb");
  const group = useRef<THREE.Group>(null);
  const model = useMemo(() => scene.clone(true), [scene]);
  const materials = useRef<THREE.MeshStandardMaterial[]>([]);
  const embroidery = useRef<THREE.MeshStandardMaterial[]>([]);

  useLayoutEffect(() => {
    embroidery.current = [];
    model.scale.setScalar(5.8);
    model.position.set(0, 0, 0);
    model.updateMatrixWorld(true);
    const bounds = new THREE.Box3().setFromObject(model);
    const center = bounds.getCenter(new THREE.Vector3());
    // La malla descargada tiene el pivote fuera del producto. Lo centramos
    // antes de animar, para que los giros no desplacen ni recorten la gorra.
    model.position.set(-center.x, -center.y - 0.1, -center.z);
    const materialSet = new Set<THREE.MeshStandardMaterial>();

    model.traverse((object) => {
      if (!(object instanceof THREE.Mesh)) return;
      object.castShadow = true;
      object.receiveShadow = true;
      const sourceMaterials = Array.isArray(object.material) ? object.material : [object.material];
      const clonedMaterials = sourceMaterials.map((material) => material.clone() as THREE.MeshStandardMaterial);
      object.material = Array.isArray(object.material) ? clonedMaterials : clonedMaterials[0];
      clonedMaterials.forEach((material) => {
        if (material.name === "SOG_Embroidery") {
          material.map = null;
          material.color.set(embroideryColors[0]);
          material.roughness = 0.34;
          material.metalness = 0.04;
          material.transparent = true;
          material.opacity = 0;
          embroidery.current.push(material);
          return;
        }
        material.map = null;
        material.color.set(variantColors[0]);
        material.roughness = Math.max(material.roughness ?? 0.72, 0.66);
        material.metalness = 0;
        material.transparent = true;
        material.opacity = 0;
        material.needsUpdate = true;
        materialSet.add(material);
      });
    });

    materials.current = [...materialSet];
  }, [model]);

  useFrame((_, delta) => {
    if (!group.current) return;
    const palettePosition = THREE.MathUtils.clamp(progress * 3, 0, 2.999);
    const stage = Math.floor(palettePosition);
    // La primera pieza entra antes, sin alterar el ritmo de las otras dos.
    const entrance = THREE.MathUtils.smoothstep(revealProgress, 0, 0.045);

    // Giro horizontal continuo: conserva el comportamiento original de la
    // experiencia y termina a 45° después de una vuelta completa.
    group.current.rotation.y = THREE.MathUtils.damp(group.current.rotation.y, Math.PI / 4 + progress * Math.PI * 2, 6, delta);
    group.current.rotation.x = THREE.MathUtils.damp(group.current.rotation.x, 0.52, 6, delta);
    group.current.position.y = THREE.MathUtils.damp(group.current.position.y, 0.18, 7, delta);
    group.current.scale.setScalar(THREE.MathUtils.damp(group.current.scale.x, 1.1, 7, delta));
    materials.current.forEach((material) => {
      material.color.lerp(variantColors[stage], 1 - Math.exp(-7 * delta));
      material.opacity = THREE.MathUtils.damp(material.opacity, entrance, 8, delta);
    });
    embroidery.current.forEach((material) => {
      material.color.lerp(embroideryColors[stage], 1 - Math.exp(-7 * delta));
      material.opacity = THREE.MathUtils.damp(material.opacity, entrance, 8, delta);
    });
  });

  return <group ref={group}><primitive object={model} /></group>;
}

export default function CapViewer({ progress, revealProgress }: { progress: number; revealProgress: number }) {
  return <Canvas shadows dpr={[1, 1.5]} camera={{ position: [0, 0.05, 5.22], fov: 31 }} gl={{ alpha: true, antialias: true, powerPreference: "high-performance" }}>
    <ambientLight intensity={2.35} />
    <directionalLight position={[4, 5, 4]} intensity={3.7} castShadow shadow-mapSize={[1024, 1024]} />
    <directionalLight position={[-4, 2, -3]} intensity={2.9} color="#c8d6ff" />
    <pointLight position={[0, -1, 3]} intensity={1.35} color="#f3c9b1" />
    <Suspense fallback={null}><ProductCap progress={progress} revealProgress={revealProgress} /></Suspense>
    <ContactShadows position={[0, -1.55, 0]} opacity={0.28} scale={4.6} blur={2.7} far={3.4} color="#000000" />
  </Canvas>;
}

useGLTF.preload("/models/baseball_cap.glb");
