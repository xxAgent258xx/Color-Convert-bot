#  Color-Convert-bot 
Конвертируй цвета из HEX RGB и CMYK прямо в Telegram!

Почти вся документация для этого бота написана на Русском языке, так как планируется, что ее будут читать только русскоязычные разработчики

## Как запустить?

Рекомендуемая версия Python 3.12.7 (версия на которой бот разрабатывался)
Вы можете использовать версии старее/новее, но я не гарантирую корректную работу бота в таких условиях, таким, какой он есть в данный момент

Запуск для Linux
```commandline\
    // создайте виртуальное окружение если оно еще не было создано
    python3 -m venv venv
    
    source venv/bin/activate
    
    // установите зависимости, если они еще не были установлены
    python3 -m pip install -r requirements.txt 
    export PYTHONPATH=.
    
    python3 bot/main.py  
```


Запуск для Windows
```commandline\
    // создайте виртуальное окружение если оно еще не было создано
    python -m venv venv
    
    ./venv/Scripts/activate.bat
    
    // установите зависимости, если они еще не были установлены
    python -m pip install -r requirements.txt 
    set PYTHONPATH=.
    
    python bot/main.py  
```


#### @raptor_tag - author telegram tag
#### @Justiks - contributor telegram tag
 