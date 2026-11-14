import { useEffect, useState } from "react";
import { FALLBACK_STAGES, loadStatus, type StageStatus } from "../lib/stages";
import { REPO } from "../lib/links";

const STATE_LABEL: Record<string, string> = {
  planned: "Planned",
  "in-progress": "In progress",
  proved: "Proved, awaiting approval",
  done: "Done",
};

function proofClass(s: StageStatus): string {
  const m = s.badge?.message ?? "";
  if (m.startsWith("passing")) return "pass";
  if (m.startsWith("failing")) return "fail";
  return "idle";
}

export default function StageGrid() {
  const [stages, setStages] = useState<StageStatus[]>(FALLBACK_STAGES);
  const [live, setLive] = useState(false);

  useEffect(() => {
    loadStatus().then((s) => {
      if (s) {
        setStages(s);
        setLive(true);
      }
    });
  }, []);

  const generated = stages.find((s) => s.generated)?.generated;

  return (
    <section className="section" id="stages" aria-labelledby="stages-title">
      <h2 id="stages-title">Stages and their proofs</h2>
      <p className="section-lede">
        {live
          ? `Live from the latest CI run${generated ? ` (${new Date(generated).toUTCString()})` : ""}.`
          : "Proof status appears here after continuous integration (CI) publishes it."}
      </p>
      <div className="stage-grid">
        {stages.map((s) => (
          <article key={s.id} className={`stage-card ${s.state}`}>
            <div className="stage-head">
              <span className="stage-id">S{s.id}</span>
              <span className={`proof-chip ${proofClass(s)}`}>{s.badge?.message ?? "no result yet"}</span>
            </div>
            <h3>{s.name}</h3>
            <p className="stage-state">{STATE_LABEL[s.state] ?? s.state}</p>
            {s.id === 0 && (
              <a className="stage-link" href={`${REPO}/blob/main/proofs/stage0/PROOF.md`}>Read the proof →</a>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}
