from main.management.commands.check_tour_ready import Command as ClearToursCommand
from main.management.commands.clear_chat import Command as ClearChatCommand
from django.core.management import call_command

def check_tournaments():
   ClearToursCommand.run_from_argv()

def clear_chat():
   ClearChatCommand.run_from_argv()

def clearsessions():
   call_command('clearsessions')
