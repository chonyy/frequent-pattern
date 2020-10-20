from collections import defaultdict, OrderedDict
from csv import reader

class treeNode:
    def __init__(self, itemName, frequency, parentNode):
        self.item = itemName
        self.count = frequency
        self.nodeLink = None
        self.parent = parentNode
        self.children = {}

    def increment(self, frequency):
        self.count += frequency

    def display(self, ind=1):
        print('  '*ind, self.item, ' ', self.count)
        for child in list(self.children.values()):
            child.display(ind+1)

def updateHeader(nodeToTest, targetNode):
    # Traverse to the last node then link it to the target
    while nodeToTest.nodeLink != None:
        nodeToTest = nodeToTest.nodeLink
    nodeToTest.nodeLink = targetNode

def updateFPtree(items, inTree, headerTable, frequency):
    if items[0] in inTree.children:
        # incrementrement the count if the item already exists
        inTree.children[items[0]].increment(frequency)
    else:
        # Create a new branch
        inTree.children[items[0]] = treeNode(items[0], frequency, inTree)
        # Link the linked list at header table
        if headerTable[items[0]][1] == None:
            headerTable[items[0]][1] = inTree.children[items[0]]
        else:
            updateHeader(headerTable[items[0]][1], inTree.children[items[0]])
    # Going to the next item
    if len(items) > 1:
        updateFPtree(items[1::], inTree.children[items[0]], headerTable, frequency)

def ascendFPtree(node, prefixPath):
    if node.parent != None:
        prefixPath.append(node.item)
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
        treeNode = treeNode.nodeLink  
    return condPats, frequency


def mineTree(inTree, headerTable, minSup, preFix, freqItemList):
    # Sort the items with frequency and create a list
    sortedItemList = [v[0] for v in sorted(list(headerTable.items()), key=lambda p:p[1][0])] 
    print('sortedItemList', sortedItemList)
    # Start with the lowest frequency
    for item in sortedItemList:  
        # Pattern growth is achieved by the concatenation of suffix pattern with frequent patterns generated from conditional FP-tree
        newFreqSet = preFix.copy()
        newFreqSet.add(item)
        freqItemList.append(newFreqSet)
        # Find all prefix path, constrcut conditional pattern base
        conditionalPattBase, frequency = findPrefixPath(item, headerTable) 
        print('current item', item)
        print('new', newFreqSet)
        print()
        # print('Condition pattern base', conditionalPattBase)
        # Construct conditonal FP Tree with conditional pattern base
        conditionalTree, headNode = constructTree(conditionalPattBase, frequency, minSup) 
        # print('head', headNode)
        # print()
        if headNode != None:
            # print('conditional tree for: ', newFreqSet)
            # conditionalTree.display(1)

            # Mining recursively on the tree
            mineTree(conditionalTree, headNode, minSup,
                       newFreqSet, freqItemList)

def getFromFile(fname):
    transactions = []
    frequency = []
    
    with open(fname, 'r') as file:
        csv_reader = reader(file)
        for line in csv_reader:
            transactions.append(line)
            frequency.append(1)

    return transactions, frequency

def constructTree(transactionList, frequency, minSup):
    headerTable = defaultdict(int)
    cleanedTransactionList = {}
    # Counting frequency and create header table
    for idx, transaction in enumerate(transactionList):
        for item in transaction:
            headerTable[item] += frequency[idx]

    # Deleting items below minSup
    headerTable = dict((item, sup) for item, sup in headerTable.items() if sup >= minSup)
    if(len(headerTable) == 0):
        return None, None

    # HeaderTable column [Item: [frequency, headNode]]
    for item in headerTable:
        headerTable[item] = [headerTable[item], None]

    # Init Null head node
    fpTree = treeNode('Null', 1, None)
    # Update FP tree for each cleaned and sorted transaction
    for idx, transaction in enumerate(transactionList):
        transaction = [item for item in transaction if item in headerTable]
        transaction.sort(key=lambda item: headerTable[item][0], reverse=True)
        # print('transaction', transaction)
        updateFPtree(transaction, fpTree, headerTable, frequency[idx])

    return fpTree, headerTable

if __name__ == "__main__":
    minSup = 3
    fname = 'tesco'
    transactionList, frequency = getFromFile(fname + '.csv')
    fpTree, headerTable = constructTree(transactionList, frequency, minSup)
    fpTree.display()

    freqItems = []
    mineTree(fpTree, headerTable, minSup, set([]), freqItems)
    for x in freqItems:
        print(x)
