from pathlib import Path
from tempfile import NamedTemporaryFile

from nomenklatura.judgement import Judgement
from nomenklatura.resolver import Resolver, Identifier


def test_identifier():
    ident = Identifier.make()
    assert len(ident) > len(Identifier.PREFIX) + 5
    assert ident.id.startswith(Identifier.PREFIX)
    ident = Identifier.make("banana")
    assert ident.id == f"{Identifier.PREFIX}banana"


def test_qid_identifier():
    ident_low = Identifier("Q3481")
    ident_hi = Identifier("Q63481")
    assert ident_low.id == "Q3481"
    assert ident_hi.id == "Q63481"


def test_resolver(engine):
    resolver = Resolver.make_default(engine=engine)
    a_canon = resolver.decide("a1", "a2", Judgement.POSITIVE)
    assert a_canon.canonical, a_canon
    assert Identifier.get("a2") in resolver.connected(Identifier.get("a1"))
    assert resolver.get_judgement("a1", "a2") == Judgement.POSITIVE
    resolver.decide("b1", "b2", Judgement.POSITIVE)
    assert resolver.get_judgement("a1", "b1") == Judgement.NO_JUDGEMENT
    resolver.decide("a2", "b2", Judgement.NEGATIVE)
    assert resolver.get_judgement("a2", "b2") == Judgement.NEGATIVE
    assert resolver.get_judgement("a1", "b1") == Judgement.NEGATIVE
    resolver.suggest("a1", "b1", 7.0)
    assert resolver.get_judgement("a1", "b1") == Judgement.NEGATIVE
    assert len(list(resolver.canonicals())) == 2, list(resolver.canonicals())

    assert resolver.get_canonical("a1") == a_canon
    assert resolver.get_canonical("a2") == a_canon
    assert resolver.get_canonical("banana") == "banana"

    resolver.decide("a1", "a17", Judgement.POSITIVE)
    assert resolver.get_canonical("a1") == a_canon
    assert resolver.get_canonical("a17") == a_canon
    resolver.decide("a1", "a0", Judgement.POSITIVE)
    assert resolver.get_canonical("a1") == a_canon
    assert resolver.get_canonical("a0") == a_canon
    assert len(list(resolver.canonicals())) == 2, list(resolver.canonicals())

    resolver.decide("a1", "a42", Judgement.POSITIVE)
    assert resolver.get_canonical("a42") == a_canon
    resolver.remove("a42")
    assert resolver.get_canonical("a42") == "a42"

    resolver.suggest("c1", "c2", 7.0)
    assert resolver.get_edge("c1", "c2").score == 7.0
    resolver.suggest("c1", "c2", 8.0)
    assert resolver.get_edge("c1", "c2").score == 8.0
    ccn = resolver.decide("c1", "c2", Judgement.POSITIVE)
    assert resolver.get_edge("c1", "c2") is None
    assert resolver.get_edge(ccn, "c2").score is None

    assert "a1" in resolver.get_referents(a_canon)
    assert "a1" in resolver.get_referents(a_canon, canonicals=False)
    # assert a_canon.id in resolver.get_referents(a_canon)
    assert a_canon.id not in resolver.get_referents(a_canon, canonicals=False)
    assert ":memory:" in repr(resolver)

    resolver.explode("a1")
    assert resolver.get_canonical("a17") == "a17"
    assert resolver.get_judgement(a_canon, "a1") == Judgement.NO_JUDGEMENT
    assert resolver.get_judgement("b1", "b2") == Judgement.POSITIVE


def test_resolver_store(engine):
    resolver = Resolver.make_default(engine=engine)
    with NamedTemporaryFile("w") as fh:
        path = Path(fh.name)
        resolver.decide("a1", "a2", Judgement.POSITIVE)
        resolver.decide("a2", "b2", Judgement.NEGATIVE)
        resolver.suggest("a1", "c1", 7.0)
        resolver.save(path)

        resolver.load(path)
        assert resolver.get_edge("a1", "c1").score == 7.0


def test_resolver_candidates(engine):
    resolver = Resolver.make_default(engine=engine)
    resolver.decide("a1", "a2", Judgement.POSITIVE)
    resolver.decide("a2", "b2", Judgement.NEGATIVE)
    resolver.suggest("a1", "b2", 7.0)
    resolver.suggest("a1", "c1", 5.0)
    resolver.suggest("a1", "d1", 4.0)

    candidates = list(resolver.get_candidates())
    assert len(candidates) == 2, candidates
    assert candidates[0][2] == 5.0, candidates

    resolver.prune()
    candidates = list(resolver.get_candidates())
    assert len(candidates) == 0, candidates
