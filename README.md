Скрипт `maprenderer.py` примитивный рендерер на pyqgis. Он открываей слой переданный первым аргументом командной строки и рендерит весь доступный экстент и сохраняет его в PNG файл, который указан вторым аргументом. В принципе все в соответсвии с [PyQGIS developer cookbook](http://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/composer.html).

Это все работает как надо c QGIS 2.0 и это позволяет использовать [ренденирг QGIS в NextGISWeb](https://github.com/nextgis/nextgisweb_qgis). Но с QGIS 2.8 все работает как-то странно и не стабильно. Ниже я описал как воспроизвести все те проблемы с которыми я столкнулся.

Создаем примитивный стиль с окружностями 5 мм и пытаемся отреднерить его в QGIS 2.0 через pyqgis. Стиль сохранен стилем по-умолчанию (одноименный qml-файл) и поэтому загружается автоматически при открытии слоя.

```
(QGIS 2.0) $ python maprenderer.py sample/qgis20-5mm.geojson sample/qgis20-5mm-96dpi.png
(QGIS 2.0) $ python maprenderer.py --dpi 150 sample/qgis20-5mm.geojson sample/qgis20-5mm-150dpi.png
```

С разным DPI получаются разные картинки - все как и должно быть. DPI, который используем сам QGIS можно посмотреть в python консоли, через `iface.mapCanvas().mapRenderer().outputDpi()`. У меня показывает 96 и я поставил его по-умолчанию. Если в коде pyqgis его не устанавливать вовсе, то используется значение 75.

Теперь попробуем то же самое в QGIS 2.8, я ставлю его в виртуальную машину через Vagrant. Для того чтобы избежать несовместимости стиля из QGIS 2.0 в 2.8 я пересоздаю его с нуля.

```
(QGIS 2.8) $ python maprenderer.py sample/qgis28-5mm.geojson sample/qgis28-5mm-96dpi.png
(QGIS 2.8) $ python maprenderer.py --dpi 150 sample/qgis28-5mm.geojson sample/qgis28-5mm-150dpi.png
```

В обоих случаях получаются абсолютна пустые изображения и это первая проблема. Можно предположить, что что-то поменялось в API pyqgis между версиями, но другой слой даже без стиля вполне себе рендерится и с API все впорядке.

```
$ python maprenderer.py sample/qgis28-highway-nostyle.geojson sample/qgis28-highway-nostyle.png
```

Но рисуется хоть что-то, попробуем разобраться с ним. Добавим к этому слою стиль из veloroad и попробуем отрисовать что получится при разных значениях DPI (там так же используются значения в миллиметрах).

```
(QGIS 2.8) $ python maprenderer.py sample/qgis28-highway.geojson sample/qgis28-highway-96dpi.png
(QGIS 2.0) $ python maprenderer.py --dpi 150 sample/qgis28-highway.geojson sample/qgis28-highway-150dpi.png
```

Что-то оно рисует, но оно очень сильно отличается от того что рисует QGIS в интерфейсе. Все линии какие-то очень тонкие, и изменение DPI на это никак не влияет. Это вторая проблема. Такое ощущение, что DPI вообще ни как не влияет на отрисовку.

И третья проблема, она самая неприятная - на некоторых стилях, которые вполне успешно рендерятся в приложении рендерер просто зависает и все на некоторых масштабах. Какой-то фрагмент слоя может рендерится, а какой-то приводит к 100% CPU и ничем не заканчивается. Пример со стилем из осмошейпов, он конечно сделан в QGIS 1.7, но в приложении рендерится без особых проблем хоть и с предупреждением.

```
 (QGIS 2.8) $ python maprenderer.py sample/qgis28-highway-osmhp.geojson sample/qgis28-highway-osmhp.png
```

В результате процесс зависает на этапе отрисовки и ни на что кроме `kill -9` не реагирует. К QGIS 2.0 этот же слой с этим же стилем рендерится без проблем.

```
(QGIS 2.0) $ python maprenderer.py sample/qgis20-highway-osmhp.geojson sample/qgis20-highway-osmhp.png
```