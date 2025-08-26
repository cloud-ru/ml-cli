mls configure
=============

|mls_configure| --- команда настройки конфигурации профиля пользователя.
Если профиль не указан, используется профиль по умолчанию ``default``.


Синтаксис:

    .. code-block::

       mls configure [options]

Пример:

    .. code-block::

       mls configure --profile name --encrypt


.. list-table:: Опции обязательные
   :widths: 5 5 5
   :header-rows: 1

   * - Параметр
     - Формат 
     - Описание
   * - ``-P  --profile``
     - [string]
     - Имя профиля
   
   * - ``-E  --encrypt``
     - [bool]
     - Шифрование профиля


   
