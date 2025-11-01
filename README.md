# Test Accumulator (TA)

Clone the repository and navigate to its corresponding directory.

Setup venv:

```
python3 -m venv ./venv/
source ./venv/bin/activate
```

While in venv (cmd line will be prefixed by `(venv)`):
```
pip install -r requirements.txt
```

Use the script:

```
Usage: python ta.py [csv_directory_path] [graph_threshold%] [days|weeks|months]
```

Results will be output to `quantity_result.csv`, `duration_result.csv`, and `/graphs/`.

### Developed using Python 3.12.3