

import re
import sqlite3

SQL_FILE = "04_sql_queries.sql"
DB_PATH = "ecommerce.db"
OUT_PATH = "reports/sql_query_results.txt"
MAX_ROWS_SHOWN = 15


def split_statements_with_titles(sql_text):
    """Very small parser: splits the file on ';' and grabs the nearest
    preceding '-- N. Title' comment line as a label for each statement."""
    lines = sql_text.splitlines()
    blocks = []
    current_lines = []
    current_title = None
    title_pattern = re.compile(r"^--\s*(\d+\..*)")

    for line in lines:
        m = title_pattern.match(line.strip())
        if m:
            current_title = m.group(1).strip()
        if line.strip().startswith("--"):
            continue
        current_lines.append(line)
        if ";" in line:
            stmt = "\n".join(current_lines).strip()
            stmt = stmt.rstrip(";").strip()
            if stmt:
                blocks.append((current_title, stmt))
            current_lines = []
    return blocks


def main():
    with open(SQL_FILE) as f:
        sql_text = f.read()

    statements = split_statements_with_titles(sql_text)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    out_lines = []
    out_lines.append("E-COMMERCE SQL ANALYSIS - QUERY RESULTS")
    out_lines.append("(each query's output truncated to first "
                      f"{MAX_ROWS_SHOWN} rows for readability)")
    out_lines.append("=" * 78)

    for i, (title, stmt) in enumerate(statements, start=1):
        label = title if title else f"Query block {i}"
        out_lines.append(f"\n--- {label} ---")
        try:
            cur.execute(stmt)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()
            out_lines.append(" | ".join(cols))
            out_lines.append("-" * 78)
            for row in rows[:MAX_ROWS_SHOWN]:
                out_lines.append(" | ".join(str(v) for v in row))
            if len(rows) > MAX_ROWS_SHOWN:
                out_lines.append(f"... ({len(rows) - MAX_ROWS_SHOWN} more rows)")
            out_lines.append(f"[{len(rows)} total row(s)]")
        except Exception as e:
            out_lines.append(f"ERROR running this statement: {e}")

    conn.close()

    with open(OUT_PATH, "w") as f:
        f.write("\n".join(out_lines))

    print(f"Wrote {len(statements)} query results to {OUT_PATH}")


if __name__ == "__main__":
    main()
