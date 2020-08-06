# -*- coding: utf-8 -*-
"""FLIGHT DELAY.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bL6j0zRd-YsD6s0PaIDj7X1Wc1BpEk6X
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
import math
import category_encoders as ce

data = pd.read_csv("/content/FlightDelayProject (6).csv")
data.head()

l = data['Used Date'][0] 
temp = re.findall(r'\d+', l) 
res = np.array(list(map(int, temp)))    

for i in range(1,data.shape[0]):
    l = data['Used Date'][i] 
    temp = re.findall(r'\d+', l) 
    a = np.array(list(map(int, temp)))
    res = np.concatenate([res,a] , axis = 0) 
r = np.reshape(res,(-1,3))
r.shape
d = pd.DataFrame(r)
d = d.rename(columns = {0:'Date',1:'Month',2:'Year'})
data = pd.concat([data,d],axis = 1)

data.head()

data = data.drop(['Used Date'],axis = 1)
data.head()

data = pd.get_dummies(data=data, columns = ['From','To','Airline'])

data.head()

data = data.drop(['From_BLR','To_BOM','Airline_Air Asia'],axis = 1)

data = data.drop(7).reset_index(drop = True)

l1 = data.index[data['Arrival'] == '-1'].tolist()
l2 = data.index[data['Scheduled Arrival'] == '-1'].tolist()

data = data.drop(l1).reset_index(drop = True)
data = data.drop(l2).reset_index(drop = True)

data = data.drop(['SDEP','Departure','DEP','Scheduled Departure'],axis = 1)
data = data.drop('Departure Delay',axis = 1)

for i in range(data.shape[0]):
    if data['ARR'][i] - math.floor(data['ARR'][i]/100)*100 >= 30:
        data['ARR'][i] = math.ceil(data['ARR'][i]/100)
    else:
        data['ARR'][i] = math.floor(data['ARR'][i]/100)

data = data.drop(['Category'],axis = 1)

pd.get_dummies(data, columns = ['weather__hourly__weatherDesc__value'])

ce_bin = ce.BinaryEncoder(cols = ['weather__hourly__weatherDesc__value'])
ce_bin.fit(data,data['Arrival Delay'])

d = ce_bin.transform(data)

data = d

from datetime import datetime
d = pd.DataFrame(np.zeros((data.shape[0],2)))
# arr_t1 = datetime.strptime(data['Arrival'][0],'%H:%M')
# arr_t2 = datetime.strptime(data['Scheduled Arrival'][0],'%H:%M')
# diff = arr_t1 - arr_t2   
# diff = str(diff)
# d.append(diff)
# print(type(diff))
print(d)
for i in range(data.shape[0]):
    arr_t1 = datetime.strptime(data['Arrival'][i],'%H:%M')
    arr_t2 = datetime.strptime(data['Scheduled Arrival'][i],'%H:%M')
    if arr_t1 >= arr_t2:
        dif = str(arr_t1 - arr_t2)
        print(arr_t1,arr_t2)
        print(i,dif)
        print('\n')
        d[0][i] = dif
    if arr_t1 < arr_t2:
        dif = str(arr_t2 - arr_t1)
        print(arr_t1,arr_t2)
        print(i,dif)
        print('\n')
        d[0][i] = dif
        d[1][i] = 1

for i in range(data.shape[0]):
    temp = re.findall(r'\d+', d[0][i]) 
    res = np.array(list(map(int, temp))).tolist()
    mins = res[0]*60 + res[1]
    if d[1][i] == 0:
        data['Arrival Delay'][i] = mins
    if d[1][i] == -1:
        data['Arrival Delay'][i] = -mins

Out = data.index[data['Arrival Delay'] > 300].tolist()
data = data.drop(Out).reset_index(drop = True)

data = data.drop(['Scheduled Arrival','Arrival'], axis = 1)

data = data.drop(['SARR'],axis = 1)

data_noweather = data.drop(['weather__hourly__windspeedKmph',
       'weather__hourly__weatherDesc__value_0',
       'weather__hourly__weatherDesc__value_1',
       'weather__hourly__weatherDesc__value_2',
       'weather__hourly__weatherDesc__value_3',
       'weather__hourly__weatherDesc__value_4',
       'weather__hourly__weatherDesc__value_5', 'weather__hourly__precipMM',
       'weather__hourly__humidity', 'weather__hourly__visibility',
       'weather__hourly__pressure', 'weather__hourly__cloudcover'], axis = 1)

ser = pd.DataFrame(np.zeros((data.shape[0],1)),columns = {"Holiday"})

data = pd.concat([data,ser],axis = 1)

Holidays = ["15-01-2019","26-01-2019","21-02-2019","10-03-2019","06-04-2019","25-05-2019","15-08-2019","22-08-2019","02-10-2019","25-10-2019","24-10-2019","14-11-2019","25-12-2019","26-01-2020"]      

for i in range(data.shape[0]):
    for j in Holidays:
        temp = re.findall(r'\d+', j) 
        res = np.array(list(map(int, temp))).tolist()
        if data['Date'][i] == res[0] and data['Month'][i] == res[1] and data['Year'][i] == res[2]:
            data['Holiday'][i] = 1

data.head()

from sklearn.model_selection import train_test_split as tts
X_train, X_test, y_train, y_test = tts(data.drop('Arrival Delay', axis = 1),data['Arrival Delay'], test_size = 0.2, random_state = 2)

print(X_train.shape)
print(X_test.shape)
print(y_train.shape)
print(y_test.shape)

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

xgb = RandomForestRegressor(n_estimators = 100,min_samples_split = 6,max_features = 20,n_jobs = -1,random_state = 1)

xgb.fit(X_train,y_train)
y_pred_train = xgb.predict(X_train)
y_pred_test = xgb.predict(X_test)
print(mean_squared_error(y_pred_train,y_train))
print(mean_squared_error(y_pred_test,y_test))
print(r2_score(y_pred_train,y_train))
print(r2_score(y_pred_test,y_test))

plt.hist(data['Arrival Delay'])
plt.show()

xgb.feature_importances_.argmin()

data = data.drop(['Status'],axis = 1)
data = data.drop(['weather__hourly__windspeedKmph'],axis = 1)

xgb.feature_importances_

for i in range(data.shape[0]):
    if data['Arrival Delay'][i] < 0 :
        data['Arrival Delay'][i] = -1
    if data['Arrival Delay'][i] > 0 and data['Arrival Delay'][i] < 10:
        data['Arrival Delay'][i] = 1
    if data['Arrival Delay'][i] >= 10 and data['Arrival Delay'][i] < 20:
        data['Arrival Delay'][i] = 2
    if data['Arrival Delay'][i] >= 20 and data['Arrival Delay'][i] < 30:
        data['Arrival Delay'][i] = 3
    if data['Arrival Delay'][i] >= 30 and data['Arrival Delay'][i] < 40:
        data['Arrival Delay'][i] = 4
    if data['Arrival Delay'][i] >= 40: 
        data['Arrival Delay'][i] = 5

data['Arrival Delay'].value_counts()

def loss_func(y_true,y_pred):
    loss = 0
    for i in range(y_true.size):
        diff = abs(y_true[i] - y_pred[i])
        loss += diff
    return loss

X_train

import xgboost
from sklearn.model_selection import RandomizedSearchCV
xgb = xgboost.XGBClassifier(n_estimators = 100,max_depth = 5, learning_rate = 0.1,booster = "gbtree",n_jobs = -1,gamma = 0.1,reg_alpha = 0.1, reg_lambda = 0.1,random_state = 1)
dist = {"n_estimators" : np.arange(100,200), "max_depth" : np.arange(2,10), "learning_rate" : np.linspace(0.1,1,10),"gamma" : np.linspace(0.1,1,10),"reg_alpha" : np.linspace(0.1,1,10), "reg_lambda" :  np.linspace(0.1,1,10)}
RCV = RandomizedSearchCV(xgb,dist,random_state = 2,n_iter = 100)
ran_fit = RCV.fit(X_train,y_train)
# from sklearn.metrics import accuracy_score

# xgb.fit(X_train,y_train)



print(ran_fit.best_estimator_)

xgb = xgboost.XGBClassifier(base_score=0.5, booster='gbtree', colsample_bylevel=1,
              colsample_bynode=1, colsample_bytree=1, gamma=1.0,
              learning_rate=0.30000000000000004, max_delta_step=0, max_depth=8,
              min_child_weight=1, missing=None, n_estimators=144, n_jobs=-1,
              nthread=None, objective='multi:softprob', random_state=1,
              reg_alpha=0.7000000000000001, reg_lambda=0.7000000000000001,
              scale_pos_weight=1, seed=None, silent=None, subsample=1,
              verbosity=1)
xgb.fit(X_train,y_train)
print(accuracy_score(xgb.predict(X_train),y_train))
print(accuracy_score(xgb.predict(X_test),y_test))

xgb = xgboost.XGBClassifier(base_score=0.5, booster='gbtree', colsample_bylevel=1,
              colsample_bynode=1, colsample_bytree=1, gamma=0.9,
              learning_rate=0.2, max_delta_step=0, max_depth=8,
              min_child_weight=1, missing=None, n_estimators=139, n_jobs=-1,
              nthread=None, objective='multi:softprob', random_state=1,
              reg_alpha=0.7000000000000001, reg_lambda=0.8, scale_pos_weight=1,
              seed=None, silent=None, subsample=1, verbosity=1)
xgb.fit(X_train,y_train)
print(accuracy_score(xgb.predict(X_train),y_train))
print(accuracy_score(xgb.predict(X_test),y_test))

np.where(xgb.feature_importances_ == 0)

