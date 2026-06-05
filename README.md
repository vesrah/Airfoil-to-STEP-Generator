# Airfoil to STEP Generator

Generates a 3D STEP model from an airfoil definition hosted on AirfoilTools.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python airfoil-to-step.py <airfoil> <chord_mm> <span_mm>
```

### Examples

Generate a Clark Y airfoil with a 180 mm chord and 500 mm span:

```bash
python airfoil-to-step.py clarky-il 180 500
```

Generate a NACA 2412 airfoil with a 250 mm chord and 1200 mm span:

```bash
python airfoil-to-step.py naca2412 250 1200
```

Specify an output filename:

```bash
python airfoil-to-step.py naca2412 250 1200 -o wing.step
```

## Arguments

| Argument | Description |
|----------|-------------|
| `airfoil` | Airfoil name from AirfoilTools (e.g. `clarky-il`, `naca2412`) |
| `chord_mm` | Chord length in millimeters |
| `span_mm` | Extrusion length / wing span in millimeters |
| `-o`, `--output` | Optional STEP output filename |