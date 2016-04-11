import sys
import pandas as pd

df = pd.read_json('data/{}/interactions.json'.format(sys.argv[1]))
dts = df['datetime']
print('{} to {}'.format(dts.min(), dts.max()))
