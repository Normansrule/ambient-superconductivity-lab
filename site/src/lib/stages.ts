/** Fallback stage list, used when status/status.json (published by CI) is unavailable. */
export interface StageStatus {
  id: number;
  name: string;
  state: string;
  badge?: { message: string; color: string };
  commit?: string | null;
  generated?: string | null;
}

export const FALLBACK_STAGES: StageStatus[] = [
  { id: 0, name: "Foundation", state: "in-progress" },
  { id: 1, name: "Theory engine", state: "planned" },
  { id: 2, name: "Curated data and landscape", state: "planned" },
  { id: 3, name: "Machine learning screening baseline", state: "planned" },
  { id: 4, name: "Claim checklist (flagship)", state: "planned" },
  { id: 5, name: "Tabletop measurement", state: "planned" },
  { id: 6, name: "First-principles check (optional)", state: "planned" },
  { id: 7, name: "Preregistered predictions preprint", state: "planned" },
  { id: 8, name: "Collaboration proposal", state: "planned" },
];

export async function loadStatus(): Promise<StageStatus[] | null> {
  try {
    const res = await fetch(`${import.meta.env.BASE_URL}status/status.json`, { cache: "no-store" });
    if (!res.ok) return null;
    return (await res.json()) as StageStatus[];
  } catch {
    return null;
  }
}
