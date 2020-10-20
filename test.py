from csv import reader
from collections import defaultdict
from itertools import chain, combinations

def dataToCSV(fname):
    first = True
    currentID = 1
    with open(fname, 'r') as dataFile, open(fname + '.csv', 'w') as outputCSV:
        for line in dataFile:
            nums = line.split()
            transactionID = nums[1]
            item = nums[2]
            if(int(transactionID) == currentID):
                if(first):
                    outputCSV.write(item)
                else:
                    outputCSV.write(',' + item)
                first = False
            else:
                outputCSV.write('\n' + item)
                currentID += 1

def powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))

def getFromFile(fname):
    transactions = []
    itemSet = set()
    
    with open(fname, 'r') as file:
        csv_reader = reader(file)
        for line in csv_reader:
            record = set(line)
            for item in record:
                itemSet.add(frozenset([item]))
            transactions.append(record)
    print(itemSet)
    print(transactions)
    return itemSet, transactions
            
def getAboveMinSup(itemSet, transactionList, minSup, globalItemSetWithSup):
    freqItemSet = set()
    localItemSetWithSup = defaultdict(int)

    for item in itemSet:
        for transaction in transactionList:
            if item.issubset(transaction):
                globalItemSetWithSup[item] += 1
                localItemSetWithSup[item] += 1

    for item, supCount in localItemSetWithSup.items():
        support = float(supCount / len(transactionList))
        if(support >= minSup):
            freqItemSet.add(item)

    return freqItemSet

def getUnion(itemSet, length):
    return set([i.union(j) for i in itemSet for j in itemSet if len(i.union(j)) == length])

def pruning(candidateSet, prevFreqSet, length):
    tempCandidateSet = candidateSet.copy()
    for item in candidateSet:
        subsets = combinations(item, length)
        for subset in subsets:
            # if the subset is not in previous K-frequent get, then remove the set
            if(frozenset(subset) not in prevFreqSet):
                tempCandidateSet.remove(item)
                break
    return tempCandidateSet

def associationRule(freqItemSet, itemSetWithSup, minConf):
    for i, itemSet in freqItemSet.items():
        for item in itemSet:
            print()
            print('item', item)
            subsets = powerset(item)
            for s in subsets:
                confidence = float(itemSetWithSup[item] / itemSetWithSup[frozenset(s)])
                if(confidence > minConf):
                    print('{} ==> {}   {:.3f}'.format(set(s), set(item.difference(s)), confidence))

if __name__ == "__main__":
    fname = 'data2'
    dataToCSV(fname)
    C1ItemSet, transactionList = getFromFile(fname + '.csv')

    # Final result global frequent itemset
    globalFreqItemSet = dict()
    # Storing global itemset with support count
    globalItemSetWithSup = defaultdict(int)
    minSup = 0.6
    minConf = 0.6

    L1ItemSet = getAboveMinSup(C1ItemSet, transactionList, minSup, globalItemSetWithSup)
    currentLSet = L1ItemSet
    k = 2

    # Calculating frequent item set
    while(currentLSet):
        # Storing frequent itemset
        globalFreqItemSet[k-1] = currentLSet
        # Self-joining Lk
        candidateSet = getUnion(currentLSet, k)
        # print('candidate', candidateSet)
        # Perform subset testing and remove pruned supersets
        candidateSet = pruning(candidateSet, currentLSet, k-1)
        # print('after pruning', candidateSet)
        # print()
        # Scanning transaction for counting support
        currentLSet = getAboveMinSup(candidateSet, transactionList, minSup, globalItemSetWithSup)
        k += 1

    # Generating rule
    associationRule(globalFreqItemSet, globalItemSetWithSup, minConf)