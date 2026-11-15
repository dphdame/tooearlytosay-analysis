---
title: "Medicaid Managed Care and Fraud Enforcement: Investigative Triage Accounts for State Output Gaps"
seo_title: "Medicaid Managed Care and Fraud Enforcement: Investigative Triage Accounts for State Output Gaps"
slug: "medicaid-managed-care-fraud-triage"
topic: "health-policy"
section: "health-policy"
reading_band: "standard"
audience: "economists, health researchers, and Medicaid integrity analysts"
description: "Within-state Medicaid managed care expansions show no detectable association with fraud convictions (beta = -0.007, 95% CI [-7.7%, +7.5%], p = 0.981), while Stage 2 triage accounts for 75.4% to 84.2% of cross-state log variance."
subtitle: "Within-state managed care expansions show no detectable association with fraud convictions at state-year precision, while case-to-indictment triage accounts for three-quarters of cross-state log variance."
date: "2026-11-15"
tags: ["medicaid", "managed-care", "program-integrity", "panel-data", "fixed-effects", "health-policy"]
related:
  - slug: "public-health-spending-regime-shifts"
    title: "Public Health Spending: When Crisis Aid Flips the Sign"
    section: "health-policy"
  - slug: "chw-spatial-financing-medi-cal"
    title: "Why Flat Medi-Cal Rates Underfund Community Health Care"
    section: "health-policy"
  - slug: "medicaid-fraud-labels"
    title: "The Label That Isn't: Why Excluded Doesn't Mean Fraudulent"
    section: "methodology"
faqs:
  - q: "Does Medicaid managed care raise state fraud convictions?"
    a: "From FY 2010 to 2024, within-state managed care increases show no detectable association with total convictions per staff-year (beta = -0.007, 95% CI [-7.7%, +7.5%], p = 0.981) or fraud convictions (beta = -0.031, p = 0.870)."
  - q: "Which stage accounts for cross-state gaps in fraud convictions?"
    a: "In a three-stage log-variance accounting identity, Stage 2 triage (indictments per case) accounts for 75.4% of cross-state variance in total convictions per staff-year and 84.2% for fraud."
---

Suppose we want to know whether shifting Medicaid enrollees into private managed care plans raises public fraud enforcement output. Over the past two decades, states have moved primary Medicaid delivery from fee-for-service payment to capitated managed care organizations (MCOs). By 2024, comprehensive risk-based plans enrolled roughly three-quarters of Medicaid enrollees nationwide and received more than half of program benefit spending.<sup><a href="#ref-1" id="fnref-1">1</a>, <a href="#ref-2" id="fnref-2">2</a></sup> Because capitated plans receive a fixed monthly payment per enrollee and bear financial risk for medical claims, a prominent policy argument holds that private plan incentives naturally curb provider fraud and boost public enforcement output.<sup><a href="#ref-3" id="fnref-3">3</a></sup>

When we pair 15 years of state MFCU records with federal managed care series, we find no detectable within-state association.<sup><a href="#ref-4" id="fnref-4">4</a>, <a href="#ref-5" id="fnref-5">5</a></sup> In a two-way fixed effects (TWFE) model on the uniform 2016 to 2024 comprehensive MCO series (*N* = 443 across 51 jurisdictions), a 10 percentage-point rise in managed care enrollment corresponds to a -0.09% shift in mean total convictions per staff-year (slope = -0.007, SE = 0.311, *p* = 0.981, 95% CI [-7.7%, +7.5%]) and a -0.56% shift in fraud-only convictions per staff-year (slope = -0.031, SE = 0.189, *p* = 0.870, 95% CI [-7.3%, +6.1%]). In the 15-year harmonized TWFE panel (*N* = 755), the 95% confidence interval spans -7.9% to +1.2% of the mean per 10 percentage-point rise (slope = -0.280, SE = 0.194, *p* = 0.152). Across all nine panel and first-difference models, the estimates rule out large positive output gains while leaving smaller positive or negative shifts inside the confidence bounds.

Meanwhile, total convictions per staff-year vary 17.9-fold across continuously operating states. If we examine aggregate convictions alone, we will miss where cross-state dispersion arises along the enforcement pipeline. To locate where cross-state differences sit, we can decompose state enforcement output per staff member into a descriptive three-stage accounting identity: case intake per staff member, indictments per opened case, and convictions per indictment (Figure 0).

