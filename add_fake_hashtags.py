import argparse
import pandas as pd
parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input')
parser.add_argument('-o', '--output')

args = parser.parse_args()

df = pd.read_json(args.input)

df['hashtags'] = pd.Series([['aaaa', 'bbbb']] * df.shape[0],
                           index=df.index)

df.to_json(args.output, orient='records')

