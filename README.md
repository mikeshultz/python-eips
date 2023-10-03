# Ethereum Improvement Proposal (EIP) Processor

CLI tools and Python library for interacting with EIPs from the [source EIPs GitHub repository](https://github.com/ethereum/EIPs).

## Features/TODO

Frontend

- [X] CLI tools
- [X] Library API
- [ ] Documentation

Data processing:

- [X] EIP Metadata processing
- [ ] EIP relationships and references
- [ ] Automated tagging
- [ ] File history, changelog
- [X] Aggregate data, statistics, and error detection

## Usage

### Show EIP

```bash
eips show 20
```

### Show EIP Headers

```bash
eips show -i 4626
```

## API Usage

### Get an EIP

```python
>>> from eips import EIPs
>>> eips = EIPs()
>>> eip_20 = eips.get(20)[0]
>>> eip_20.title
'Token Standard'
```

### Get all EIPs

```python
>>> from eips import EIPs
>>> eips = EIPs()
>>> for e in eips.get():
...   print(e.eip_id)
... 
2018
5216
999
606
[...]
```

### Get count of EIPs

```python
>>> from eips import EIPs
>>> eips = EIPs()
>>> eips.len()
687
```

### Get EIPs aggregate stats

```python
>>> from eips import EIPs
>>> eips = EIPs()
>>> eips.stats().total
687
>>> eips.stats().errors
0
>>> [c.value for c in eips.stats().categories]
['ERC', 'Core', 'Interface', 'Networking']
>>> [s.value for s in eips.stats().statuses]
['Stagnant', 'Last Call', 'Withdrawn', 'Final', 'Review', 'Draft', 'Living']
>>> [t.value for t in eips.stats().types]
['Standards Track', 'Meta', 'Informational']
```

## Development

### Run Tests

```bash
hatch run test
```

### Linting

```bash
hatch run lint
```

### Release

```bash
# Bump the version major/minor/patch
hatch version patch
# Tag the git commit with the version
git tag -a "v$(hatch version)" -m "v$(hatch version)"
# Push it up to GH, don't forget the tag
git push --follow-tags
```

Now [create a GitHub release](https://github.com/mikeshultz/python-eips/releases/new) and CI will do the rest.
