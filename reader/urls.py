from django.urls import path
from . import views

urlpatterns = [
    path('',                                        views.landing_view,               name='landing'),
    path('register/',                               views.register_view,              name='register'),
    path('login/',                                  views.login_view,                 name='login'),
    path('logout/',                                 views.logout_view,                name='logout'),
    path('dashboard/',                              views.dashboard_view,             name='dashboard'),
    path('subjects/',                               views.subject_select_view,        name='subject_select'),
    path('subject/<int:subject_id>/texts/',         views.text_list_view,             name='text_list'),
    path('read/<int:subject_id>/',                  views.reading_session_view,       name='reading_session'),
    path('read/text/<int:text_id>/',                views.start_reading_text_view,    name='start_reading_text'),
    path('finish/<int:session_id>/',                views.finish_reading_view,        name='finish_reading'),
    path('quiz/<int:session_id>/',                  views.quiz_session_view,          name='quiz_session'),
    path('retry/<int:text_id>/',                    views.retry_text_view,            name='retry_text'),
    path('history/',                                views.history_view,               name='history'),
    path('badges/',                                 views.badges_view,                name='badges'),
    path('daily/',                                  views.daily_challenge_view,       name='daily_challenge'),
    path('daily/start/<int:challenge_id>/',         views.start_daily_challenge_view, name='start_daily_challenge'),
    path('learn/',                                  views.learn_hub_view,             name='learn_hub'),
    path('learn/lesson/<int:number>/',              views.lesson_view,                name='lesson'),
    path('learn/assistant/',                        views.assistant_view,             name='assistant'),
    path('learn/assistant/ask/',                    views.assistant_ask_view,         name='assistant_ask'),
    path('custom/',                                 views.custom_text_view,           name='custom_text'),
    path('preferences/',                            views.save_preferences_view,      name='save_preferences'),
    path('offline/', views.offline_view, name='offline'),
    path('manifest.json', views.manifest_view, name='manifest'),
]