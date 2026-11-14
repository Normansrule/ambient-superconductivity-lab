const WORDS = [
  {
    word: "superconductor",
    tone: "solid",
    meaning: "Zero resistance and bulk diamagnetism, independently replicated, with a citation.",
  },
  {
    word: "claimed",
    tone: "warn",
    meaning: "Someone asserted superconductivity. The record is unsettled, refuted, or retracted.",
  },
  {
    word: "predicted",
    tone: "info",
    meaning: "A model in this repository says it might be. Nobody has measured it.",
  },
  {
    word: "screened",
    tone: "muted",
    meaning: "A candidate passed a filter, such as thermodynamic stability. It says nothing about Tc.",
  },
];

export default function Vocabulary() {
  return (
    <section className="section" aria-labelledby="vocab-title">
      <h2 id="vocab-title">Four words, used precisely</h2>
      <p className="section-lede">
        A candidate in this lab is never called a superconductor. These are the only words we use.
      </p>
      <div className="vocab-grid">
        {WORDS.map((w) => (
          <article key={w.word} className={`vocab-card tone-${w.tone}`}>
            <h3>{w.word}</h3>
            <p>{w.meaning}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
