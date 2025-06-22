# routes/agendamento.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from datetime import datetime, timedelta
from functools import wraps

from models.usuarios import Usuario, Paciente, ProfissionalSaude
from models.agendamento import Agendamento, Hospital, ListaEspera, Notificacao, Chat
from controllers.agendamento import AgendamentoController, ListaEsperaController, NotificacaoController

# Blueprint para agendamentos
agendamento_bp = Blueprint('agendamento', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def paciente_required(f