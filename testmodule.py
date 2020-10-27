from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from csv import reader


def getFromFile(fname):
    itemSets = []
    itemSet = set()

    with open(fname, 'r') as file:
        csv_reader = reader(file)
        for line in csv_reader:
            line = list(filter(None, line))
            record = set(line)
            for item in record:
                itemSet.add(frozenset([item]))
            itemSets.append(record)
    # print(itemSet)
    # print(itemSets)
    return itemSet, itemSets


fname = 'data7'
# dataToCSV(fname)
C1ItemSet, dataset = getFromFile(fname + '.csv')

te = TransactionEncoder()
te_ary = te.fit(dataset).transform(dataset)
df = pd.DataFrame(te_ary, columns=te.columns_)


df = apriori(df, min_support=0.1, use_colnames=True)
print(df)

rules = association_rules(df, metric='confidence', min_threshold=0.5)
print(rules)