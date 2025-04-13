import csv
import os
import torch
from torch import nn

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("mushroom_dataset_enum.csv")

features = [col for col in df.columns if col != 'class' and col != 'poison' and col != 'edible' and col != "Unnamed: 0"]
target = ["poison", 'edible']

class MSE_Loss(nn.Module):
    def __init__(self):
        super().__init__()
    
    def forward(self, y_pred, y_true):
        # Implementation of custom loss calculation
        diff = torch.sub(y_true, y_pred)
        return torch.mean(torch.square(diff))

class neural_network(nn.Module):
    def __init__(self, n = 1000):
        super().__init__()
        self.embeddings = []

        count = 0
        for feature in features:
            n_categories = df[feature].nunique()
            embed_dim = n_categories#min(50, (n_categories + 1) // 2)
            count+=embed_dim
            self.embeddings.append(nn.Embedding(n_categories, embed_dim))
        
        self.model = nn.Sequential(
            nn.Linear(count, n),
            nn.Sigmoid(),
            nn.Linear(n, n),
            nn.Sigmoid(),
            nn.Linear(n, n),
            nn.Sigmoid(),
            nn.Linear(n, n),
            nn.Sigmoid(),
            nn.Linear(n, n),
            nn.Sigmoid(),
            nn.Linear(n, 2),
            nn.Softmax(dim=1)
        )
        

    def forward(self, x):
        embed_inputs = []
        for feature_index in range(len(features)):
            embed = self.embeddings[feature_index](x[:,feature_index])
            embed_inputs.append(embed)
            #print(embed.shape)
        #print(x[:5], torch.cat(embed_inputs, dim = 1)[:5,:10])
        x = torch.cat(embed_inputs, dim = 1)
        #print(x[0,:10])
        #print(x.shape)
        return self.model(x)


# takes in dataframe for data
def train(model, optimizer, data, loss_funct, batches = 100, batch_size = 100):

    for epoch in range(100):
        shuffled = data.sample(frac = 1)
        x = torch.from_numpy(shuffled[features].values).int()
        y = torch.from_numpy(shuffled[target].values).float()
        running_loss = 0.0

        for i in range(min(batches, int(data.shape[0]/batch_size))):#range(data.shape[0]):
            inputs = x[batch_size*i : batch_size*(i+1)]
            labels = y[batch_size*i : batch_size*(i+1)]

            optimizer.zero_grad()

            #print(torch.sum(inputs,dim=1))
            #print(torch.sum(inputs,dim=1).shape)
            #print("try:")
            #print(inputs[:5])
            outputs = model(inputs)
            #print(outputs[:5])
            loss = loss_funct(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()
            if i % min(batches, int(data.shape[0]/batch_size)) == min(batches, int(data.shape[0]/batch_size)) - 1:    # print every 10 mini-batches
                print(f'[{epoch + 1}, {i + 1:5d}] loss: {running_loss/10 :.5f}')
                print("example: ", "predicted", outputs[0:5].detach(), ", actual", labels[0:5],'\n')
                running_loss = 0.0
        print("------------------------------")


def evaluate_loss(model, data, loss_funct):
    x = torch.from_numpy(data[features].values).int()
    y = torch.from_numpy(data[target].values).float()
    pred = model(x)
    print("example:",pred[0], y[0],'\n')
    return loss_funct(pred, y)

def evaluate_acc(model, data) :
    x = torch.from_numpy(data[features].values).int()
    y = torch.from_numpy(data[target].values).int()
    y_hat = model(x)
    pred = torch.tensor([1 if i[0] >= 0.5 else 0 for i in y_hat])
    print(y_hat)
    #print(y[:,0])
    return 1-torch.sum(torch.abs(pred-y[:,0])).item()/pred.shape[0]

def split(data, train_ratio = 0.8, validation_ratio = 0.1):
    shuffled = data.sample(frac = 1)
    divider1 = int(train_ratio*shuffled.shape[0])
    divider2 = int((train_ratio+validation_ratio) * shuffled.shape[0])
    train_set = shuffled[:divider1]
    valid_set = shuffled[divider1 : divider2]
    test = shuffled[divider2:]
    return train_set, valid_set, test



train_set, valid_set, test_set  = split(df)
#train_set = train_set[train_set['poison']==1]
#train_set.to_csv("test.csv")

model = neural_network(n = 1000)
optimizer = torch.optim.SGD(model.parameters(), lr=0.001)

print(f'[  base  ] loss: {evaluate_loss(model, train_set, MSE_Loss()) :.5f}')
train(model, optimizer, train_set, MSE_Loss())
torch.save(model.state_dict(), "nn_MSE")
print("training:", evaluate_acc(model, train_set))
print("test:", evaluate_acc(model, test_set))

#print(x.dtypes)

'''models = []
for i in range(1, 10, 1):
    percentile = 0.1*i
    model = quantile_regression()
    optimizer = torch.optim.SGD(model.parameters(), lr=0.00001, momentum=0.9)

    
    train(model, optimizer, df, quantile_loss())
    models.append(model)
    torch.save(model.state_dict(), "quantile_regression"+str(int(percentile*100))+"percentile")
    print("saved percentile regression " + str(percentile))'''