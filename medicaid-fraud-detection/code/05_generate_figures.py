"""
Regenerate paper figures with publication-quality formatting.
Uses stored results JSON files and data parquets — does NOT require re-running
the full pipeline.

Figures regenerated:
  - Figure 1: Billing Feature Distributions (from figure1_data.parquet)
  - Figure 3: PR and ROC Curves (requires phase3 pipeline re-run — SKIPPED)
  - Figure 4: SHAP Feature Importance (from phase3_results.json)
  - Figure 5: Cost-Benefit Frontier (from phase5_policy_results.json)
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np
import pandas as pd

FRAUD = "/Users/victoriaperez/Library/CloudStorage/GoogleDrive-victoriaeperez@gmail.com/My Drive/Projects/Mcaid/05_fraud_detection"

# Publication settings
plt.rcParams.update({
    'font.size': 14,
    'axes.labelsize': 16,
    'axes.titlesize': 18,
    'xtick.labelsize': 13,
    'ytick.labelsize': 13,
    'legend.fontsize': 13,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'font.family': 'serif',
})

# ============================================================
# Label mapping for SHAP features
# ============================================================
FEATURE_LABELS = {
    'entity_type_enc': 'Entity Type (Individual=1)',
    'months_active': 'Months Active',
    'claims_per_month': 'Claims per Month',
    'z_cpm': 'Claims/Month (Peer Z-Score)',
    'billing_gap_ratio': 'Billing Gap Ratio',
    'avg_monthly_paid': 'Avg. Monthly Payment',
    'claims_per_beneficiary': 'Claims per Beneficiary',
    'monthly_spending_volatility': 'Monthly Spending Volatility',
    'total_paid': 'Total Paid',
    'total_beneficiaries': 'Total Beneficiaries',
    'z_paid': 'Total Paid (Peer Z-Score)',
    'avg_paid_per_beneficiary': 'Avg. Paid per Beneficiary',
    'max_single_month_paid': 'Max Single-Month Payment',
    'z_ppb': 'Paid/Beneficiary (Peer Z-Score)',
    'avg_paid_per_claim': 'Avg. Paid per Claim',
    'cv_monthly_paid': 'CV of Monthly Payment',
    'total_claims': 'Total Claims',
    'z_entropy': 'Code Entropy (Peer Z-Score)',
    'hcpcs_entropy': 'HCPCS Code Entropy',
    'share_em_codes': 'E&M Code Share',
    'telehealth_share': 'Telehealth Share',
    'hcpcs_hhi': 'HCPCS Concentration (HHI)',
    'share_top_code': 'Top Code Share',
    'unique_hcpcs': 'Unique HCPCS Codes',
    'rbcs_category_diversity': 'Service Category Diversity',
    'share_high_reimburse': 'High-Reimbursement Share',
}


def regenerate_figure1_distributions():
    """Figure 1: Billing Feature Distributions — Excluded vs. Non-Excluded."""
    df = pd.read_parquet(f'{FRAUD}/figure1_data.parquet')

    excluded = df[df['is_excluded'] == True]
    non_excluded = df[df['is_excluded'] == False]

    features = [
        ('total_paid', 'Total Paid ($)', True),
        ('total_claims', 'Total Claims', True),
        ('unique_hcpcs', 'Unique HCPCS Codes', True),
        ('monthly_spending_volatility', 'Monthly Spending\nVolatility ($)', True),
        ('hcpcs_hhi', 'HCPCS Concentration\n(HHI)', False),
        ('months_active', 'Months Active', False),
    ]

    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes = axes.flatten()

    for i, (col, label, use_log) in enumerate(features):
        ax = axes[i]
        data_ne = non_excluded[col].dropna()
        data_ex = excluded[col].dropna()

        if use_log:
            data_ne = np.log10(data_ne.clip(lower=1))
            data_ex = np.log10(data_ex.clip(lower=1))
            label += '\n(log$_{10}$ scale)'

        parts_ne = ax.violinplot([data_ne], positions=[0], showmedians=True,
                                  showextrema=False)
        parts_ex = ax.violinplot([data_ex], positions=[1], showmedians=True,
                                  showextrema=False)

        for pc in parts_ne['bodies']:
            pc.set_facecolor('#b0b0b0')
            pc.set_alpha(0.7)
        parts_ne['cmedians'].set_color('black')

        for pc in parts_ex['bodies']:
            pc.set_facecolor('#D4652F')
            pc.set_alpha(0.7)
        parts_ex['cmedians'].set_color('black')

        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Non-Excluded', 'Excluded'], fontsize=13)
        ax.set_title(label, fontsize=14)
        ax.grid(True, alpha=0.2, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

    n_ex = len(excluded)
    n_ne = len(non_excluded)
    fig.suptitle('Figure 1: Billing Feature Distributions \u2014 Excluded vs. Non-Excluded Providers',
                 fontsize=18, y=1.02)
    fig.text(0.5, -0.02,
             f'Excluded N={n_ex:,} | Non-Excluded N={n_ne:,} (sampled)',
             ha='center', fontsize=13, color='#666666')

    plt.tight_layout()
    fig.savefig(f'{FRAUD}/figure1_distributions.png')
    print(f"Saved figure1_distributions.png (N_ex={n_ex}, N_ne={n_ne})")
    plt.close()


def regenerate_figure4_shap():
    """Figure 4: SHAP Feature Importance with readable labels."""
    with open(f'{FRAUD}/phase3_results.json') as f:
        data = json.load(f)

    shap_data = data['table7_shap'][:15]  # top 15

    names = [FEATURE_LABELS.get(d['feature'], d['feature']) for d in shap_data][::-1]
    vals = [d['mean_abs_shap'] for d in shap_data][::-1]
    dirs = [d['direction'] for d in shap_data][::-1]

    colors = ['#D4652F' if d == 'Higher->Fraud' else '#008080' for d in dirs]

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(range(len(names)), vals, color=colors, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=13)
    ax.set_xlabel('Mean |SHAP Value|', fontsize=16)
    ax.set_title('SHAP Feature Importance: Random Forest\n(Fraud-Only Labels, Specification A)', fontsize=17)

    legend_elements = [
        Patch(facecolor='#D4652F', label='Higher Value → Predicts Fraud'),
        Patch(facecolor='#008080', label='Lower Value → Predicts Fraud'),
    ]
    ax.legend(handles=legend_elements, fontsize=13, loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    fig.savefig(f'{FRAUD}/figure4_shap_fraud.png')
    print(f"Saved figure4_shap_fraud.png ({len(names)} features)")
    plt.close()


def regenerate_figure5_cost_benefit():
    """Figure 5: Cost-Benefit Frontier."""
    with open(f'{FRAUD}/phase5_policy_results.json') as f:
        data = json.load(f)

    cb = data['cost_benefit']
    thres_x = [d['threshold_pct'] for d in cb]
    prec_y = [d['precision'] for d in cb]
    roi_y = [d['roi'] for d in cb]
    base_rate = 230 / (230 + 488030 - 230)  # approximate

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # (a) Detection Precision
    ax1.plot(thres_x, prec_y, 'o-', color='#2c3e50', linewidth=2.5, markersize=10)
    ax1.axhline(y=base_rate, color='#95a5a6', linestyle='--', linewidth=1.5,
                label=f'Base rate ({base_rate:.4f})')
    ax1.set_xlabel('Screening Threshold (%)', fontsize=16)
    ax1.set_ylabel('Precision', fontsize=16)
    ax1.set_title('(a) Detection Precision by Threshold', fontsize=17)
    ax1.legend(fontsize=13)
    ax1.grid(True, alpha=0.3)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # (b) Expected ROI
    color_roi = ['#27ae60' if r > 3.5 else '#f39c12' if r > 1 else '#e74c3c' for r in roi_y]
    bars = ax2.bar(range(len(thres_x)), roi_y, color=color_roi, alpha=0.85,
                   edgecolor='#2c3e50', linewidth=0.8)
    ax2.axhline(y=3.5, color='#333333', linestyle='--', linewidth=1.5,
                label='MFCU baseline (3.5\u00d7)')
    ax2.axhline(y=1.0, color='#e74c3c', linestyle=':', linewidth=1.5,
                label='Break-even (1.0\u00d7)')
    ax2.set_xticks(range(len(thres_x)))
    ax2.set_xticklabels([f'{t}%' for t in thres_x], fontsize=13)
    ax2.set_xlabel('Screening Threshold', fontsize=16)
    ax2.set_ylabel('Expected ROI (\u00d7)', fontsize=16)
    ax2.set_title('(b) Expected ROI by Threshold', fontsize=17)
    ax2.legend(fontsize=13, loc='upper right')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    for bar, roi_val in zip(bars, roi_y):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 f'{roi_val:.1f}\u00d7', ha='center', va='bottom', fontsize=12, fontweight='bold')

    plt.tight_layout(w_pad=3)
    fig.savefig(f'{FRAUD}/figure5_cost_benefit.png')
    print(f"Saved figure5_cost_benefit.png ({len(cb)} thresholds)")
    plt.close()


if __name__ == '__main__':
    print("Regenerating figures with publication-quality formatting...")
    print("=" * 60)

    regenerate_figure1_distributions()
    regenerate_figure4_shap()
    regenerate_figure5_cost_benefit()

    print("=" * 60)
    print("Done. Figures 1, 4, and 5 regenerated at 300 DPI.")
    print()
    print("NOTE: Figure 3 (PR/ROC curves) requires raw model predictions")
    print("which are not stored in the results JSON. To regenerate, re-run:")
    print("  phase3_classifiers_v2.py (font sizes already updated)")
