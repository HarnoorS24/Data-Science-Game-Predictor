import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

#just general info on data we have so far
#make any plot you want to see visual stuff

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

mikumikubeaaaaam = pd.read_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\relevant CSV files\cleaned_positive_critic_reviews.csv")

mikumikubeaaaaamREVIEWWWW = pd.read_csv(r"C:\Users\there\IdeaProjects\Data_Science_Project\scraped_positive_metacritic_user_reviews.csv")


#this is all done now
#drop the huge amount of dupes i had before i had 40K+
#monitoringbestsong = mikumikubeaaaaam.drop_duplicates()
#drop null values i have a couple and honestly i cant be boethered to manually find and add them 5ish games isnt going to be the dealbreaker
#monitoringbestsong = monitoringbestsong.dropna()
#reset the indices because they were still around 60K
#monitoringbestsong = monitoringbestsong.reset_index(drop=True)



print('--------------- Top 5 Games ---------------\n')

print(mikumikubeaaaaam.head())

print('\n--------------- Bottom 5 Games ---------------\n')

print(mikumikubeaaaaam.tail())

print('\n--------------- Description ---------------\n')

print(mikumikubeaaaaam.describe())

print('\n--------------- Info ---------------\n')

mikumikubeaaaaam.info()

#now we have a usable dataframe
#here now i will split the games by 'good' or 'bad'
#im splitting critic and user reviews here, because professionals are more likely to use different language compared to normal consumers
#normal users might use words like 'retard' or just complain about companies like ubisoft or EA which isn't not useful, but i need to separate that as something else


#we have different CSV's for this now
#goodcriticmiku = monitoringbestsong[monitoringbestsong['Metascore'] >= 70.0]
#evilcriticmiku = monitoringbestsong[monitoringbestsong['Metascore'] < 70.0]

#goodnormiemiku = monitoringbestsong[monitoringbestsong['User Score (out of 100)'] >= 70.0]
#evilnormiemiku = monitoringbestsong[monitoringbestsong['User Score (out of 100)'] < 70.0]

#positive scored games (by critics)
#goodcriticmiku.info()

#negatively scored games (by critics)
#evilcriticmiku.info()

#positively scored games (by users)
#goodnormiemiku.info()

#negatively scored games (by users)
#evilnormiemiku.info()

print(mikumikubeaaaaamREVIEWWWW.head())


