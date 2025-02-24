# -*- coding: utf-8 -*-
"""twittersentimentalanalysis.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1mfRVre1Rh0qE1snwabAoqRomhQyM0F28
"""

#importing req. Lib.
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import re
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,confusion_matrix,classification_report

#load our data set
data = pd.read_csv(r'/content/Tweets.csv (2).zip')



data

data.shape

#looking into our data
data.head()

data.tail()

#checking columns in our data
data.columns

#checking info our data
data.info()

#checking unique values
data.nunique()

#checking null values in our data
data.isnull().sum()

"""Preprocessing on data

tweet_created column got the date recorts and showing type is object we have to change it of date time format
"""

data['tweet_created'] = pd.to_datetime(data['tweet_created']).dt.date

data['tweet_created'] = pd.to_datetime(data['tweet_created'])

data.info()

data.head()

data['tweet_created'].min()

data['tweet_created'].max()

"""we have data from 16th feb 2015 to 25 feb 2015 mins we have data of 9 days"""

#checking uniques values in tweet_created columns
data['tweet_created'].nunique()

numberoftweets = data.groupby('tweet_created').size()

numberoftweets.dtype

numberoftweets

"""treating with null values"""

data.isna().sum()

print("Percentage null or na values in df")
((data.isnull() | data.isna()).sum() * 100 / data.index.size).round(2)

"""airline_sentiment_gold, negativereason_gold have more than 99% missing data And tweet_coord have nearly 93% missing data. It will be better to delete these columns as they will not provide any constructive informatio"""

del data['tweet_coord']
del data['airline_sentiment_gold']
del data['negativereason_gold']
data.head()

freq = data.groupby('negativereason').size()

freq

"""we cant fill it will affect in bad way for example we have positive reviwe and we fill the values with mode that means with Customer Service Issue it is missmatch and can be affect on train model so we keep the data as it is

EDA

Count of Type of Sentiment
"""

counter = data.airline_sentiment.value_counts()
index = [1,2,3]
plt.figure(1,figsize=(12,6))
plt.bar(index,counter,color=['green','red','blue'])
plt.xticks(index,['negative','neutral','positive'],rotation=0)
plt.xlabel('Sentiment Type')
plt.ylabel('Sentiment Count')
plt.title('Count of Type of Sentiment')

"""Airline sentiments for each airline"""

#checking differtent airlines we have
data['airline'].unique()

print("Total number of tweets for each airline \n ",data.groupby('airline')['airline_sentiment'].count().sort_values(ascending=False))
airlines= ['US Airways','United','American','Southwest','Delta','Virgin America']
plt.figure(1,figsize=(12, 12))
for i in airlines:
    indices= airlines.index(i)
    plt.subplot(2,3,indices+1)
    new_df=data[data['airline']==i]
    count=new_df['airline_sentiment'].value_counts()
    Index = [1,2,3]
    plt.bar(Index,count, color=['red', 'green', 'blue'])
    plt.xticks(Index,['negative','neutral','positive'])
    plt.ylabel('Mood Count')
    plt.xlabel('Mood')
    plt.title('Count of Moods of '+i)

"""Looks like people are not having pleasant flights these days. It is important to know which airline pleases their costumers the most and vice versa, so we sill be looking at the percentage of the negative reviews for each airline."""

neg_tweets = data.groupby(['airline','airline_sentiment']).count().iloc[:,0]
total_tweets = data.groupby(['airline'])['airline_sentiment'].count()

my_dict = {'American':neg_tweets[0] / total_tweets[0],'Delta':neg_tweets[3] / total_tweets[1],'Southwest': neg_tweets[6] / total_tweets[2],
'US Airways': neg_tweets[9] / total_tweets[3],'United': neg_tweets[12] / total_tweets[4],'Virgin': neg_tweets[15] / total_tweets[5]}
perc = pd.DataFrame.from_dict(my_dict, orient = 'index')
perc.columns = ['Percent Negative']
print(perc)
ax = perc.plot(kind = 'bar', rot=0, colormap = 'Greens_r', figsize = (15,6))
ax.set_xlabel('Airlines')
ax.set_ylabel('Percentage of negative tweets')
plt.show()

"""- United, US Airways, American substantially get negative reactions.
- Tweets for Virgin America are the most balanced.
"""

figure_2 = data.groupby(['airline', 'airline_sentiment']).size()
figure_2.unstack().plot(kind='bar', stacked=True, figsize=(15,10))

print(figure_2)

"""Last but not least, people complain for many reasons about their flights; 10 reasons to be specific"""

negative_reasons = data.groupby('airline')['negativereason'].value_counts(ascending=True)
negative_reasons.groupby(['airline','negativereason']).sum().unstack().plot(kind='bar',figsize=(22,12))
plt.xlabel('Airline Company')
plt.ylabel('Number of Negative reasons')
plt.title("The number of the count of negative reasons for airlines")
plt.show()

"""What are the reasons for negative sentimental tweets for each airline ?
We will explore the negative reason column of our dataframe to extract conclusions about negative sentiments in the tweets by the customers
"""

