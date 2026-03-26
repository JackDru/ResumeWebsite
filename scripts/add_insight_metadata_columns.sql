-- Optional: run in Supabase SQL editor so the scorer can persist tier/confidence.
-- If you skip this, the scorer still works — it retries without these columns.

alter table public.insights
  add column if not exists insight_tier text,
  add column if not exists evidence_confidence text;

comment on column public.insights.insight_tier is 'strategic | operational';
comment on column public.insights.evidence_confidence is 'pattern | recurring | anecdotal';
