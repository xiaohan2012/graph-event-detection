# coding: utf-8
import pandas as pd

# Save contents line-by-line into txt file 
t = pd.read_csv('~/Downloads/IslamicAwakening.txt', sep='\t',
                error_bad_lines=False)
ms = pd.DataFrame(t['Message'])
ms.to_csv('~/code/lst_dag/data/islam.txt',
          header=False, index=False)


# Some stats

t['ThreadID'].count()
t['ThreadID'].value_counts()
t['ThreadID'].value_counts().shape
(t['ThreadID'].value_counts() == 1).nonzero()[0].shape
t['ThreadID'].value_counts().max()
t['ThreadID'].value_counts().min()
t['ThreadID'].value_counts().mean()
t['ThreadID'].value_counts().median()