#get the number of negative reasons
data['negativereason'].nunique()

NR_Count=dict(data['negativereason'].value_counts(sort=False))
def NR_Count(Airline):
    if Airline=='All':
        a=data
    else:
        a=data[data['airline']==Airline]
    count=dict(a['negativereason'].value_counts())
    Unique_reason=list(data['negativereason'].unique())
    Unique_reason=[x for x in Unique_reason if str(x) != 'nan']
    Reason_frame=pd.DataFrame({'Reasons':Unique_reason})
    Reason_frame['count']=Reason_frame['Reasons'].apply(lambda x: count[x])
    return Reason_frame
def plot_reason(Airline):

    a=NR_Count(Airline)
    count=a['count']
    Index = range(1,(len(a)+1))
    plt.bar(Index,count, color=['red','yellow','blue','green','black','brown','gray','cyan','purple','orange'])
    plt.xticks(Index,a['Reasons'],rotation=90)
    plt.ylabel('Count')
    plt.xlabel('Reason')
    plt.title('Count of Reasons for '+Airline)

plot_reason('All')
plt.figure(2,figsize=(13, 13))
for i in airlines:
    indices= airlines.index(i)
    plt.subplot(2,3,indices+1)
    plt.subplots_adjust(hspace=0.9)
    plot_reason(i)

"""- Customer Service Issue is the main neagtive reason for US Airways,United,American,Southwest,Virgin America
- Late Flight is the main negative reason for Delta
- Interestingly, Virgin America has the least count of negative reasons (all less than 60)
- Contrastingly to Virgin America, airlines like US Airways,United,American have more than 500 negative reasons (Late flight, Customer Service Issue)

Is there a relationship between negative sentiments and date?

It will be interesting to see if the date has any effect on the sentiments of the tweets(especially negative !). We can draw various coclusions by visualizing this.
"""

date = data.reset_index()
#convert the Date column to pandas datetime
date.tweet_created = pd.to_datetime(date.tweet_created)
#Reduce the dates in the date column to only the date and no time stamp using the 'dt.date' method
date.tweet_created = date.tweet_created.dt.date
date.tweet_created.head()
df = date
day_df = df.groupby(['tweet_created','airline','airline_sentiment']).size()
# day_df = day_df.reset_index()
day_df

# Reset the index to convert the groupby result to a DataFrame
day_df = day_df.reset_index()

# Rename columns for clarity
day_df.columns = ['Date', 'Airline', 'Sentiment', 'Count']

# Convert Date to datetime for proper plotting (if not already done)
day_df['Date'] = pd.to_datetime(day_df['Date'])

# Plot the data using seaborn
plt.figure(figsize=(14, 7))
sns.lineplot(
    data=day_df,
    x='Date',
    y='Count',
    hue='Sentiment',  # Color by sentiment
    style='Airline',  # Different line styles for each airline
    markers=True,
    dashes=False
)

# Add title and labels
plt.title('Tweet Sentiment Trends by Airline', fontsize=16)
plt.xlabel('Date', fontsize=14)
plt.ylabel('Tweet Count', fontsize=14)

# Rotate the x-axis labels for better readability
plt.xticks(rotation=45)

# Customize the legend to show both sentiment and airline
plt.legend(title='Sentiment & Airline', bbox_to_anchor=(1.05, 1), loc='upper left')

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plot
plt.show()

"""- Interestingly, American has a sudden upsurge in negative sentimental tweets on 2015-02-23, which reduced to half the very next day 2015-02-24. (I hope American is doing better these days and resolved their Customer Service Issue as we saw before)
- Virgin America has the least number of negative tweets throughout the weekly data that we have. It should be noted that the total number of tweets for Virgin America was also significantly less as compared to the rest airlines, and hence the least negative tweets.
- The negative tweets for all the rest airlines is slightly skewed towards the end of the week !

Wordcloud for positive reasons
"""

from wordcloud import WordCloud,STOPWORDS

# Filter the data to get positive sentiment tweets
new_df = data[data['airline_sentiment'] == 'positive']

# Join all the text from the filtered data
words = ' '.join(new_df['text'])

# Clean the text by removing URLs, @mentions, and retweets (RT)
cleaned_word = " ".join([word for word in words.split()
                         if 'http' not in word
                         and not word.startswith('@')
                         and word != 'RT'
                         ])

# Generate the word cloud with a vibrant and engaging design
wordcloud = WordCloud(
    stopwords=STOPWORDS,                # Remove common stopwords
    background_color='white',           # Set a white background for a brighter look
    width=2500,                         # Image width
    height=2000,                        # Image height
    colormap='YlGnBu',                  # Use a color palette with a gradient (yellow to blue)
    contour_color='yellow',             # Set the contour color to yellow to highlight words
    contour_width=2,                    # Set contour width for a soft boundary
    max_words=200,                      # Limit to the top 200 words
    max_font_size=100,                  # Set max font size
    random_state=42                     # Set random state for reproducibility
).generate(cleaned_word)

