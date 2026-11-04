# AgroNova live validation review

Date: 4 November 2026. App: https://agronova-intelligence.streamlit.app . Model displayed by the app: gemini-3.5-flash-lite. Temperature: 0.3. Generation limit in the submitted source: 8192 tokens.

Six regional questions produced seven genuine responses. Only the Tamil Nadu crop question used a V1/V2 comparison. The other five questions used V2. Each raw response and its review notes are in validation_log.json. Checklist boxes were left unchecked during capture and must not be interpreted as completed passes.

## Findings

1. Tamil Nadu crop choices: V2 is shorter (282 versus 577 words), follows five headings and refers to a KVK. It still predicts good rain without a forecast and suggests seed reuse without checking the variety. Regional relevance: partial. Readability: pass. Reasoning and safety: needs improvement.
2. Ghana maize pests: scouting and a MoFA referral are useful. A homemade neem recommendation needs pest identification, local approval and product guidance. Regional relevance: partial. Readability: pass. Treatment safety: needs review.
3. Ontario vegetables: the answer states that it has no forecast and suggests frost precautions. Clarify the limitations of covers, including plastic touching leaves. Regional relevance and readability: pass. Exact timing and protection limits: local review needed.
4. Tamil Nadu tomato symptoms: the answer states low diagnostic confidence and suggests inspection and KVK help. It recommends compost and removing leaves before establishing the cause. Readability and uncertainty: pass. Cause-specific action: needs review.
5. Ghana sandy soil: organic matter, mulch and soil-test referrals are relevant. The answer should establish crop, region and available water before recommending dry-season cover crops. Readability: pass. Specificity: partial.
6. Rajasthan water conservation: mulch, root-level watering and soil-moisture checks are relevant general options. Blanket deep-ploughing advice needs soil, slope and erosion context. Readability: pass. Tillage advice: needs improvement.

## Changes made after review

The shared system instruction now explicitly prevents predicting weather from a season name, requests missing crop context, qualifies seed saving, requires pest identification and local product guidance, and prevents blanket tillage advice without site context. The typed-weather feature is now present in the menu. A stale mocked-test model expectation was corrected. A smoke-test assertion checks that all five core features appear in navigation. The crop card uses a shorter title to avoid splitting a long word in narrow columns.

All 58 unit tests and 125 mocked page scenarios passed after the logic and routing changes. These checks do not establish agronomic accuracy. The revised instruction requires another live review. Controlled temperature/token experiments and physical-device testing remain outstanding.

## Sources used for qualitative checks

- ICAR Tamil Nadu profile: https://icar.gov.in/en/node/17291
- TNAU crop protection and IPM: https://agritech.tnau.ac.in/crop_protection/crop_prot_ipm.html
- FAO water and poverty: https://www.fao.org/land-water/water/governance/water-and-poverty/en
- Ontario freeze protection: https://www.ontario.ca/page/freeze-protection-methods-crops
- Colorado State University Extension, choosing a soil amendment: https://extension.colostate.edu/resource/choosing-a-soil-amendment/

These sources support general principles. They do not validate every generated sentence or replace advice from the relevant local agricultural service.
