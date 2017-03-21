% prolog

nlp_macro ('MOVIES', MOVIE, LABEL) :-
    rdf (distinct,
         MOVIE, wdpd:InstanceOf,   wde:Film,
         MOVIE, rdfs:label,        LABEL,
         filter (lang(LABEL) = 'de')).

answer(topic, de) :-
    context_score(topic, movies, 100, SCORE), say_eoa(de, 'Wir hatten das Thema Filme.', SCORE).

answer (movieDirector, de, MOVIE, MOVIE_LABEL) :-
    rdf (distinct, limit(1),
         MOVIE,    wdpd:Director, DIRECTOR,
         DIRECTOR, rdfs:label,    LABEL,
         filter (lang(LABEL) = 'de')),
    context_push(topic, movies),
    context_push(topic, MOVIE),
    context_push(topic, DIRECTOR),
    say_eoa(de, format_str('Der Regisseur von %s ist %s.', MOVIE_LABEL, LABEL)).

nlp_gen (de, '(HAL,|Computer,|) wer hat (eigentlich|) @MOVIES:LABEL gedreht?',
             answer(movieDirector, de, '@MOVIES:MOVIE', "@MOVIES:LABEL")). 

nlp_gen (de, '(HAL,|Computer,|) wer ist (eigentlich|) der Regisseur von @MOVIES:LABEL?',
             answer(movieDirector, de, '@MOVIES:MOVIE', "@MOVIES:LABEL")). 

nlp_test(de,
         ivr(in('wer ist der regisseur von der dritte mann?'),
             out('Der Regisseur von Der dritte Mann ist Carol Reed.'))).

is_director(PERSON) :- 
    rdf(MOVIE, wdpd:Director, PERSON).

answer (knownPerson, de, PERSON, LABEL) :-
    SCORE is 10,
    context_score (topic, movies, 100, SCORE),
    is_director(PERSON),
    is_male(PERSON),
    context_push(topic, movies),
    context_push(topic, PERSON),
    say_eoa(de, 'Ja, der ist Regisseur.', SCORE).

answer (knownPerson, de, PERSON, LABEL) :-
    SCORE is 10,
    context_score (topic, movies, 100, SCORE),
    is_director(PERSON),
    is_female(PERSON),
    context_push(topic, movies),
    context_push(topic, PERSON),
    say_eoa(de, 'Ja, die ist Regisseurin.', SCORE).

nlp_test(de,
         ivr(in('wer ist Alfred Hitchcock?'),
             out('Ja, der ist Regisseur.'))).

answer (movieCreationDate, de, MOVIE, MOVIE_LABEL) :-
    rdf (distinct, limit(1),
         MOVIE,    wdpd:PublicationDate, TS),
    stamp_date_time(TS, date(Y,M,D,H,Mn,S,'local')),
    context_push(topic, movies),
    context_push(topic, MOVIE),
    say_eoa(de, format_str('%s wurde %s gedreht.', MOVIE_LABEL, Y), 100).

nlp_gen (de, '(HAL,|Computer,|) wann (ist|wurde) (eigentlich|) @MOVIES:LABEL (gedreht|gemacht)?',
             answer(movieCreationDate, de, '@MOVIES:MOVIE', "@MOVIES:LABEL")). 

nlp_test(de,
         ivr(in('wann wurde der dritte mann gedreht?'),
             out('Der dritte Mann wurde 1949 gedreht.'))).

answer (movieSeen, de, MOVIE, MOVIE_LABEL) :-
    context_push(topic, movies),
    context_push(topic, MOVIE),
    say_eoa(de, format_str('ja, %s kenne ich - ist ein bekannter Film.', MOVIE_LABEL)).

nlp_gen (de, '(HAL,|Computer,|) kennst du (eigentlich|) (den film|) @MOVIES:LABEL?',
             answer(movieSeen, de, '@MOVIES:MOVIE', "@MOVIES:LABEL")). 

nlp_gen (de, '(HAL,|Computer,|) hast du (eigentlich|) (den film|) @MOVIES:LABEL gesehen?',
             answer(movieSeen, de, '@MOVIES:MOVIE', "@MOVIES:LABEL")). 

nlp_test(de,
         ivr(in('kennst du den film der dritte mann?'),
             out('ja, der dritte mann kenne ich - ist ein bekannter film.'))).

% FIXME nlp_gen (de, '(HAL,|Computer,|) weisst du (eigentlich|) wer ihn (gedreht|gemacht) hat?',
% FIXME              context_score(topic, answer(movieSeen, de, '@MOVIES:MOVIE', "@MOVIES:LABEL")). 
% FIXME 
% FIXME nlp_test(de,
% FIXME          ivr(in('kennst du den film der dritte mann?'),
% FIXME              out('ja, der dritte mann kenne ich - ist ein bekannter film.')),
% FIXME          ivr(in('weisst du, wer ihn gedreht hat?'),
% FIXME              out('ja, der dritte mann kenne ich - ist ein bekannter film.')),
% FIXME          ivr(in('und weisst du, wann er gedreht wurde?'),
% FIXME              out('ja, der dritte mann kenne ich - ist ein bekannter film.'))).


%
% FIXME: cast members, genre, topics, ...
%