# Display the word cloud with the updated design
plt.figure(figsize=(12, 12))            # Set the figure size
plt.imshow(wordcloud, interpolation='bilinear')  # Use bilinear interpolation for smooth output
plt.axis('off')                         # Remove axis for a cleaner look
plt.show()

"""Wordcloud for Negative sentiments of tweets"""

# Filter the data to get negative sentiment tweets
new_df = data[data['airline_sentiment'] == 'negative']

# Join all the text from the filtered data
words = ' '.join(new_df['text'])

# Clean the text by removing URLs, @mentions, and retweets (RT)
cleaned_word = " ".join([word for word in words.split()
                         if 'http' not in word
                         and not word.startswith('@')
                         and word != 'RT'
                         ])

# Load a custom mask (for example, a circular mask or other shapes)
# mask = np.array(Image.open('path_to_image.png'))  # Un-comment if you have a custom mask image

# Generate the word cloud with a different shape and color
wordcloud = WordCloud(
    stopwords=STOPWORDS,
    background_color='white',  # Background color changed to white
    width=2500,                # Width of the image
    height=2000,               # Height of the image
    colormap='plasma',         # Use a different color palette
    contour_color='black',     # Add a contour around the words
    contour_width=1,           # Contour width
    max_words=200,             # Limit the number of words
    max_font_size=100,         # Set the max font size for the words
    font_path=None,            # Path to custom font (optional)
    random_state=42            # Set a seed for reproducibility
    # mask=mask                # Apply a custom shape if using an image mask
).generate(cleaned_word)

# Display the word cloud
plt.figure(figsize=(12, 12))  # Set the figure size
plt.imshow(wordcloud, interpolation='bilinear')  # Display the word cloud image
plt.axis('off')  # Remove axis
plt.show()

"""Droping the rows with neutral sentiments"""

data.drop(data.loc[data['airline_sentiment']=='neutral'].index, inplace=True)

"""label encoding on airline_sentiment"""

from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
le.fit(data['airline_sentiment'])

data['airline_sentiment_encoded'] = le.transform(data['airline_sentiment'])
data.head()

"""Preprocessing the tweet text data

Now, we will clean the tweet text data and apply classification algorithms on it
"""

def tweet_to_words(tweet):
    letters_only = re.sub("[^a-zA-Z]", " ",tweet)
    words = letters_only.lower().split()
    stops = set(stopwords.words("english"))
    meaningful_words = [w for w in words if not w in stops]
    return( " ".join( meaningful_words ))

nltk.download('stopwords')
data['clean_tweet']=data['text'].apply(lambda x: tweet_to_words(x))

"""Vectorization"""

x = data.clean_tweet
y = data.airline_sentiment

print(len(x), len(y))

"""The data is split in the standard 80,20 ratio"""

x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=42)
print(len(x_train), len(y_train))
print(len(x_test), len(y_test))

# Import CountVectorizer from sklearn
from sklearn.feature_extraction.text import CountVectorizer

# Step 1: Text Vectorization with N-grams
vect = CountVectorizer(ngram_range=(2, 2))  # Using bigrams
X_train_vec = vect.fit_transform(x_train)
X_test_vec = vect.transform(x_test)

# Step 2: Train a Random Forest Classifier
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)  # Ensemble learning
rf_model.fit(X_train_vec, y_train)

# Step 3: Predict and Evaluate
y_pred = rf_model.predict(X_test_vec)

print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:\n", classification_report(y_test, y_pred))

"""Random forest accuracy"""

from sklearn.feature_extraction.text import CountVectorizer

# instantiate the vectorizer
vect = CountVectorizer()
vect.fit(x_train)

# Use the trained to create a document-term matrix from train and test sets
x_train_dtm = vect.transform(x_train)
x_test_dtm = vect.transform(x_test)

vect_tunned = CountVectorizer(stop_words='english', ngram_range=(1,2), min_df=0.1, max_df=0.7, max_features=100)
vect_tunned

"""Model Building

"""

#training SVM model with linear kernel
#Support Vector Classification-wrapper around SVM
from sklearn.svm import SVC
model = SVC(kernel='linear', random_state = 10)
model.fit(x_train_dtm, y_train)
#predicting output for test data
pred = model.predict(x_test_dtm)

#accuracy score
accuracy_score(y_test,pred)

print(classification_report(y_test,pred))



"""negative 0.94 0.94 0.94 2323: This line shows the performance for the "negative" class: * Precision: 0.94 means that out of all the tweets the model predicted as negative, 94% were actually negative. * Recall: 0.94 means that out of all the actually negative tweets, the model correctly identified 94% of them. * F1-score: 0.94 is a balanced measure combining precision and recall, also indicating strong performance for this class. * Support: 2323 is the number of actual negative tweets in your test data.

- As we you can see above we have plotted the confusion matrix for predicted sentiments and actual sentiments (negative and positive)
- SVM Classifier gives us the best accuracy score i.e 91% precision scores according to the classification report.
)

Thank You
"""