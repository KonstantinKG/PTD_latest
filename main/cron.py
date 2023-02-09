from main.management.commands.check_tour_ready import Command
from django.core.management import call_command

def check_tournaments():
   Command.run_from_argv()

def clearsessions():
   call_command('clearsessions')