###############################################################################
#   Code written by Kareem Darwish (Qatar Computing Research Institute)
#   kdarwish@hbku.edu.qa
#   The code is provided for research purposes ONLY
###############################################################################

###############################################################################
# sys.argv[1] = current labels file (input) -- ex. trump.labels.0
#   format: userID\tLabel
# sys.argv[2] = tweets file (input) -- ex. trump.tsv
#   format: userID\tTweet
# sys.argv[3] = new label file (output) -- ex. trump.labels.1
#   format: userID\tLabel
# sys.argv[4] = gold labels for evaluation (input) -- ex. trump.labels
#   format: userID\tLabel
###############################################################################

from collections import defaultdict
import re
import sys

def cleanTweet(text):
    # removes URLs, RT, and user mentions, and perform case folding
    text = text.lower()
    text = re.sub('http\S+', '', text)
    text = re.sub(' +', ' ', text).strip()
    text = re.sub('@\S+', '', text).strip()
    text = re.sub('rt @\S+?\:', '', text).strip()
    return text

def labelPropagationTweets(labelFile, tweetsFile, threshold):
    # load training set (initial set of labeled users)
    userLabels = defaultdict()
    with open(labelFile) as f:
        for line in f:
            parts = line.strip().lower().split('\t')
            if len(parts) >= 2:
                userLabels[parts[0]] = parts[1]

    # load tweets of labeled users and assign user labels to tweets
    # if tweet is mentioned by different groups, it gets a tag of 'UNK' and is later ignored
    tweetLabels = defaultdict()
    with open(tweetsFile) as f:
        for line in f:
            parts = line.strip().lower().split('\t')
            if len(parts) >= 2:
                user = parts[0]
                tweet = cleanTweet(parts[1])
                if user in userLabels:
                    if tweet not in tweetLabels:
                        tweetLabels[tweet] = userLabels[user]
                    elif tweetLabels[tweet] != userLabels[user]:
                        tweetLabels[tweet] = 'UNK'

    # iterate over tweets of all unlabeled users, and count the number of tweets
    # they have retweeted from different groups
    newUserLabels = defaultdict()
    with open(tweetsFile) as f:
        for line in f:
            parts = line.strip().lower().split('\t')
            if len(parts) >= 2:
                user = parts[0]
                tweet = cleanTweet(parts[1])
                if tweet in tweetLabels and tweetLabels[tweet] != 'UNK':
                    if user not in newUserLabels:
                        newUserLabels[user] = dict()
                    if tweetLabels[tweet] not in newUserLabels[user]:
                        newUserLabels[user][tweetLabels[tweet]] = 1
                    else:
                        newUserLabels[user][tweetLabels[tweet]] += 1

    # if users have tweets with single labels that are more than the threshold
    # then add to the final list
    finalUserLabels = defaultdict()
    for user in newUserLabels:
        if len(newUserLabels[user]) == 1:
            for u in newUserLabels[user]:
                if newUserLabels[user][u] > threshold:
                    finalUserLabels[user] = u

    # put back the training set that we started with
    for user in userLabels:
        finalUserLabels[user] = userLabels[user]

    return finalUserLabels

def computeAccuracy(refFile, newFile):
    # load list of all labeled users
    userLabels = defaultdict()
    with open(refFile) as f:
        for line in f:
            parts = line.strip().lower().split('\t')
            if len(parts) >= 2:
                userLabels[parts[0]] = parts[1]

    # compute number of correct and incorrect users
    correct = 0
    incorrect = 0
    with open(newFile) as f:
        for line in f:
            parts = line.strip().lower().split('\t')
            if len(parts) >= 2:
                if userLabels[parts[0]] == parts[1]:
                    correct += 1
                else:
                    incorrect += 1

    accuracy = correct/(correct + incorrect)
    total = correct + incorrect
    print(str(accuracy) + ' (' + str(correct) + ' out of ' + str(total) + ')')


newUserLabels = labelPropagationTweets(sys.argv[1], sys.argv[2], 5)

with open(sys.argv[3], mode='w') as f:
    for user in newUserLabels:
        f.write(user + '\t' + newUserLabels[user] + '\n')

computeAccuracy(sys.argv[4], sys.argv[3])
