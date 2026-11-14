import { REPO } from "../lib/links";

/** Renders a [bibkey] that links to the project's verified bibliography. */
export default function Cite({ keys }: { keys: string[] }) {
  return (
    <a className="cite" href={`${REPO}/blob/main/docs/references.bib`} title="Open references.bib">
      [{keys.join("; ")}]
    </a>
  );
}
