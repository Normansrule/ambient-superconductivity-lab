import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";

/**
 * A cartoon of phonon-mediated pairing: positive ions (cyan) vibrate in a
 * lattice wave; a passing electron (amber) pulls nearby ions toward it, and a
 * second electron is drawn into the distortion it leaves behind.
 * Qualitative only — not to scale and not a simulation. The quantitative
 * theory arrives in Stage 1 with citations [bardeen1957; cooper1956].
 */

const NX = 11;
const NY = 5;
const NZ = 3;
const SPACING = 0.8;
const WIDTH = (NX - 1) * SPACING;

function Lattice() {
  const ions = useRef<THREE.InstancedMesh>(null);
  const e1 = useRef<THREE.Mesh>(null);
  const e2 = useRef<THREE.Mesh>(null);
  const dummy = useMemo(() => new THREE.Object3D(), []);
  const sites = useMemo(() => {
    const out: THREE.Vector3[] = [];
    for (let i = 0; i < NX; i++)
      for (let j = 0; j < NY; j++)
        for (let k = 0; k < NZ; k++)
          out.push(
            new THREE.Vector3(
              (i - (NX - 1) / 2) * SPACING,
              (j - (NY - 1) / 2) * SPACING,
              (k - (NZ - 1) / 2) * SPACING,
            ),
          );
    return out;
  }, []);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    const span = WIDTH + 3;
    const x1 = ((t * 1.1) % span) - span / 2;
    const x2 = x1 - 1.4;
    const ePos1 = new THREE.Vector3(x1, 0.15 * Math.sin(t * 3), 0);
    const ePos2 = new THREE.Vector3(x2, -0.15 * Math.sin(t * 3 + 0.8), 0);
    e1.current?.position.copy(ePos1);
    e2.current?.position.copy(ePos2);

    const pull = new THREE.Vector3();
    sites.forEach((s, idx) => {
      // lattice wave (phonon)
      const wave = 0.07 * Math.sin(1.4 * s.x - 2.2 * t + 0.6 * s.z);
      // attraction toward the first electron, fading with distance
      pull.subVectors(ePos1, s);
      const r2 = pull.lengthSq();
      pull.normalize().multiplyScalar(0.22 * Math.exp(-r2 / 0.9));
      dummy.position.set(s.x + pull.x, s.y + wave + pull.y, s.z + pull.z);
      dummy.updateMatrix();
      ions.current?.setMatrixAt(idx, dummy.matrix);
    });
    if (ions.current) ions.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <group position={[3.0, 0.1, 0]} rotation={[0.35, -0.5, 0]} scale={0.78}>
      <instancedMesh ref={ions} args={[undefined, undefined, sites.length]}>
        <sphereGeometry args={[0.13, 18, 18]} />
        <meshStandardMaterial color="#7fe7ff" emissive="#1b6f8f" emissiveIntensity={0.6} roughness={0.35} />
      </instancedMesh>
      {[e1, e2].map((ref, i) => (
        <mesh key={i} ref={ref}>
          <sphereGeometry args={[0.22, 24, 24]} />
          <meshStandardMaterial color="#ffd36e" emissive="#ffb000" emissiveIntensity={1.4} />
        </mesh>
      ))}
    </group>
  );
}

export default function LatticeScene() {
  return (
    <Canvas
      data-testid="hero-canvas"
      camera={{ position: [0, 1.0, 9.5], fov: 45 }}
      dpr={[1, 2]}
      gl={{ preserveDrawingBuffer: true, antialias: true }}
    >
      <color attach="background" args={["#05121f"]} />
      <ambientLight intensity={0.35} />
      <pointLight position={[4, 5, 6]} intensity={60} color="#bff4ff" />
      <pointLight position={[-5, -3, 2]} intensity={25} color="#ffd36e" />
      <Lattice />
      <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.25} />
    </Canvas>
  );
}
