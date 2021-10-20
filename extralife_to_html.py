from urllib import parse
import bs4
import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet
import pathlib
import json
import os
# import HTMLSession from requests_html
from requests_html import HTMLSession

extralife_base_path = 'https://www.extra-life.org/index.cfm?fuseaction=donorDrive'
extralife_participant_path = '.participant&participantID={}'
extralife_team_path = '.team&teamID={}'

extralife_team_api_path = 'https://www.extra-life.org/api/1.3/teams/{}'
extralife_participant_api_path = 'https://www.extra-life.org/api/1.3/participants/{}'

team_save_dir = 'team'
participant_save_dir = 'user'

session = None

participants = []
teams = []

class Participant:
    def __init__(self, name, p_id):
        self.name: str = name
        self.id: str = p_id

class Team:
    def __init__(self, name, t_id):
        self.name: str = name
        self.id: str = t_id

def _read_configs():
    global participants
    global teams
    with open("config.json", "r") as config:
        data = json.load(config)
        for p in data['participants']:
            participants += [Participant(p, data['participants'][p])]
        for t in data['teams']:
            teams += [Team(t, data['teams'][t])]

def _create_folder_if_not_exist(path):
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)

    if not isExist:    
        # Create a new directory because it does not exist 
        os.makedirs(path)

def _save_file(output_path, filename, html):
    global chapters
    f = os.path.join(os.path.curdir, output_path)
    _create_folder_if_not_exist(f)
    f = os.path.join(f, filename)
    with open(f, "w") as file:
        file.write(str(html))

def establish_session():
    global session
    session = HTMLSession() 

    # session = requests.Session()
    # session.headers['User-Agent'] = 'Mozilla/5.0'

def get_participant_data(save_path, item_name, item_id):
    global extralife_participant_api_path
    
    r = requests.session().get(extralife_participant_api_path.format(item_id))
    _save_file(save_path, item_name +'_data.json', r.json())

def get_team_data(save_path, item_name, item_id):
    global extralife_team_api_path
    
    r = requests.session().get(extralife_team_api_path.format(item_id))
    _save_file(save_path, item_name +'_data.json', r.json())

def process_item(save_path, item_name, item_id, isTeam):
    global session
    global extralife_base_path
    global extralife_participant_path
    global extralife_team_path
    
    connectionString: str = ''
    if isTeam:
        connectionString = (extralife_base_path + extralife_team_path).format(item_id)
    else:        
        connectionString = (extralife_base_path + extralife_participant_path).format(item_id)

    r = session.get(connectionString)
    r.html.render()
    item_page_soup: BeautifulSoup = BeautifulSoup(r.html.html, 'lxml')

    thermo = item_page_soup.find("div", id="thermo-wrap")

    _save_file(save_path, item_name+'.html', thermo)
    

def save_all_widgets():
    global teams
    global participants

    global team_save_dir
    global participant_save_dir

    for team in teams:
        process_item(team_save_dir, team.name, team.id, True)
        get_team_data(team_save_dir, team.name, team.id)
        
    for participant in participants:
        process_item(participant_save_dir, participant.name, participant.id, False)
        get_participant_data(participant_save_dir, participant.name, participant.id)
    
establish_session()
_read_configs()
save_all_widgets()