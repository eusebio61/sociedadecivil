#!/usr/bin/env python

import pandas as pd

read_file = pd.read_excel('2022.xlsx')

read_file.to_csv('test.csv', index=None, header=True)


