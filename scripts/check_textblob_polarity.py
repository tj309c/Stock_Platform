from textblob import TextBlob
s1='Company raises guidance and reports profit gains'
s2='Company misses revenue and issues a downward guidance'
print('s1:', TextBlob(s1).sentiment.polarity)
print('s2:', TextBlob(s2).sentiment.polarity)
