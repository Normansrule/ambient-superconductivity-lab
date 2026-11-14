import Hero from "./components/Hero";
import Vocabulary from "./components/Vocabulary";
import ProofLoop from "./components/ProofLoop";
import StageGrid from "./components/StageGrid";
import Footer from "./components/Footer";

export default function App() {
  return (
    <>
      <Hero />
      <main>
        <Vocabulary />
        <ProofLoop />
        <StageGrid />
      </main>
      <Footer />
    </>
  );
}
