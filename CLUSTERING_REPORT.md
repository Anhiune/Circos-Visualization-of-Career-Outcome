# Clustering Rebuild Report

## Purpose

This report documents how the major and career clusters were rebuilt from the raw dataset, what decisions were made, and the rationale behind each decision. The goal was to create a lookup file that classifies as many records as reasonably possible while keeping the clustering interpretable for the dashboard.

## Source Files Used

- Raw source data: [Ire Anh Data 3.16.26.xlsx](c:/Users/hoang/Documents/Career_Major_project/Ire%20Anh%20Data%203.16.26.xlsx)
- Existing major cluster reference: `C:\Users\hoang\Documents\project_test\csv_data\Major_Career_Analysis_v4__Cluster_Breakdown.csv`
- Existing career cluster reference: `C:\Users\hoang\Documents\project_test\csv_data\Major_Career_Analysis_v4__Career_Analysis.csv`
- Rebuild script: [rebuild_cluster_lookup.py](c:/Users/hoang/Documents/Career_Major_project/rebuild_cluster_lookup.py)

## Rebuild Goal

The old filtered dataset was too small because many rows were being dropped before they reached the dashboard. The rebuild was designed to:

- start from the raw original data instead of the previously filtered CSV
- preserve the existing cluster framework where it still made sense
- classify obvious job titles even when the exact title was not already in the old lookup table
- leave only true edge cases or blank entries unclassified

## Final Output Files

- Full rebuilt lookup: [Major_Job_Cluster_Lookup_Rebuilt_Full.csv](c:/Users/hoang/Documents/Career_Major_project/Major_Job_Cluster_Lookup_Rebuilt_Full.csv)
- Rebuilt filtered lookup: [rebuild_outputs/Major_Job_Cluster_Lookup_rebuilt_filtered.csv](c:/Users/hoang/Documents/Career_Major_project/rebuild_outputs/Major_Job_Cluster_Lookup_rebuilt_filtered.csv)
- Live dashboard lookup: [Major_Job_Cluster_Lookup_Filtered.csv](c:/Users/hoang/Documents/Career_Major_project/Major_Job_Cluster_Lookup_Filtered.csv)
- Rebuild summary: [rebuild_outputs/Rebuild_Summary.csv](c:/Users/hoang/Documents/Career_Major_project/rebuild_outputs/Rebuild_Summary.csv)

## High-Level Results

The rebuild summary shows:

- Raw rows: `4129`
- Filtered classified rows: `2244`
- Major unmatched rows: `0`
- Job exact matches: `1078`
- Job normalized matches: `10`
- Job heuristic matches: `1703`
- Blank job-title rows: `1338`
- Job unclassified rows after rebuild: `0`

Interpretation:

- The major clustering problem is solved. Every row matched a major cluster.
- The career clustering problem is also solved for nonblank titles. Any row that still drops out now does so because the raw data has no job title, not because the clustering logic failed.

## Rebuild Logic

The rebuild script applies the following decision order.

### 1. Major cluster lookup first

The major is first matched against the old major-cluster reference table.

Rationale:

- This preserves continuity with the earlier project structure.
- It avoids inventing a new major taxonomy unless there was a clear problem.
- It keeps the dashboard comparable to earlier versions.

### 2. Direct major overrides before general lookup

Some majors were obviously placed better through an override than by the old lookup file. These were added to `DIRECT_CLUSTER_OVERRIDES`.

Rationale:

- This is the safest place to correct known bad placements.
- It is more transparent than silently changing the source reference file.
- It keeps the exceptions explicit and reviewable.

### 3. Major aliases before failure

If the exact major name does not match, the script uses `MAJOR_NAME_ALIASES`.

Rationale:

- The raw dataset contains spelling variants, degree-format variants, and track labels.
- Many of these are semantically the same major for dashboard purposes.
- Alias mapping reduces artificial fragmentation without changing the user-facing label logic elsewhere.

### 4. Exact career-title lookup first

Job titles are first matched directly against the old career-cluster reference table.

Rationale:

- If a title already exists in the previous curated mapping, that is the most trustworthy classification.
- This keeps continuity with the older project and avoids unnecessary reclassification.

### 5. Normalized career-title lookup second

If exact match fails, the script normalizes titles by lowercasing, stripping punctuation, collapsing spaces, and removing suffixes like `Jr` or `III`.

Rationale:

