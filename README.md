# Repository for the PPM Process Miner

## Getting started

Setup and installation is easy:
1. ```clone``` this repository
2. Create a virtual environment
3. Activate the virtual environment
4. ```pip install -r process_miner/requirements.txt```
5. ```gunicorn -b [::]:8012 "process_miner:create_app()" --timeout 6000```

## Supported Features

Currently a subset of standard process mining features are available in the tool. These are limited to:
- Alpha Miner
- Alpha Plus Miner
- Heuristic Miner
- General decision statistics
- Transition heat maps
- Occurrence counters
- Median execution per project chain type over time
- Occurrence over Time

## Usage
The usage should be reasonably self explanatory from the UI.

## Authors and acknowledgment
The petrinet viewer is based on the Mobile Patent Suits Example by the D3 Team (Mike Bostock). 
The original example is available under https://observablehq.com/@d3/mobile-patent-suits. 

## License
Currently no license has been selected.

## Project status
In development.