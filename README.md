# morph-parser

## Алгоритм

Основная идея реализации морфологического парсера в следующем:

1) Лексический контекст
- на основе обучающей выборки каждое слово представляем как массив лексических контекстов,
и выглядит это примерно так (в каждом контексте по 2 слова слева и справа, для чисел используется плейсхолдер _NUM_):

```js
{ стали: [{'context': '_0_ _0_ _WORD_ разговаривать о', 'tags': ['V', 'intr', 'pf=praet', 'pl', 'act', 'indic']}] }
```

- затем каждый контекст представляем в виде `average` вектора векторов каждого слова с помощью word2vec,
где плейсхолдерам также присваивается соответсвюущий вектор 
(пробовали вариант с doc2vec, однако, в текущей реализации word2vec оказвается предпочтительнее (пояснение далее))

- затем строим бинарное дерево для каждого набора векторов, чтобы поиск по ним был быстрее

- когда мы получаем на вход текст, то ищем в нем омонимии и представляем их также в виде текущего контекста, который,
в свою очередь, тоже представляем в виде вектора

- ищем наиболее схожий вектор с данным контекстом искомого слова, и берем тэги из полученного контекста. Поиск осуществляем с помощью KNN (k-nearest neighbors)

2) Есть (еще не до конца реализованная) мысль по улучшению с помощью морфологического контекста.

- То есть контекст слова мы представляем вместе с тэгами как, например,
`{'VERB/NOUN': [{ context: '_0_ NPRO _WORD_ INFN/NOUN NOUN', tags ]}`

- контекст искомого слова для разрешения омонимии мы также представляем в виде частиречного контекста,
и в итоге стараемся найти наиболее схожий контекст

- предполагается использовать подобный подход можно использовать как фолбэк предыдущего

## Проблемы

- нужно очень много данных для обучения, чтобы иметь более-менее полноценные контексты
- приходится хранить достаточно много информации в памяти, необходимо оптимизировать ее потребление
- есть сложности с разрешением омонимии для неизвестных модели слов.
второй подход с морфологическим контекстом как раз призван с этим помочь
- сложности сравнения векторов таких контекстов, как, например, `пошел по берегу _ _` и `пошел по берегу у моря`
В текущей реализации эти вектора будут относительно далеки друг от друга. Решается расстановкой весов для плейсхолдеров, либо
присвоением им каких-то усредненных значений векторов, пока точно не ясно

## Преимущества
- в отличие, например, от pymorphy, смотрит на контекст, делая таким образом прогноз более комплексно
- теоретически такая модель может работать не только с частиречной омонимией, но и смыслов, как например,
"большой замок на двери" и "большой замок на холме", как раз благодаря дистрибутивной семантике и знаниях о контекстах