- Many titles differ only by punctuation or formatting.
- These are not meaningful career differences.
- Normalization recovers straightforward matches with low risk of distortion.

### 6. Rule-based heuristic classification last

If a title still does not match, the script uses keyword and context rules in `classify_job_by_rules`.

Rationale:

- The old lookup table did not cover enough real titles from the raw dataset.
- Many titles are still obvious even without an exact match.
- The user explicitly requested an overfit approach so that most reasonable job titles are classified, leaving only extreme cases unresolved.

## Major-Cluster Decisions and Rationale

### Economics moved to Social Sciences

Decision:

- `Economics` and its track variants were moved to `SOCIAL SCIENCES & HUMANITIES`.

Affected variants include:

- `Economics`
- `Economics - Business`
- `Economics - International`
- `Economics - Mathematical`
- `Economics - Public Policy`

Rationale:

- Economics is conceptually a social science, even when some tracks overlap with business or quantitative work.
- Keeping all Economics variants together creates a cleaner and more defensible presentation.
- Splitting Economics across business and social science would make the dashboard harder to interpret and visually inconsistent.

### Engineering and computing aliases were consolidated

Examples:

- `Data Science` -> `Computer Science & IT`
- `Information Technology` -> `Computer Science & IT`
- `Software Engineering` -> `Computer Science & IT`
- `Systems Engineering` -> `Engineering Disciplines`

Rationale:

- These names represent adjacent programs that belong in the engineering and technology area for this dashboard.
- Consolidation reduces fragmentation and aligns with how audiences interpret those degrees.

### Education and special-services programs were cleaned up

Examples:

- `Educational Studies` -> `Teacher Education`
- `Educational Leadership & Admin` -> `Educational Leadership`
- `Autism Spectrum Disorders` -> `Special Education & Counseling`

Rationale:

- These programs are better represented by functionally meaningful clusters than by highly specific program names.
- This creates clearer dashboard slices and matches likely stakeholder expectations.

## Career-Cluster Decisions and Rationale

The career rebuild intentionally favors practical interpretation over strict occupational coding. Below are the main rule families.

### Education titles -> `Education`

Examples of matched terms:

- `teacher`
- `professor`
- `faculty`
- `lecturer`
- `educator`
- `paraeducator`

Rationale:

- These roles are direct education outcomes.
- The titles are explicit and low-ambiguity.

### Social-service titles -> `Social Service`

Examples of matched terms:

- `social worker`
- `case manager`
- `family advocate`
- `youth worker`
- `care coordinator`

Rationale:

- These roles primarily represent human-services and community-support work.
- They fit better in social service than in generic healthcare or education buckets.

### Therapy and patient-facing care titles -> `Clinical Care`

Examples of matched terms:

- `therapist`
- `counselor`
- `mental health`
- `registered nurse`
- `nurse practitioner`
- `behavioral health`

Rationale:

- These roles involve direct clinical or patient-centered care.
- Grouping them together makes the healthcare outcomes easier to read.
- This follows the user’s preference that therapist-type roles should not remain unclassified.

### Research and laboratory titles -> `Research & Science`

Examples of matched terms:

- `research`
- `scientist`
- `laboratory`
- `chemist`
- `microbiologist`
- `regulatory affairs`

Rationale:

- These titles align more closely with scientific and technical research than with patient care.
- Keeping them separate from `Clinical Care` improves interpretability.

### Law, compliance, and public-policy titles -> `Legal & Policy`

Examples of matched terms:

- `attorney`
- `law`
- `legal`
- `compliance`
- `policy`
- `contract specialist`

Rationale:

- These roles form a coherent policy and legal grouping.
- They are more meaningful together than if spread across business or government categories.

### Accounting and finance separated

Accounting examples:

- `accountant`
- `auditor`
- `tax`
- `controller`
- `bookkeeper`

Finance examples:

- `financial`
- `investment`
- `banking`
- `wealth`
- `credit analyst`
- `underwriter`

Rationale:

- Accounting and finance are related but distinct outcome types.
- Keeping them separate improves the usefulness of the business-side career clusters.

### Sales, marketing, and communications business roles -> `Sales & Marketing`

Examples of matched terms:

- `sales`
- `marketing`
- `business development`
- `brand manager`
- `account executive`
- `customer success`

Rationale:

- These roles operate around growth, demand generation, and account expansion.
- They are different enough from finance and operations to justify their own group.

### Software, data, and IT were split into two clusters

