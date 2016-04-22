import os
import pandas as pd
from datetime import datetime as dt


def main():
    df = pd.read_pickle('data/letter/interactions.pkl')
    timespans = [(1350, 1419),
                 (1420, 1499),
                 (1500, 1569),
                 (1570, 1639),
                 (1640, 1710)]
    for start, end in timespans:
        output_dir = 'data/letter-{}-{}'.format(start, end)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        sub_df = df[(df['datetime'] >= dt(start, 1, 1, 1)) & (df['datetime'] <= dt(end, 12, 31, 23))]
        sub_df.to_pickle('{}/interactions.pkl'.format(output_dir))


if __name__ == "__main__":
    main()
