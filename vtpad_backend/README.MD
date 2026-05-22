env переменные

// Настройка базы

db_name = 

db_user = 

db_password = 

db_port = 

db_host = 

// Настройка базы

// порт бека

backend_port = 

// Настройки сервиса репортера

report_url = 

report_port = 

report_api_hash = 


##
Для запуска проекта на сервере запустить docker-compose up --build
создается контейнер с базой и приложением от переменной backend_port зависит на каком порту будет приложение

##
переменная report_api_hash должны совпадать с переменной api_hash в сервисе report-poortal


