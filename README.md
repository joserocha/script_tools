# SEARCH FOR STRING IN KUBERNETES CLUSTER

Scan all namespaces in a Kubernete's cluster, retrieving a running pod per namespace and also all user-defined secrets. The goal is to find common keys and / or values.

|Linguagem|Python 3|
|---------|----|

## Usage

```shell
python -m pip install -r requirements.txt
python main.py --find "value_to_be_searched" --output [simple/detailed] --verbose
```
the simple output will show only one line even if the value was found it in different places in the same pod / secret
the detailed output will show every ocurrence and also the whole line when the value was found it