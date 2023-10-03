TEST_EIP_HEADER = """---
eip: 4200
title: EOF - Static relative jumps
description: RJUMP, RJUMPI and RJUMPV instructions with a signed immediate encoding the jump destination
author: Alex Beregszaszi (@axic), Andrei Maiboroda (@gumb0), Paweł Bylica (@chfast)
discussions-to: https://ethereum-magicians.org/t/eip-3920-static-relative-jumps/7108
status: Review
type: Standards Track
category: Core
created: 2021-07-16
requires: 3540, 3670
---

## Abstract

Three new EVM jump instructions are introduced (`RJUMP`, `RJUMPI` and `RJUMPV`) which encode destinations as signed immediate values. These can be useful in the majority of (but not all) use cases and offer a cost reduction.
"""
