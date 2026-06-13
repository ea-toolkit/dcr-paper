# DCR Paper — 50 Eval Questions for Review

**Domain:** Synthetic Healthcare Claims (Clearview Health Plans)
**KB:** 408 entities across 18 types, 6 layers
**Source:** All generated from seed context document via Claude Sonnet

## Behavioral (9 questions)

26. **Claims Process** — What is the high-level flow of a claim from submission to payment?
27. **Claim Adjudication** — What happens when the Rules Engine determines a claim should be pended?
31. **Payment Logic** — How does the Payment Engine know how much to pay a provider for a claim?
34. **Gateway Validation** — What validation does the Claims Gateway perform before routing claims downstream?
38. **Duplicate Detection** — How does the system handle duplicate claim submissions?
39. **Payment Corrections** — What happens when a provider needs to void and reissue a payment?
41. **Fee Schedules** — How does the Rules Engine access current fee schedules for providers?
44. **Post-payment Fraud** — What happens when fraud is detected after a claim has already been paid?
48. **duplicate detection** — How does the Claims Gateway determine whether an incoming claim is a duplicate?

## Structural (3 questions)

32. **Authorization Flow** — Which systems are involved when a provider submits a prior authorization request?
37. **Portal Features** — What information can members access through the Member Portal?
50. **provider identification** — What is an NPI and which systems in our architecture would need to store or validate this information?

## Organizational (3 questions)

30. **Provider Data** — Who is responsible for keeping provider credentials up to date?
36. **Issue Ownership** — Which team would handle an issue with member deductible calculations?
46. **team ownership** — Which team would I contact if there's an issue with member deductible tracking not updating correctly?

## Language (2 questions)

33. **Payment Documents** — What is the purpose of ERA 835 remittance advice?
35. **COB Process** — What is Coordination of Benefits and when does it apply?

## Reference (3 questions)

29. **Data Formats** — What is an EDI 837 file and where does it come from?
43. **Company Scale** — How many members does Clearview cover and across which geographic area?
47. **rules engine** — What are the three possible outcomes when the Rules Engine processes a claim?

## Decision (2 questions)

28. **Fraud Scoring** — How does the Fraud Detection system determine which claims to hold for review?
42. **Manual Review** — What triggers a claim to be sent for manual review instead of auto-adjudication?

## Cross-Cutting (28 questions)

 1. **claims flow** — What happens to a claim from the moment it enters the Claims Gateway until payment is issued?
 2. **team ownership** — Which team is responsible for maintaining the Rules Engine system?
 3. **claim status** — What does it mean when a claim is 'pended' during adjudication?
 4. **adjudication logic** — How does the Rules Engine determine whether to pay, deny, or pend a claim?
 5. **payment documents** — What is the difference between an ERA and an EOB?
 6. **member benefits** — Which system handles member deductible tracking and out-of-pocket maximums?
 7. **pre-auth targets** — What percentage of prior authorization requests does Clearview target for auto-approval?
 8. **fraud models** — How often are the fraud detection models retrained?
 9. **fraud thresholds** — What fraud detection score threshold triggers a hold for SIU review?
10. **system ownership** — Which team owns the Provider Directory system?
11. **gateway inputs** — What types of claim submission formats does the Claims Gateway accept?
12. **benefits coordination** — What does COB stand for and when does it apply?
13. **company size** — How many members does Clearview Health Plans cover?
14. **provider identification** — What is an NPI and why is it important in claims processing?
15. **payment processing** — Which system generates the 835 remittance advice files?
16. **duplicate handling** — What happens when the Claims Gateway detects a duplicate claim submission?
17. **eligibility integration** — How does the Eligibility Service support the adjudication process?
18. **payment terms** — What does 'allowed amount' refer to in claims processing?
19. **support escalation** — Which team would I contact about issues with digital ID cards on the member portal?
20. **payment corrections** — What triggers a void and reissue process in the Payment Engine?
21. **auth routing** — How does Pre-Auth Service route complex authorization cases?
22. **provider data** — What information does the Provider Directory maintain about contracted providers?
23. **system status** — What does it mean when someone says 'the gateway is backed up'?
24. **cross-system flow** — When a claim requires both fraud review and prior authorization, how do these processes interact across the different systems?
25. **eligibility changes** — If a member's eligibility status changes mid-month, how does this impact claims that are already in the adjudication pipeline across multiple teams' systems?
40. **Contract Updates** — Which systems need to be updated when a provider's contract terms change?
45. **Enrollment Updates** — How do changes in member enrollment status flow from source systems to claims processing?
49. **COB workflow** — Which systems need to communicate when processing a claim that requires coordination of benefits with another insurer?

## Distribution Summary

| Layer | Count | % |
|-------|-------|---|
| behavioral | 9 | 18% |
| structural | 3 | 6% |
| organizational | 3 | 6% |
| language | 2 | 4% |
| reference | 3 | 6% |
| decision | 2 | 4% |
| cross-cutting | 28 | 56% |
| **Total** | **50** | **100%** |

## Question Type Analysis

| Type | Count |
|------|-------|
| what | 25 |
| how | 12 |
| which | 10 |
| when/if | 2 |
| who | 1 |

## Topic Coverage

Systems/concepts referenced: 17

| System/Concept | Questions |
|----------------|-----------|
| claims gateway | 5 |
| rules engine | 5 |
| fraud | 5 |
| era | 4 |
| prior authorization | 3 |
| clearview | 3 |
| provider directory | 2 |
| npi | 2 |
| eligibility | 2 |
| member portal | 2 |
| payment engine | 2 |
| coordination of benefits | 2 |
| eob | 1 |
| siu | 1 |
| cob | 1 |
| pre-auth | 1 |
| edi 837 | 1 |

## Potential Issues to Review

1. **56% cross-cutting** — the pilot's 25 questions had no layer hints (original generator didn't tag them). The new 25 are better distributed. Should we re-tag the original 25 with layer hints, or is cross-cutting fine since those questions genuinely span layers?

2. **Near-duplicate pairs** — Q16/38/48 (duplicate detection), Q36/46 (deductible ownership), Q26/1 (claims flow). Dedup didn't catch these because phrasing differs enough. Could inflate certain topics. Should we trim or keep as robustness checks?

## Methodology

- 25 questions from pilot run (already evaluated once) + 25 new
- Deduplication: Jaccard similarity >0.55 on content words + entity overlap >0.7
- Each question evaluated 3 times (3 trials) across 9 conditions:
  - 3 baselines: naive vector, vanilla RAG, full DCR
  - 6 ablation: full DCR, -intent, -graph, -layer boost, -confidence, -dedup
- Scoring: LLM judges answer as ANSWERABLE/PARTIAL/NOT_ANSWERABLE mapped to CLEAN/INCOMPLETE/MISSING
- Results reported as mean +/- SD across 3 trials
- Estimated cost: ~$28, runtime: ~3 hours