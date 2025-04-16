from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(message: str) -> str:
    scores = analyzer.polarity_scores(message)
    compound = scores['compound']
    
    if compound >= 0.5:
        return "positive"
    elif compound <= -0.5:
        return "negative"
    else:
        return "neutral"
