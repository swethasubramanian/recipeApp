from flask import render_template, request
from app import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import numpy as np

import pickle

from nltk.stem.wordnet import WordNetLemmatizer

from sqlCalls import *
#from processText import *

#from forms import inventory, inventoryAll
from collections import defaultdict

#import pandas_highcharts
import os
APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC = os.path.join(APP_ROOT, 'static')

@app.route('/')
@app.route('/index')
def index():
    with open(os.path.join(APP_STATIC, 'veggieslist2.txt'), "rb") as fo:
      veggiesAll1 = pickle.load(fo) 
    veggiesAll = sorted(veggiesAll1)
    veggiesAll.append('none')
    return render_template("index.html", veggiesall = veggiesAll)


def indexFake():
    form = inventoryAll()
    # Adding inventory to dictionary
    if form.validate_on_submit():
        veggieQuantity = defaultdict(float)
        veggieQuantity[form.veggie.data] = int(form.quantity.data)*1.0
        return render_template("index.html",
            form = form)
    else:
        return render_template("index2.html",
            form = form)


def lemmatizePhrase(phrase):
    """ 
    Lemmatize each word in a pharse
    """
    words = phrase.lower().split()
    return ' '.join(str(WordNetLemmatizer().lemmatize(word.encode('utf-8'))) for word in words)
   
    
def getScore(selDf, veggiesQuantity, vDf, numServings):
      selDf['score'] = 0.0
      for veggie in veggiesQuantity.keys():
        diffinQuantity = 1/(np.abs((selDf[veggie].astype(float)/selDf['num_servings'].astype(float)*numServings - veggiesQuantity[veggie]*1.0 ))+1)
        weight = 1/(vDf[vDf.veggie == veggie].shelf_life)
        product =  diffinQuantity*list(set(weight))[0]
        selDf['score'] = selDf['score'] + product
      selDf['score'] = selDf['score']*100
      selDf['recipe_name'] = selDf['index'].str.split('/').apply(lambda x: ' '.join(x[4].split('-')[:-1]).title())
      selDf = selDf.sort_values('score', ascending=False).head(50)
      return selDf



@app.route('/output')
def display_output():
    veggieQuantity = {lemmatizePhrase(str(request.args.get('veggie1')).replace(" ", "_")): int(request.args.get('quantity1')),\
                lemmatizePhrase(str(request.args.get('veggie2')).replace(" ", "_")): int(request.args.get('quantity2')),\
                lemmatizePhrase(str(request.args.get('veggie3')).replace(" ", "_")): int(request.args.get('quantity3')),\
                lemmatizePhrase(str(request.args.get('veggie4')).replace(" ", "_")): int(request.args.get('quantity4')),\
                lemmatizePhrase(str(request.args.get('veggie5')).replace(" ", "_")): int(request.args.get('quantity5'))}
    numServings = int(request.args.get('numServings'))*1.0
    keywords = request.args.get('mealdescription')

    #tags = ['vegetarian', 'vegan']
    ##    veggiesQuantity = {'fennel':1, 'beet':5, 'shallot':1, 'carrot':5, 'tomato':5, 'broccoli':1}
    veggies1 = veggieQuantity.keys()
    veggies = list(set(veggies1))
    if 'none' in veggies:
      veggies.remove('none')
    vDf = getRecipesForVeggies(veggies)
    recipesListFromVeggies = list(set(sum([recipe_id for recipe_id in vDf.recipes.str.split(',')], [])))
    
    if (request.args.get('vegetarian') is not None) & (request.args.get('vegan') is not None):          
      tags = [lemmatizePhrase(request.args.get('vegetarian')), request.args.get('vegan')]
      df = getRecipesForTags(tags)
      ## Extract recipes from tags
      recipesListFromTags = list(set(sum([recipe_id for recipe_id in df.recipe_ids.str.split(',')], [])))
      selectedRecipesList = list(set(recipesListFromTags)&set(recipesListFromVeggies))
    else:
      selectedRecipesList = recipesListFromVeggies

    # Sides or no?
    #sidesDf = getRecipesForTags(['side'])
    #sidesListFromTags = list(set(sum([recipe_id for recipe_id in sidesDf.recipe_ids.str.split(',')], [])))
    #selectedRecipesList = list(set(selectedRecipesList2)-set(sidesListFromTags))

    selDf = getRecipeIngredientsForVeggies(selectedRecipesList, veggies)
    selDf = selDf.fillna(0)
    selDf = selDf[selDf['num_servings']!=0].reset_index()
    for veggie in veggies:
        if veggie != 'none':
          selDf[veggie] = selDf[veggie].astype(float)
          selDf[veggie] = (selDf[veggie])/np.max(selDf[veggie])
        
    vDf['norm_shelf_life'] = vDf['shelf_life']/np.max(vDf['shelf_life'])

    selDf = getScore(selDf, veggieQuantity, vDf, numServings)

    
    imageDf = getRecipeImageURLs(selDf)
    selDf['id'] = selDf['index']
    selDf2 = pd.merge(selDf, imageDf, on='id', how='outer').reset_index(drop=True)
    #selDf3 = doNLPStuff(selDf2, keywords)
    selDf3 = selDf2.head(10)
    selDf3['id'] = selDf3['id'].apply(lambda x: "http://www.epicurious.com"+str(x))
    recipeInfo = []
    for i in range(0, len(selDf3)):
        recipeInfo.append([selDf3['recipe_name'][i],\
          selDf3['image_url'][i],\
          selDf3['id'][i]]+ \
          [int(selDf3[veggie][i]) for veggie in veggies])
    return render_template("output.html",\
     recipeInfo=recipeInfo,\
     recipeNames = selDf3['recipe_name'],\
     recipeImgUrl=selDf3['image_url'],\
     recipeId=selDf3['id'],\
      veggiesList = veggies, veggiesQuantity=veggieQuantity.values(), veggiesShit = [selDf3[veggie].tolist() for veggie in veggies ])
