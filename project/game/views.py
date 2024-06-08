from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
import logging
from django.urls import reverse


logger = logging.getLogger(__name__)

# Create your views here.


def main(request):
    return render(request, 'main.html')


def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.score = 0  # 기본값 설정
                user.save()
            request.session['username'] = user.username  # 세션에 사용자 이름 저장
            request.session.modified = True  # 세션이 수정되었음을 명시
            logger.debug(f"User {user.username} saved in session.")
            logger.debug(f"Session data after saving: {
                         request.session.items()}")
            return redirect('start')
        else:
            logger.debug(f"Form is not valid: {form.errors}")
    else:
        form = UserForm()

    return render(request, 'name.html', {'form': form})


def name(request):
    current_username = request.session.get('username')
    if current_username:
        return render(request, 'start.html', {'logged_in': True, 'username': current_username})
    return render(request, 'name.html', {'logged_in': False})


def start(request):
    departments = Department.objects.all()
    professors = Professor.objects.all()
    if request.method == 'POST':
        form = StartForm(request.POST)
        if form.is_valid():
            department = form.cleaned_data['department']
            professor = form.cleaned_data['professor']
            return redirect(reverse('game', args=[department.id, professor.id]))
    else:
        form = StartForm()
    return render(request, 'start.html', {'form': form, 'departments': departments, 'professors': professors})
# def logout(request):
#     request.session.flush()  # 세션 데이터 삭제
#     return redirect('name')


def ranking(request):
    users = User.objects.all().order_by('-score')
    current_username = request.session.get('username')
    current_user = User.objects.get(
        username=current_username) if current_username else None

    ctx = {'users': users, 'current_user': current_user}
    return render(request, 'ranking.html', ctx)


def game(request, department_id, professor_id):
    current_username = request.session.get('username')  # 세션에서 사용자 이름 가져오기
    department = Department.objects.get(id=department_id)
    professor = Professor.objects.get(id=professor_id)
    logger.debug(f"Current username from session: {current_username}")
    return render(request, 'game.html', {'department': department, 'professor': professor, 'current_username': current_username})
