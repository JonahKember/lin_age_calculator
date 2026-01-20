import numpy as np
import pandas as pd


gender_dict = {1:'male', 2:'female'}


def calculate(data: dict, z_limit: int = 6) -> dict:
    """
    Calculate lin_age and lin_age_2.
    """

    data = pd.Series(data)

    age = _get_age_years(data)
    gender = _get_gender(data)

    output = {}
    output['age'] = age
    output['gender'] = gender

    for bio_age in ['lin_age','lin_age_2','pheno_age']:

        model = pd.read_csv(f'models/{bio_age}.csv')
        weights     = model[f'{gender}_weight'].values
        medians     = model[f'{gender}_median'].values
        deviations  = model[f'{gender}_MAD'].values

        data_clean = _prepare_data(data, bio_age=bio_age)

        data_normed = (data_clean - medians) / deviations
        data_normed = data_normed.clip(-z_limit, z_limit)

        data_weighted = data_normed * weights
        delta_age = (data_weighted).sum()

        output[f'{bio_age}__contributions'] = data_weighted
        output[bio_age]= (age + delta_age).item()
        output[f'{bio_age}__delta'] = delta_age.item()

    return output


def _prepare_data(data: pd.Series, bio_age: str) -> pd.Series:
    """
    Prepare data for modeling.
    """

    model = pd.read_csv(f'models/{bio_age}.csv')
    biomarkers = model['biomarker'].to_numpy()
    log_markers = biomarkers[model['log_transform']]

    # Add constant.
    data['constant'] = 1

    # Digitize cotinine if needed.
    if bio_age == 'lin_age_2':
        cot = data['LBXCOT']
        data['LBXCOT'] = (
            (cot >= 10).astype(int)
            + (cot >= 100).astype(int)
            + (cot >= 200).astype(int)
        )

    # Ensure all biomarkers are present and in the correct order (missing become NaN).
    data = data.reindex(biomarkers)
    data = pd.to_numeric(data, errors='coerce')

    # Log-transform specified biomarkers.
    data_log = data.copy()
    data_log[log_markers] = np.log(data[log_markers])

    return data_log


def _get_age_years(data):
    return (data['RIDAGEEX'] / 12).item()

def _get_gender(data):
    return gender_dict[data['RIAGENDR']]
