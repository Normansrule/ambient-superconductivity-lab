import Equation from "./Equation";

const STEPS = [
  { n: "1", title: "Freeze the target", body: "targets.yaml fixes the quantity, the expected value, the tolerance, and the source, before any result exists." },
  { n: "2", title: "Measure", body: "prove.py computes the number from code, data, or logged hardware, never from a hand-typed value." },
  { n: "3", title: "Check", body: "make prove-N compares every number to its target and fails loudly on any miss or unknown citation." },
  { n: "4", title: "Approve", body: "A stage is done only when the proof passes and Aleksander signs off. Then the next stage may start." },
];

export default function ProofLoop() {
  return (
    <section className="section" aria-labelledby="proof-title">
      <h2 id="proof-title">How every stage is proved</h2>
      <ol className="proof-steps">
        {STEPS.map((s) => (
          <li key={s.n}>
            <span className="step-n">{s.n}</span>
            <h3>{s.title}</h3>
            <p>{s.body}</p>
          </li>
        ))}
      </ol>
      <p className="section-lede">Two equations Stage 1 builds on, with their sources:</p>
      <div className="equations">
        <Equation
          tex={String.raw`\frac{\Delta(0)}{k_B T_c} \approx 1.764 \quad (\text{within } 0.5\%)`}
          label="Weak-coupling BCS gap ratio, to be reproduced by the numerical gap-equation solver"
          cite={["bardeen1957", "muhlschlegel1959"]}
        />
        <Equation
          tex={String.raw`\lambda = 2\int_0^{\infty} \frac{\alpha^2 F(\omega)}{\omega}\, d\omega`}
          label="Electron–phonon coupling constant used in the Allen–Dynes Tc formula"
          cite={["allen1975"]}
        />
      </div>
    </section>
  );
}
