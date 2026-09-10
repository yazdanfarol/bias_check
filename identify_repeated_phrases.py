from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# 1. File settings — change this path if necessary
input_file = Path(
    "real_testset_300.xlsx"
)
output_dir = Path("outputs_repeated_phrases")
output_dir.mkdir(exist_ok=True)

# 2. Read the Excel table
df = pd.read_excel(
    input_file,
    sheet_name="Testfälle",
    dtype=str,
).reset_index(drop=True)

required_columns = ["id", "skill", "text"]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing column: {column}")
    if df[column].fillna("").str.strip().eq("").any():
        raise ValueError(f"Missing or empty values in: {column}")

if df["id"].duplicated().any():
    raise ValueError("Duplicate IDs found.")

# 3. Extract repeated phrases
# binary=True: count a phrase only once per item.
# min_df=3: retain phrases appearing in at least 3 items.
# Keep articles, negation and other common words.
vectorizer = CountVectorizer(
    lowercase=True,
    ngram_range=(2, 5),
    min_df=3,
    binary=True,
    stop_words=None,
    strip_accents=None,
)

try:
    X = vectorizer.fit_transform(df["text"])
except ValueError as error:
    raise ValueError(
        "Phrase extraction failed. There may be no phrases appearing "
        "in at least 3 items. Check the text or try min_df=2."
    ) from error

phrases = vectorizer.get_feature_names_out()

# 4. Build the audit report
report = pd.DataFrame({
    "phrase": phrases,
    "word_count": [len(phrase.split()) for phrase in phrases],
    "items_total": X.sum(axis=0).A1.astype(int),
})

# Compare counts and within-label percentages.
for label in sorted(df["skill"].unique()):
    mask = df["skill"].eq(label).to_numpy()
    label_total = int(mask.sum())
    counts = X[mask].sum(axis=0).A1.astype(int)

    report[f"{label}_count"] = counts
    report[f"{label}_pct"] = (counts / label_total * 100).round(1)

# Include matching IDs so you can review the original sentences.
X_by_phrase = X.tocsc()

report["matching_ids"] = [
    ", ".join(
        df.iloc[X_by_phrase[:, index].nonzero()[0]]["id"]
    )
    for index in range(len(phrases))
]

report = report.sort_values(
    ["items_total", "word_count", "phrase"],
    ascending=[False, False, True],
).reset_index(drop=True)

# 5. Export the phrase report
report.to_csv(
    "outputs_repeated_phrases/repeated_phrases.csv",
    index=False,
    encoding="utf-8-sig",
    sep=";",
)

# Export the actual binary vectors for inspection.
# Rows = items; columns = retained phrases; values = 0 or 1.
vectors = pd.DataFrame(
    X.toarray(),
    index=df["id"],
    columns=phrases,
)
vectors.index.name = "id"

vectors.to_csv(
    output_dir / "phrase_vectors.csv",
    encoding="utf-8-sig",
    sep=";",
)

print(f"Items analysed: {len(df)}")
print(f"Repeated phrases found: {len(report)}")
print(f"Files saved in: {output_dir}")
print(report.head(20).to_string(index=False))