import re
from pathlib import Path

import pandas as pd


def analyse_item_length(df):
    required = ["id", "konto", "text", "skill", "branche"]

    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    for column in required:
        if df[column].isna().any():
            raise ValueError(f"Missing values in: {column}")

        if df[column].astype(str).str.strip().eq("").any():
            raise ValueError(f"Empty values in: {column}")

    if not df["text"].map(lambda value: isinstance(value, str)).all():
        raise ValueError("Every text must be a string.")

    result = df[required].copy()

    # Numbers count as words.
    # Hyphenated or apostrophised words stay together.
    word_pattern = r"[^\W_]+(?:[-'’][^\W_]+)*"

    result["word_count"] = result["text"].map(
        lambda text: len(re.findall(word_pattern, text))
    )

    # Includes spaces and punctuation.
    result["character_count"] = result["text"].str.len()

    def summarise(group_columns):
        return (
            result.groupby(group_columns)
            .agg(
                items=("word_count", "size"),
                mean_words=("word_count", "mean"),
                median_words=("word_count", "median"),
                min_words=("word_count", "min"),
                p25_words=("word_count", lambda x: x.quantile(0.25)),
                p75_words=("word_count", lambda x: x.quantile(0.75)),
                max_words=("word_count", "max"),
                mean_characters=("character_count", "mean"),
            )
            .round(1)
            .reset_index()
        )

    # Return a dictionary, so reports.items() works.
    return {
        "item_lengths": result,
        "length_by_skill": summarise(["skill"]),
        "length_by_skill_and_branche": summarise(
            ["skill", "branche"]
        ),
        "length_by_branche": summarise(["branche"]),
    }


# Read the Excel file.
df = pd.read_excel(
    "real_testset_300.xlsx",
    sheet_name="Testfälle",
)
# Run the analysis.
reports = analyse_item_length(df)

# Save all four reports.
output_dir = Path("outputs_word_length")
output_dir.mkdir(parents=True, exist_ok=True)

for name, report in reports.items():
    report.to_csv(
        output_dir / f"{name}.csv",
        index=False,
        encoding="utf-8-sig",
        sep=";",
    )

print(reports["length_by_skill"].to_string(index=False))
print(f"\nReports saved in: {output_dir.resolve()}")