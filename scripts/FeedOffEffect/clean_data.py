import pandas as pd
import numpy as np
import warnings

## reading in round level data
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    round_data = pd.concat([pd.read_csv('~/GolfData/Round-Raw/%d.txt' % (year,), sep=';') 
                            for year in range(2003,2017)])

## making the columns easier to work with
round_data.columns = [col.replace(' ','_') for col in round_data.columns]

round_cols = ['Tournament_Year','Permanent_Tournament_#','Event_Name',
              'Course_#','Course_Name','Player_Number','Player_Name',
              'Round_Number','Tee_Time','Round_Score',
              'End_of_Round_Finish_Pos._(text)']
for col in round_data.columns:
    if col in round_cols:
        continue
    del round_data[col]

## I will drop this data since it seems to be missing the Tee Times
round_data = round_data[~((round_data.Tournament_Year==2003)
                          & (round_data.Event_Name=='Masters Tournament'))]

## drop match play data
round_data = round_data.loc[round_data['Permanent_Tournament_#']!=470]

## reading in hole level data and making columns easier to work with
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    hole_data = pd.concat([pd.read_csv('~/GolfData/Hole-Raw/%d.txt' % (year,), sep=';') 
                           for year in range(2003,2017)])
    hole_data.columns = [col.replace(' ','_') for col in hole_data.columns]


## re-naming Tournament_# field so it is compatible with other table
hole_data = hole_data.rename(columns={'Permanent_#':'Permanent_Tournament_#'})

## selecting only the columns that we'll need, deleting rest
hole_cols = ['Tournament_Year','Permanent_Tournament_#',
             'Player_Name','Player_#','Course_#','Hole_#',
             'Round_#','Hole_Seq_#','Score']
for col in hole_data.columns:
    if col in hole_cols:
        continue
    del hole_data[col]
    
## removing match play championship
hole_data = hole_data[hole_data['Permanent_Tournament_#']!=470]

## removing the masters in 2003
hole_data = hole_data[~((hole_data.Tournament_Year==2003) &
                        (hole_data['Permanent_Tournament_#']==14))]

## subsetting to only first hole of round, 
## dropping irrelevant fields, making dictionary
hole_data = hole_data[hole_data['Hole_Seq_#']==1]

hole_data.drop(['Player_Name','Score','Hole_Seq_#'],
               axis=1,inplace=True)

hole_data.set_index(['Tournament_Year','Permanent_Tournament_#',
                     'Player_#','Course_#','Round_#'],inplace=True)

start_hole = hole_data.squeeze().to_dict()

## inserting Hole Started On field
round_data['Hole_Started_On'] = [start_hole[(year,tourn,player,course,round_)]
                                 if (year,tourn,player,course,round_) in start_hole 
                                 else np.nan
                                 for year,tourn,player,course,round_ in 
                                 zip(round_data.Tournament_Year,
                                     round_data['Permanent_Tournament_#'],
                                     round_data['Player_Number'],
                                     round_data['Course_#'],
                                     round_data['Round_Number'])]

## dropping the few rounds that were not matched
round_data = round_data.dropna(subset=['Hole_Started_On'])

## tossing out groups with >3 players
group_sizes = round_data.groupby(['Tournament_Year',
                                  'Permanent_Tournament_#',
                                  'Course_#','Round_Number',
                                  'Tee_Time','Hole_Started_On'])\
                        .size().to_dict()
to_keep_mask = [1<group_sizes[(year,tourn,course,round_,
                               teetime,holestart)]<4
                for year,tourn,course,round_,teetime,holestart in
                zip (round_data.Tournament_Year,
                     round_data['Permanent_Tournament_#'],
                     round_data['Course_#'],
                     round_data['Round_Number'],
                     round_data['Tee_Time'],
                     round_data['Hole_Started_On'])]

round_data = round_data.loc[np.array(to_keep_mask)]

## inserting ave score for each course-round combo
ave_scores = round_data[['Tournament_Year','Permanent_Tournament_#',
                         'Course_#','Round_Number','Round_Score']]\
             .groupby(['Tournament_Year','Permanent_Tournament_#',
                      'Course_#','Round_Number'])['Round_Score']\
             .mean().to_dict()

round_data['Field_Ave'] = [ave_scores[(year,tourn,course,round_)]
                           for year,tourn,course,round_ in 
                           zip(round_data.Tournament_Year,
                               round_data['Permanent_Tournament_#'],
                               round_data['Course_#'],
                               round_data['Round_Number'])]

## inserting Strokes Gained to the Field
round_data['Strokes_Gained'] = round_data.Field_Ave - round_data.Round_Score

## recording correlation with future results of ewma precition
results = []
for halflife in np.linspace(2,80,40):
    df = round_data[['Player_Number','Strokes_Gained']].copy()
    df['prediction'] = df.groupby('Player_Number')['Strokes_Gained']\
                         .transform(lambda x: 
                                    x.shift(1)\
                                    .ewm(halflife=halflife).mean())
    df = df.dropna()
    results.append(np.corrcoef(df.Strokes_Gained,df.prediction)[0,1])

## inserting Expected Result and difference bettwen expected and true
halflife = np.linspace(2,80,40)[np.argmax(results)]
round_data['Exp_StrokesGained'] = round_data.groupby('Player_Number')\
                                  ['Strokes_Gained']\
                                  .transform(lambda x: x.shift(1)\
                                      .ewm(halflife=halflife).mean())

## first round for each player is null because no data 
## so filling with 0 which is saying he is expected to tie field
round_data.Exp_StrokesGained.fillna(0,inplace=True)
round_data['Net_Result'] = round_data['Strokes_Gained'] - round_data['Exp_StrokesGained']

round_data.to_csv('../../data/FeedOffEffect/clean_data.csv',index=False)