import json
from typing import Dict, Any
from src.delta.comparator import DeltaResult

class DeltaReportGenerator:
    """Generates multi-format delta reports and executive AI summaries."""

    def __init__(self, delta_result: DeltaResult):
        self.result = delta_result

    def generate_ai_summary(self) -> str:
        s = self.result.summary
        items = [i for i in self.result.items if i.change_type != "Unchanged"]
        
        # Categorize by object type
        valves_rem = [i for i in items if i.object_type == "Valve" and i.change_type == "Removed"]
        valves_mod = [i for i in items if i.object_type == "Valve" and i.change_type == "Modified"]
        inst_mod = [i for i in items if i.object_type == "Instrument" and i.change_type == "Modified"]
        equip_mod = [i for i in items if i.object_type == "Equipment" and i.change_type == "Modified"]

        lines = [
            "**AI Change Executive Summary**",
            f"• **{s['total_changes']} total changes** detected across document revisions.",
            f"• **{s['added']} items added**, **{s['removed']} items removed**, and **{s['modified']} items modified**.",
        ]
        
        if valves_rem:
            lines.append(f"• **{len(valves_rem)} valves removed** (e.g. {', '.join(v.tag or v.text_a or '' for v in valves_rem[:3])}).")
        if inst_mod:
            lines.append(f"• **{len(inst_mod)} instruments modified** (e.g. {', '.join(i.tag or i.text_b or '' for i in inst_mod[:3])}).")
        if equip_mod:
            lines.append(f"• **{len(equip_mod)} equipment items modified**.")
            
        lines.append(f"• **Overall Delta Detection Confidence:** {int(self.result.overall_confidence * 100)}%")
        return "\n".join(lines)

    def to_json(self) -> str:
        return self.result.model_dump_json(indent=2)

    def to_markdown(self) -> str:
        s = self.result.summary
        lines = [
            "# DeltaDoc AI - Engineering Document Delta Report",
            "",
            self.generate_ai_summary(),
            "",
            "## Summary Matrix",
            "| Metric | Count |",
            "| :--- | :--- |",
            f"| Total Changes | {s['total_changes']} |",
            f"| Added Elements | {s['added']} |",
            f"| Removed Elements | {s['removed']} |",
            f"| Modified Elements | {s['modified']} |",
            f"| Unchanged Elements | {s['unchanged']} |",
            f"| Confidence Score | {int(self.result.overall_confidence * 100)}% |",
            "",
            "## Detailed Delta Items",
            "",
            "| Status | Type | Tag / Identifier | Description | Page (A -> B) | Confidence |",
            "| :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        for item in self.result.items:
            if item.change_type == "Unchanged":
                continue
            pg_str = f"Page {item.page_a or '-'}" if item.page_a == item.page_b or not item.page_b else f"P{item.page_a or '-'} -> P{item.page_b or '-'}"
            tag_str = item.tag or "-"
            badge = f"**[{item.change_type.upper()}]**"
            lines.append(f"| {badge} | {item.object_type} | `{tag_str}` | {item.description} | {pg_str} | {int(item.confidence * 100)}% |")

        return "\n".join(lines)

    def to_html(self) -> str:
        md = self.to_markdown()
        # Clean HTML styled document
        items_html = ""
        for item in self.result.items:
            if item.change_type == "Unchanged":
                continue
            color = "#22c55e" if item.change_type == "Added" else "#ef4444" if item.change_type == "Removed" else "#eab308"
            items_html += f"""
            <tr style="border-bottom: 1px solid #374151;">
                <td style="padding: 12px;"><span style="background: {color}20; color: {color}; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;">{item.change_type}</span></td>
                <td style="padding: 12px; color: #e5e7eb;">{item.object_type}</td>
                <td style="padding: 12px; font-family: monospace; color: #60a5fa;">{item.tag or '-'}</td>
                <td style="padding: 12px; color: #9ca3af;">{item.description}</td>
                <td style="padding: 12px; color: #9ca3af;">Page {item.page_a or item.page_b or 1}</td>
                <td style="padding: 12px; color: #10b981;">{int(item.confidence * 100)}%</td>
            </tr>
            """

        ai_summary_html = self.generate_ai_summary().replace("\n", "<br/>").replace("**", "<b>").replace("</b>", "</b>")

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8"/>
            <title>DeltaDoc AI Report</title>
            <style>
                body {{ font-family: system-ui, -apple-system, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 32px; }}
                .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 24px; margin-bottom: 24px; }}
                table {{ width: 100%; border-collapse: collapse; text-align: left; }}
                th {{ padding: 12px; border-bottom: 2px solid #475569; color: #94a3b8; }}
            </style>
        </head>
        <body>
            <h1 style="color: #38bdf8;">DeltaDoc AI - Engineering Delta Report</h1>
            <div class="card">
                <div style="color: #e2e8f0; font-size: 15px; line-height: 1.6;">
                    {ai_summary_html}
                </div>
            </div>
            <div class="card">
                <h2>Detailed Changes</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Status</th>
                            <th>Type</th>
                            <th>Tag</th>
                            <th>Description</th>
                            <th>Page</th>
                            <th>Confidence</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """
