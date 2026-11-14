import { useLayoutEffect, useRef } from "react";
import gsap from "gsap";
import LatticeScene from "../three/LatticeScene";
import Cite from "./Cite";
import { REPO } from "../lib/links";

export default function Hero() {
  const copy = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from(".hero-line", { y: 24, opacity: 0, duration: 0.9, stagger: 0.12, ease: "power3.out" });
    }, copy);
    return () => ctx.revert();
  }, []);

  return (
    <header className="hero">
      <div className="hero-canvas">
        <LatticeScene />
      </div>
      <div className="hero-copy" ref={copy}>
        <p className="eyebrow hero-line">Open research platform · Stage 0</p>
        <h1 className="hero-line">Ambient Superconductivity Lab</h1>
        <p className="lede hero-line">
          A staged, provable search toward ambient-pressure, room-temperature superconductors, and a
          trustworthy way to evaluate the claims made along the way.
        </p>
        <div className="actions hero-line">
          <a className="btn primary" href={REPO}>View the repository</a>
          <a className="btn" href="#stages">See the proofs</a>
        </div>
        <p className="caption hero-line">
          Cartoon of phonon-mediated pairing: a passing electron pulls the ion lattice, and a second electron
          follows the distortion. Qualitative, not to scale <Cite keys={["cooper1956", "bardeen1957"]} />.
        </p>
      </div>
    </header>
  );
}
