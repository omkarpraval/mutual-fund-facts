# Frontend

    npm install
    npm run dev          # http://localhost:3000

Backend must be running on :8000, or set `NEXT_PUBLIC_API`.

## UI states

All nine required states are implemented in `components/Cards.tsx`, driven
by the `state` field the API returns: `answer`, `refusal`, `pii`,
`needs_scheme`, `no_evidence`, `too_long`, `error`, plus empty and loading
handled in `app/page.tsx`.

## Design notes

The provenance strip is the signature element. Every factual answer carries
its source and as-of date as a filing stamp rather than a footnote, because
sourcing is the product rather than a citation obligation.

Amber appears in exactly one place: a value that has passed its staleness
window. Because it is used nowhere else, it always means the same thing.

The scheme selector shows the former name under the dropdown when one
exists. All three corpus schemes were renamed under SEBI categorisation,
so a long-term holder searching for "SBI Bluechip" needs to see that they
have landed on the right fund.
