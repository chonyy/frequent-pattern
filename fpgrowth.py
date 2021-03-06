from collections import defaultdict, OrderedDict
from csv import reader
from itertools import chain, combinations
import time

class Node:
    def __init__(self, itemName, frequency, parentNode):
        self.itemName = itemName
        self.count = frequency
        self.parent = parentNode
        self.children = {}
        self.next = None

    def increment(self, frequency):
        self.count += frequency

    def display(self, ind=1):
        print('  ' * ind, self.itemName, ' ', self.count)
        for child in list(self.children.values()):
            child.display(ind+1)

def getFromFile(fname):
    itemSetList = []
    frequency = []
    
    with open(fname, 'r') as file:
        csv_reader = reader(file)
        for line in csv_reader:
            line = list(filter(None, line))
            itemSetList.append(line)
            frequency.append(1)

    return itemSetList, frequency

def constructTree(itemSetList, frequency, minSup):
    headerTable = defaultdict(int)
    # Counting frequency and create header table
    for idx, itemSet in enumerate(itemSetList):
        for item in itemSet:
            headerTable[item] += frequency[idx]

    # Deleting items below minSup
    headerTable = dict((item, sup) for item, sup in headerTable.items() if sup >= minSup)
    if(len(headerTable) == 0):
        return None, None

    # HeaderTable column [Item: [frequency, headNode]]
    for item in headerTable:
        headerTable[item] = [headerTable[item], None]

    # Init Null head node
    fpTree = Node('Null', 1, None)
    # Update FP tree for each cleaned and sorted itemSet
    for idx, itemSet in enumerate(itemSetList):
        itemSet = [item for item in itemSet if item in headerTable]
        itemSet.sort(key=lambda item: headerTable[item][0], reverse=False)
        # Traverse from root to leaf, update tree with given item
        currentNode = fpTree
        for item in itemSet:
            currentNode = updateTree(item, currentNode, headerTable, frequency[idx])

    return fpTree, headerTable

def updateHeaderTable(item, targetNode, headerTable):
    if(headerTable[item][1] == None):
        headerTable[item][1] = targetNode
    else:
        currentNode = headerTable[item][1]
        # Traverse to the last node then link it to the target
        while currentNode.next != None:
            currentNode = currentNode.next
        currentNode.next = targetNode

def updateTree(item, treeNode, headerTable, frequency):
    if item in treeNode.children:
        # If the item already exists, increment the count
        treeNode.children[item].increment(frequency)
    else:
        # Create a new branch
        newItemNode = Node(item, frequency, treeNode)
        treeNode.children[item] = newItemNode
        # Link the new branch to header table
        updateHeaderTable(item, newItemNode, headerTable)

    return treeNode.children[item]

def ascendFPtree(node, prefixPath):
    if node.parent != None:
        prefixPath.append(node.itemName)
        ascendFPtree(node.parent, prefixPath)

def findPrefixPath(basePat, headerTable):
    # First node in linked list
    treeNode = headerTable[basePat][1] 
    condPats = []
    frequency = []
    while treeNode != None:
        prefixPath = []
        # From leaf node all the way to root
        ascendFPtree(treeNode, prefixPath)  
        if len(prefixPath) > 1:
            # Storing the prefix path and it's corresponding count
            condPats.append(prefixPath[1:])
            frequency.append(treeNode.count)

        # Go to next node
        treeNode = treeNode.next  
    return condPats, frequency

def mineTree(headerTable, minSup, preFix, freqItemList):
    # Sort the items with frequency and create a list
    sortedItemList = [item[0] for item in sorted(list(headerTable.items()), key=lambda p:p[1][0])] 
    print('Finish sorting:', sortedItemList)
    # Start with the lowest frequency
    for item in sortedItemList:  
        print('Checking item:', item)
        print('in', sortedItemList)
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        print('Adding new frequent set: ', newFreqSet)
        freqItemList.append(newFreqSet)
        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 
        # Construct conditonal FP Tree with conditional pattern base
        conditionalTree, newHeaderTable = constructTree(conditionalPattBase, frequency, minSup) 
        print(newHeaderTable)
        if newHeaderTable != None:
            print('Conditional tree for item:', item)
            conditionalTree.display()
            print()
            # print('current item', item)
            # print('conditional tree for: ', newFreqSet)
            # conditionalTree.display(1)

            # Mining recursively on the tree
            mineTree(newHeaderTable, minSup,
                       newFreqSet, freqItemList)
        else:
            print()

def powerset(s):
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)))

def getSupport(testSet, itemSetList):
    count = 0
    for itemSet in itemSetList:
        if(set(testSet).issubset(itemSet)):
            count += 1
    return count

def associationRule(freqItemSet, itemSetList, minConf):
    rules = []
    for itemSet in freqItemSet:
        subsets = powerset(itemSet)
        for s in subsets:
            confidence = float(getSupport(itemSet, itemSetList) / getSupport(s, itemSetList))
            if(confidence > minConf):
                rules.append([set(s), set(itemSet.difference(s)),
                              confidence, getSupport(itemSet, itemSetList), getSupport(s, itemSetList)])
    return rules

if __name__ == "__main__":
    minSupRatio = 0.07
    minConf = 0.5
    fname = 'data7'
    itemSetList, frequency = getFromFile(fname + '.csv')
    minSup = len(itemSetList) * minSupRatio
    startTime = time.time()
    fpTree, headerTable = constructTree(itemSetList, frequency, minSup)
    # fpTree.display()
    if(fpTree == None):
        print('No frequent item set')
    else:
        # fpTree.display()
        freqItems = []
        mineTree(headerTable, minSup, set(), freqItems)
        print(time.time() - startTime)
        # print('Frequent patterns:')
        # for x in freqItems:
        #     print(x)

        # rules = associationRule(freqItems, itemSetList, minConf)
        # print('\nRules:')
        # for rule in rules:
        #     print('{} ==> {}   {:.3f}   sup: {:.3f}  subsetsup: {:.3f}'.format(rule[0], rule[1], rule[2], rule[3] / len(itemSetList), rule[4] / len(itemSetList)))
        

# https://www.kaggle.com/newshuntkannada/dataset-for-apriori-and-fp-growth-algorithm
