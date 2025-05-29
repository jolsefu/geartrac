#!/bin/bash

SESSION="geartrac"

tmux new-session -d -s $SESSION

# # Backend server
tmux rename-window -t $SESSION:0 'Backend'
tmux send-keys -t $SESSION:0 'source pyvenv/bin/activate && cd geartrac_backend && py manage.py runserver' C-m

# # Frontend server
tmux new-window -t $SESSION:1 -n 'Frontend'
tmux send-keys -t $SESSION:1 'cd geartrac_frontend && npm run dev' C-m

# # Celery worker
tmux new-window -t $SESSION:2 -n 'CeleryWorker'
tmux send-keys -t $SESSION:2 'source pyvenv/bin/activate && cd geartrac_backend && celery -A geartrac_site worker -l info' C-m

# # Celery beat
tmux new-window -t $SESSION:3 -n 'CeleryBeat'
tmux send-keys -t $SESSION:3 'source pyvenv/bin/activate && cd geartrac_backend && celery -A geartrac_site beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler' C-m
