import numpy as np
import pandas as pd
from pathlib import Path

models_path = Path(__file__).resolve().parent / 'models'
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

    for bio_age in ['lin_age','lin_age_2']:

        model       = _get_model(bio_age)
        weights     = model[f'{gender}_weight'].values

        data_clean  = _prepare_data(data, bio_age=bio_age)
        data_normed = _normalize_data(gender, data_clean, model, z_limit)

        data_weighted = data_normed * weights
        delta_age = (data_weighted).sum()

        output[f'{bio_age}__deviations']    = data_normed
        output[f'{bio_age}__contributions'] = data_weighted
        output[bio_age]= (age + delta_age).item()
        output[f'{bio_age}__delta'] = delta_age.item()

    return output


def _prepare_data(data: pd.Series, bio_age: str) -> pd.Series:
    """
    Prepare data for modeling.
    """

    model = _get_model(bio_age)
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


def _get_model(bio_age):
    model_path = models_path.joinpath(f'{bio_age}.csv')
    model = pd.read_csv(model_path)
    return model


def _normalize_data(gender, data, model, z_limit):

    data_normed = data.copy()

    model = model.set_index('biomarker')
    for _, marker in model.iterrows():

        median    = marker[f'{gender}_median']
        deviation = marker[f'{gender}_MAD']

        if median == 0 and deviation == 1:
            continue

        data_normed[marker.name] = (data_normed[marker.name] - median) / deviation
        data_normed[marker.name] = data_normed[marker.name].clip(-z_limit, z_limit)

    return data_normed


def _get_age_years(data):
    return (data['RIDAGEEX'] / 12).item()

def _get_gender(data):
    return gender_dict[data['RIAGENDR']]
