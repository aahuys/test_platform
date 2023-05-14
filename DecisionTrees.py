#imports
import pandas as pd
import numpy as np
from InitData import InitMoviesData25M


########### class containing binary tree node ###########
class BinaryNode:
    #initializatoin
    def __init__(self, item, parent, path):
        self.item = item
        self.parent = parent
        self.path = path
        self.lchild = None
        self.rchild = None

########### class containing binary decision  tree with extended width ###########   
class BinaryDecisionTree:
    #initalization
    def __init__(self, df, max_depth, determineSplit,intervalSplit, dfSplits=10):
        self.df = df                                    #dataframe of tree
        self.rng = np.random.RandomState(1)             #seed
        self.dfs = self.splitDataFrame(df, dfSplits)    #subsets of dataframe
        self.splits = dfSplits                          #number of datasubsplits
        self.max_depth = max_depth
        self.determineSplit = determineSplit            #splitting function of tree
        self.intervalSplit = intervalSplit              #function to determine interval of ratings in split
        self.Ncounter = 0
        self.root = self.createTree(df, None, 0, None)  

    def createTree(self, functionDF, parent, depth, path):
        #see proces
        self.Ncounter +=1
        if self.Ncounter%1000==0:
            print(self.Ncounter//1000)
        #stop condition
        if depth==self.max_depth:
            return None
        #check if dataset is not none, otherwise add items
        if functionDF.shape[0]==0:
            #collect previous items
            prev_items = []
            nodeIt = parent
            while nodeIt != None:
                prev_items.append(nodeIt.item)
                nodeIt = nodeIt.parent
            #gen new dataset
            idx = self.rng.randint(0,self.splits)
            tempDF = self.dfs[idx]
            functionDF=tempDF[~tempDF['item'].isin(prev_items)]
        #determine split item
        item = self.determineSplit(functionDF)  
        #create new node
        node = BinaryNode(item,parent,path)
    #create first child
        #find users that disliked item
        interval = (self.intervalSplit(2))[0]
        users = functionDF[functionDF['item'] == item].reset_index(drop=True)
        users = users[users['rating'].isin(interval)]['user'].to_list()
        #create dataset for node, consisting of all ratings of users above, and without item
        child_dataset = functionDF[functionDF['item']!=item]
        child_dataset = child_dataset[child_dataset['user'].isin(users)]
        #add child to current node      #path is 0 for dislike
        node.lchild = self.createTree(child_dataset,node,depth+1,0)
    #create second child
        #find users that disliked item
        interval = (self.intervalSplit(2))[1]
        users = functionDF[functionDF['item'] == item].reset_index(drop=True)
        users = users[users['rating'].isin(interval)]['user'].to_list()
        #create dataset for node, consisting of all ratings of users above, and without item
        child_dataset = functionDF[functionDF['item']!=item]
        child_dataset = child_dataset[child_dataset['user'].isin(users)]
        #add child to current node      #path is 0 for dislike
        node.rchild = self.createTree(child_dataset,node,depth+1,1)
        return node
    #split total frame into subframes
    def splitDataFrame(self, df, amount=10):
        items = df['item'].unique()
        #results in same split of dataset for different tries
        rng = np.random.RandomState(1)
        #shuffle items
        rng.shuffle(items)
        dfs = []
        size = (items.shape[0])//amount
        #append subsets to dfs
        for i in range(amount):
            if i == amount+1:
                subItems = items[i*size:]
            subItems = items[i*size:(i+1)*size]
            temp = df[df['item'].isin(subItems)]
            dfs.append(temp)
        return dfs
    #visualize tree
    def visualize(self,title=True):
        print('not implemented')
        return

    #get node for certain item
    def getNode(self, ratings):
        node = self.root
        for r in ratings:
            if r > 3:
                node = node.rchild
            else:
                node = node.lchild
        return node
    
################# class containing functions that determine item of node #################
#return a random item of the dataset
class SplitFunction:
    #return a random item of dataset
    #input = pandas dataset
    #output = proposed items itemID
    def randomSplit(df):
        items = list(df['item'].unique())
        if len(items) == 0:
            return False
        index = np.random.randint(len(items))
        return items[index]

    #return the most popular item of the dataset
    #input = pandas dataset
    #output = proposed items itemID
    def popularSplit(df):
        if(df.shape[0]==0):
            return False
        return df['item'].value_counts().idxmax()
    
    #return the  popular random item of the dataset
    #input = pandas dataset
    #output = proposed items itemID
    def popularRandomSplit(df):
        if(df.shape[0]==0):
            return False
        temp = df.groupby('item',as_index=False).size().sort_values('size')
        quant = temp['size'].quantile(0.9)
        temp = temp[temp['size']>=quant]
        index = np.random.randint(temp.shape[0])
        return temp.iloc[index]['item']
    
    #returns the highest log(popular)*entropy item of dataset
    def logPopEntropySplit(df):
        if(df.shape[0]==0):
            return False
        #get counts of every item
        counts = df['item'].value_counts().reset_index()
        counts.rename(columns={'item': 'count', 'index': 'item'}, inplace=True)
        #merge with entropy dataset
        merged = pd.merge(counts,df,on='item')
        #create log(pop)*entropy
        merged['popentr'] = np.log(merged['count'])*merged['entr']
        #find max item
        item = merged.loc[merged['popentr'].idxmax()]['item']
        return int(item)
    
    
################# class containing functions for the intervals of the children #################
class IntervalFunction:
    #function returns hard coded intervals used to determine dataset of children
    #input = int
    #output = list of list containing intervals
    def getIntervals(width):
        if width == 2:
            #list returns [dislike,like] intervals
            return [[0.5,1,1.5,2,2.5],[3,3.5,4,4.5,5]]
        if width == 3:
            #list returns [dislike, average, like] intervals
            return [[0.5,1,1.5],[2,2.5,3,3.5],[4,4.5,5]]
        if width == 4:
            #list returns [strong dislike, weak dislike, weak like, strong like] intervals
            return [[0.5,1],[1.5,2,2.5],[3,3.5,4],[4.5,5]]
        if width == 5:
            #list returns [strong dislike, weak dislike, average, weak like, strong like] intervals
            return [[0.5,1],[1.5,2],[2.5,3],[3.5,4],[4.5,5]]
        else:
            print('Wrong amount given')
            return None

    #function returns the intervals used to determine dataset of children based on the current dataset
    #input = pandas dataframe and width
    #output = is a list of intervals
    def getDynamicIntervals(df,width):
        return None
    #function returns the names of each interval, is used in plotting trees
    #input = int
    #output = hardcoded list with edge names
    def edgeNames(width):
        if width == 2:
            return ['Dislike','Like']
        if width == 3:
            return ['Dislike','Average','Like']
        if width == 4:
            return ['Strong Dislike', 'Weak Dislike', 'Weak Like', 'Strong Like']
        if width == 5:
            return ['Strong Dislike', 'Weak Dislike','Average', 'Weak Like', 'Strong Like']
        else:
            print('Wrong amount given')
            return None