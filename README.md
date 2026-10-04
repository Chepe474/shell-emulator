Эмулятор оболочки UNIX-подобной ОС (Вариант №27)

Учебный проект по дисциплине «Конфигурационное управление».

Общее описание

Программа имитирует работу в командной строке UNIX-подобной операционной системы.

Поддерживается:
- Интерактивный режим (REPL)
- Раскрытие переменных окружения реальной ОС (`$HOME`, `${USER}` и др.)
- Загрузка параметров из командной строки и XML-конфигурации
- Виртуальная файловая система (VFS), загружаемая из ZIP-архива (все операции только в памяти)
- Команды: `ls`, `cd`, `exit`, `clear`, `history`, `cat`, `rm`, `rmdir`

Структура проекта

shell-emulator/
├── README.md
├── .gitignore
├── src/
│   └── main.py          
├── tests/               
├── configs/
│   └── default.xml      
├── scripts/
│   ├── create_vfs.py    
│   ├── startup_demo.sh
│   ├── startup_stage4.sh
│   └── startup_full.sh  
└── vfs/
├── minimal.zip
├── several.zip
├── deep.zip
└── sample.zip

Интерактивный режим

python src/main.py --vfs-name MyVFS

С виртуальной файловой системой

python src/main.py --vfs vfs/sample.zip --vfs-name Demo

С конфигурационным файлом

python src/main.py --config configs/default.xml

Полный автоматический тест

python src/main.py --vfs vfs/sample.zip --script scripts/startup_full.sh --vfs-name Demo

Параметры командной строки

Параметр,Описание
--vfs PATH,Путь к ZIP-архиву VFS
--script PATH,Путь к стартовому скрипту
--config PATH,Путь к XML-конфигурации
--vfs-name NAME,Имя VFS в приглашении (по умолчанию VFS)

Описание команд

Команда,Аргументы,Описание
ls,[путь],Показать содержимое директории
cd,[путь],Сменить текущую директорию
exit,—,Выйти из эмулятора
clear,—,Очистить экран
history,—,Показать историю команд
cat,файл...,Показать содержимое файла
rm,файл...,Удалить файл (только в памяти)
rmdir,папка...,Удалить пустую папку (только в памяти)

Этапы разработки

feat(repl): ... — базовый REPL + раскрытие переменных
feat(config): ... — CLI + XML-конфигурация + стартовые скрипты
feat(vfs): ... — загрузка VFS из ZIP в память
feat(commands): ... — настоящие ls, cd, clear, history, cat
feat(commands): ... — rm и rmdir