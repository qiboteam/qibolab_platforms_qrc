import pathlib
RUNCARD = pathlib.Path(__file__).parent / "qw5q_gold_qblox.yml"


def create(runcard=RUNCARD):
    """QuantWare 5q-chip controlled using qblox cluster rf."""
    from qibolab.platforms.multiqubit import MultiqubitPlatform

    return MultiqubitPlatform("qw5q_gold_qblox", runcard)
