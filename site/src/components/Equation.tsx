import { useMemo } from "react";
import katex from "katex";
import Cite from "./Cite";

/** A display equation rendered with KaTeX. Every equation must carry its bibkeys. */
export default function Equation({ tex, cite, label }: { tex: string; cite: string[]; label: string }) {
  const html = useMemo(() => katex.renderToString(tex, { displayMode: true, throwOnError: false }), [tex]);
  return (
    <figure className="equation" aria-label={label}>
      <div dangerouslySetInnerHTML={{ __html: html }} />
      <figcaption>
        {label} <Cite keys={cite} />
      </figcaption>
    </figure>
  );
}
