import { REPO } from "../lib/links";

export default function Footer() {
  return (
    <footer className="footer">
      <p>
        Built in the open by Aleksander Norman. Code: <a href={`${REPO}/blob/main/LICENSE`}>MIT</a>. Docs and media:{" "}
        <a href={`${REPO}/blob/main/LICENSE-docs`}>CC BY 4.0</a>. <a href={`${REPO}/blob/main/CITATION.cff`}>Cite this project</a>.
      </p>
    </footer>
  );
}