<div class="methodology-box">
  <h4>Data and Design.</h4>
  <p>We pair annual HHS Office of Inspector General (OIG) statistical reports on 51 U.S. Medicaid Fraud Control Units (50 states and DC, FY 2010 to 2024, <em>N</em> = 755 state-years) with CMS managed care share series from CMS-64 expenditure reports and the uniform 2016 to 2024 CMS Managed Care Enrollment Summary (<em>N</em> = 443).<sup><a href="#ref-1">1</a>, <a href="#ref-4">4</a>, <a href="#ref-5">5</a></sup> Full panel regressions, variance decompositions, and replication scripts appear in the companion working paper (<a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7710301">SSRN 7710301</a>) and <a href="https://github.com/dphdame/tooearlytosay-analysis/tree/main/medicaid-managed-care-fraud-triage">triage-decomposition repository</a>.</p>
</div>

<figure>
  <img src="/images/health-policy/medicaid-managed-care-fraud-triage/figure0_pipeline_conceptual_map.webp" width="1260" height="735" loading="eager" decoding="async" alt="Conceptual map schematic of the three-stage Medicaid fraud enforcement pipeline comparing cooperative plan screening against administrative recoupment and investigative triage bottlenecks.">
  <figcaption>Three-stage multiplicative enforcement pipeline comparing front-end plan referral predictions against upstream administrative recoupment and Stage 2 investigative triage dispersion.</figcaption>
</figure>

Across the 50 continuously operating jurisdictions, Stage 2 investigative triage (indictments per opened case) accounts for 75.4% of the cross-state log variance in total convictions per staff-year (*r* = +0.58, *p* &lt; 0.001). When we isolate fraud-only enforcement actions, Stage 2 triage accounts for 84.2% of cross-state log variance (*r* = +0.73, *p* &lt; 0.001). Stage 1 case intake accounts for 24.6% of total variance (19.0% for fraud), while Stage 3 courtroom adjudication accounts for 0.0% (-3.2% for fraud). Because this decomposition is an accounting identity rather than a causal experiment, it measures where cross-state dispersion sits rather than proving what caused it. The accounting split shows that cross-state output differences cluster in investigative triage, where units evaluate raw leads and plan referrals for criminal indictment.


## Three Stages of the Enforcement Production Function

Every state operates a federally certified MFCU, typically housed within the state Attorney General's office, to prosecute healthcare provider fraud and patient abuse.<sup><a href="#ref-4" id="fnref-4">4</a></sup> When states carve benefits into capitated plans, public prosecutors lose direct access to state-paid fee-for-service claims and depend on plan Special Investigation Units (SIUs) to detect and refer suspected fraud.<sup><a href="#ref-6" id="fnref-6">6</a>, <a href="#ref-7" id="fnref-7">7</a></sup>

To locate where cross-state output differences sit, we can write convictions per staff member (*Y*<sub>*st*</sub> / *S*<sub>*st*</sub>) as a three-stage multiplicative accounting identity:

<div class="equation">Y<sub>st</sub> / S<sub>st</sub> = (C<sub>st</sub> / S<sub>st</sub>) &times; (I<sub>st</sub> / C<sub>st</sub>) &times; (Y<sub>st</sub> / I<sub>st</sub>).</div>

Here *S*<sub>*st*</sub> denotes total unit staff, *C*<sub>*st*</sub> denotes opened investigative cases, *I*<sub>*st*</sub> denotes criminal indictments, and *Y*<sub>*st*</sub> denotes criminal convictions. Taking natural logarithms converts this product into an exact additive sum across the three ratios:

<div class="equation">ln(Y<sub>s</sub> / S<sub>s</sub>) = ln(C<sub>s</sub> / S<sub>s</sub>) + ln(I<sub>s</sub> / C<sub>s</sub>) + ln(Y<sub>s</sub> / I<sub>s</sub>).</div>

Because covariance is linear, each stage's exact descriptive share of cross-state log variance equals its covariance with total log productivity divided by the total variance:

<div class="equation">Share<sub>k</sub> = Cov(ln Stage<sub>ks</sub>, ln(Y<sub>s</sub> / S<sub>s</sub>)) / Var(ln(Y<sub>s</sub> / S<sub>s</sub>)), &nbsp;&nbsp; Share<sub>1</sub> + Share<sub>2</sub> + Share<sub>3</sub> = 100%.</div>

Two institutional hypotheses offer competing predictions for how managed care interacts with this three-stage funnel.

1. **Cooperative Front-End Screening Hypothesis:** Under a cooperative delegation view, capitated plans apply automated prepayment edits to block routine billing errors and forward well-documented fraud schemes to state prosecutors.<sup><a href="#ref-3">3</a></sup> If private plan SIUs supply higher-grade investigative leads as managed care expands, within-state increases in managed care share should be associated with higher MFCU convictions per staff-year.

2. **Administrative Recoupment and Triage Filtering Hypothesis:** Under an organizational filtering view, commercial capitation changes how plans label billing anomalies upstream while leaving criminal convictions governed by internal prosecutorial capacity and referral quality.<sup><a href="#ref-8" id="fnref-8">8</a>, <a href="#ref-9" id="fnref-9">9</a></sup> Federal rules require MCO contracts to mandate prompt referral of potential fraud (42 C.F.R. Section 438.608(a)(7)) and reporting of overpayments within 30 days (Section 438.608(a)(2)). In practice, state contract definitions vary from any potential fraud to credible allegations of fraud, referral timelines span 1 to 270 days, and 78% of plans share integrity staff across commercial, Medicare, and Medicaid lines.<sup><a href="#ref-6">6</a>, <a href="#ref-10" id="fnref-10">10</a></sup> Because proving criminal intent is costly and state contracts under Section 438.608(d) let plans keep routine overpayment recoveries, plans may prefer administrative recoupment over criminal referrals. In addition, aggressive fraud takedowns shrink the historical claims base used to set future actuarially sound capitation rates (Sections 438.4 and 438.5(c)) and reduce the 85% Medical Loss Ratio numerator (Section 438.8).<sup><a href="#ref-2">2</a>, <a href="#ref-11" id="fnref-11">11</a></sup> Without standardized encounter data and clear referral floors, the expansion of managed care yields no detectable gain in state conviction rates under this hypothesis.


## Testing Within-State Managed Care Expansions

To test whether managed care expansion coincides with higher enforcement output within states, we estimate TWFE and first-difference regressions across 51 U.S. jurisdictions from fiscal year 2010 through 2024 (*N* = 755). Following prior Medicaid enforcement panels, we exclude Puerto Rico due to territorial funding caps and missing covariates, while North Dakota enters in fiscal year 2020 upon establishing its unit.<sup><a href="#ref-4">4</a>, <a href="#ref-8">8</a>, <a href="#ref-12" id="fnref-12">12</a></sup>

When we work with multi-decade CMS managed care series, we must account for an administrative reporting boundary between 2015 and 2016. Before 2016, harmonized state series tracked enrollment shares from MACPAC and CMS summaries. Starting in 2016, CMS-64 financial management reports tracked expenditure shares, which sit 20 to 25 percentage points lower because high-cost populations are frequently carved out of capitated contracts. If we pool across 2015 and 2016 without checking each regime separately, that measurement step-shift can distort within-state slopes.

We can guard against that measurement break by estimating two parallel panels (Figure 1 and Table 1). Panel A covers the 15-year harmonized series (*N* = 755), while Panel B isolates the uniform 2016 to 2024 CMS Managed Care Enrollment Summary (*N* = 443). Because MFCUs prosecute both billing fraud and patient abuse or neglect (817 fraud convictions and 334 patient abuse or neglect convictions nationwide in FY 2024), Panel B also separates fraud-only convictions per staff-year (mean = 0.55) and newly opened fraud cases per staff-year (mean = 10.09) from total convictions per staff-year (mean = 0.81).<sup><a href="#ref-4">4</a></sup>

<figure>
  <img src="/images/health-policy/medicaid-managed-care-fraud-triage/figure1_twfe_managed_care_null_forest.webp" width="1260" height="765" loading="lazy" decoding="async" alt="Horizontal forest plot of nine regression specifications showing implied percentage changes in MFCU enforcement output per 10 percentage-point increase in Medicaid managed care share from FY 2010 to 2024.">
  <figcaption>Implied percentage change in mean enforcement output per +10 percentage-point increase in state Medicaid managed care share across nine cross-sectional, two-way fixed effects, and first-difference specifications (FY 2010 to 2024). Error bars show 95% confidence intervals clustered by state (51 clusters).</figcaption>
</figure>

```python
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

# Within-state TWFE and three-stage covariance decomposition check
def decompose_three_stage_funnel(df_states: pd.DataFrame) -> dict:
    """Exact log-covariance shares for Y/S = (C/S) * (I/C) * (Y/I)."""
    ln_s1 = np.log(df_states["cases"] / df_states["staff"])
    ln_s2 = np.log(df_states["indictments"] / df_states["cases"])
    ln_s3 = np.log(df_states["convictions"] / df_states["indictments"])
    ln_tot = np.log(df_states["convictions"] / df_states["staff"])
    var_tot = np.var(ln_tot, ddof=1)
    shares = {
        "stage1_intake": np.cov(ln_s1, ln_tot, ddof=1)[0, 1] / var_tot,
        "stage2_triage": np.cov(ln_s2, ln_tot, ddof=1)[0, 1] / var_tot,
        "stage3_adjudication": np.cov(ln_s3, ln_tot, ddof=1)[0, 1] / var_tot,
    }
    assert np.isclose(sum(shares.values()), 1.0, atol=1e-6)
    return shares
```

Across all nine models in Table 1, within-state expansions of capitated managed care show no detectable positive association with public enforcement output at state-year precision.

<div class="table-wrapper" tabindex="0" role="region" aria-label="Medicaid managed care penetration and MFCU enforcement productivity regressions">
<table>
  <caption><strong>Table 1.</strong> Medicaid Managed Care Penetration and MFCU Enforcement Productivity, FY 2010–2024</caption>
  <thead>
    <tr>
      <th scope="col">Specification &amp; Panel Window</th>
      <th scope="col">Outcome Measure</th>
      <th scope="col">State-Years (<em>N</em>)</th>
      <th scope="col">Mean Outcome</th>
      <th scope="col">MC Slope (Clustered SE)</th>
      <th scope="col">95% CI per +10 pp (<em>p</em>-Value)</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td><strong>1. Cross-Section OLS (2010–2015)</strong><span class="table-sub">Panel A: Enrollment Era</span></td>
      <td>Total convictions / staff</td>
      <td>300</td>
      <td>0.89</td>
      <td>-0.340<span class="table-sub">(0.307)</span></td>
      <td>[-10.2%, +2.9%]<span class="table-sub">p = 0.273</span></td>
    </tr>
    <tr>
      <td><strong>2. Cross-Section OLS (2016–2024)</strong><span class="table-sub">Panel A: Expenditure Era</span></td>
      <td>Total convictions / staff</td>
      <td>455</td>
      <td>0.80</td>
      <td>-0.330<span class="table-sub">(0.350)</span></td>
      <td>[-12.7%, +4.4%]<span class="table-sub">p = 0.346</span></td>
    </tr>
    <tr>
      <td><strong>3. Two-Way Fixed Effects (2010–2024)</strong><span class="table-sub">Panel A: Harmonized Series</span></td>
      <td>Total convictions / staff</td>
      <td>755</td>
      <td>0.84</td>
      <td>-0.280<span class="table-sub">(0.194)</span></td>
      <td>[-7.9%, +1.2%]<span class="table-sub">p = 0.152</span></td>
    </tr>
    <tr>
      <td><strong>4. First Differences (2017–2024)</strong><span class="table-sub">Panel A: Annual Changes</span></td>
      <td>&Delta; Total convictions / staff</td>
      <td>405</td>
      <td>0.80</td>
      <td>-0.340<span class="table-sub">(0.342)</span></td>
      <td>[-12.0%, +3.9%]<span class="table-sub">p = 0.320</span></td>
    </tr>

    <tr>
      <td><strong>5. Two-Way FE: Comprehensive MCO</strong><span class="table-sub">Panel B: Uniform CMS (2016–2024)</span></td>
      <td>Total convictions / staff</td>
      <td>443</td>
      <td>0.81</td>
      <td>-0.007<span class="table-sub">(0.311)</span></td>
      <td>[-7.7%, +7.5%]<span class="table-sub">p = 0.981</span></td>
    </tr>
    <tr>
      <td><strong>6. First Differences: Comprehensive MCO</strong><span class="table-sub">Panel B: Uniform CMS (2017–2024)</span></td>
      <td>&Delta; Total convictions / staff</td>
      <td>392</td>
      <td>0.80</td>
      <td>+0.290<span class="table-sub">(0.342)</span></td>
      <td>[-4.8%, +12.0%]<span class="table-sub">p = 0.401</span></td>
    </tr>
    <tr>
      <td><strong>7. Two-Way FE: Fraud Convictions Only</strong><span class="table-sub">Panel B: Uniform CMS (2016–2024)</span></td>
      <td>Fraud convictions / staff</td>
      <td>443</td>
      <td>0.55</td>
      <td>-0.031<span class="table-sub">(0.189)</span></td>
      <td>[-7.3%, +6.1%]<span class="table-sub">p = 0.870</span></td>
    </tr>
    <tr>
      <td><strong>8. Two-Way FE: Fraud Case Intake</strong><span class="table-sub">Panel B: Uniform CMS (2016–2024)</span></td>
      <td>Fraud cases opened / staff</td>
      <td>443</td>
      <td>10.09</td>
      <td>+1.319<span class="table-sub">(2.310)</span></td>
      <td>[-3.2%, +5.8%]<span class="table-sub">p = 0.571</span></td>
    </tr>
    <tr>
      <td><strong>9. Two-Way FE: Any Managed Care Share</strong><span class="table-sub">Panel B: Uniform CMS (2016–2024)</span></td>
      <td>Total convictions / staff</td>
      <td>451</td>
      <td>0.80</td>
      <td>-0.569<span class="table-sub">(0.525)</span></td>
      <td>[-20.0%, +5.7%]<span class="table-sub">p = 0.283</span></td>
    </tr>
  </tbody>
</table>
</div>

In Panel A, cross-sectional regressions return negative, imprecise slopes during both the 2010 to 2015 enrollment era (-0.340, *p* = 0.273) and the 2016 to 2024 expenditure era (-0.330, *p* = 0.346). Including state and fiscal-year fixed effects across all 755 state-years yields a slope of -0.280 (SE = 0.194, *p* = 0.152). For a 10 percentage-point expansion in managed care share, the 95% confidence interval spans -7.9% to +1.2% of the sample mean (0.84 convictions per staff-year), ruling out productivity gains above 1.2%.

In Panel B, using the uniform 2016 to 2024 comprehensive MCO enrollment series (*N* = 443) removes the 2015/2016 reporting break. The baseline TWFE slope on comprehensive MCO share is -0.007 (SE = 0.311, *p* = 0.981), with a 95% confidence interval of -7.7% to +7.5% of the mean per 10 percentage-point increase. When we isolate fraud-only convictions per staff-year (Row 7), the slope is -0.031 (SE = 0.189, *p* = 0.870, 95% CI [-7.3%, +6.1%]). Upstream fraud case openings per staff-year (Row 8) also show no measurable shift (+1.319, SE = 2.310, *p* = 0.571, 95% CI [-3.2%, +5.8%]).


## Decomposing the Cross-State Productivity Funnel

Where along the enforcement pipeline do cross-state differences in convictions per staff member arise? We can locate that dispersion by applying the three-stage log-variance accounting identity to state-pooled totals over FY 2010 to 2024 across the 50 continuously operating units (Figure 2 and Table 2). Because North Dakota opened its unit in FY 2020 and recorded 3 convictions and 12 indictments over five years, its small denominator widens the national max/min ratio from 17.9x to 45.9x; Table 2 reports the 50-unit baseline alongside the 51-unit sensitivity in parentheses.

<figure>
  <img src="/images/health-policy/medicaid-managed-care-fraud-triage/figure2_three_stage_variance_decomposition.webp" width="1260" height="720" loading="lazy" decoding="async" alt="Horizontal grouped bar chart showing the share of cross-state log variance in convictions per staff-year attributable to Stage 1 case intake, Stage 2 investigative triage, and Stage 3 courtroom adjudication.">
  <figcaption>Exact log-variance decomposition of state MFCU convictions per staff-year across Stage 1 case intake (C/S), Stage 2 investigative triage (I/C), and Stage 3 courtroom adjudication (Y/I), FY 2010 to 2024 (50 continuously operating jurisdictions).</figcaption>
</figure>

Moving backward from courtroom verdicts to initial intake reveals a clear accounting split across the three pipeline stages.

1. **Stage 3 Courtroom Adjudication Is Uniformly High (0.0% of Variance):** Across the 50 continuously operating units, convictions per indictment (*Y* / *I*) show a narrow 2.2x range and a coefficient of variation (CV) of 0.15. Stage 3 accounts for 0.0% of the cross-state log variance in total convictions per staff-year (*r* = -0.04, *p* = 0.781) and -3.2% for fraud-only convictions (*r* = -0.18, *p* = 0.201). Once a state unit secures an indictment, conviction rates cluster tightly between 0.75 and 0.95 in 32 of the 50 jurisdictions.

2. **Stage 1 Case Intake Plays a Secondary Role (24.6% of Variance):** Opened cases per staff-year (*C* / *S*) vary 12.2-fold across states (CV = 0.54) and account for 24.6% of total log variance (*r* = +0.37, *p* = 0.008). For fraud-only cases (*C*<sub>*F*</sub> / *S*), intake varies 13.0-fold and accounts for 19.0% of cross-state log variance (*r* = +0.20, *p* = 0.162).

3. **Stage 2 Investigative Triage Accounts for Three-Quarters of Variance (75.4% to 84.2%):** Indictments per opened case (*I* / *C*) vary 28.2-fold across all enforcement actions (CV = 0.72) and account for 75.4% of the cross-state log variance in total convictions per staff-year (*r* = +0.58, *p* &lt; 0.001; 67.8% with North Dakota included). When we restrict the funnel to fraud-only actions in Panel B, fraud indictments per fraud case (*I*<sub>*F*</sub> / *C*<sub>*F*</sub>) vary 57.1-fold (CV = 0.81) and account for 84.2% of the cross-state log variance in fraud convictions per staff-year (*r* = +0.73, *p* &lt; 0.001).

<div class="table-wrapper" tabindex="0" role="region" aria-label="Three-stage multiplicative log-variance decomposition of state MFCU productivity">
<table>
  <caption><strong>Table 2.</strong> Three-Stage Multiplicative Log-Variance Decomposition of State MFCU Productivity, FY 2010–2024</caption>
  <thead>
    <tr>
      <th scope="col">Pipeline Stage &amp; Panel</th>
      <th scope="col">Operational Ratio</th>
      <th scope="col">Max / Min Ratio</th>
      <th scope="col">Coeff. of Variation (CV)</th>
      <th scope="col">Log-Variance Share</th>
      <th scope="col">Correlation with ln(Y/S)</th>
    </tr>
  </thead>

  <tbody>
    <tr>
      <td><strong>Stage 1: Case Intake</strong><span class="table-sub">Panel A: All Actions (50 Units; 51 in parens)</span></td>
      <td>Cases opened / staff (<em>C/S</em>)</td>
      <td>12.2x<span class="table-sub">(12.2x)</span></td>
      <td>0.54<span class="table-sub">(0.53)</span></td>
      <td>24.6%<span class="table-sub">(20.7%)</span></td>
      <td>r = +0.37<span class="table-sub">p = 0.008</span></td>
    </tr>
    <tr>
      <td><strong>Stage 2: Investigative Triage</strong><span class="table-sub">Panel A: All Actions (50 Units; 51 in parens)</span></td>
      <td>Indictments / case (<em>I/C</em>)</td>
      <td>28.2x<span class="table-sub">(28.2x)</span></td>
      <td>0.72<span class="table-sub">(0.72)</span></td>
      <td>75.4%<span class="table-sub">(67.8%)</span></td>
      <td>r = +0.58<span class="table-sub">p &lt; 0.001</span></td>
    </tr>
    <tr>
      <td><strong>Stage 3: Courtroom Adjudication</strong><span class="table-sub">Panel A: All Actions (50 Units; 51 in parens)</span></td>
      <td>Convictions / indictment (<em>Y/I</em>)</td>
      <td>2.2x<span class="table-sub">(5.2x)</span></td>
      <td>0.15<span class="table-sub">(0.18)</span></td>
      <td>0.0%<span class="table-sub">(11.5%)</span></td>
      <td>r = -0.04<span class="table-sub">p = 0.781</span></td>
    </tr>
    <tr>
      <td><strong>Combined Case Conversion</strong><span class="table-sub">Panel A: Stages 2 + 3 Combined</span></td>
      <td>Convictions / case (<em>Y/C</em>)</td>
      <td>21.7x<span class="table-sub">(31.4x)</span></td>
      <td>0.68<span class="table-sub">(0.70)</span></td>
      <td>75.4%<span class="table-sub">(79.3%)</span></td>
      <td>r = +0.59<span class="table-sub">p &lt; 0.001</span></td>
    </tr>

    <tr>
      <td><strong>Stage 1: Fraud Intake Only</strong><span class="table-sub">Panel B: Fraud Actions (50 Units)</span></td>
      <td>Fraud cases / staff (<em>C<sub>F</sub>/S</em>)</td>
      <td>13.0x</td>
      <td>0.59</td>
      <td>19.0%</td>
      <td>r = +0.20<span class="table-sub">p = 0.162</span></td>
    </tr>
    <tr>
      <td><strong>Stage 2: Fraud Triage Only</strong><span class="table-sub">Panel B: Fraud Actions (50 Units)</span></td>
      <td>Fraud indictments / case (<em>I<sub>F</sub>/C<sub>F</sub></em>)</td>
      <td>57.1x</td>
      <td>0.81</td>
      <td>84.2%</td>
      <td>r = +0.73<span class="table-sub">p &lt; 0.001</span></td>
    </tr>
    <tr>
      <td><strong>Stage 3: Fraud Adjudication Only</strong><span class="table-sub">Panel B: Fraud Actions (50 Units)</span></td>
      <td>Fraud convictions / indictment (<em>Y<sub>F</sub>/I<sub>F</sub></em>)</td>
      <td>2.4x</td>
      <td>0.16</td>
      <td>-3.2%</td>
      <td>r = -0.18<span class="table-sub">p = 0.201</span></td>
    </tr>
    <tr>
      <td><strong>Total Fraud Productivity</strong><span class="table-sub">Panel B: Full Fraud Pipeline (50 Units)</span></td>
      <td>Fraud convictions / staff (<em>Y<sub>F</sub>/S</em>)</td>
      <td>13.1x</td>
      <td>0.77</td>
      <td>100.0%</td>
      <td>r = +1.00<span class="table-sub">Reference</span></td>
    </tr>
  </tbody>
</table>
</div>


## Synthesis: What We Know, What We Cannot Prove, and Policy Design

### What We Know From the Panel and Funnel Data

Combining the within-state panel regressions with the three-stage decomposition shows what aggregate state data can and cannot establish. Within states, expanding comprehensive MCO enrollment shows no detectable association with total convictions per staff-year (slope = -0.007, 95% CI [-7.7%, +7.5%], *p* = 0.981) or fraud-only convictions per staff-year (slope = -0.031, 95% CI [-7.3%, +6.1%], *p* = 0.870) at the panel's precision. Across states, Stage 2 investigative triage (indictments per opened case) accounts for 75.4% to 84.2% of the log variance in conviction output.

Federal audit records point to a candidate mechanism consistent with this Stage 2 dispersion. In the OIG's FY 2024 annual report, reviewed MCO referrals rose from 2,971 in FY 2021 to 4,650 in FY 2024, yet state MFCUs opened formal cases on only 23% (1,078 of 4,650) of those referrals.<sup><a href="#ref-4">4</a></sup> A 2025 OIG evaluation similarly found that 10% of surveyed Medicaid plans (covering 1.6 million enrollees and 8 billion dollars in payments across 13 states) sent zero fraud referrals in 2022, while more than half of referring plans sent two or fewer referrals per 10,000 enrollees.<sup><a href="#ref-6">6</a></sup> If plans recover routine overpayments internally under 42 C.F.R. Section 438.608(d) or send thin leads that lack proof of criminal intent, state units will face uneven intake at Stage 1 and high triage attrition at Stage 2.<sup><a href="#ref-10">10</a></sup> Moreover, as of November 2024, 28 of 53 MFCUs lacked federal approval to conduct independent data mining under 42 C.F.R. Section 1007.20, leaving them reliant on outside referrals.<sup><a href="#ref-4">4</a></sup>

### What the State-Year Panel Cannot Prove

Five methodological limits govern how we read these findings.

1. **Observational State Timing and Statistical Precision:** Because state managed care expansions do not occur at random, fixed-effects and first-difference slopes capture conditional within-state associations rather than causal shocks.<sup><a href="#ref-13" id="fnref-13">13</a></sup> In addition, while the 15-year TWFE confidence interval rules out gains above +1.2% per 10 percentage-point rise (and the 2016 to 2024 TWFE rules out gains above +6.1% to +7.5%), smaller positive or negative effects remain inside the confidence bounds.

2. **Descriptive Accounting Identity vs. Causal Mechanism:** The covariance shares of 75.4% and 84.2% describe where cross-state variance sits along the enforcement funnel. They do not prove that thin MCO referrals caused that dispersion or identify the marginal effect of adding staff without an exogenous staffing or contract shock.

3. **Prosecuted Output vs. Underlying Fraud:** Administrative records measure prosecuted cases rather than unobserved billing fraud.<sup><a href="#ref-9">9</a></sup> If managed care plans blocked fraud on the front end while prosecutors held output steady, a regression slope could also sit near zero. However, federal Payment Error Rate Measurement (PERM) audits review state capitation payments rather than provider-level managed care claims, and OIG audits document widespread zero-referral plans, so near-zero conviction slopes do not prove lower underlying fraud.<sup><a href="#ref-6">6</a>, <a href="#ref-14" id="fnref-14">14</a></sup>

4. **Short-Run First-Difference Precision:** Annual first-difference confidence intervals (-4.8% to +12.0% per 10 percentage-point MCO expansion) are wider than the within-state TWFE bounds, leaving room for modest short-run swings.

5. **Annual Flow Ratios:** Because OIG statistical tables report annual counts rather than individual case cohorts, Stage 3 ratios compare convictions and indictments recorded in the same fiscal year. Pooling 15 years of state totals smooths out year-to-year cohort timing noise.

### Policy Proposals for Medicaid Program Integrity

Because the descriptive variation sits in Stage 1 intake and Stage 2 triage, states can test three policy proposals.

1. **Proposal 1 — Standardize MCO Referral Contracts and Evidentiary Floors:** CMS and state Medicaid agencies can standardize contract definitions of reportable fraud under 42 C.F.R. Section 438.608(a)(7), set uniform reporting deadlines, and test whether requiring plan SIUs to attach billing and clinical records improves Stage 2 case-to-indictment conversion.<sup><a href="#ref-10">10</a>, <a href="#ref-14">14</a></sup>

2. **Proposal 2 — Mandate Encounter Visibility and Independent Data Mining:** States can require near-real-time submission of both paid and denied MCO encounter claims to state data warehouses and expand federal data-mining approvals under 42 C.F.R. Section 1007.20 so MFCUs can screen across plans on their own.<sup><a href="#ref-4">4</a></sup>

3. **Proposal 3 — Test Stage 2 Forensic and Investigative Staffing:** Using the 75% federal MFCU matching rate to hire forensic auditors and investigators offers a testable way to evaluate whether expanding Stage 2 triage capacity raises indictment conversion in low-conversion units.<sup><a href="#ref-8">8</a>, <a href="#ref-12">12</a></sup>


## References

<ol class="references">
<li id="ref-1">Centers for Medicare &amp; Medicaid Services. (2024). <em>Medicaid Managed Care Enrollment and Program Characteristics, 2022–2024</em>. Baltimore, MD: U.S. Department of Health and Human Services. <a href="#fnref-1" class="footnote-backref">&uarr;</a></li>
<li id="ref-2">Medicaid and CHIP Payment and Access Commission (MACPAC). (2022). <em>MACStats: Medicaid and CHIP Data Book</em>. Washington, DC: MACPAC. <a href="#fnref-2" class="footnote-backref">&uarr;</a></li>
<li id="ref-3">Sanchez, M., Miller, B., &amp; DiGiorgio, L. (2026). Improving Medicaid program integrity through managed care. <em>Health Affairs Forefront</em>, October 5, 2026. <a href="#fnref-3" class="footnote-backref">&uarr;</a></li>
<li id="ref-4">Office of Inspector General. (2025). <em>Medicaid Fraud Control Units Fiscal Year 2024 Annual Report</em> (OEI-09-25-00090). Washington, DC: U.S. Department of Health and Human Services. <a href="#fnref-4" class="footnote-backref">&uarr;</a></li>
<li id="ref-5">Cholette, V. (2026). <em>Privatizing Program Integrity? Managed Care Penetration and Medicaid Fraud Enforcement</em>. SSRN Working Paper No. 7710301. <a href="https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7710301" target="_blank" rel="noopener">https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7710301</a> <a href="#fnref-5" class="footnote-backref">&uarr;</a></li>
<li id="ref-6">Office of Inspector General. (2025). <em>Some Medicaid Managed Care Plans Made Few or No Fraud Referrals</em> (OEI-03-22-00410). Washington, DC: U.S. Department of Health and Human Services. <a href="#fnref-6" class="footnote-backref">&uarr;</a></li>
<li id="ref-7">Office of Inspector General. (2024). <em>Medicaid Fraud Control Units Encounter Challenges Overseeing Managed Care Fraud</em> (OEI-03-23-00340). Washington, DC: U.S. Department of Health and Human Services. <a href="#fnref-7" class="footnote-backref">&uarr;</a></li>

<li id="ref-8">Perez, V., &amp; Wing, C. (2019). Should we spend more on policing Medicaid fraud? Evidence from the Medicaid Fraud Control Units. <em>American Journal of Health Economics</em>, 5(4), 481–508. <a href="https://doi.org/10.1162/ajhe_a_00130" target="_blank" rel="noopener">doi:10.1162/ajhe_a_00130</a> <a href="#fnref-8" class="footnote-backref">&uarr;</a></li>
<li id="ref-9">Nguyen, H., &amp; Perez, V. (2020). Privatizing plaintiffs: How Medicaid fraud litigation responds to decentralized whistleblowers. <em>Journal of Health Economics</em>, 74, 102378. <a href="https://doi.org/10.1016/j.jhealeco.2020.102378" target="_blank" rel="noopener">doi:10.1016/j.jhealeco.2020.102378</a> <a href="#fnref-9" class="footnote-backref">&uarr;</a></li>
<li id="ref-10">Office of Inspector General. (2026). <em>States Require Managed Care Plans To Refer Suspected Fraud, But Oversight Gaps Remain</em> (OEI-03-23-00341). Washington, DC: U.S. Department of Health and Human Services. <a href="#fnref-10" class="footnote-backref">&uarr;</a></li>
<li id="ref-11">Office of Inspector General. (2024). <em>CMS Oversight of State-Submitted Medicaid Managed Care Medical Loss Ratio Data</em> (OEI-03-22-00100). Washington, DC: U.S. Department of Health and Human Services. <a href="#fnref-11" class="footnote-backref">&uarr;</a></li>
<li id="ref-12">Perez, V., &amp; Ramos, M. (2023). Finding fraud in health insurance: Does the Affordable Care Act matter? <em>Journal of Policy Analysis and Management</em>, 42(3), 754–781. <a href="https://doi.org/10.1002/pam.22481" target="_blank" rel="noopener">doi:10.1002/pam.22481</a> <a href="#fnref-12" class="footnote-backref">&uarr;</a></li>
<li id="ref-13">de Chaisemartin, C., &amp; D'Haultf&oelig;uille, X. (2020). Two-way fixed effects estimators with heterogeneous treatment effects. <em>American Economic Review</em>, 110(9), 2964–2996. <a href="https://doi.org/10.1257/aer.20181169" target="_blank" rel="noopener">doi:10.1257/aer.20181169</a> <a href="#fnref-13" class="footnote-backref">&uarr;</a></li>
<li id="ref-14">U.S. Government Accountability Office. (2025). <em>Medicaid: Actions Needed to Strengthen Program Integrity and Address Managed Care Risks</em> (GAO-25-107770). Washington, DC: GAO. <a href="#fnref-14" class="footnote-backref">&uarr;</a></li>
</ol>
