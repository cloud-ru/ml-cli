### Руководство по настройке



**Шаги:**

**Настройка:**
    
   В качестве совета - не пытайтесь использовать оба похода сразу.  
   
   > mls configure --profile <NAME> --encrypt
   
   Создаст файл credentials.key 

   При повторном вводе опции до записи должны быть подтверждены тем же паролем. 

** Кейс: 1 **
> Я хочу зашифровать существующий credentials
    
Здесь использовался openssl и он обратно совместимый.  

Пример для шифрования
```bash
cat ~/.mls/credentials | openssl aes-256-cbc -pbkdf2 -a
```
```bash
cat ~/.mls/credentials | openssl aes-256-cbc -pbkdf2 -a > ~/.mls/credentials.key
```

Пример для расшифрования
```bash
cat ~/.mls/credentials.key | openssl aes-256-cbc -pbkdf2 -a -d
```

```bash
cat ~/.mls/credentials.key | openssl aes-256-cbc -pbkdf2 -a -d > ~/.mls/credentials
```

**Еще описание**
   Если мы хотим предотвратить утекание истории нужно сделать 
   Откройте файл конфигурации в текстовом редакторе (например, для bash это может быть ~/.bashrc или ~/.bash_profile)
   
   Пример 
   > unset HISTFILE
   
   > source ~/.bashrc
   
   Т.е. если есть условие при котором данные нужно шифровать - то надо наверно и обезопасить и попадание пароля в ~/.bash_history
   

**Запуск задачи**
   
   в одной строке передайте 
   > MLS_PASSWORD=<Ваш пароль> mls job submit .... 
   
   Или
   
   > export MLS_PASSWORD=<Ваш пароль>
   > 
   > mls job submit ....

или определите ввод в функции 
```bash
function set_mls_password() {
    echo "Введите пароль:"
    read var_value
    export MLS_PASSWORD="$var_value"
}
```
