# Gender and Race/Color Biases in LLM Recommendations for Brazilian Undergraduate Fields

This repository contains the code, prompts, configurations, generated outputs, and analysis notebooks for the paper:

> **Who Gets Recommended What? Gender and Race/Color Biases in LLM Recommendations for Brazilian Undergraduate Fields**  
> Submitted to IEEE LACCI 2026.

The study evaluates whether large language models (LLMs) produce demographically biased representations and recommendations for Brazilian undergraduate fields. We focus on gender and race/color categories in the Brazilian context and compare model outputs with external statistics from IBGE.

## Overview

The repository supports two main experiments.

### 1. Demographic attribution task

Models are prompted to generate structured profiles of Brazilian adults who completed a specific undergraduate field. Each generated profile includes demographic and socioeconomic attributes such as:

- name;
- age;
- Brazilian state;
- monthly income;
- attributed sex;
- attributed race/color.

The goal is to analyze how LLMs represent demographic groups across undergraduate fields and how these representations compare with IBGE statistics.

### 2. Educational recommendation task

Models are prompted as if the user were a final-year high-school student in Brazil seeking advice about undergraduate fields. The prompt varies demographic cues such as gender and race/color, and may also include an academic-interest signal based on ENEM knowledge areas.

The model is instructed to recommend exactly three undergraduate fields from a fixed list. We analyze whether demographic cues affect the exposure of different fields in the recommendations.

## Repository structure

```text
.
├── conf/
│   ├── main_config.yaml
│   ├── profile_config.yaml
│   └── recommendation_config.yaml
│
├── data/
│   ├── generated_profiles.csv
│   ├── generated_profiles.jsonl
│   ├── generated_profiles.pkl
│   ├── generated_recommendations.csv
│   ├── generated_recommendations.jsonl
│   ├── generated_recommendations.pkl
│   ├── undergraduate_fields_for_profile.yaml
│   ├── undergraduate_fields_for_recommendation.yaml
│   └── tables/
│       └── ibge_undergraduate_fields.xlsx
│
├── src/
│   ├── main/
│   │   └── utils.py
│   └── analysis/
│       ├── preprocessing_undergraduate_fields.ipynb
│       ├── processing_profile_results.ipynb
│       └── processing_recommendation_results.ipynb
│
├── run_main.py
├── pixi.toml
├── pixi.lock
├── LICENSE
└── README.md
```

## Data

### 1. The data/ directory includes:

- generated_profiles.csv: generated outputs for the demographic attribution task;
- generated_profiles.jsonl: JSONL version of the generated profile outputs;
- generated_profiles.pkl: cache file used during profile generation;
- generated_recommendations.csv: generated outputs for the recommendation task;
- generated_recommendations.jsonl: JSONL version of the generated recommendation outputs;
- generated_recommendations.pkl: cache file used during recommendation generation;
- tables/ibge_undergraduate_fields.xlsx: processed IBGE reference data used in the analyses;
- undergraduate_fields_for_profile.yaml: undergraduate-field list used in the profile-generation task;
- undergraduate_fields_for_recommendation.yaml: undergraduate-field list used in the recommendation task.

## Configuration files

### 1. The experiments are controlled through Hydra configuration files in conf/.

- profile_config.yaml: configuration for the demographic attribution task.
- recommendation_config.yaml: configuration for the educational recommendation task.
- main_config.yaml: default configuration used by run_main.py.

### 2. The configuration files specify:

- models to evaluate;
- provider/backend for each model;
- temperature;
- number of repetitions;
- output paths;
- cache paths;
- system prompts;
- user prompts;
- demographic conditions;
- undergraduate-field lists;
- academic-interest conditions.

## Environment setup

This repository uses pixi for environment management. Install the environment with:

```bash
pixi install
```
Then activate the environment:

```bash
pixi shell
```

Alternatively, commands can be run directly with:

```bash
pixi run <task-name>
```

## Running experiments

The main experiment runner is:

```bash
python run_main.py
```

By default, this uses the Hydra configuration specified in run_main.py.

To run a specific configuration, use:

```bash
python run_main.py --config-name some_config
```
