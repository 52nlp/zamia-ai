#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2015, 2016, 2017 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
# HAL-Prolog runtime with builtin predicates for AI use
#

import sys
import logging

from zamiaprolog.runtime  import PrologRuntime
from zamiaprolog.errors   import PrologRuntimeError
from zamiaprolog.logic    import NumberLiteral, StringLiteral, ListLiteral, Literal, Variable, Predicate, Clause, SourceLocation
from zamiaprolog.builtins import do_gensym, do_assertz, do_retract
from nltools.tokenizer    import tokenize
from nltools.misc         import edit_distance
from aiprolog.ner         import builtin_ner
from zamiaai              import model

USER_PREFIX        = u'user'
DEFAULT_USER       = USER_PREFIX + u'Default'

def builtin_tokenize(g, pe):

    """ tokenize (+Lang, +Str, -Tokens) """

    pe._trace ('CALLED BUILTIN tokenize', g)

    pred = g.terms[g.inx]
    args = pred.args
    if len(args) != 3:
        raise PrologRuntimeError('tokenize: 3 args expected.', g.location)

    arg_lang    = pe.prolog_eval (args[0], g.env, g.location)
    if not isinstance(arg_lang, Predicate) or len(arg_lang.args) >0:
        raise PrologRuntimeError('tokenize: first argument: constant expected, %s found instead.' % repr(args[0]), g.location)

    arg_str     = pe.prolog_get_string   (args[1], g.env, g.location)
    arg_tokens  = pe.prolog_get_variable (args[2], g.env, g.location)

    tokens = list(map(lambda s: StringLiteral(s), tokenize(arg_str, lang=arg_lang.name)))

    g.env[arg_tokens] = ListLiteral(tokens)

    return True

def builtin_edit_distance(g, pe):

    """" edit_distance (+Tokens1, +Tokens2, -Distance) """

    pe._trace ('CALLED BUILTIN edit_distance', g)

    pred = g.terms[g.inx]
    args = pred.args
    if len(args) != 3:
        raise PrologRuntimeError('edit_distance: 3 args expected.', g.location)

    arg_tok1  = pe.prolog_get_list     (args[0], g.env, g.location)
    arg_tok2  = pe.prolog_get_list     (args[1], g.env, g.location)
    arg_dist  = pe.prolog_get_variable (args[2], g.env, g.location)

    g.env[arg_dist] = NumberLiteral(edit_distance(arg_tok1.l, arg_tok2.l))

    return True

def builtin_r_say(g, pe):

    """" r_say (+Context, +Token) """

    pe._trace ('CALLED BUILTIN r_say', g)

    pred = g.terms[g.inx]
    args = pred.args
    if len(args) != 2:
        raise PrologRuntimeError('r_say: 2 args (+Context, +Token) expected.', g.location)

    arg_context = pe.prolog_eval (args[0], g.env, g.location)
    arg_token   = pe.prolog_eval (args[1], g.env, g.location)

    # import pdb; pdb.set_trace()

    res = {}

    res = do_assertz (g.env, Clause ( Predicate('c_say', [arg_context, arg_token]) , location=g.location), res=res)

    return [ res ]

def builtin_r_sayv(g, pe):

    """" r_sayv (+Context, +Var, +Fmt) """

    pe._trace ('CALLED BUILTIN r_sayv', g)

    pred = g.terms[g.inx]
    args = pred.args
    if len(args) != 3:
        raise PrologRuntimeError('r_sayv: 3 args (+Context, +Var, +Fmt) expected.', g.location)

    arg_context = pe.prolog_eval         (args[0], g.env, g.location)
    arg_var     = pe.prolog_eval         (args[1], g.env, g.location)
    arg_fmt     = pe.prolog_get_constant (args[2], g.env, g.location)

    if not isinstance (arg_var, Literal):
        raise PrologRuntimeError(u'r_sayv: failed to eval "%s"' % unicode(args[1]), g.location)

    # import pdb; pdb.set_trace()

    res = {}

    if isinstance(arg_var, StringLiteral):
        v = arg_var.s
    else:
        v = unicode(arg_var)

    if arg_fmt == 'd':
        v = unicode(int(float(v)))
    elif arg_fmt == 'f':
        v = unicode(float(v))

    res = do_assertz (g.env, Clause ( Predicate('c_say', [arg_context, StringLiteral(v)]) , location=g.location), res=res)

    return [ res ]

def builtin_r_action(g, pe):

    """" r_action (+Context, +Action) """

    pe._trace ('CALLED BUILTIN r_action', g)

    pred = g.terms[g.inx]
    args = pred.args
    if len(args) != 2:
        raise PrologRuntimeError('r_action: 2 args (+Context, +Action) expected.', g.location)

    arg_context = pe.prolog_eval     (args[0], g.env, g.location)
    arg_action  = pe.prolog_get_list (args[1], g.env, g.location)

    # import pdb; pdb.set_trace()

    res = {}

    res = do_assertz (g.env, Clause ( Predicate('c_action', [arg_context, arg_action]) , location=g.location), res=res)

    return [ res ]

def builtin_r_score(g, pe):

    """" r_score (+Context, +Score) """

    pe._trace ('CALLED BUILTIN r_score', g)

    pred = g.terms[g.inx]
    args = pred.args
    if len(args) != 2:
        raise PrologRuntimeError('r_score: 2 args (+Context, +Score) expected.', g.location)

    arg_context = pe.prolog_eval (args[0], g.env, g.location)
    arg_score  = pe.prolog_eval (args[1], g.env, g.location)

    # import pdb; pdb.set_trace()

    res = {}
        
    res = do_assertz (g.env, Clause ( Predicate('c_score', [arg_context, arg_score]) , location=g.location), res=res)

    return [ res ]

class AIPrologRuntime(PrologRuntime):

    def __init__(self, db):

        super(AIPrologRuntime, self).__init__(db)

        # natural language processing

        self.register_builtin ('tokenize',        builtin_tokenize)            # tokenize (+Lang, +Str, -Tokens)
        self.register_builtin ('edit_distance',   builtin_edit_distance)       # edit_distance (+Str1, +Str2, -Distance)

        # response generation

        self.register_builtin ('r_say',           builtin_r_say)               # r_say (+Context, +Token)
        self.register_builtin ('r_sayv',          builtin_r_sayv)              # r_sayv (+Context, +Var, +Fmt)
        self.register_builtin ('r_action',        builtin_r_action)            # r_action (+Context, +Action)
        self.register_builtin ('r_score',         builtin_r_score)             # r_score (+Context, +Score)

        # named entity recognition (NER)

        self.register_builtin ('ner',             builtin_ner)                 # ner (+Lang, +Cat, +TS, +TE, +Tokens, -Entity, -Score)

