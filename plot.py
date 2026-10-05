

import pandas as pd
import matplotlib.pyplot as plt

from extract import extract_data

extracted_data = extract_data()

row_counts = []

for sheet_name, df in extracted_data.items():

    row_counts.append({
        "sheet_name": sheet_name,
        "row_count": df.shape[0]
    })

row_counts = pd.DataFrame(row_counts)

print(row_counts)

row_counts.plot.bar(
    x="sheet_name",
    y="row_count"
)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()