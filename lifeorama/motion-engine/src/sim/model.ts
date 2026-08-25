// ─────────────────────────────────────────────────────────────────────────────
// PROTOTYPE simulation model — "1,000 Families: Rent vs Buy, 30 years".
// Deterministic + seeded so the same run reproduces exactly.
//
// IMPORTANT: these are ILLUSTRATIVE look-test parameters, NOT sourced/publishable
// figures. A shipping episode replaces the constants below with values from FRED /
// Case-Shiller / Census, each entered in the episode's sources.md manifest.
//
// Honest finding this scenario produces: families who BUY at t0 and HOLD 30 years
// almost never go "underwater" — a crash 17 years in is a dip, not a bankruptcy.
// The drama is the visible recession plunge (renters' portfolios ~-45%) and the
// recovery + final gap, NOT fabricated foreclosures.
// ─────────────────────────────────────────────────────────────────────────────

export const N = 1000;
export const MONTHS = 360; // 30 years
export const RENTERS = 500;

// Recession window (months). ~year 17 drawdown, ~year 18.5 recovery.
export const RECESSION_START = 204;
export const RECESSION_END = 228;

function mulberry32(seed: number) {
  let a = seed;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Monthly total-return factor for a diversified stock portfolio, with an
// idiosyncratic per-family offset so the swarm fans out.
function marketMonthly(m: number, idio: number): number {
  const base = Math.pow(1.102, 1 / 12) - 1; // ~10.2%/yr NOMINAL — S&P 500 CAGR 1928-2024 w/ dividends reinvested, Damodaran/NYU Stern dataset. (Corrected 2026-07-04: video displays plain nominal dollar figures with no inflation-adjustment caveat, so the equity assumption must be nominal too — the prior 7% figure was Damodaran's REAL/inflation-adjusted rate, inconsistent with the nominal housing rate and nominal dollar display, which understated the renter outcome.)
  let r = base + idio;
  if (m >= RECESSION_START && m <= 216) r = -0.068 + idio * 0.5; // sharp drawdown (~-57% over ~12mo — matches verified S&P 500 Oct 2007-Mar 2009 peak-to-trough, federalreservehistory.org)
  else if (m > 216 && m <= RECESSION_END) r = 0.022 + idio; // bounce
  r += 0.004 * Math.sin(m / 3.3); // mild vol
  return r;
}

// Housing price index (national-ish), normalized to 1.0 at t0. Bubble peak ~yr15,
// crash yrs 17-19, partial recovery after.
function housingIndex(m: number): number {
  const y = m / 12;
  let idx = Math.pow(1.032, y); // ~3.2%/yr baseline
  idx *= 1 + 0.12 * Math.exp(-Math.pow(y - 15.5, 2) / 6); // bubble
  if (y > 16.5 && y < 19.5) idx *= 1 - 0.27 * Math.min(1, (y - 16.5) / 1.5); // crash (~-27% — matches verified Case-Shiller US National Index 2006 peak→2012 trough, FRED CSUSHPINSA)
  else if (y >= 19.5) idx *= 0.8 + 0.06 * (y - 19.5); // recovery
  return idx;
}

export type Agent = {
  cohort: "rent" | "buy";
  x: number; // fixed horizontal jitter 0..1
  nw: Float32Array; // net worth per month [0..MONTHS]
};

export function build(): Agent[] {
  const agents: Agent[] = [];
  const rnd = mulberry32(20260702);
  const h0 = housingIndex(0);

  for (let i = 0; i < N; i++) {
    const cohort: "rent" | "buy" = i < RENTERS ? "rent" : "buy";
    const idio = (rnd() - 0.5) * 0.01; // wider spread → a real cloud, not a line
    const x = rnd();
    const nw = new Float32Array(MONTHS + 1);

    if (cohort === "rent") {
      // Heterogeneous households: starting savings 25k–60k, invest 450–1200/mo.
      let v = 25000 + rnd() * 35000;
      const sm = 450 + rnd() * 750;
      nw[0] = v;
      for (let m = 1; m <= MONTHS; m++) {
        v = v * (1 + marketMonthly(m, idio)) + sm;
        nw[m] = v;
      }
    } else {
      // Bought a 300k–380k home at ~88–92% LTV, holds. Local appreciation varies.
      const house0 = 300000 + rnd() * 80000;
      let bal = house0 * (0.86 + rnd() * 0.06);
      const r = 0.005;
      const pay = bal * 0.006; // ~30yr @6% monthly payment
      const appr = 0.9 + rnd() * 0.4;
      let savings = 2000 + rnd() * 8000;
      const sSave = 150 + rnd() * 250;
      nw[0] = house0 * appr - bal + savings;
      for (let m = 1; m <= MONTHS; m++) {
        const interest = bal * r;
        bal = Math.max(0, bal - Math.max(0, pay - interest));
        savings = savings * (1 + marketMonthly(m, idio) * 0.35) + sSave;
        const hv = house0 * appr * (housingIndex(m) / h0);
        nw[m] = hv - bal + savings;
      }
    }
    agents.push({ cohort, x, nw });
  }
  return agents;
}

function median(arr: Float64Array): number {
  const a = Array.from(arr).sort((p, q) => p - q);
  const n = a.length;
  return n % 2 ? a[(n - 1) / 2] : (a[n / 2 - 1] + a[n / 2]) / 2;
}

export type Aggregates = {
  medRent: Float32Array;
  medBuy: Float32Array;
};

export function aggregates(agents: Agent[]): Aggregates {
  const rents = agents.filter((a) => a.cohort === "rent");
  const buys = agents.filter((a) => a.cohort === "buy");
  const medRent = new Float32Array(MONTHS + 1);
  const medBuy = new Float32Array(MONTHS + 1);
  const tmpR = new Float64Array(rents.length);
  const tmpB = new Float64Array(buys.length);

  for (let m = 0; m <= MONTHS; m++) {
    for (let i = 0; i < rents.length; i++) tmpR[i] = rents[i].nw[m];
    for (let i = 0; i < buys.length; i++) tmpB[i] = buys[i].nw[m];
    medRent[m] = median(tmpR);
    medBuy[m] = median(tmpB);
  }
  return { medRent, medBuy };
}

// Honest focus: the median buyer (a typical outcome), not a fabricated worst case.
export function focusAgentIndex(agents: Agent[]): number {
  const buys: { i: number; v: number }[] = [];
  for (let i = RENTERS; i < N; i++) buys.push({ i, v: agents[i].nw[MONTHS] });
  buys.sort((a, b) => a.v - b.v);
  return buys[Math.floor(buys.length / 2)].i;
}
