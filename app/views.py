from flask import render_template, request
from flaskexample import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import numpy as np

from nltk.stem.wordnet import WordNetLemmatizer



@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Miguel' },
       )

def lemmatizePhrase(phrase):
    """ 
    Lemmatize each word in a pharse
    """
    words = phrase.lower().split()
    return ' '.join(str(WordNetLemmatizer().lemmatize(word.encode('utf-8'))) for word in words)
   
def getRecipesForTags(tags):
    username = 'nemo'
    pswd = 'eatsalot'
    dbname = 'catrecipes_db'
    engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))
    
    con = None
    con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)
    cur = con.cursor()
    df = pd.DataFrame(columns = ['tag', 'recipe_ids', 'count', 'tag2'])
    for tag in tags:
        cur.execute(
            "SELECT * FROM tags_recipe_ids WHERE tags_recipe_ids.index = %s;", (tag,))
        dfx = pd.DataFrame(cur.fetchall(), columns = ['tag', 'recipe_ids', 'count', 'tag2'])
        df = pd.concat([df, dfx], ignore_index = True)
    return df  

def getRecipesForVeggies(vegs):
    username = 'nemo'
    pswd = 'eatsalot'
    dbname = 'veggie_db'
    engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))
    
    
    con = None
    con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)
    cur = con.cursor()
    df = pd.DataFrame(columns = ['veggie', 'shelf_life', 'recipes', 'recipe_count'])
    for veggie in vegs:
        cur.execute(
            "SELECT * FROM veggie_info_db WHERE veggie_info_db.index = %s;", (veggie,))
        dfx = pd.DataFrame(cur.fetchall(), columns = ['veggie', 'shelf_life', 'recipes', 'recipe_count'])
        df = pd.concat([df, dfx], ignore_index = True)
        #df['recipe_ids'] = df['recipe_ids'].str.split(',')
        #recipesList = list(set(sum([recipe_id for recipe_id in df.recipe_ids.str.split(',')], [])))
    return df 

def getRecipeIngredientsForVeggies(selectedRecipesList, veggies1):
    username = 'nemo'
    pswd = 'eatsalot'
    dbname = "recipe_ingredients_db"
    vegs = veggies1+['num_servings', 'index']
    
    
    engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))
    con = None
    con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)
    cur = con.cursor()
    SQL_query = "SELECT " +','.join(vegs)+  " FROM recipe_ingredients_quant WHERE index IN %s"
    cur.execute(SQL_query, (tuple(selectedRecipesList),))
    dfx = pd.DataFrame(cur.fetchall(), columns = vegs)
    # query:
    #sql_query = """
    #SELECT * FROM recipe_ingredients_quant;
    #"""
    return dfx


    
def getScore(selDf, veggiesQuantity, vDf):
      selDf['score'] = 0.0
      for veggie in veggiesQuantity.keys():
        diffinQuantity = 1/(np.abs((selDf[veggie].astype(float)/selDf['num_servings'].astype(float) - veggiesQuantity[veggie]*1.0 ))+1)
        weight = 1/(vDf[vDf.veggie == veggie].shelf_life)
        product =  diffinQuantity*list(set(weight))[0]
        selDf['score'] = selDf['score'] + product
      selDf['score'] = selDf['score']*100
      selDf['recipe_name'] = selDf['index'].str.split('/').apply(lambda x: ' '.join(x[4].split('-')[:-1]).title())
      selDf = selDf.sort_values('score', ascending=False).head(50)
      return selDf

def getRecipeImageURLs(selDf):
    username = 'nemo'
    pswd = 'eatsalot'
    dbname = 'recipes_db'
    engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))
    con = None
    con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)
    cur = con.cursor()
    SQL_query = "SELECT image_url, id FROM recipes_db WHERE id IN %s"
    cur.execute(SQL_query, (tuple(list(set(selDf['index']))),))
    dfx = pd.DataFrame(cur.fetchall(), columns = ['image_url', 'id'])
    return dfx


@app.route('/output')
def display_output():
    veggieQuantity = {lemmatizePhrase(request.args.get('veggie1')): int(request.args.get('quantity1')),\
                lemmatizePhrase(request.args.get('veggie2')): int(request.args.get('quantity2')),\
                lemmatizePhrase(request.args.get('veggie3')): int(request.args.get('quantity3')),\
                lemmatizePhrase(request.args.get('veggie4')): int(request.args.get('quantity4')),\
                lemmatizePhrase(request.args.get('veggie5')): int(request.args.get('quantity5'))}
    #tags = [lemmatizePhrase(request.args.get('vegetarian')), request.args.get('vegan')]


    tags = ['vegetarian', 'vegan']
    ##    veggiesQuantity = {'fennel':1, 'beet':5, 'shallot':1, 'carrot':5, 'tomato':5, 'broccoli':1}
    veggies = veggieQuantity.keys()
    df = getRecipesForTags(tags)
    recipesListFromTags = list(set(sum([recipe_id for recipe_id in df.recipe_ids.str.split(',')], [])))
    vDf = getRecipesForVeggies(veggies)
    recipesListFromVeggies = list(set(sum([recipe_id for recipe_id in vDf.recipes.str.split(',')], [])))
    selectedRecipesList = list(set(recipesListFromTags)&set(recipesListFromVeggies))
    selDf = getRecipeIngredientsForVeggies(selectedRecipesList, veggies)
    selDf = selDf.fillna(0)
    for veggie in veggies:
        selDf[veggie] = selDf[veggie].astype(float)
        selDf[veggie] = (selDf[veggie])/np.max(selDf[veggie])
        
    vDf['norm_shelf_life'] = vDf['shelf_life']/np.max(vDf['shelf_life'])

    selDf = getScore(selDf, veggieQuantity, vDf)
    imageDf = getRecipeImageURLs(selDf)
    selDf['id'] = selDf['index']
    selDf2 = pd.merge(selDf, imageDf, on='id', how='outer').head(9)
    selDf2['index'] = selDf2['index'].apply(lambda x: "http://www.epicurious.com"+str(x))
    return render_template("output.html",\
     recipeName=list(set(selDf2['recipe_name'])), \
     imageURLS=list(set(selDf2['image_url'])),\
     recipeURLS =list(set(selDf2['index'])))
