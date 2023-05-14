#read in data
import numpy as np
import pandas as pd

############################### 25M dataset ###############################
#function for getting the ratings data
#input: None
#output: Pandas datafram
#first row of the array is the header (userId,movieId,rating,timestamp)
def InitRatingsData25M():
    data = pd.read_csv("./dataset25M/ratings.csv")
    return data

#function for getting the ratings data
#input: None
#output: Pandas datafram
#first row of the array is the header (movieId,title,genres)
#genres contained: * Action* Adventure* Animation* Children's* Comedy* Crime* Documentary* Drama* Fantasy* Film-Noir* Horror* Musical* Mystery* Romance* Sci-Fi* Thriller* War* Western * (no genres listed)
def InitMoviesData25M():
    data = pd.read_csv("./dataset25M/movies.csv")
    return data

#function for getting the tags data
#input: None
#output: Pandas datafram
#first row of the array is the header (userId,movieId,tag,timestamp)
def InitTagsData25M():
    data = pd.read_csv("./dataset25M/tags.csv")
    return data

#function for getting the links data
#input: None
#output: Pandas datafram
#first row of the array is the header (movieId,imdbId,tmdbId)
def InitLinksData25M():
    data = pd.read_csv("./dataset25M/links.csv")
    return data

#function for getting the ratings data put only a subset where a fraction of the users is used.
#input: integer split
#output: Pandas datafram
#first row of the array is the header (userId,movieId,rating,timestamp)
def InitRatingsData25MSmall(fraction):
    #results in same split of dataset for different tries
    rng = np.random.RandomState(1)
    data = pd.read_csv("./dataset25M/ratings.csv")
    all_users = data['userId'].unique()
    #create subset of users
    sub_users = rng.choice(all_users,
                           np.shape(all_users)[0]//fraction,
                           replace=False)
    #filter out users
    data = data[data['userId'].isin(sub_users)]
    return data
    
def InitRatingsSubSet(fraction):
    #get user based split of dataset
    df = InitRatingsData25MSmall(fraction)
    #set seed
    rng = np.random.RandomState(1)
    #counts of movie occurences
    counts = df['movieId'].value_counts()
    #hard coded manipulation
    fractions = [1]+[0.7/(i**2) for i in range(1,11)]
    tot_removables = np.array([0])
    #change items with less than 10 ratings
    for i in range(1,11):
        #get all itemids with i ratings
        items = counts[counts==i].index.to_numpy()
        #find itemids to filter out
        size = np.shape(items)[0]*fractions[i]
        removables = rng.choice(items,int(size),replace=False)
        #add to all item ids that need to be removed
        tot_removables = np.concatenate((tot_removables,removables))
    #edit dataset
    df = df[~df['movieId'].isin(tot_removables)]
    return df