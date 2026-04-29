APP_CSS = """
<style>
    .stApp {
        background:
            linear-gradient(180deg, #f8fafc 0%, #eef7ff 44%, #f8fafc 100%);
        color: #172033;
    }

    section[data-testid="stSidebar"] {
        display: none;
    }

    div[data-testid="stAppViewContainer"] {
        padding-left: 0;
    }

    div.stButton > button,
    div[data-testid="stLinkButton"] > a {
        opacity: 1 !important;
        visibility: visible !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #4f46e5 0%, #0891b2 100%) !important;
        border: 1px solid #4f46e5 !important;
        border-radius: 10px !important;
        font-weight: 850 !important;
        box-shadow: 0 10px 24px rgba(79, 70, 229, 0.18) !important;
    }

    div.stButton > button:hover,
    div[data-testid="stLinkButton"] > a:hover {
        color: #ffffff !important;
        border-color: #4338ca !important;
        transform: translateY(-1px);
    }

    div.stButton > button:focus,
    div[data-testid="stLinkButton"] > a:focus {
        color: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.24) !important;
    }

    h1, h2, h3 {
        color: #172033;
        letter-spacing: 0;
    }

    .command-bar {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 20px;
        padding: 10px 0 14px 0;
        border-bottom: 1px solid #dbeafe;
        margin-bottom: 12px;
    }

    .product-title {
        font-size: 31px;
        line-height: 1.08;
        font-weight: 850;
        color: #172033;
        margin: 0;
    }

    .product-subtitle {
        margin-top: 6px;
        color: #475569;
        font-size: 15px;
        line-height: 1.45;
    }

    .bar-actions {
        display: flex;
        justify-content: flex-end;
        flex-wrap: wrap;
        gap: 8px;
        max-width: 560px;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 7px 10px;
        border-radius: 999px;
        border: 1px solid #c7d2fe;
        background: rgba(255, 255, 255, 0.86);
        color: #3730a3;
        font-size: 13px;
        font-weight: 700;
        white-space: nowrap;
    }

    .pill-ok {
        border-color: #bae6fd;
        color: #0369a1;
        background: #f0f9ff;
    }

    .pill-warn {
        border-color: #fde68a;
        color: #92400e;
        background: #fffbeb;
    }

    .pill-error {
        border-color: #fecaca;
        color: #b91c1c;
        background: #fef2f2;
    }

    .pipeline-badge {
        display: inline-flex;
        padding: 7px 10px;
        border-radius: 999px;
        border: 1px solid #ddd6fe;
        background: #f5f3ff;
        color: #5b21b6;
        font-size: 13px;
        font-weight: 700;
        white-space: normal;
    }

    .filter-dock {
        border: 1px solid #dbeafe;
        background: rgba(255, 255, 255, 0.72);
        border-radius: 14px;
        padding: 14px;
        box-shadow: 0 18px 44px rgba(99, 102, 241, 0.07);
        margin-bottom: 16px;
    }

    .dock-title {
        color: #4f46e5;
        font-size: 12px;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }

    .chip-cloud {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 8px 0 4px 0;
    }

    .skill-chip {
        display: inline-flex;
        align-items: center;
        padding: 7px 10px;
        border-radius: 999px;
        border: 1px solid #c7d2fe;
        background: rgba(238, 242, 255, 0.9);
        color: #312e81;
        font-size: 13px;
        font-weight: 700;
    }

    .soft-panel {
        border: 1px solid #dbeafe;
        background: rgba(255, 255, 255, 0.7);
        border-radius: 14px;
        padding: 16px;
        min-height: 140px;
    }

    .role-profile-title {
        color: #4f46e5;
        font-size: 12px;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }

    .role-profile-value {
        color: #172033;
        font-size: 24px;
        font-weight: 850;
        line-height: 1.15;
        margin-bottom: 8px;
    }

    .panel-text {
        color: #475569;
        font-size: 14px;
        line-height: 1.5;
    }

    .ranked-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }

    .ranked-tile {
        border: 1px solid #dbeafe;
        background: #ffffff;
        border-radius: 14px;
        padding: 12px;
        min-height: 104px;
    }

    .ranked-tile-leader {
        border-color: #818cf8;
        background: linear-gradient(135deg, #eef2ff 0%, #ecfeff 100%);
    }

    .rank-label {
        color: #6366f1;
        font-size: 12px;
        font-weight: 850;
        margin-bottom: 5px;
    }

    .rank-name {
        color: #172033;
        font-size: 17px;
        font-weight: 850;
        margin-bottom: 7px;
    }

    .rank-meta {
        color: #475569;
        font-size: 13px;
        line-height: 1.35;
    }

    .insight-card {
        border-left: 4px solid #8b5cf6;
        background: #ffffff;
        border-radius: 12px;
        padding: 12px 14px;
        border-top: 1px solid #ede9fe;
        border-right: 1px solid #ede9fe;
        border-bottom: 1px solid #ede9fe;
    }

    .insight-title {
        color: #6d28d9;
        font-size: 12px;
        font-weight: 850;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .insight-value {
        color: #172033;
        font-size: 20px;
        font-weight: 850;
        margin-bottom: 5px;
    }

    .status {
        border-radius: 10px;
        padding: 10px 12px;
        margin: 8px 0;
        border: 1px solid;
        font-size: 14px;
        line-height: 1.45;
    }

    .status-ok {
        background: #ecfeff;
        color: #155e75;
        border-color: #a5f3fc;
    }

    .status-warn {
        background: #fffbeb;
        color: #92400e;
        border-color: #fde68a;
    }

    .status-error {
        background: #fef2f2;
        color: #b91c1c;
        border-color: #fecaca;
    }

    .command-list {
        display: grid;
        gap: 7px;
        margin-top: 10px;
    }

    .command-item {
        border: 1px solid #dbeafe;
        background: #ffffff;
        border-radius: 10px;
        padding: 9px 10px;
        color: #1e293b;
        font-size: 13px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    }

    .check-row {
        display: grid;
        grid-template-columns: 160px 170px 140px 1fr 70px;
        gap: 10px;
        padding: 10px 0;
        border-bottom: 1px solid #e0e7ff;
        align-items: center;
        font-size: 13px;
    }

    .check-head {
        color: #64748b;
        font-weight: 850;
        text-transform: uppercase;
        font-size: 11px;
    }

    @media (max-width: 900px) {
        .command-bar,
        .bar-actions {
            display: block;
        }

        .ranked-grid,
        .check-row {
            grid-template-columns: 1fr;
        }
    }
</style>
"""
