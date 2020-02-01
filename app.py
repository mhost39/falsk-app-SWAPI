from flask import Flask, render_template, request
import swapi
import json
import requests
import time
import functools


app = Flask(__name__)

url = "https://swapi.co/api/people/"
def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()    # 1
        value = func(*args, **kwargs)
        end_time = time.perf_counter()      # 2
        run_time = end_time - start_time    # 3
        print(f"Finished {func.__name__!r} in {run_time:.4f} secs")
        return value
    return wrapper_timer


@app.route('/')
def hello_world():  
    return render_template('home.html')
@app.route('/result',methods = ['POST', 'GET'])
@timer
def result():
    name = request.form['Name']
    character = get_charcter(name)
    if (character == "false"):
        return render_template("not-found.html")
    result = generate_result(character)
    return render_template("result.html" , result = result)
def get_charcter(name):
    characters = requests.get(url = url).json()['results']
    for c in characters:
        if (c['name'] == name):
            return c
    return "false"
def generate_result(character):
    dic = {}
    dic['Full Name'] = character['name']
    dic['Gender'] = character['gender']
    species_and_lifespan = get_species_and_lifespan(character['species'])
    dic['Species Name'] = species_and_lifespan['Species']
    dic['Average Lifespan'] = species_and_lifespan['lifespan']
    dic['Home Planet'] = get_planet(character['homeworld'])
    dic['List Of Movies'] = get_films(character['films'])
    return dic
def get_species_and_lifespan(s_url):
    req = requests.get(url = s_url[0]).json()
    dic = {}
    dic['Species'] = req['name']
    dic['lifespan'] = req['average_lifespan']
    return dic
def get_planet(p_url):
    return requests.get(url = p_url).json()['name']
def get_films(films):
    result = []
    for f_url in films:
        result.append(requests.get(url = f_url).json()['title'])
    return result

if __name__ == '__main__':
   app.run(debug = True)
