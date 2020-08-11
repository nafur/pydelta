from .. import parser

def test_basic():
    assert parser.parse_smtlib('(reset)') == [['reset']]
