from flask import Flask, render_template, request
import json
import requests
import time
import functools
import asyncio
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

url = "https://swapi.co/api/people/?search="
def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter() 
        value = func(*args, **kwargs)
        end_time = time.perf_counter()   
        run_time = end_time - start_time 
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
    characters = get_charcters(name)
    if (characters == "false"):
        return render_template("not-found.html")
    result = generate_result(characters['results'])
    return render_template("result.html" , result = result)
def get_charcters(name):
    characters = requests.get(url = url+name).json()  #['results']
    if (characters["count"] == 0):
        return "false"
    return characters
def generate_result(characters):
    result_list = []
    for c in characters:
        dic = {}
        dic['Full Name'] = c['name']
        dic['Gender'] = c['gender']
        species_and_lifespan = get_species_and_lifespan(c['species'])
        dic['Species Name'] = species_and_lifespan['Species']
        dic['Average Lifespan'] = species_and_lifespan['lifespan']
        dic['Home Planet'] = get_planet(c['homeworld'])
        dic['List Of Movies'] = get_films(c['films'])
        result_list.append(dic)
    return result_list
def get_species_and_lifespan(s_url):
    req = requests.get(url = s_url[0]).json()
    dic = {}
    dic['Species'] = req['name']
    dic['lifespan'] = req['average_lifespan']
    return dic
def get_planet(p_url):
    return requests.get(url = p_url).json()['name']
def get_films(films):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(get_data_asynchronous(films))
    loop.run_until_complete(future)

    return future.result()

def fetch(session, film):
    with session.get(film) as response:
        data = response.text
        return data

async def get_data_asynchronous(films):
    result = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        with requests.Session() as session:
            # Set any session parameters here before calling `fetch`
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(session, film) # Allows us to pass in multiple arguments to `fetch`
                )
                for film in films
            ]
            for response in await asyncio.gather(*tasks):
                data = response.split('"')
                result.append(data[3])
    return result

if __name__ == '__main__':
   app.run(debug = True,  host='0.0.0.0')