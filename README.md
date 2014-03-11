Swiss-system Chess Tournament
=============================
[![Build Status](https://travis-ci.org/vood/chess-tournament.png?branch=master)](https://travis-ci.org/vood/chess-tournament)

Purpose
-------
This application is inteded to show my python and django skills.

What is swiss-system tournament (Wiki)
--------------------------------------
A Swiss-system tournament is a non-elimination tournament format designed to award the team which perform best when matched with opponents of similar skill.
It involves several rounds of competition where the winners are the players with the highest aggregate of points earned from all rounds.
Players meet one-to-one in each round and are paired using a predetermined formula (though they may be paired by randomly in the first round or in pre-determined rounds). The first tournament of this type was a chess tournament in Zurich in 1895, hence the name "Swiss system".

Demo
----
The demo app is located here: http://wargaming-tournament.herokuapp.com/

Login/password: admin/password

Russian version
===============

Демо
----

Для рассчета следующего тура турнира:
  1. Зайдите в админку по адресу http://wargaming-tournament.herokuapp.com/admin
  2. Выберите Tournaments
  3. Кликните Seed next round напротив записи Wargaming Chess Tournament. Для того, чтобы следующий тур успешно рассчитался нужно сначала выставить результаты всех игр в предыдущем. В демо данных это уже сделано за вас.

Затраченое время: по 30-60 каждый день в течение недели

Основное время потрачено на:
  1. Определение требований. Изучение швейцарской системы
  2. Проектировка базы данных
  3. Изучение синтаксиса и особенностей python и django

Ввиду отсутствия четких требований были сделаны следующие допущения:
  1. Количество игроков всегда четное (частный случай)
  2. Опускается коэффициент Бухгольца (т.к. его применение опционально по правилам Швейцарской системы)

Требуемые улучшения:
  1. Оптимизация алгоритма сопоставления пар
  2. Реализация использования коэффициент Бухгольца
  3. Работа с нечетным количеством игроков
