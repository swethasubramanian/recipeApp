from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import numpy as np

from nltk.stem.wordnet import WordNetLemmatizer

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

def getRecipeDescriptionAndTags():
    username = 'nemo'
    pswd = 'eatsalot'
    dbname = 'recipes_db'
    engine = create_engine('postgresql://%s:%s@localhost/%s'%(username,pswd,dbname))
    print engine.url
    
    con = None
    con = psycopg2.connect(database = dbname, user = username, host='localhost', password=pswd)
    cur = con.cursor()
    cur.execute("SELECT description,tags,id,name, review_text FROM recipes_db;")
    dfx = pd.DataFrame(cur.fetchall(), columns = ['description_one', 'tags', 'id', 'recipe_name', 'review_text'])
    return dfx  
   