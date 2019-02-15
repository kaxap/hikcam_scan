

CREATE TEXT SEARCH DICTIONARY russian_ispell (
     TEMPLATE = ispell,
     DictFile = ru,
     AffFile = ru,
     StopWords = ru
);

CREATE TEXT SEARCH DICTIONARY kazakh_ispell (
     TEMPLATE = ispell,
     DictFile = kazakh,
     AffFile = kazakh,
     StopWords = kazakh

);

CREATE TEXT SEARCH CONFIGURATION ru (COPY=russian);

ALTER TEXT SEARCH CONFIGURATION ru ALTER MAPPING FOR hword, hword_part, word WITH russian_ispell, kazakh_ispell, russian_stem;