Software and data examples:

- `software`
- `developer`
- `programmer`
- `data scientist`
- `machine learning`
- `web developer`

IT and infrastructure examples:

- `network`
- `help desk`
- `technical support`
- `system administrator`
- `infrastructure`

Rationale:

- Software-building roles and support/infrastructure roles are both technical, but they describe different kinds of work.
- Splitting them makes engineering and computing outcomes more informative.

### Engineering titles -> `Engineering`

Examples of matched terms:

- `engineer`
- `engineering`
- `controls engineer`
- `traffic engineer`
- `manufacturing engineer`

Rationale:

- These titles are explicit and should not be diluted into general operations or management categories.
- This is especially important for engineering majors.

### Operations, logistics, project, and program work -> `Management & Operations`

Examples of matched terms:

- `operations`
- `project`
- `program manager`
- `supply chain`
- `procurement`
- `logistics`
- `consultant`

Rationale:

- These titles usually center on coordination, execution, delivery, or process ownership.
- This is the most practical business-facing cluster for those roles.

### Product manager uses major context

Decision:

- `Technical Product Manager` goes to `Software & Data`.
- `Product Manager` goes to `Software & Data` for engineering/technology majors and `Management & Operations` otherwise.

Rationale:

- Product management sits between technical and business work.
- A single rule for all product managers would misclassify many records.
- Using major context is a practical compromise that matches likely career pathways.

### Leadership titles default to management unless clearly technical

Examples:

- `director`
- `vice president`
- `manager`
- `administrator`
- `owner`

Rationale:

- Leadership titles are common and often broad.
- If the title clearly references engineering or technical product work, it stays technical.
- Otherwise it is most useful to treat it as a leadership or management outcome.

### Analyst, specialist, coordinator, and associate titles use title clues first, major context second

Rationale:

- These are generic role words that appear across many industries.
- Title keywords like `finance`, `marketing`, `system`, `clinical`, or `operations` are more informative than the rank word itself.
- When title clues are weak, major context gives a reasonable fallback.

## Why Some Rows Still Do Not Appear in the Filtered Dataset

The rebuild eliminated unmatched major rows and unmatched job-title rows, but some rows still do not appear in the filtered output.

Main reason:

- `1338` rows in the raw data have blank job titles.

Rationale:

- A career cluster cannot be inferred responsibly when the job title field is empty.
- These rows should be excluded rather than guessed.

## Why the Dashboard Shows 2184 Graduates Instead of 2244

The rebuilt filtered lookup contains `2244` classified rows, but the rendered Circos dashboard shows `2184`.

Reason:

- The original Circos generation pipeline excludes rows whose small-major layout position is not included in the chart configuration.
- In practice, this means some records associated with `Unclassified` or non-rendered layout groups are dropped during image generation even though they exist in the rebuilt CSV.

Rationale for keeping this behavior:

- The user asked to reuse the existing code so that the output remains visually identical in style.
- Preserving the original rendering pipeline was prioritized over changing layout logic at the same time.

## Dashboard Regeneration Method

The dashboard images were regenerated with the existing project pipeline rather than a new renderer.

Steps:

- replace the old filtered CSV with the rebuilt filtered CSV
- rerun the original Circos data generator
- rerun the original individual major and career image generators
- rerender the main diagram and thumbnails with the existing Circos configuration

Rationale:

- This keeps the dashboard appearance consistent with the earlier project.
- It avoids introducing visual drift while fixing the underlying data.
- It makes it easier to attribute changes to the data rebuild rather than to a new charting system.

## Current Recommendation

For the current project version, the rebuilt clustering should be treated as the working source of truth because:

- it starts from the original raw data
- it resolves the severe undercounting problem
- it classifies all nonblank job titles
- it makes key domain decisions explicit and reviewable

If additional refinement is needed later, the safest next edits are:

- add or refine specific keyword rules in [rebuild_cluster_lookup.py](c:/Users/hoang/Documents/Career_Major_project/rebuild_cluster_lookup.py)
- review whether the remaining non-rendered records should be added to the Circos layout
- document any future major overrides in the same explicit override section

## Summary

The rebuild corrected two major issues in the old dataset:

- too many rows were lost because career titles were not classified
- Economics was grouped in a way that did not match the intended academic framing

The new process keeps the old project structure where possible, adds explicit overrides where necessary, and uses rule-based career classification to make the dashboard much more complete and interpretable.
