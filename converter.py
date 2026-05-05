import pandas as pd


def dataframe_to_markdown(df: pd.DataFrame) -> tuple[str, str, int]:
    doc_col = df["document"].dropna()
    title = str(doc_col.iloc[0]).strip() if not doc_col.empty else "EU Legal Document"
    article_count = int(df["article"].nunique())

    lines: list[str] = [f"# {title}", ""]

    current_section: str | None = None
    current_article: str | None = None

    for _, row in df.iterrows():
        text = row.get("text")
        if not text or str(text).strip() == "":
            continue

        section = row.get("section")
        article = row.get("article")
        article_subtitle = row.get("article_subtitle")
        paragraph = row.get("paragraph")
        modifier = row.get("modifier")
        group = row.get("group")
        ref = row.get("ref") or []

        # Section header on change
        if pd.notna(section) and section and section != current_section:
            current_section = section
            lines.append(f"## {section}")
            lines.append("")

        # Article header on change
        if pd.notna(article) and article and article != current_article:
            current_article = article
            subtitle = (
                str(article_subtitle).rstrip("`").strip()
                if pd.notna(article_subtitle)
                else ""
            )
            header = f"### Article {article}"
            if subtitle:
                header += f" — {subtitle}"
            lines.append(header)
            lines.append("")

        # Skip signatories
        if modifier == "signatory":
            continue

        # Group title (bold, own line)
        if pd.notna(group) and group:
            lines.append(f"**{group}**")
            lines.append("")

        text = str(text).strip()

        if modifier == "note":
            lines.append(f"> {text}")
        elif ref:
            indent = "   " * len(ref)
            sub_point = ref[-1]
            lines.append(f"{indent}{sub_point} {text}")
        elif pd.notna(paragraph) and paragraph:
            lines.append(f"{paragraph}. {text}")
        else:
            lines.append(text)

    lines.append("")
    return "\n".join(lines), title, article_count
