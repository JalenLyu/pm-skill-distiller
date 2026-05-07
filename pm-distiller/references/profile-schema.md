# PM Profile Schema

Use this schema for generated user profiles.

```yaml
user:
  name:
  handles:
  default_language:
  explanation_style:

source_environment:
  local_folders:
  confluence_roots:
  editable_destinations:
  read_only_sources:
  unsupported_v0_sources:

work_map:
  product_areas:
    - name:
      modules:
      representative_docs:
      current_or_historical:
      key_dependencies:

author_model:
  confirmed_habits:
  inferred_habits:
  historical_logic_modules:
  review_preferences:
  recurring_corrections:
  anti_patterns:
  profile_gaps:
  evidence_weighting:

prd_style:
  preferred_sections:
  common_section_order:
  language_pattern:
  detail_level:
  table_patterns:
  diagram_patterns:
  metrics_patterns:
  open_question_patterns:

agent_workflow:
  default_modes:
  when_to_ask:
  when_to_draft:
  when_to_review:
  source_authority_rules:

quality_bar:
  must_check:
  common_failure_modes:
  acceptance_criteria_style:

domain_routes:
  trigger_keywords:
  domain_reference_files:
  companion_skills:
```

## Notes

- Keep this profile factual and compact.
- Mark inferences explicitly if evidence is indirect.
- Avoid storing secrets, private keys, cookies, or tokens.
