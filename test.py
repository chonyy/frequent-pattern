from csv import reader
from collections import defaultdict
from itertools import chain, combinations
import matplotlib.pyplot as plt
import numpy as np
import time

def dataToCSV(fname):
    first = True
    currentID = 1
    with open(fname, 'r') as dataFile, open(fname + '.csv', 'w') as outputCSV:
        for line in dataFile:
            nums = line.split()
            itemSetID = nums[1]
            item = nums[2]
            if(int(itemSetID) == currentID):
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
            
def getAboveMinSup(itemSet, itemSetList, minSup, globalItemSetWithSup):
    freqItemSet = set()
    localItemSetWithSup = defaultdict(int)

    for item in itemSet:
        for itemSet in itemSetList:
            if item.issubset(itemSet):
                globalItemSetWithSup[item] += 1
                localItemSetWithSup[item] += 1

    for item, supCount in localItemSetWithSup.items():
        support = float(supCount / len(itemSetList))
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
    rules = []
    for k, itemSet in freqItemSet.items():
        for item in itemSet:
            subsets = powerset(item)
            for s in subsets:
                confidence = float(itemSetWithSup[item] / itemSetWithSup[frozenset(s)])
                if(confidence > minConf):
                    rules.append([set(s), set(item.difference(s)), confidence])
    return rules

def recordTime(startTime, timeAtStage):
    tempTime = time.time() - startTime
    timeAtStage.append(tempTime)
    print('time used {:.3f}'.format(tempTime))
    return time.time()

if __name__ == "__main__":
    fname = 'data4'
    # dataToCSV(fname)
    C1ItemSet, itemSetList = getFromFile(fname + '.csv')

    # Final result global frequent itemset
    globalFreqItemSet = dict()
    # Storing global itemset with support count
    globalItemSetWithSup = defaultdict(int)
    minSup = 0.1
    minConf = 0.5

    timeAtStage = []
    candidateTime = []
    pruneTime = []
    supTime = []


    sizeAtStage = []
    pruneAtStage = []
    frequentAtStage = []

    startTime = time.time()
    L1ItemSet = getAboveMinSup(C1ItemSet, itemSetList, minSup, globalItemSetWithSup)
    sizeAtStage.append(len(L1ItemSet))
    pruneAtStage.append(len(L1ItemSet))
    frequentAtStage.append(len(L1ItemSet))

    print('time at counting')
    startTime = recordTime(startTime, supTime)
    pruneTime.append(0)
    candidateTime.append(0)

    print('Candidate size:', len(L1ItemSet))
    currentLSet = L1ItemSet
    k = 2


    # Calculating frequent item set
    while(currentLSet):
        # Storing frequent itemset
        globalFreqItemSet[k-1] = currentLSet
        # Self-joining Lk
        print(k)
        startTime = time.time()
        candidateSet = getUnion(currentLSet, k)
        # startTime = recordTime(startTime, candidateTime)
        sizeAtStage.append(len(candidateSet))
        print('Candidate size:', len(candidateSet))
        print('time at joining')
        # startTime = recordTime(startTime, timeAtStage)
        # print('candidate', candidateSet)
        # Perform subset testing and remove pruned supersets
        candidateSet = pruning(candidateSet, currentLSet, k-1)
        # startTime = recordTime(startTime, pruneTime)
        pruneAtStage.append(len(candidateSet))
        print("After pruning", len(candidateSet))
        print('time at pruning')
        # startTime = recordTime(startTime)
        # print('after pruning', candidateSet)
        # print()
        # Scanning itemSet for counting support
        currentLSet = getAboveMinSup(candidateSet, itemSetList, minSup, globalItemSetWithSup)
        startTime = recordTime(startTime, supTime)
        frequentAtStage.append(len(currentLSet))
        print('time at counting')
        k += 1

    # t = np.arange(1, 8, 1)
    # plt.xlabel('Stage')
    # plt.ylabel('Time elapsed (sec)')
    # plt.plot(t, timeAtStage, linewidth=4)
    # plt.show()

    # t = np.arange(1, 8, 1)
    # plt.xlabel('Stage')
    # plt.ylabel('Itemset Size')
    # plt.plot(t, sizeAtStage, linewidth=4, label='Candidate generated', alpha=0.7)
    # plt.plot(t, pruneAtStage, linewidth=4,
    #          label='Candidate after pruning', alpha=0.7)
    # plt.plot(t, frequentAtStage, linewidth=4,
    #          label='Frequent itemsets', alpha=0.7)
    # plt.legend(loc="upper right")
    # plt.title('Size during each process in a stage')
    # plt.show()

    t = np.arange(1, 8, 1)
    plt.xlabel('Stage')
    plt.ylabel('Time elapsed (sec)')
    # plt.plot(t, candidateTime, linewidth=4,
    #          label='Candidate generation', alpha=0.7)
    # plt.plot(t, pruneTime, linewidth=4,
    #          label='Pruning', alpha=0.7)
    plt.plot(t, supTime, linewidth=4,
             label='Counting support', alpha=0.7)
    # plt.legend(loc="upper right")
    plt.title('Time elapsed at each stage')
    plt.show()

    print('Frequent patterns:')
    for k, itemSetList in globalFreqItemSet.items():
        for itemSet in itemSetList:
            print(set(itemSet))
    
    # Generating rule
    print('rules:')
    rules = associationRule(globalFreqItemSet, globalItemSetWithSup, minConf)
    for rule in rules:
        print('{} ==> {}   {:.3f}'.format(rule[0], rule[1], rule[2]))
