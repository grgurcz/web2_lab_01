import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Game:
   id: int
   round_num: int
   team_1: str
   team_2: str
   team_1_score: int
   team_2_score: int
   match_time: datetime


@dataclass
class Comment:
   id: int
   round_num: int
   comment_text: str
   username: str
   date_created: datetime


@dataclass
class TeamScore:
   team_name: str
   points: int = 0
   goal_diff: int = 0

   def set_goal_diff():
      self.goal_diff = self.goals_scored - self.goals_received


class AllData:
   def __init__(self):
      self.all_games = {}
      self.all_comments = {}

      with open('initial_data.json') as f:
         data = json.load(f)
         
         for game in data:
            new_game = Game(
               id = game['MatchNumber'],
               round_num = game['RoundNumber'],
               team_1 = game['HomeTeam'],
               team_2 = game['AwayTeam'],
               team_1_score = game['HomeTeamScore'],
               team_2_score = game['AwayTeamScore'],
               match_time = datetime.strptime(game['DateUtc'][:-1], '%Y-%m-%d %H:%M:%S')
            )
            self.all_games[new_game.id] = new_game

         self.add_initial_comments()
   
   def add_comment(self, round_num, comment_str, username):
      id = 0
      while id in self.all_comments:
         id += 1
      new_comment = Comment(id, round_num, comment_str, username, datetime.now())
      self.all_comments[id] = new_comment

   def edit_comment(self, existing_comment_id, new_comment_str):
      existing_comment = self.all_comments[existing_comment_id]
      new_comment = Comment(existing_comment.id, existing_comment.round_num, new_comment_str, existing_comment.username, datetime.now())
      self.all_comments[existing_comment.id] = new_comment

   def remove_comment(self, existing_comment_id):
      if existing_comment_id in self.all_comments:
         del self.all_comments[existing_comment_id]

   def add_initial_comments(self):
      self.add_comment(1, 'this is interesting', 'random_user')
      self.add_comment(2, 'this is great', 'admin_user')
      self.add_comment(2, 'i lost all my money betting on this round', 'random_user')
      self.add_comment(3, 'wow, i feel like i saw these games last year', 'grgur.crnogorac6')

   def get_round_comments(self, round_num):
      for comment in self.all_comments.values():
         if comment.round_num == round_num:
            yield comment

   def add_game(self, round_num, team_1, team_2, team_1_score, team_2_score, match_time):
      id = 0
      while id in self.all_comments:
         id += 1
      new_game = Game(id, round_num, team_1, team_2, team_1_score, team_2_score, match_time)
      self.all_games[id] = new_game

   def edit_game(self, game_id, team_1_score, team_2_score):
      existing_game = self.all_games[game_id]
      new_game = Game(existing_game.id, existing_game.round_num, existing_game.team_1, existing_game.team_2, team_1_score, team_2_score, existing_game.match_time)
      self.all_games[game_id] = new_game

   def get_round_games(self, round_num):
      for game in self.all_games.values():
         if game.round_num == round_num:
            yield game   

   def get_num_rounds_played(self):
      min_round = 100
      for game in self.all_games.values():
         if game.match_time > datetime.now():
            min_round = min(min_round, game.round_num)
      return min_round - 1
   
   def get_scheduled_games(self):
      for game in self.all_games.values():
         if game.match_time > datetime.now():
            yield game

   def get_points_table(self):
      teams = {}
      
      for game in self.all_games.values():
         if game.match_time > datetime.now():
            continue
         
         if game.team_1 not in teams:
            teams[game.team_1] = TeamScore(team_name=game.team_1)
         if game.team_2 not in teams:
            teams[game.team_2] = TeamScore(team_name=game.team_2)
         
         teams[game.team_1].goal_diff += game.team_1_score
         teams[game.team_1].goal_diff -= game.team_2_score
         teams[game.team_2].goal_diff += game.team_2_score
         teams[game.team_2].goal_diff -= game.team_1_score

         if game.team_1_score > game.team_2_score:
            teams[game.team_1].points += 3
         elif game.team_2_score > game.team_1_score:
            teams[game.team_2].points += 3
         elif game.team_1_score == game.team_2_score:
            teams[game.team_1].points += 1
            teams[game.team_2].points += 1

      teams_sorted = sorted(teams.values(), key = lambda team: (team.points, team.goal_diff), reverse=True)
      return teams_sorted


def load_initial_data():
   return AllData()
