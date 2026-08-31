# Gender and Race/Color Biases in LLM Recommendations for Brazilian Undergraduate Fields

Code, prompts, configurations, generated outputs, and analysis notebooks for the paper *Who Gets Recommended What? Gender and Race/Color Biases in LLM Recommendations for Brazilian Undergraduate Fields*.

The paper was accepted for the **2026 IEEE Latin American Conference on Computational Intelligence (LA-CCI)**, to be held in Lima, Peru, on November 3–6, 2026.

## Overview

This study audits gender and race/color bias in LLM outputs about Brazilian undergraduate fields. It uses the Brazilian Institute of Geography and Statistics (IBGE) as a **descriptive empirical reference**, not as a normative fairness target. All prompts are in Brazilian Portuguese and all model runs use temperature 0 with one response per experimental condition.

The camera-ready paper evaluates eight instruction-tuned LLMs:

- DeepSeek-V4-Pro;
- Gemini-2.5-Flash;
- Qwen3-235B-A22B;
- GPT-OSS-120B;
- Sabia-4;
- Llama-4-Maverick;
- Mistral-Small-24B; and
- Gemma-4-31B.

## Experiments

### 1. Demographic attribution

For each of 87 detailed undergraduate fields, every model generates a JSON profile of a hypothetical Brazilian adult who completed that field. The profile includes name, age, state, monthly income, attributed sex, and race/color.

The paper analyzes 696 profiles (87 fields × 8 models) and compares the attributed sex and race/color distributions with the corresponding IBGE distributions. The category with no people in the IBGE reference data is excluded from field-level comparisons that require proportions, leaving 86 non-empty fields for those analyses.

### 2. Demographic-conditioned educational recommendations

Models advise a Brazilian student in the final year of high school and must recommend exactly three undergraduate fields from a fixed list. Prompts vary along two axes:

- **Social markers (18 conditions):** two gender-only markers, five race/color-only markers, ten joint gender-by-race/color markers, and one condition without demographic information.
- **Academic interest (5 conditions):** the four ENEM knowledge areas—Languages, Human Sciences, Natural Sciences, and Mathematics—and a condition with no declared interest.

This produces 90 prompt conditions per model and 720 recommendations overall (90 × 8). Recommendations are analyzed with a rank-weighted exposure metric that gives weights 3, 2, and 1 to the first, second, and third recommendation, respectively.

The paper reports that demographic differences in recommendation exposure are most pronounced when the prompt contains no academic-interest information. Providing an ENEM interest area constrains the recommendation space and reduces those differences.

## Paper-aligned artifacts

The files below reproduce the data and analyses reported in the camera-ready paper.

| Experiment | Configuration | Generated outputs | Analysis notebook |
| --- | --- | --- | --- |
| Demographic attribution | `conf/profile_config.yaml` | `data/generated_profiles.csv`, `data/generated_profiles.jsonl`, `data/generated_profiles.pkl` | `src/analysis/processing_profile_results.ipynb` |
| Educational recommendations | `conf/recommendation_config.yaml` | `data/fixed_prompts_generated_recommendations.{csv,jsonl,pkl}`, `data/fixed_prompts_gemma_generated_recommendations.{csv,jsonl,pkl}`, `data/fixed_prompts_sabia_generated_recommendations.{csv,jsonl,pkl}` | `src/analysis/processing_recommendation_results_fixed_prompts.ipynb` |

The camera-ready recommendation results are split across three model-output files: `fixed_prompts_generated_recommendations.jsonl` contains 540 records from six models, while `fixed_prompts_gemma_generated_recommendations.jsonl` and `fixed_prompts_sabia_generated_recommendations.jsonl` contribute 90 records each. Together they contain the 720 recommendations analyzed in the paper. Use these files, their corresponding CSV/cache files, `recommendation_config.yaml`, and `processing_recommendation_results_fixed_prompts.ipynb` for the camera-ready experiment.

The raw profile-output files contain 783 records because they also retain 87 outputs from NVIDIA Nemotron. That model is excluded from the paper's eight-model attribution analysis because of its high rate of invalid responses; the attribution notebook applies this exclusion.

## Repository structure

```text
.
├── conf/
│   ├── main_config.yaml
│   ├── profile_config.yaml
│   └── recommendation_config.yaml
├── data/
│   ├── generated_profiles.{csv,jsonl,pkl}
│   ├── fixed_prompts_generated_recommendations.{csv,jsonl,pkl}
│   ├── fixed_prompts_gemma_generated_recommendations.{csv,jsonl,pkl}
│   ├── fixed_prompts_sabia_generated_recommendations.{csv,jsonl,pkl}
│   ├── tables/
│   │   └── ibge_undergraduate_fields.xlsx
│   ├── undergraduate_fields_for_profile.yaml
│   └── undergraduate_fields_for_recommendation.yaml
├── src/
│   ├── main/
│   │   └── utils.py
│   └── analysis/
│       ├── preprocessing_undergraduate_fields.ipynb
│       ├── processing_profile_results.ipynb
│       └── processing_recommendation_results_fixed_prompts.ipynb
├── run_main.py
├── pixi.toml
└── pixi.lock
```

## Data

`data/tables/ibge_undergraduate_fields.xlsx` contains the processed data derived from IBGE table 10065: people with completed higher education by detailed field, sex, and color/race (2022 Demographic Census). The detailed field lists in `undergraduate_fields_for_profile.yaml` and `undergraduate_fields_for_recommendation.yaml` support preprocessing and prompt construction.

The `.csv` files are tabular outputs, the `.jsonl` files preserve one generated record per line, and the `.pkl` files are response caches used by the experiment runner.

## Environment setup

This project uses [pixi](https://pixi.sh/) for environment management.

```bash
pixi install
```

Commands can then be run through pixi, for example:

```bash
pixi run python run_main.py --config-name profile_config
pixi run python run_main.py --config-name recommendation_config
```

The runner queries external model providers. Configure the required API credentials in a local `.env` file before running it, and adjust the cache/output paths in the configuration if you do not want to replace the supplied artifacts. `main_config.yaml` is the default Hydra configuration; the two commands above select the paper-aligned experiment configurations explicitly.

## Citation

Please cite the accepted conference paper as follows:

```bibtex
@inproceedings{midlej2026who,
  author    = {Juliana Midlej and Anderson Luis Bento Soares and Leonardo Nascimento Ferreira and Helio Pedrini and Zanoni Dias},
  title     = {Who Gets Recommended What? Gender and Race/Color Biases in {LLM} Recommendations for Brazilian Undergraduate Fields},
  booktitle = {2026 IEEE Latin American Conference on Computational Intelligence ({LA-CCI})},
  year      = {2026},
  month     = nov,
  address   = {Lima, Peru},
  note      = {Accepted for publication}
}
```

The proceedings DOI and page range had not yet been assigned at the camera-ready stage, so they are intentionally not included above. They should be added once the IEEE Xplore record is available.

## License

See [LICENSE](LICENSE).
