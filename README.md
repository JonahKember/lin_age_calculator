```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from calculator import calculate
%config InlineBackend.figure_format='retina'

# Load example data.
data = pd.read_csv('example_user.csv')
data = dict(zip(data['biomarker'],data['value']))

# Run calculator.
results = calculate(data)

# Print results.
print(f"age       = {results['age']:.2f} years")
print(f"lin_age   = {results['lin_age']:.2f} years")
print(f"lin_age_2 = {results['lin_age_2']:.2f} years")

```

    age       = 77.17 years
    lin_age   = 88.23 years
    lin_age_2 = 86.47 years



```python
# Print contribution of each biomarker to delta-age.

fig, ax = plt.subplots(2, 1, figsize=(9, 9))

for idx, model in enumerate(['lin_age','lin_age_2']):

    weights = results[f'{model}__contributions'].sort_values().dropna()

    sns.barplot(weights, orient='v', ax=ax[idx], color='tab:gray')
    sns.despine()

    ax[idx].set_ylabel('$\Delta$ age')
    ax[idx].tick_params(axis='x', rotation=70)
    ax[idx].axhline(0, color='k', lw=1)
    ax[idx].grid(linestyle='-', axis='x', alpha=.2)
    ax[idx].set_title(model, loc='left')


plt.tight_layout()
```


    
![png](example_files/example_1_0.png)
    

